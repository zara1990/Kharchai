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