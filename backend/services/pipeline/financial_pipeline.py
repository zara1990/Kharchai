"""Financial document pipeline orchestrator."""

from schemas.receipt import ReceiptUploadResponse
from services.document_classifier import DocumentClassifierService
from services.image_quality import ImageQualityService
from services.normalization import NormalizationService
from services.pipeline.pipeline_context import PipelineContext
from services.pipeline.pipeline_result import PipelineResult
from services.pipeline.stages.classifier_stage import ClassifierStage
from services.pipeline.stages.parser_stage import ParserStage
from services.pipeline.stages.quality_stage import QualityStage
from services.pipeline.stages.ufr_stage import UFRStage
from services.pipeline.stages.validation_stage import ValidationStage
from services.receipt_analysis import ReceiptAnalysisService
from services.ufr_mapper import UniversalFinancialRecordMapper
from services.validation import ReceiptValidationService


class FinancialPipeline:
    """Executes financial document processing stages in a fixed order."""

    def __init__(
        self,
        *,
        quality_service: ImageQualityService | None = None,
        classifier_service: DocumentClassifierService | None = None,
        receipt_service: ReceiptAnalysisService | None = None,
        normalization_service: NormalizationService | None = None,
        validation_service: ReceiptValidationService | None = None,
        ufr_mapper: UniversalFinancialRecordMapper | None = None,
    ):
        quality_service = quality_service or ImageQualityService()
        classifier_service = classifier_service or DocumentClassifierService()
        receipt_service = receipt_service or ReceiptAnalysisService()
        normalization_service = normalization_service or NormalizationService()
        validation_service = validation_service or ReceiptValidationService()
        ufr_mapper = ufr_mapper or UniversalFinancialRecordMapper()

        self.quality_stage = QualityStage(quality_service)
        self.classifier_stage = ClassifierStage(classifier_service)
        self.parser_stage = ParserStage(receipt_service, normalization_service)
        self.validation_stage = ValidationStage(validation_service)
        self.ufr_stage = UFRStage(ufr_mapper)

    async def process(self, context: PipelineContext) -> PipelineResult:
        """Run the pipeline and return a result containing the legacy response."""
        for stage in (
            self.quality_stage,
            self.classifier_stage,
        ):
            result = stage.process(context)
            if not result.success:
                return result

        # Preserve existing endpoint behavior: every non-receipt classification
        # is rejected before extraction. The utility-bill parser remains
        # available for the milestone's future parser dispatch path.
        if context.document_type != "receipt":
            return PipelineResult.fail(
                "classifier",
                errors=["Only receipt documents are currently supported."],
                payload={
                    "status": "unsupported_document",
                    "document_type": context.document_type,
                    "message": "This document type is planned but not yet supported.",
                },
                http_status_code=400,
            )

        result = await self.parser_stage.process(context)
        if not result.success:
            return result

        result = self.validation_stage.process(context)
        if not result.success:
            return result

        result = self.ufr_stage.process(context)
        if not result.success:
            return result

        if (
            context.quality_report is None
            or context.parser_output is None
            or context.validation_result is None
        ):
            return PipelineResult.fail(
                "response",
                errors=["Pipeline completed without all response fields."],
                http_status_code=500,
            )

        context.final_response = ReceiptUploadResponse(
            status=context.parser_output.status,
            quality=context.quality_report,
            validation=context.validation_result,
            receipt=context.parser_output,
        )
        return PipelineResult.ok("response", payload=context.final_response)