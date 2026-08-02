"""Document classification stage."""

from services.document_classifier import DocumentClassifierService
from services.pipeline.pipeline_context import PipelineContext
from services.pipeline.pipeline_result import PipelineResult


class ClassifierStage:
    """Runs the existing document classifier."""

    name = "classifier"

    def __init__(self, service: DocumentClassifierService):
        self.service = service

    def process(self, context: PipelineContext) -> PipelineResult:
        classification = self.service.classify_document(context.image_bytes)
        context.classification = classification
        context.document_type = classification.document_type
        return PipelineResult.ok(self.name, payload=classification)