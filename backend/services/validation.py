"""
Receipt Validation Service.

Validates the JSON returned by OpenAI before it reaches the Android app.
Runs as the final step in the pipeline, after image quality checking and
OpenAI extraction.

Pipeline position:
    Upload → Image Quality → OpenAI Analysis → Receipt Validation → Response
"""

import logging
from typing import Optional

from schemas.receipt import ReceiptAnalysisResponse, ReceiptValidationReport

logger = logging.getLogger(__name__)

# ── Pakistani currency aliases normalised to PKR ──────────────────────────────
# Add further local variants here as they are discovered in the wild.
PKR_ALIASES = {"rs", "rs.", "pkr", "rupees", "rupee", "روپے", "روپیہ"}

# ── Total reconciliation tolerance ───────────────────────────────────────────
# A mismatch is flagged only when it exceeds BOTH the flat and percentage floors,
# so small rounding differences on low-value receipts are not surfaced.
TOTAL_FLAT_TOLERANCE = 1.0      # ±1 currency unit (covers typical rounding)
TOTAL_PCT_TOLERANCE  = 0.02     # ±2 % of the extracted total


class ReceiptValidationService:
    """
    Validates AI-extracted receipt data against business rules.

    The single public entry point is:
        validate_receipt(receipt_json: ReceiptAnalysisResponse)
            -> ReceiptValidationReport

    The method mutates `receipt_json.currency` in place when a Pakistani
    currency alias is detected and normalises it to "PKR".
    """

    def validate_receipt(
        self, receipt_json: ReceiptAnalysisResponse
    ) -> ReceiptValidationReport:
        """
        Run all validation rules against extracted receipt data.

        Errors   → hard problems that indicate the data cannot be trusted
                   (missing total, empty items, negative prices/quantities).
        Warnings → soft issues worth surfacing to the user but not blocking
                   (missing merchant/date, total mismatch, duplicates).

        Args:
            receipt_json: The ReceiptAnalysisResponse produced by OpenAI.
                          currency field may be mutated to "PKR" if normalised.

        Returns:
            ReceiptValidationReport with valid flag, warnings, errors,
            calculated_total, and difference from extracted total.
        """
        warnings: list[str] = []
        errors:   list[str] = []
        calculated_total: Optional[float] = None
        subtotal_difference: Optional[float] = None
        difference:       Optional[float] = None

        # ── A. Merchant name ─────────────────────────────────────────────────
        if not receipt_json.merchant_name or not receipt_json.merchant_name.strip():
            warnings.append("Merchant name is missing from the receipt.")

        # ── B. Purchase date ─────────────────────────────────────────────────
        if not receipt_json.purchase_date or not receipt_json.purchase_date.strip():
            warnings.append("Purchase date is missing from the receipt.")

        # TODO: validate purchase_date conforms to YYYY-MM-DD (future rule).

        # ── C. Total amount — hard error ─────────────────────────────────────
        if receipt_json.total_amount is None:
            errors.append("Total amount is missing from the receipt.")
        elif (
            receipt_json.reported_total_amount is not None
            and receipt_json.grand_total_amount is not None
            and receipt_json.reported_total_amount != receipt_json.grand_total_amount
        ):
            warnings.append(
                "Reported total conflicts with the extracted grand total; "
                "the grand total is used as the final payable amount."
            )

        # ── D. Items list — hard error ───────────────────────────────────────
        if not receipt_json.items:
            errors.append("No line items were extracted from the receipt.")

        # ── E–H require at least one item ────────────────────────────────────
        if receipt_json.items:
            seen_names: set[str] = set()

            for item in receipt_json.items:
                name_key = (item.item_name or "").strip().lower()

                # E. Negative total / unit price ─────────────────────────────
                if item.total_price is None:
                    errors.append(
                        f"Line-item amount is missing for '{item.item_name}'."
                    )
                elif item.total_price < 0:
                    errors.append(
                        f"Negative total price for '{item.item_name}': {item.total_price}."
                    )
                if item.unit_price is not None and item.unit_price < 0:
                    errors.append(
                        f"Negative unit price for '{item.item_name}': {item.unit_price}."
                    )

                # F. Negative quantity ────────────────────────────────────────
                if item.quantity is not None and item.quantity < 0:
                    errors.append(
                        f"Negative quantity for '{item.item_name}': {item.quantity}."
                    )

                # H. Duplicate detection (collect names first) ────────────────
                if name_key in seen_names:
                    warnings.append(
                        f"Duplicate line item detected: '{item.item_name}'."
                    )
                seen_names.add(name_key)

            # G. Total reconciliation ─────────────────────────────────────────
            if all(item.total_price is not None for item in receipt_json.items):
                calculated_total = round(
                    sum(
                        item.total_price
                        for item in receipt_json.items
                        if item.total_price is not None
                    ),
                    2,
                )

                if receipt_json.subtotal_amount is not None:
                    raw_subtotal_diff = abs(
                        calculated_total - receipt_json.subtotal_amount
                    )
                    subtotal_tolerance = max(
                        TOTAL_FLAT_TOLERANCE,
                        abs(receipt_json.subtotal_amount) * TOTAL_PCT_TOLERANCE,
                    )
                    subtotal_difference = round(raw_subtotal_diff, 2)
                    if raw_subtotal_diff > subtotal_tolerance:
                        warnings.append(
                            f"Calculated subtotal ({calculated_total}) differs from "
                            f"extracted subtotal ({receipt_json.subtotal_amount}) by "
                            f"{subtotal_difference}."
                        )

                if receipt_json.total_amount is not None:
                    base_total = (
                        receipt_json.subtotal_amount
                        if receipt_json.subtotal_amount is not None
                        else calculated_total
                    )
                    expected_final_total = base_total + (
                        receipt_json.service_charge or 0
                    )
                    raw_diff = abs(expected_final_total - receipt_json.total_amount)
                    tolerance = max(
                        TOTAL_FLAT_TOLERANCE,
                        abs(receipt_json.total_amount) * TOTAL_PCT_TOLERANCE,
                    )
                    difference = round(raw_diff, 2)
                    if raw_diff > tolerance:
                        warnings.append(
                            f"Calculated final total ({expected_final_total}) differs "
                            f"from extracted total ({receipt_json.total_amount}) by "
                            f"{difference}."
                        )

        if receipt_json.service_charge is not None and receipt_json.service_charge < 0:
            errors.append(
                f"Negative service charge: {receipt_json.service_charge}."
            )

        # ── I. Pakistani currency normalisation ──────────────────────────────
        if receipt_json.currency:
            if receipt_json.currency.strip().lower() in PKR_ALIASES:
                receipt_json.currency = "PKR"
        # Foreign currencies (USD, EUR, GBP, …) are left unchanged.

        # TODO: Add future validation rules below this line:
        #   - Validate currency against ISO 4217 whitelist.
        #   - Validate item categories against an allowed taxonomy.
        #   - Flag outlier amounts (unusually high single items).
        #   - Cross-check merchant name against a known store registry.
        #   - Validate GST / tax line items for Pakistani fiscal compliance.

        logger.debug(
            "Validation complete — errors=%d warnings=%d calculated_total=%s",
            len(errors), len(warnings), calculated_total,
        )

        return ReceiptValidationReport(
            valid=len(errors) == 0,
            warnings=warnings,
            errors=errors,
            calculated_total=calculated_total,
            subtotal_difference=subtotal_difference,
            service_charge=receipt_json.service_charge,
            difference=difference,
        )
