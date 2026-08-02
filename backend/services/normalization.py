"""
Normalization Service — KharchAI Milestone 7A.1

Receives the raw AI extraction output and normalises it into a canonical
financial document schema.

MVP behaviour
-------------
For receipts, the extraction schema IS the canonical schema, so this service
is a transparent pass-through.  Future document types (invoices, bank
statements, utility bills, wallet screenshots) will each require a dedicated
normalizer that maps their extractor's output into this same structure.

Extension points
----------------
Add a branch inside ``normalize()`` keyed on ``document_type`` to plug in a
document-specific normalizer without touching the rest of the pipeline.
"""

import logging

from schemas.receipt import ReceiptAnalysisResponse

logger = logging.getLogger(__name__)


class NormalizationService:
    """
    Normalises AI extraction output into the canonical financial document schema.

    Currently a pass-through for receipts.  As new document types are added,
    each gets its own normalisation branch here.

    Usage
    -----
    ::

        normalizer = NormalizationService()
        normalized = normalizer.normalize(receipt_analysis, document_type="receipt")
    """

    def normalize(
        self,
        analysis: ReceiptAnalysisResponse,
        document_type: str = "receipt",
    ) -> ReceiptAnalysisResponse:
        """
        Normalize the extraction result for the given document type.

        Args:
            analysis:      Output from ReceiptAnalysisService (or a future
                           document-type-specific extractor).
            document_type: Classifier result string (e.g. "receipt", "invoice").

        Returns:
            Normalised ReceiptAnalysisResponse (same schema, potentially with
            fields remapped or filled in from document-type-specific logic).
        """
        if document_type == "receipt":
            # ── Receipt: schema is already canonical — pass through ────────────
            # Future: add light field-level fixes here (e.g. date format coercion,
            # merchant name title-casing) without changing the overall structure.
            logger.debug("NormalizationService: receipt — pass-through.")
            return analysis

        # ── Future plug-in points ─────────────────────────────────────────────
        # Add elif branches for each new document type as its extractor is built.
        #
        # elif document_type == "invoice":
        #     return self._normalize_invoice(analysis)
        #
        # elif document_type == "bank_statement":
        #     return self._normalize_bank_statement(analysis)
        #
        # elif document_type == "wallet_screenshot":
        #     return self._normalize_wallet_screenshot(analysis)
        #
        # elif document_type == "utility_bill":
        #     return self._normalize_utility_bill(analysis)

        # Fallback: unknown/unsupported type — return as-is with a warning.
        logger.warning(
            "NormalizationService: no normalizer for document_type=%r — returning as-is.",
            document_type,
        )
        return analysis
