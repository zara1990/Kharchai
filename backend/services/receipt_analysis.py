import base64
import json
import logging
import os

from openai import AsyncOpenAI, OpenAIError

from schemas.receipt import ReceiptAnalysisResponse, ReceiptItem

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a receipt-parsing assistant.
Analyse the receipt image and return ONLY a valid JSON object — no markdown, no explanation.

The JSON must follow this exact schema:
{
  "merchant_name": "<string or null>",
  "purchase_date": "<ISO-8601 date string or null>",
  "currency": "<3-letter currency code or null>",
  "subtotal_amount": <number or null>,
  "service_charge": <number or null>,
  "grand_total_amount": <number or null>,
  "total_amount": <number or null>,
  "items": [
    {
      "item_name": "<string>",
      "quantity": <number or null>,
      "unit_price": <number or null>,
      "total_price": <number or null>,
      "category": "<best-guess category string>"
    }
  ]
}

Rules:
- Always return valid JSON.
- Use null for any field you cannot determine.
- Never calculate or infer a missing amount, quantity, subtotal, service charge,
  grand total, or total. If it is unreadable, return null.
- currency should be a 3-letter ISO code (e.g. PKR, USD, GBP).
- purchase_date should be YYYY-MM-DD where possible.
- For receipt tables with columns such as "Description | Rate | Qty | Amount":
  - map Rate to unit_price;
  - map Qty to quantity;
  - map Amount to total_price, the line total.
- Never substitute Rate for Amount. Never use Rate as total_price just because
  the Amount column is difficult to read. Never calculate total_price as
  unit_price multiplied by quantity; return null when Amount is unreadable.
- Keep subtotal_amount, service_charge, and grand_total_amount separate.
  Service charges are not line items.
- Set total_amount to the final payable amount printed as Grand Total, G.Total,
  Final Total, or an equivalent final-total label. It must match
  grand_total_amount when that field is present.
- Do not include any text outside the JSON object."""


class ReceiptAnalysisService:
    """
    Responsible for OpenAI Vision extraction.

    Sends a receipt image to gpt-4.1-mini and returns structured
    financial data (merchant, date, currency, total, line items).
    """

    def __init__(self):
        api_key = os.environ.get("OPENAI_API_KEY")
        self._client = AsyncOpenAI(api_key=api_key) if api_key else None

    async def process(self, file) -> ReceiptAnalysisResponse:
        """
        Convenience wrapper: reads bytes from an UploadFile then delegates
        to process_bytes().  Kept for backward compatibility.
        """
        image_bytes: bytes = await file.read()
        return await self.process_bytes(image_bytes, file.filename, file.content_type)

    async def process_bytes(
        self,
        image_bytes: bytes,
        filename: str,
        content_type: str,
    ) -> ReceiptAnalysisResponse:
        """
        Send pre-read image bytes to OpenAI Vision and return structured data.

        This is the primary entry point when the caller has already read the
        bytes (e.g. the route layer read them for quality checking first).

        Args:
            image_bytes:  Raw image bytes.
            filename:     Original file name (for the response metadata).
            content_type: MIME type string (e.g. "image/jpeg").

        Returns:
            ReceiptAnalysisResponse with file metadata and AI-extracted fields.
        """
        base_meta = dict(
            filename=filename,
            content_type=content_type,
            size_bytes=len(image_bytes),
        )

        if not self._client:
            logger.error("OPENAI_API_KEY is not set — cannot perform analysis.")
            return ReceiptAnalysisResponse(
                **base_meta,
                status="error",
                message="OPENAI_API_KEY is not configured on the server.",
            )

        # Base64-encode the image for the Vision API.
        b64_image = base64.b64encode(image_bytes).decode("utf-8")
        data_url = f"data:{content_type};base64,{b64_image}"

        try:
            response = await self._client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {"url": data_url, "detail": "high"},
                            },
                            {
                                "type": "text",
                                "text": "Extract all receipt data and return it as JSON.",
                            },
                        ],
                    },
                ],
                max_tokens=1024,
                timeout=30,
            )
        except OpenAIError as exc:
            logger.error("OpenAI API error: %s", exc)
            return ReceiptAnalysisResponse(
                **base_meta,
                status="error",
                message=f"OpenAI API error: {exc}",
            )
        except Exception as exc:
            logger.error("Unexpected error calling OpenAI: %s", exc)
            return ReceiptAnalysisResponse(
                **base_meta,
                status="error",
                message="Unexpected error during AI analysis.",
            )

        raw_text = response.choices[0].message.content or ""

        try:
            data = json.loads(raw_text)
        except json.JSONDecodeError:
            logger.error("OpenAI returned non-JSON: %s", raw_text)
            return ReceiptAnalysisResponse(
                **base_meta,
                status="error",
                message="AI returned an invalid response. Please try again.",
            )

        # Parse items list, tolerating missing or malformed entries.
        items = None
        raw_items = data.get("items")
        if isinstance(raw_items, list):
            items = []
            for entry in raw_items:
                if not isinstance(entry, dict):
                    continue
                try:
                    items.append(
                        ReceiptItem(
                            item_name=str(entry.get("item_name", "Unknown")),
                            quantity=entry.get("quantity"),
                            unit_price=entry.get("unit_price"),
                            total_price=entry.get("total_price"),
                            category=str(entry.get("category", "Uncategorised")),
                        )
                    )
                except Exception:
                    continue  # Skip malformed individual items

        reported_total_amount = data.get("total_amount")
        grand_total_amount = data.get("grand_total_amount")

        return ReceiptAnalysisResponse(
            **base_meta,
            status="analysed",
            message="Receipt analysed successfully.",
            merchant_name=data.get("merchant_name"),
            purchase_date=data.get("purchase_date"),
            currency=data.get("currency"),
            subtotal_amount=data.get("subtotal_amount"),
            service_charge=data.get("service_charge"),
            grand_total_amount=grand_total_amount,
            total_amount=(
                grand_total_amount
                if grand_total_amount is not None
                else reported_total_amount
            ),
            reported_total_amount=reported_total_amount,
            items=items,
        )
