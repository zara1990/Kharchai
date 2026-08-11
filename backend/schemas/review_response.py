"""Frontend-friendly response schema for the Android human-review screen."""

from typing import Any, List, Optional

from pydantic import BaseModel, Field

from schemas.receipt import (
    ImageQualityReport,
    ReceiptAnalysisResponse,
    ReceiptValidationReport,
)
from schemas.ufr import ReviewHint


class EditableField(BaseModel):
    """One editable extracted value presented to the review UI."""

    value: Any = None
    editable: bool = True
    confidence: Optional[float] = None


class ReviewResponseItem(BaseModel):
    """An extracted purchase or wallet transaction item."""

    description: str
    amount: Optional[float] = None
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    category: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ReviewResponse(BaseModel):
    """
    Frontend-friendly response for the Android Review Screen.

    The legacy upload fields remain embedded for compatibility with clients
    that already consume the receipt-shaped response.
    """

    document_type: str
    original_image_reference: Optional[str] = None
    editable_fields: dict[str, EditableField] = Field(default_factory=dict)
    extracted_items: List[ReviewResponseItem] = Field(default_factory=list)
    validation_warnings: List[str] = Field(default_factory=list)
    review_hints: List[ReviewHint] = Field(default_factory=list)
    overall_confidence: Optional[float] = None
    processing_metadata: dict[str, Any] = Field(default_factory=dict)

    # Backward-compatible fields from ReceiptUploadResponse.
    status: str
    quality: Optional[ImageQualityReport] = None
    validation: Optional[ReceiptValidationReport] = None
    receipt: Optional[ReceiptAnalysisResponse] = None