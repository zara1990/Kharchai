"""
Mappers for converting parser-specific output into Universal Financial Records.

The receipt mapper is the first adapter in this layer. Future document parsers
should add their own mapper methods here (or in focused mapper modules) while
returning the same UniversalFinancialRecord schema.
"""

from uuid import uuid4

from schemas.receipt import ReceiptAnalysisResponse
from schemas.ufr import (
    UniversalFinancialRecord,
    UniversalFinancialRecordItem,
    UniversalFinancialRecordMetadata,
)
from services.utility_bill_analysis import (
    UTILITY_BILL_PARSER_VERSION,
    UtilityBillAnalysisResponse,
)


CONFIDENCE_SCORES = {
    "high": 0.9,
    "medium": 0.6,
    "low": 0.3,
}


class UniversalFinancialRecordMapper:
    """Converts document parser responses into the canonical UFR schema."""

    def from_receipt_analysis(
        self,
        analysis: ReceiptAnalysisResponse,
        *,
        document_type: str = "receipt",
        source: str = "receipt_analysis",
        confidence: str | float | None = None,
        quality_score: int | None = None,
        parser_version: str = "receipt-parser-v1",
    ) -> UniversalFinancialRecord:
        """
        Map the existing receipt analysis response into a UFR.

        This adapter deliberately does not change the receipt analysis object.
        It creates a separate canonical record for downstream consumers.
        """
        if isinstance(confidence, str):
            confidence_value = CONFIDENCE_SCORES.get(confidence.lower())
        else:
            confidence_value = confidence

        items = [
            UniversalFinancialRecordItem(
                description=item.item_name,
                amount=item.total_price,
                quantity=item.quantity,
                unit_price=item.unit_price,
                category=item.category,
            )
            for item in (analysis.items or [])
        ]

        return UniversalFinancialRecord(
            record_id=str(uuid4()),
            document_type=document_type,
            merchant=analysis.merchant_name,
            document_date=analysis.purchase_date,
            currency=analysis.currency,
            total_amount=analysis.total_amount,
            # ReceiptAnalysisResponse does not currently extract payment method.
            payment_method=None,
            category=None,
            items=items,
            metadata=UniversalFinancialRecordMetadata(
                source=source,
                confidence=confidence_value,
                quality_score=quality_score,
                parser_version=parser_version,
            ),
        )

    def from_utility_bill_analysis(
        self,
        analysis: UtilityBillAnalysisResponse,
        *,
        confidence: str | float | None = None,
        quality_score: int | None = None,
    ) -> UniversalFinancialRecord:
        """Map utility-specific extraction into the unchanged generic UFR."""
        if isinstance(confidence, str):
            confidence_value = CONFIDENCE_SCORES.get(confidence.lower())
        else:
            confidence_value = confidence

        utility_metadata = {
            "consumer_number": analysis.consumer_number,
            "billing_period": analysis.billing_period,
            "issue_date": analysis.issue_date,
            "due_date": analysis.due_date,
        }
        items = []
        if analysis.bill_type or analysis.amount_due is not None:
            items.append(
                UniversalFinancialRecordItem(
                    description=analysis.bill_type or "Utility bill",
                    amount=analysis.amount_due,
                    category="utilities",
                    metadata=utility_metadata,
                )
            )

        return UniversalFinancialRecord(
            record_id=str(uuid4()),
            document_type="utility_bill",
            merchant=analysis.provider,
            document_date=analysis.issue_date,
            currency=analysis.currency,
            total_amount=analysis.amount_due,
            payment_method=None,
            category="utilities",
            items=items,
            metadata=UniversalFinancialRecordMetadata(
                source="utility_bill_analysis",
                confidence=confidence_value,
                quality_score=quality_score,
                parser_version=UTILITY_BILL_PARSER_VERSION,
            ),
        )