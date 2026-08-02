"""Document parser dispatch stage."""

from typing import Callable, Awaitable

from schemas.receipt import ReceiptAnalysisResponse
from services.normalization import NormalizationService
from services.pipeline.pipeline_context import PipelineContext
from services.pipeline.pipeline_result import PipelineResult
from services.receipt_analysis import ReceiptAnalysisService


class ParserStage:
    """
    Dispatches parser work by document type.

    Receipt uses the existing OpenAI receipt analysis service. Utility bills
    have a placeholder parser so a future implementation can be added without
    changing pipeline orchestration.
    """

    name = "parser"

    def __init__(
        self,
        receipt_service: ReceiptAnalysisService,
        normalization_service: NormalizationService,
    ):
        self.receipt_service = receipt_service
        self.normalization_service = normalization_service
        self._parsers: dict[str, Callable[[PipelineContext], Awaitable[ReceiptAnalysisResponse]]] = {
            "receipt": self._parse_receipt,
            "utility_bill": self._parse_utility_bill,
        }

    async def process(self, context: PipelineContext) -> PipelineResult:
        parser = self._parsers.get(context.document_type or "")
        if parser is None:
            return PipelineResult.fail(
                self.name,
                errors=[f"No parser registered for document type: {context.document_type}"],
                payload={
                    "status": "unsupported_document",
                    "document_type": context.document_type,
                    "message": "This document type is planned but not yet supported.",
                },
                http_status_code=400,
            )

        parsed = await parser(context)
        context.parser_output = parsed
        return PipelineResult.ok(self.name, payload=parsed)

    async def _parse_receipt(self, context: PipelineContext) -> ReceiptAnalysisResponse:
        parsed = await self.receipt_service.process_bytes(
            context.image_bytes,
            context.filename,
            context.content_type,
        )
        return self.normalization_service.normalize(parsed, "receipt")

    async def _parse_utility_bill(
        self, context: PipelineContext
    ) -> ReceiptAnalysisResponse:
        # Placeholder until a utility-bill-specific extractor is implemented.
        # It returns the existing parser schema so downstream validation/UFR
        # stages remain reusable without changing the public response contract.
        return ReceiptAnalysisResponse(
            status="error",
            filename=context.filename,
            content_type=context.content_type,
            size_bytes=len(context.image_bytes),
            message="Utility bill parser is not implemented yet.",
        )