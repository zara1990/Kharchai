from fastapi import APIRouter, File, HTTPException, UploadFile, status

from schemas.receipt import ReceiptUploadResponse
from services.document_classifier import DocumentClassifierService
from services.image_quality import ImageQualityService
from services.normalization import NormalizationService
from services.receipt_analysis import ReceiptAnalysisService
from services.ufr_mapper import UniversalFinancialRecordMapper
from services.validation import ReceiptValidationService

router = APIRouter(prefix="/api/v1/receipt", tags=["Receipt"])

ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "image/bmp",
    "image/tiff",
}

_quality_service     = ImageQualityService()
_classifier_service  = DocumentClassifierService()
_receipt_service     = ReceiptAnalysisService()
_normalization_service = NormalizationService()
_ufr_mapper          = UniversalFinancialRecordMapper()
_validation_service  = ReceiptValidationService()


@router.post(
    "/upload",
    response_model=ReceiptUploadResponse,
    summary="Upload a financial document image for AI analysis",
    description=(
        "Accepts a financial document image (JPEG, PNG, GIF, WebP, BMP, TIFF). "
        "Pipeline: content-type check → image quality validation → "
        "document classification → OpenAI Vision extraction → "
        "schema normalisation → receipt validation → JSON response.\n\n"
        "Returns HTTP 415 for unsupported MIME types. "
        "Returns HTTP 400 if image quality fails. "
        "Returns HTTP 400 with `status='unsupported_document'` if the image is "
        "not a receipt (invoice, bank statement, wallet screenshot, and utility "
        "bill support is planned). "
        "On success, returns quality report, validation report, and extracted receipt data."
    ),
)
async def upload_receipt(file: UploadFile = File(...)):
    # ── 1. Content-type gate ──────────────────────────────────────────────────
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail={
                "error": "Unsupported file type",
                "received": file.content_type,
                "allowed": sorted(ALLOWED_IMAGE_TYPES),
            },
        )

    # ── 2. Read bytes once (reused by all services) ───────────────────────────
    image_bytes = await file.read()

    # ── 3. Image quality validation ───────────────────────────────────────────
    quality = _quality_service.validate_image(image_bytes)

    if not quality.passed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Image quality check failed",
                "quality": quality.model_dump(),
            },
        )

    # ── 4. Document classification ────────────────────────────────────────────
    # Determines the document type so the pipeline can route to the correct
    # extractor.  Currently only "receipt" is fully supported; all other types
    # return HTTP 400 with an informative message.
    #
    # Future plug-in point: when a new extractor is ready (e.g. invoice),
    # add a branch here to call it instead of raising HTTP 400.
    classification = _classifier_service.classify_document(image_bytes)

    if classification.document_type != "receipt":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "status": "unsupported_document",
                "document_type": classification.document_type,
                "message": "This document type is planned but not yet supported.",
            },
        )

    # ── 5. OpenAI Vision extraction ───────────────────────────────────────────
    # Future plug-in point: swap ReceiptAnalysisService for a document-type-
    # specific extractor (e.g. InvoiceAnalysisService) based on classification.
    receipt = await _receipt_service.process_bytes(
        image_bytes, file.filename, file.content_type
    )

    # ── 6. Schema normalisation ───────────────────────────────────────────────
    # Pass-through for receipts; future document types will remap fields here.
    receipt = _normalization_service.normalize(receipt, classification.document_type)

    # ── 7. Universal Financial Record mapping ──────────────────────────────────
    # The UFR is the canonical internal representation. The legacy receipt
    # response remains separate so the current API contract is unchanged.
    # Future parsers (utility bill, wallet, bank statement) should map their
    # parser-specific output into UniversalFinancialRecord at this boundary.
    ufr = _ufr_mapper.from_receipt_analysis(
        receipt,
        document_type=classification.document_type,
        confidence=classification.confidence,
        quality_score=quality.quality_score,
    )

    # ── 8. Receipt validation (runs even when OpenAI returned an error status,
    #        so the caller always gets a validation block in the response) ──────
    validation = _validation_service.validate_receipt(receipt)

    # Keep the local variable explicit until downstream UFR consumers are added.
    # The object is intentionally not added to this response to avoid an API
    # contract change for existing clients.
    _ = ufr

    # ── 9. Return combined response ───────────────────────────────────────────
    return ReceiptUploadResponse(
        status=receipt.status,   # "analysed" | "error"
        quality=quality,
        validation=validation,
        receipt=receipt,
    )
