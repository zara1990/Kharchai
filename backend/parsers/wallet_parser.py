"""
EasyPaisa/JazzCash wallet screenshot parser.

The parser uses the existing OpenAI Vision integration and deliberately keeps
wallet-specific extraction separate from the receipt and utility parsers.
Missing or unreadable fields are represented as ``None``.
"""

import base64
import json
import logging
import os
from pathlib import Path
from typing import Any

from openai import AsyncOpenAI, OpenAIError

from schemas.receipt import ReceiptAnalysisResponse, ReceiptItem, ReceiptValidationReport
from schemas.wallet import WalletAnalysisResponse

logger = logging.getLogger(__name__)

WALLET_PARSER_VERSION = "wallet-parser-v1"
WALLET_PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "wallet_prompt.txt"


class WalletParser:
    """Extract structured EasyPaisa/JazzCash transaction data from an image."""

    parser_version = WALLET_PARSER_VERSION

    def __init__(self):
        api_key = os.environ.get("OPENAI_API_KEY")
        self._client = AsyncOpenAI(api_key=api_key) if api_key else None
        self._system_prompt = WALLET_PROMPT_PATH.read_text(encoding="utf-8")

    async def process(self, file) -> WalletAnalysisResponse:
        """Read an UploadFile and delegate to ``process_bytes``."""
        image_bytes: bytes = await file.read()
        return await self.process_bytes(image_bytes, file.filename, file.content_type)

    async def process_bytes(
        self,
        image_bytes: bytes,
        filename: str,
        content_type: str,
    ) -> WalletAnalysisResponse:
        """Extract nullable wallet transaction fields from image bytes."""
        base_meta = {
            "filename": filename,
            "content_type": content_type,
            "size_bytes": len(image_bytes),
        }
        empty_fields = {
            "wallet_name": None,
            "transaction_type": None,
            "amount": None,
            "currency": None,
            "counterparty": None,
            "transaction_date": None,
            "transaction_time": None,
            "transaction_reference": None,
        }

        if not self._client:
            logger.error("OPENAI_API_KEY is not set — cannot analyze wallet screenshot.")
            return WalletAnalysisResponse(
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
                    {"role": "system", "content": self._system_prompt},
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {"url": data_url, "detail": "high"},
                            },
                            {
                                "type": "text",
                                "text": "Extract the wallet transaction fields as JSON.",
                            },
                        ],
                    },
                ],
                max_tokens=900,
                timeout=30,
                response_format={"type": "json_object"},
            )
        except OpenAIError as exc:
            logger.error("OpenAI wallet API error: %s", exc)
            return WalletAnalysisResponse(
                **base_meta,
                status="error",
                message=f"OpenAI API error: {exc}",
                **empty_fields,
            )
        except Exception:
            logger.exception("Unexpected wallet analysis error.")
            return WalletAnalysisResponse(
                **base_meta,
                status="error",
                message="Unexpected error during wallet screenshot analysis.",
                **empty_fields,
            )

        raw_text = response.choices[0].message.content or ""
        try:
            data = json.loads(raw_text)
        except json.JSONDecodeError:
            logger.error("OpenAI returned non-JSON for wallet screenshot: %s", raw_text)
            return WalletAnalysisResponse(
                **base_meta,
                status="error",
                message="AI returned an invalid response. Please try again.",
                **empty_fields,
            )

        return self._build_response(base_meta, data)

    def validate(self, analysis: WalletAnalysisResponse) -> ReceiptValidationReport:
        """
        Validate wallet extraction without requiring receipt line items.

        Missing fields are warnings because screenshots may omit a timestamp,
        reference, or counterparty. A negative amount is the only hard error in
        this MVP.
        """
        warnings: list[str] = []
        errors: list[str] = []

        fields = (
            "wallet_name",
            "transaction_type",
            "amount",
            "currency",
            "counterparty",
            "transaction_date",
            "transaction_time",
            "transaction_reference",
        )
        for field_name in fields:
            value = getattr(analysis, field_name)
            if value is None or (isinstance(value, str) and not value.strip()):
                warnings.append(f"Wallet field is missing: {field_name}.")

        if analysis.amount is not None and analysis.amount < 0:
            errors.append("Wallet transaction amount cannot be negative.")

        return ReceiptValidationReport(
            valid=not errors,
            warnings=warnings,
            errors=errors,
            calculated_total=analysis.amount,
            difference=0.0 if analysis.amount is not None else None,
        )

    def to_legacy_receipt_response(
        self, analysis: WalletAnalysisResponse
    ) -> ReceiptAnalysisResponse:
        """
        Project wallet output into the unchanged public upload response shape.

        Wallet-specific fields remain available through the UFR. The optional
        single item gives legacy clients a useful transaction summary when an
        amount is present without changing the response schema.
        """
        items = None
        if analysis.amount is not None:
            items = [
                ReceiptItem(
                    item_name=analysis.transaction_type or "Wallet transaction",
                    quantity=1,
                    unit_price=analysis.amount,
                    total_price=analysis.amount,
                    category="wallet",
                )
            ]

        return ReceiptAnalysisResponse(
            status=analysis.status,
            filename=analysis.filename,
            content_type=analysis.content_type,
            size_bytes=analysis.size_bytes,
            message=analysis.message,
            merchant_name=analysis.wallet_name,
            purchase_date=analysis.transaction_date,
            currency=analysis.currency,
            total_amount=analysis.amount,
            items=items,
        )

    def _build_response(
        self, base_meta: dict[str, Any], data: Any
    ) -> WalletAnalysisResponse:
        """Coerce model fields while preserving nulls for missing values."""
        if not isinstance(data, dict):
            data = {}

        amount = data.get("amount")
        try:
            amount = float(amount) if amount is not None else None
        except (TypeError, ValueError):
            amount = None

        def text_or_none(value: Any) -> str | None:
            if value is None:
                return None
            text = str(value).strip()
            return text or None

        return WalletAnalysisResponse(
            **base_meta,
            status="analysed",
            message="Wallet screenshot analysed successfully.",
            wallet_name=text_or_none(data.get("wallet_name")),
            transaction_type=text_or_none(data.get("transaction_type")),
            amount=amount,
            currency=text_or_none(data.get("currency")),
            counterparty=text_or_none(data.get("counterparty")),
            transaction_date=text_or_none(data.get("transaction_date")),
            transaction_time=text_or_none(data.get("transaction_time")),
            transaction_reference=text_or_none(data.get("transaction_reference")),
        )