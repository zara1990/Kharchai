"""State carried between financial-document pipeline stages."""

from dataclasses import dataclass, field
from typing import Any, Optional

from schemas.receipt import (
    ImageQualityReport,
    ReceiptAnalysisResponse,
    ReceiptUploadResponse,
    ReceiptValidationReport,
)
from schemas.ufr import UniversalFinancialRecord
from services.document_classifier import DocumentClassificationResult


@dataclass
class PipelineContext:
    """Mutable processing state shared by all pipeline stages."""

    image_bytes: bytes
    filename: str
    content_type: str

    quality_report: Optional[ImageQualityReport] = None
    classification: Optional[DocumentClassificationResult] = None
    document_type: Optional[str] = None
    parser_output: Optional[Any] = None
    legacy_receipt_output: Optional[ReceiptAnalysisResponse] = None
    validation_result: Optional[ReceiptValidationReport] = None
    universal_record: Optional[UniversalFinancialRecord] = None
    warnings: list[str] = field(default_factory=list)
    final_response: Optional[ReceiptUploadResponse] = None