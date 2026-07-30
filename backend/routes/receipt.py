from fastapi import APIRouter, File, HTTPException, UploadFile, status

from schemas.receipt import ReceiptUploadResponse

router = APIRouter(prefix="/api/v1/receipt", tags=["Receipt"])

ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "image/bmp",
    "image/tiff",
}


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
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail={
                "error": "Unsupported file type",
                "received": file.content_type,
                "allowed": sorted(ALLOWED_IMAGE_TYPES),
            },
        )

    contents = await file.read()

    return ReceiptUploadResponse(
        status="received",
        filename=file.filename,
        content_type=file.content_type,
        size_bytes=len(contents),
        message="Receipt uploaded successfully. AI analysis is not implemented yet.",
    )
