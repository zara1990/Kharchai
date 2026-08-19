from typing import List, Optional

from pydantic import BaseModel


# ── Line-item schema ──────────────────────────────────────────────────────────

class ReceiptItem(BaseModel):
    item_name: str
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    total_price: Optional[float] = None
    category: str


# ── AI extraction result ──────────────────────────────────────────────────────

class ReceiptAnalysisResponse(BaseModel):
    # File metadata (always present)
    status: str          # "analysed" | "error"
    filename: str
    content_type: str
    size_bytes: int
    message: str

    # AI-extracted fields (None when analysis failed)
    merchant_name: Optional[str] = None
    purchase_date: Optional[str] = None   # ISO-8601 date string where possible
    currency: Optional[str] = None        # e.g. "PKR", "USD"
    subtotal_amount: Optional[float] = None
    service_charge: Optional[float] = None
    grand_total_amount: Optional[float] = None
    # Always the final payable amount. For receipts with service charges, this
    # is the printed grand/final total rather than the line-item subtotal.
    total_amount: Optional[float] = None
    # Preserves the model's raw total_amount when grand_total_amount is used to
    # deterministically select the final payable total.
    reported_total_amount: Optional[float] = None
    items: Optional[List[ReceiptItem]] = None


# ── Image quality report ──────────────────────────────────────────────────────

class ImageQualityReport(BaseModel):
    passed: bool
    warnings: List[str]
    errors: List[str]
    is_long_receipt: bool
    quality_score: int             # 0–100


# ── Receipt validation report ─────────────────────────────────────────────────

class ReceiptValidationReport(BaseModel):
    valid: bool
    warnings: List[str]
    errors: List[str]
    calculated_total: Optional[float] = None   # sum of line-item total_prices
    subtotal_difference: Optional[float] = None
    service_charge: Optional[float] = None
    difference: Optional[float] = None         # final-total reconciliation difference


# ── Top-level upload response ─────────────────────────────────────────────────

class ReceiptUploadResponse(BaseModel):
    status: str                                        # "analysed" | "error"
    quality: ImageQualityReport
    validation: Optional[ReceiptValidationReport] = None  # None if OpenAI failed
    receipt: Optional[ReceiptAnalysisResponse] = None
