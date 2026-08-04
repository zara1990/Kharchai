"""Deterministic UFR confidence stage."""

from services.confidence import ConfidenceService
from services.pipeline.pipeline_context import PipelineContext
from services.pipeline.pipeline_result import PipelineResult


class ConfidenceStage:
    """Enriches a generated UFR with confidence and review metadata."""

    name = "confidence"

    def __init__(self, service: ConfidenceService):
        self.service = service

    def process(self, context: PipelineContext) -> PipelineResult:
        if context.universal_record is None:
            return PipelineResult.fail(
                self.name,
                errors=["Universal Financial Record is missing."],
                http_status_code=500,
            )

        parser_confidence = (
            context.classification.confidence if context.classification else None
        )
        result = self.service.calculate(
            record=context.universal_record,
            quality_report=context.quality_report,
            validation_report=context.validation_result,
            parser_confidence=parser_confidence,
        )
        context.universal_record.metadata.confidence = result.confidence
        context.universal_record.metadata.confidence_level = result.confidence_level
        context.universal_record.metadata.review_required = result.review_required
        return PipelineResult.ok(self.name, payload=result)