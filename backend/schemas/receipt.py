from pydantic import BaseModel


class ReceiptUploadResponse(BaseModel):
    status: str
    filename: str
    content_type: str
    size_bytes: int
    message: str
