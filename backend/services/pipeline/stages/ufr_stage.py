"""Universal Financial Record stage."""

from services.pipeline.pipeline_context import PipelineContext
from services.pipeline.pipeline_result import PipelineResult
from services.ufr_mapper import UniversalFinancialRecordMapper


class UFRStage:
    """Maps parser output into the canonical Universal Financial Record."""

    name = "ufr"

    def __init__(self, mapper: UniversalFinancialRecordMapper):
        self.mapper = mapper

    def process(self, context: PipelineContext) -> PipelineResult:
        if context.parser_output is None:
            return PipelineResult.fail(
                self.name,
                errors=["Parser output is missing."],
                http_status_code=500,
            )

        classification = context.classification
        record = self.mapper.from_receipt_analysis(
            context.parser_output,
            document_type=context.document_type or "unknown",
            confidence=classification.confidence if classification else None,
            quality_score=(
                context.quality_report.quality_score
                if context.quality_report
                else None
            ),
        )
        context.universal_record = record
        return PipelineResult.ok(self.name, payload=record)