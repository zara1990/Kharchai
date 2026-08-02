"""
KharchAI services package.

Exports:
    ImageQualityService        — image quality checks (OpenCV)
    DocumentClassifierService  — lightweight financial document classifier
    ReceiptAnalysisService     — OpenAI Vision extraction
    NormalizationService       — canonical schema normalizer (pass-through for receipts)
    UniversalFinancialRecordMapper — parser output to canonical UFR mapping
    ReceiptValidationService   — extracted-data validation
"""

from services.document_classifier import DocumentClassifierService
from services.image_quality import ImageQualityService
from services.normalization import NormalizationService
from services.receipt_analysis import ReceiptAnalysisService
from services.ufr_mapper import UniversalFinancialRecordMapper
from services.validation import ReceiptValidationService

__all__ = [
    "ImageQualityService",
    "DocumentClassifierService",
    "ReceiptAnalysisService",
    "NormalizationService",
    "UniversalFinancialRecordMapper",
    "ReceiptValidationService",
]
