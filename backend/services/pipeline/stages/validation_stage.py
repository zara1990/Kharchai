"""Receipt validation stage."""

from services.pipeline.pipeline_context import PipelineContext
from services.pipeline.pipeline_result import PipelineResult
from services.validation import ReceiptValidationService


class ValidationStage:
    """Runs the existing validation service."""

    name = "validation"

    def __init__(self, service: ReceiptValidationService):
        self.service = service

    def process(self, context: PipelineContext) -> PipelineResult:
        if context.parser_output is None:
            return PipelineResult.fail(
                self.name,
                errors=["Parser output is missing."],
                http_status_code=500,
            )

        validation = self.service.validate_receipt(context.parser_output)
        context.validation_result = validation
        return PipelineResult.ok(self.name, payload=validation, warnings=validation.warnings)