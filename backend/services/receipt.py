from fastapi import UploadFile

from schemas.receipt import ReceiptUploadResponse


class ReceiptService:
    """
    Handles receipt file processing.

    Current milestone: reads bytes and returns file metadata.
    Future milestone: TODO — integrate OpenAI Vision API here to analyse
    the receipt image and extract structured financial data.
    """

    async def process(self, file: UploadFile) -> ReceiptUploadResponse:
        """
        Read the uploaded image and prepare a response.

        Args:
            file: Validated image UploadFile (content-type already checked by
                  the route layer before this method is called).

        Returns:
            ReceiptUploadResponse with file metadata.
        """
        # Read raw bytes — file is never saved to disk.
        image_bytes: bytes = await file.read()

        # TODO: Pass image_bytes to OpenAI Vision API (future milestone).
        #   Example:
        #     result = await openai_client.chat.completions.create(
        #         model="gpt-4o",
        #         messages=[{
        #             "role": "user",
        #             "content": [
        #                 {"type": "image_url", "image_url": {"url": f"data:{file.content_type};base64,..."}},
        #                 {"type": "text", "text": "Extract receipt data as JSON."},
        #             ],
        #         }],
        #     )

        return ReceiptUploadResponse(
            status="received",
            filename=file.filename,
            content_type=file.content_type,
            size_bytes=len(image_bytes),
            message="Receipt uploaded successfully. AI analysis is not implemented yet.",
        )
