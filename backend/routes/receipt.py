from fastapi import APIRouter, File, HTTPException, UploadFile, status

from schemas.receipt import ReceiptUploadResponse
from services.receipt import ReceiptService

router = APIRouter(prefix="/api/v1/receipt", tags=["Receipt"])

ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "image/bmp",
    "image/tiff",
}

_receipt_service = ReceiptService()


@router.post(
    "/upload",
    response_model=ReceiptUploadResponse,
    summary="Upload a receipt image",
    description=(
        "Accepts a receipt image file (JPEG, PNG, GIF, WebP, BMP, TIFF). "
        "Returns file metadata. OCR/AI analysis is not implemented yet."
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

    # Delegate all processing to the service layer.
    return await _receipt_service.process(file)
