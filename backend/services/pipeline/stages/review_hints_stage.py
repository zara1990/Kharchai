"""Deterministic human-review hint stage."""

from services.pipeline.pipeline_context import PipelineContext
from services.pipeline.pipeline_result import PipelineResult
from services.review_hints import ReviewHintService


class ReviewHintsStage:
    """Enriches the UFR with field-level review hints after confidence scoring."""

    name = "review_hints"

    def __init__(self, service: ReviewHintService):
        self.service = service

    def process(self, context: PipelineContext) -> PipelineResult:
        if context.universal_record is None:
            return PipelineResult.fail(
                self.name,
                errors=["Universal Financial Record is missing."],
                http_status_code=500,
            )

        hints = self.service.generate(
            record=context.universal_record,
            quality_report=context.quality_report,
            validation_report=context.validation_result,
        )
        context.universal_record.metadata.review_hints = hints
        return PipelineResult.ok(self.name, payload=hints)