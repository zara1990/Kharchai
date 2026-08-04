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
- Registered the utility-bill parser entry point for future implementation.
- Added ADR-0003 documenting the pipeline architecture.

## Pakistani Utility Bill Parser MVP

- Added `UtilityBillAnalysisService` with structured OpenAI Vision extraction
  for provider, bill type, consumer number, billing period, issue date, due
  date, amount due, and currency.
- Added null-safe parsing and utility-specific validation.
- Added utility-bill classifier routing and pipeline dispatch.
- Added utility-bill-to-UFR mapping while preserving the existing upload
  response schema.
- Receipt extraction and its prompt remain unchanged.
- Added ADR-0002 documenting the utility-bill parser MVP.

## Parser Registry

- Added `ParserRegistry` with receipt and utility-bill registrations.
- Refactored `ParserStage` to resolve parsers from the registry.
- Preserved existing parser services, validation, UFR mapping, and API
  response behavior.
- Added controlled unsupported-document handling for registry lookup misses.
- Added ADR-0003 documenting parser registry architecture.

## Wallet Screenshot Parser MVP

- Added a typed `WalletAnalysisResponse` schema for EasyPaisa/JazzCash
  transaction screenshots.
- Added `WalletParser` with the existing OpenAI Vision integration and a
  file-backed structured JSON prompt.
- Added null-safe extraction for wallet name, transaction type, amount,
  currency, counterparty, date, time, and transaction reference.
- Registered wallet screenshots in `ParserRegistry`.
- Added wallet screenshot classifier routing and wallet-specific validation.
- Mapped wallet transactions into the existing UFR, retaining wallet-specific
  fields in item metadata.
- Preserved the existing receipt-shaped upload response and receipt/utility
  parser implementations.
- Added ADR-0005 documenting the wallet parser architecture.