"""Validation and persistence for user-approved Universal Financial Records."""

from __future__ import annotations

import math
from decimal import Decimal, InvalidOperation
from typing import Any

from schemas.ufr import UniversalFinancialRecord
from services.supabase_client import (
    SupabaseClient,
    get_supabase_client,
)


class FinancialRecordValidationError(ValueError):
    """Raised when a reviewed UFR fails persistence-specific validation."""

    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        super().__init__("; ".join(errors))


class FinancialRecordPersistenceService:
    """Validate and save a canonical UFR without invoking parsing or AI."""

    TOTAL_FLAT_TOLERANCE = Decimal("1.00")
    TOTAL_PERCENT_TOLERANCE = Decimal("0.02")

    def __init__(self, client: SupabaseClient | None = None) -> None:
        self._client = client

    def save(self, record: UniversalFinancialRecord) -> None:
        """Validate and insert a UFR, preserving duplicate-ID safety."""
        self.validate(record)
        self.client.insert_financial_record(self.to_database_payload(record))

    @property
    def client(self) -> SupabaseClient:
        return self._client or get_supabase_client()

    @classmethod
    def validate(cls, record: UniversalFinancialRecord) -> None:
        """Apply UFR, database, and reviewed-total consistency checks."""
        errors: list[str] = []

        if not record.record_id.strip():
            errors.append("record_id must not be blank.")
        if not record.document_type.strip():
            errors.append("document_type must not be blank.")
        if not record.metadata.source.strip():
            errors.append("metadata.source must not be blank.")
        if not record.metadata.parser_version.strip():
            errors.append("metadata.parser_version must not be blank.")

        numeric_values: list[tuple[str, float | None]] = [
            ("total_amount", record.total_amount),
            ("confidence", record.metadata.confidence),
            ("metadata.subtotal_amount", record.metadata.subtotal_amount),
            ("metadata.service_charge", record.metadata.service_charge),
            ("metadata.grand_total_amount", record.metadata.grand_total_amount),
        ]
        for index, item in enumerate(record.items):
            numeric_values.extend(
                [
                    (f"items[{index}].amount", item.amount),
                    (f"items[{index}].quantity", item.quantity),
                    (f"items[{index}].unit_price", item.unit_price),
                ]
            )

        for field_name, value in numeric_values:
            if value is not None and not math.isfinite(value):
                errors.append(f"{field_name} must be a finite number.")

        confidence = record.metadata.confidence
        if confidence is not None and not 0 <= confidence <= 1:
            errors.append("metadata.confidence must be between 0 and 1.")

        item_amounts = [item.amount for item in record.items]
        if record.total_amount is not None and item_amounts and all(
            amount is not None for amount in item_amounts
        ):
            calculated_total = sum(
                (cls._decimal(amount) for amount in item_amounts if amount is not None),
                Decimal("0"),
            )
            if record.metadata.subtotal_amount is not None:
                subtotal_difference = abs(
                    calculated_total
                    - cls._decimal(record.metadata.subtotal_amount)
                )
                subtotal_tolerance = max(
                    cls.TOTAL_FLAT_TOLERANCE,
                    abs(cls._decimal(record.metadata.subtotal_amount))
                    * cls.TOTAL_PERCENT_TOLERANCE,
                )
                if subtotal_difference > subtotal_tolerance:
                    errors.append(
                        "subtotal_amount does not reconcile with the submitted item amounts."
                    )
            submitted_total = cls._decimal(record.total_amount)
            expected_total = (
                cls._decimal(record.metadata.subtotal_amount)
                if record.metadata.subtotal_amount is not None
                else calculated_total
            ) + (
                cls._decimal(record.metadata.service_charge)
                if record.metadata.service_charge is not None
                else Decimal("0")
            )
            difference = abs(expected_total - submitted_total)
            tolerance = max(
                cls.TOTAL_FLAT_TOLERANCE,
                abs(submitted_total) * cls.TOTAL_PERCENT_TOLERANCE,
            )
            if difference > tolerance:
                errors.append(
                    "total_amount does not reconcile with the submitted item amounts."
                )

        if errors:
            raise FinancialRecordValidationError(errors)

    @staticmethod
    def to_database_payload(record: UniversalFinancialRecord) -> dict[str, Any]:
        """Map UFR fields exactly to the existing financial_records columns."""
        return {
            "id": record.record_id,
            "document_type": record.document_type,
            "source": record.metadata.source,
            "transaction_date": record.document_date,
            "merchant_provider": record.merchant,
            "amount": record.total_amount,
            "currency": record.currency,
            "category": record.category,
            "payment_method": record.payment_method,
            "items": [
                item.model_dump(mode="json")
                for item in record.items
            ],
            "metadata": record.metadata.model_dump(mode="json"),
            "confidence": record.metadata.confidence,
            "parser_version": record.metadata.parser_version,
        }

    @staticmethod
    def _decimal(value: float) -> Decimal:
        try:
            return Decimal(str(value))
        except (InvalidOperation, ValueError) as exc:
            raise FinancialRecordValidationError(
                ["Financial record contains an invalid numeric value."]
            ) from exc