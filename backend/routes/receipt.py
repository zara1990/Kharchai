from fastapi import APIRouter, File, HTTPException, UploadFile, status

from schemas.receipt import ReceiptAnalysisResponse
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

_receipt_service = ReceiptAnalysisService()


@router.post(
    "/upload",
    response_model=ReceiptAnalysisResponse,
    summary="Upload a receipt image for AI analysis",
    description=(
        "Accepts a receipt image (JPEG, PNG, GIF, WebP, BMP, TIFF). "
        "Sends the image to OpenAI Vision (gpt-4.1-mini) and returns "
        "structured receipt data including merchant, date, currency, "
        "total amount, and itemised line items."
    ),
)
async def upload_receipt(file: UploadFile = File(...)):
    # Validate content type — reject non-image files immediately.
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail={
                "error": "Unsupported file type",
                "received": file.content_type,
                "allowed": sorted(ALLOWED_IMAGE_TYPES),
            },
        )

    # Delegate processing and AI analysis to the service layer.
    return await _receipt_service.process(file)
