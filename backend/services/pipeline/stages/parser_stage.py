"""Document parser dispatch stage."""

from services.pipeline.pipeline_context import PipelineContext
from services.pipeline.pipeline_result import PipelineResult
from services.parsers.parser_registry import ParserRegistry


class ParserStage:
    """
    Dispatches parser work by document type.

    Parser selection is delegated to ParserRegistry. This stage only executes
    the resolved parser and its registered adapters.
    """

    name = "parser"

    def __init__(
        self,
        parser_registry: ParserRegistry,
    ):
        self.parser_registry = parser_registry

    async def process(self, context: PipelineContext) -> PipelineResult:
        document_type = context.document_type or ""
        registration = self.parser_registry.get_registration(document_type)
        if registration is None:
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

        parsed = await registration.parser.process_bytes(
            context.image_bytes,
            context.filename,
            context.content_type,
        )
        parsed = registration.normalize(parsed)
        context.parser_output = parsed
        context.legacy_receipt_output = registration.to_legacy_response(parsed)
        return PipelineResult.ok(self.name, payload=parsed)