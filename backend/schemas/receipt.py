from typing import List, Optional

from pydantic import BaseModel


class ReceiptItem(BaseModel):
    item_name: str
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    total_price: float
    category: str


class ReceiptAnalysisResponse(BaseModel):
    # ── File metadata (always present) ──────────────────────────────────────
    status: str          # "analysed" | "error"
    filename: str
    content_type: str
    size_bytes: int
    message: str

    # ── AI-extracted fields (None when analysis failed) ──────────────────────
    merchant_name: Optional[str] = None
    purchase_date: Optional[str] = None   # ISO-8601 date string where possible
    currency: Optional[str] = None        # e.g. "PKR", "USD"
    total_amount: Optional[float] = None
    items: Optional[List[ReceiptItem]] = None
