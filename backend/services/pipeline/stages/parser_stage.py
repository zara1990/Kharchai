"""Document parser dispatch stage."""

from typing import Any, Awaitable, Callable

from schemas.receipt import ReceiptAnalysisResponse
from services.normalization import NormalizationService
from services.pipeline.pipeline_context import PipelineContext
from services.pipeline.pipeline_result import PipelineResult
from services.receipt_analysis import ReceiptAnalysisService
from services.utility_bill_analysis import (
    UtilityBillAnalysisResponse,
    UtilityBillAnalysisService,
)


class ParserStage:
    """
    Dispatches parser work by document type.

    Receipt uses the existing OpenAI receipt analysis service. Utility bills
    use the dedicated UtilityBillAnalysisService.
    """

    name = "parser"

    def __init__(
        self,
        receipt_service: ReceiptAnalysisService,
        normalization_service: NormalizationService,
        utility_bill_service: UtilityBillAnalysisService | None = None,
    ):
        self.receipt_service = receipt_service
        self.normalization_service = normalization_service
        self.utility_bill_service = utility_bill_service or UtilityBillAnalysisService()
        self._parsers: dict[str, Callable[[PipelineContext], Awaitable[Any]]] = {
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
        if context.document_type == "receipt":
            context.legacy_receipt_output = parsed
        elif isinstance(parsed, UtilityBillAnalysisResponse):
            context.legacy_receipt_output = (
                self.utility_bill_service.to_legacy_receipt_response(parsed)
            )
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
    ) -> UtilityBillAnalysisResponse:
        return await self.utility_bill_service.process_bytes(
            context.image_bytes,
            context.filename,
            context.content_type,
        )