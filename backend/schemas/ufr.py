"""
Universal Financial Record (UFR) schema.

UFR is the canonical internal representation for financial documents. Parsers
for receipts, utility bills, wallet screenshots, bank statements, and future
document types should map their output into this schema before downstream
storage, calculations, or reasoning are added.
"""

from typing import Any, List, Optional

from pydantic import BaseModel, Field


class UniversalFinancialRecordItem(BaseModel):
    """Generic line item that can represent a purchase or a transaction."""

    description: str
    amount: Optional[float] = None
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    category: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class UniversalFinancialRecordMetadata(BaseModel):
    """Processing provenance, quality, and deterministic review information."""

    source: str
    confidence: Optional[float] = None
    confidence_level: Optional[str] = None
    review_required: Optional[bool] = None
    quality_score: Optional[int] = None
    parser_version: str


class UniversalFinancialRecord(BaseModel):
    """
    Canonical internal financial record shared by all document parsers.

    Fields are intentionally document-agnostic. For example, ``merchant`` may
    be a utility provider, ``items`` may contain bank transactions, and
    ``payment_method`` may remain unset when a source document does not expose
    it.
    """

    record_id: str
    document_type: str
    merchant: Optional[str] = None
    document_date: Optional[str] = None
    currency: Optional[str] = None
    total_amount: Optional[float] = None
    payment_method: Optional[str] = None
    category: Optional[str] = None
    items: List[UniversalFinancialRecordItem] = Field(default_factory=list)
    metadata: UniversalFinancialRecordMetadata