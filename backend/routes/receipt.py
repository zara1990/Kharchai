from fastapi import APIRouter, File, HTTPException, UploadFile, status

from schemas.receipt import ReceiptUploadResponse
from services.image_quality import ImageQualityService
from services.receipt_analysis import ReceiptAnalysisService

router = APIRouter(prefix="/api/v1/receipt", tags=["Receipt"])

ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "image/bmp",
    "image/tiff",
}

_quality_service = ImageQualityService()
_receipt_service = ReceiptAnalysisService()


@router.post(
    "/upload",
    response_model=ReceiptUploadResponse,
    summary="Upload a receipt image for AI analysis",
    description=(
        "Accepts a receipt image (JPEG, PNG, GIF, WebP, BMP, TIFF). "
        "Runs image quality validation first — returns HTTP 400 if the image "
        "fails quality checks (too blurry, too dark/bright, or too low resolution). "
        "On pass or warning, sends the image to OpenAI Vision (gpt-4.1-mini) and "
        "returns structured receipt data alongside the quality report."
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

    # ── 2. Read bytes once (used by both services) ────────────────────────────
    image_bytes = await file.read()

    # ── 3. Image quality validation ───────────────────────────────────────────
    quality = _quality_service.validate_image(image_bytes)

    if not quality.passed:
        # Hard failure — return 400 with the quality report so the client
        # can show the user exactly what needs to be fixed.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Image quality check failed",
                "quality": quality.model_dump(),
            },
        )

    # ── 4. PASS or WARNING — proceed to OpenAI analysis ───────────────────────
    receipt = await _receipt_service.process_bytes(
        image_bytes, file.filename, file.content_type
    )

    # ── 5. Return combined response ───────────────────────────────────────────
    return ReceiptUploadResponse(
        status=receipt.status,   # "analysed" | "error"
        quality=quality,
        receipt=receipt,
    )
