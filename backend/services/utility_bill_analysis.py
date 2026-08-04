"""
Pakistani utility-bill analysis service.

This parser is intentionally separate from ReceiptAnalysisService. It extracts
utility-bill fields with OpenAI Vision and returns a typed result with nulls
for fields that are missing or cannot be read.
"""

import base64
import json
import logging
import os
from datetime import date
from typing import Optional

from openai import AsyncOpenAI, OpenAIError
from pydantic import BaseModel

from schemas.receipt import ReceiptAnalysisResponse, ReceiptValidationReport

logger = logging.getLogger(__name__)

UTILITY_BILL_PARSER_VERSION = "utility-bill-parser-v1"

UTILITY_BILL_SYSTEM_PROMPT = """You are a Pakistani utility-bill parsing assistant.
Analyse the utility bill image and return ONLY one valid JSON object — no markdown,
no explanation, and no text outside the JSON object.

The JSON must follow this exact schema:
{
  "provider": "<string or null>",
  "bill_type": "<electricity, gas, water, internet, or other string, or null>",
  "consumer_number": "<string or null>",
  "billing_period": "<string or null>",
  "issue_date": "<YYYY-MM-DD string or null>",
  "due_date": "<YYYY-MM-DD string or null>",
  "amount_due": <number or null>,
  "currency": "<3-letter currency code or null>"
}

Rules:
- Always return valid JSON.
- Use null for any field that cannot be determined.
- Preserve consumer numbers as strings, including leading zeroes.
- Use PKR for Pakistani rupees when the bill clearly shows rupees, Rs, or PKR.
- Use YYYY-MM-DD for issue_date and due_date where possible.
- Do not invent values.
- Do not include any text outside the JSON object."""


class UtilityBillAnalysisResponse(BaseModel):
    """Structured output from the utility-bill parser."""

    status: str
    filename: str
    content_type: str
    size_bytes: int
    message: str
    provider: Optional[str] = None
    bill_type: Optional[str] = None
    consumer_number: Optional[str] = None
    billing_period: Optional[str] = None
    issue_date: Optional[str] = None
    due_date: Optional[str] = None
    amount_due: Optional[float] = None
    currency: Optional[str] = None


class UtilityBillAnalysisService:
    """
    Extract and validate Pakistani utility-bill data.

    Supported bill sources include electricity providers such as K-Electric,
    LESCO, and WAPDA, and gas providers such as SNGPL and SSGC. The parser
    does not hard-code provider-specific layouts; Vision reads the shared
    fields and gracefully returns null for missing values.
    """

    parser_version = UTILITY_BILL_PARSER_VERSION

    def __init__(self):
        api_key = os.environ.get("OPENAI_API_KEY")
        self._client = AsyncOpenAI(api_key=api_key) if api_key else None

    async def process(self, file) -> UtilityBillAnalysisResponse:
        """Read an UploadFile and delegate to ``process_bytes``."""
        image_bytes: bytes = await file.read()
        return await self.process_bytes(image_bytes, file.filename, file.content_type)

    async def process_bytes(
        self,
        image_bytes: bytes,
        filename: str,
        content_type: str,
    ) -> UtilityBillAnalysisResponse:
        """Extract structured utility-bill fields from image bytes."""
        base_meta = {
            "filename": filename,
            "content_type": content_type,
            "size_bytes": len(image_bytes),
        }
        empty_fields = {
            "provider": None,
            "bill_type": None,
            "consumer_number": None,
            "billing_period": None,
            "issue_date": None,
            "due_date": None,
            "amount_due": None,
            "currency": None,
        }

        if not self._client:
            logger.error("OPENAI_API_KEY is not set — cannot analyze utility bill.")
            return UtilityBillAnalysisResponse(
                **base_meta,
                status="error",
                message="OPENAI_API_KEY is not configured on the server.",
                **empty_fields,
            )

        b64_image = base64.b64encode(image_bytes).decode("utf-8")
        data_url = f"data:{content_type};base64,{b64_image}"

        try:
            response = await self._client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": UTILITY_BILL_SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {"url": data_url, "detail": "high"},
                            },
                            {
                                "type": "text",
                                "text": "Extract the utility-bill fields as JSON.",
                            },
                        ],
                    },
                ],
                max_tokens=800,
                timeout=30,
                response_format={"type": "json_object"},
            )
        except OpenAIError as exc:
            logger.error("OpenAI utility-bill API error: %s", exc)
            return UtilityBillAnalysisResponse(
                **base_meta,
                status="error",
                message=f"OpenAI API error: {exc}",
                **empty_fields,
            )
        except Exception as exc:
            logger.error("Unexpected utility-bill analysis error: %s", exc)
            return UtilityBillAnalysisResponse(
                **base_meta,
                status="error",
                message="Unexpected error during utility-bill analysis.",
                **empty_fields,
            )

        raw_text = response.choices[0].message.content or ""
        try:
            data = json.loads(raw_text)
        except json.JSONDecodeError:
            logger.error("OpenAI returned non-JSON for utility bill: %s", raw_text)
            return UtilityBillAnalysisResponse(
                **base_meta,
                status="error",
                message="AI returned an invalid response. Please try again.",
                **empty_fields,
            )

        return self._build_response(base_meta, data)

    def validate(
        self, analysis: UtilityBillAnalysisResponse
    ) -> ReceiptValidationReport:
        """
        Validate utility fields before UFR creation.

        Missing fields are warnings, not failures, so partially readable bills
        still produce a UFR with null values. Only contradictory numeric data
        is treated as an error.
        """
        warnings: list[str] = []
        errors: list[str] = []

        required_fields = {
            "provider": analysis.provider,
            "bill_type": analysis.bill_type,
            "consumer_number": analysis.consumer_number,
            "billing_period": analysis.billing_period,
            "issue_date": analysis.issue_date,
            "due_date": analysis.due_date,
            "amount_due": analysis.amount_due,
            "currency": analysis.currency,
        }
        for field_name, value in required_fields.items():
            if value is None or (isinstance(value, str) and not value.strip()):
                warnings.append(f"Utility bill field is missing: {field_name}.")

        if analysis.amount_due is not None and analysis.amount_due < 0:
            errors.append("Utility bill amount_due cannot be negative.")

        for field_name, value in (
            ("issue_date", analysis.issue_date),
            ("due_date", analysis.due_date),
        ):
            if value:
                try:
                    date.fromisoformat(value)
                except ValueError:
                    warnings.append(
                        f"Utility bill {field_name} is not in YYYY-MM-DD format."
                    )

        if analysis.currency and len(analysis.currency.strip()) != 3:
            warnings.append("Utility bill currency is not a 3-letter code.")

        return ReceiptValidationReport(
            valid=not errors,
            warnings=warnings,
            errors=errors,
            calculated_total=analysis.amount_due,
            difference=0.0 if analysis.amount_due is not None else None,
        )

    def to_legacy_receipt_response(
        self, analysis: UtilityBillAnalysisResponse
    ) -> ReceiptAnalysisResponse:
        """
        Project utility output into the unchanged public receipt response shape.

        Utility-specific fields remain available in the internal UFR; this
        compatibility projection prevents a breaking Upload API response change.
        """
        return ReceiptAnalysisResponse(
            status=analysis.status,
            filename=analysis.filename,
            content_type=analysis.content_type,
            size_bytes=analysis.size_bytes,
            message=analysis.message,
            merchant_name=analysis.provider,
            purchase_date=analysis.issue_date,
            currency=analysis.currency,
            total_amount=analysis.amount_due,
            items=[],
        )

    def _build_response(
        self, base_meta: dict, data: dict
    ) -> UtilityBillAnalysisResponse:
        """Coerce nullable model fields without failing the whole parse."""
        if not isinstance(data, dict):
            data = {}

        amount_due = data.get("amount_due")
        try:
            amount_due = float(amount_due) if amount_due is not None else None
        except (TypeError, ValueError):
            amount_due = None

        def text_or_none(value):
            if value is None:
                return None
            text = str(value).strip()
            return text or None

        return UtilityBillAnalysisResponse(
            **base_meta,
            status="analysed",
            message="Utility bill analysed successfully.",
            provider=text_or_none(data.get("provider")),
            bill_type=text_or_none(data.get("bill_type")),
            consumer_number=text_or_none(data.get("consumer_number")),
            billing_period=text_or_none(data.get("billing_period")),
            issue_date=text_or_none(data.get("issue_date")),
            due_date=text_or_none(data.get("due_date")),
            amount_due=amount_due,
            currency=text_or_none(data.get("currency")),
        )