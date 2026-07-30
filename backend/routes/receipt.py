from fastapi import APIRouter, File, HTTPException, UploadFile, status

from schemas.receipt import ReceiptUploadResponse
from services.image_quality import ImageQualityService
from services.receipt_analysis import ReceiptAnalysisService
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

_quality_service    = ImageQualityService()
_receipt_service    = ReceiptAnalysisService()
_validation_service = ReceiptValidationService()


@router.post(
    "/upload",
    response_model=ReceiptUploadResponse,
    summary="Upload a receipt image for AI analysis",
    description=(
        "Accepts a receipt image (JPEG, PNG, GIF, WebP, BMP, TIFF). "
        "Pipeline: content-type check → image quality validation → "
        "OpenAI Vision extraction → receipt validation → JSON response. "
        "Returns HTTP 400 if image quality fails. "
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

    # ── 4. OpenAI Vision extraction ───────────────────────────────────────────
    receipt = await _receipt_service.process_bytes(
        image_bytes, file.filename, file.content_type
    )

    # ── 5. Receipt validation (runs even when OpenAI returned an error status,
    #        so the caller always gets a validation block in the response) ──────
    validation = _validation_service.validate_receipt(receipt)

    # ── 6. Return combined response ───────────────────────────────────────────
    return ReceiptUploadResponse(
        status=receipt.status,   # "analysed" | "error"
        quality=quality,
        validation=validation,
        receipt=receipt,
    )
