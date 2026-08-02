# KharchAI Progress Log

## Universal Financial Record Foundation

- Added the generic `UniversalFinancialRecord` schema.
- Added generic UFR items and processing metadata for source, confidence,
  quality score, and parser version.
- Added a receipt-analysis-to-UFR mapper.
- Added UFR generation to the receipt pipeline without changing the public
  `ReceiptUploadResponse`.
- Preserved the existing receipt extraction, validation, quality checks, and
  classifier behavior.
- Added ADR-0001 documenting the UFR decision.

## Financial Document Processing Pipeline

- Added `FinancialPipeline` and a shared `PipelineContext`.
- Split orchestration into quality, classifier, parser, validation, and UFR
  stages.
- Kept the receipt route's public response model, Swagger contract, and error
  behavior unchanged.
- Added receipt parser dispatch using the existing receipt analysis service.
- Added a utility-bill parser placeholder for future implementation.
- Added ADR-0002 documenting the pipeline architecture.