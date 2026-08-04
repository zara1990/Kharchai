"""Financial document pipeline orchestrator."""

from schemas.receipt import ReceiptUploadResponse
from services.document_classifier import DocumentClassifierService
from services.image_quality import ImageQualityService
from services.normalization import NormalizationService
from services.pipeline.pipeline_context import PipelineContext
from services.pipeline.pipeline_result import PipelineResult
from services.pipeline.stages.classifier_stage import ClassifierStage
from services.pipeline.stages.confidence_stage import ConfidenceStage
from services.pipeline.stages.parser_stage import ParserStage
from services.pipeline.stages.quality_stage import QualityStage
from services.pipeline.stages.review_hints_stage import ReviewHintsStage
from services.pipeline.stages.ufr_stage import UFRStage
from services.pipeline.stages.validation_stage import ValidationStage
from services.parsers.parser_registry import ParserRegistry
from services.receipt_analysis import ReceiptAnalysisService
from services.ufr_mapper import UniversalFinancialRecordMapper
from services.validation import ReceiptValidationService
from services.utility_bill_analysis import UtilityBillAnalysisService
from parsers.wallet_parser import WalletParser
from services.confidence import ConfidenceService
from services.review_hints import ReviewHintService


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
        utility_bill_service: UtilityBillAnalysisService | None = None,
        wallet_parser: WalletParser | None = None,
        confidence_service: ConfidenceService | None = None,
        review_hint_service: ReviewHintService | None = None,
        parser_registry: ParserRegistry | None = None,
    ):
        quality_service = quality_service or ImageQualityService()
        classifier_service = classifier_service or DocumentClassifierService()
        receipt_service = receipt_service or ReceiptAnalysisService()
        normalization_service = normalization_service or NormalizationService()
        validation_service = validation_service or ReceiptValidationService()
        ufr_mapper = ufr_mapper or UniversalFinancialRecordMapper()
        utility_bill_service = utility_bill_service or UtilityBillAnalysisService()
        wallet_parser = wallet_parser or WalletParser()
        confidence_service = confidence_service or ConfidenceService()
        review_hint_service = review_hint_service or ReviewHintService()
        parser_registry = parser_registry or ParserRegistry(
            receipt_parser=receipt_service,
            utility_bill_parser=utility_bill_service,
            wallet_parser=wallet_parser,
            normalization_service=normalization_service,
        )

        self.quality_stage = QualityStage(quality_service)
        self.classifier_stage = ClassifierStage(classifier_service)
        self.parser_stage = ParserStage(parser_registry)
        self.validation_stage = ValidationStage(
            validation_service,
            utility_bill_service,
            wallet_parser,
        )
        self.ufr_stage = UFRStage(ufr_mapper)
        self.confidence_stage = ConfidenceStage(confidence_service)
        self.review_hints_stage = ReviewHintsStage(review_hint_service)

    async def process(self, context: PipelineContext) -> PipelineResult:
        """Run the pipeline and return a result containing the legacy response."""
        for stage in (
            self.quality_stage,
            self.classifier_stage,
        ):
            result = stage.process(context)
            if not result.success:
                return result

        result = await self.parser_stage.process(context)
        if not result.success:
            return result

        result = self.validation_stage.process(context)
        if not result.success:
            return result

        result = self.ufr_stage.process(context)
        if not result.success:
            return result

        result = self.confidence_stage.process(context)
        if not result.success:
            return result

        result = self.review_hints_stage.process(context)
        if not result.success:
            return result

        if (
            context.quality_report is None
            or context.parser_output is None
            or context.validation_result is None
            or context.legacy_receipt_output is None
        ):
            return PipelineResult.fail(
                "response",
                errors=["Pipeline completed without all response fields."],
                http_status_code=500,
            )

        context.final_response = ReceiptUploadResponse(
            status=context.legacy_receipt_output.status,
            quality=context.quality_report,
            validation=context.validation_result,
            receipt=context.legacy_receipt_output,
        )
        return PipelineResult.ok("response", payload=context.final_response)