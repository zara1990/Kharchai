# ADR-0001: Adopt Universal Financial Records as the Canonical Internal Schema

- **Status:** Accepted
- **Date:** 2026-08-02

## Context

KharchAI will process multiple financial document types. Receipt extraction
currently produces a receipt-specific response, while future utility bill,
wallet screenshot, and bank statement parsers will have different source
structures. Allowing every downstream feature to understand each parser output
would tightly couple the system to individual document types.

The existing receipt API response is already used by clients and must remain
backward compatible.

## Decision

Introduce `UniversalFinancialRecord` (UFR) as the canonical internal schema for
all financial documents. Each document-specific parser will map its output into
the UFR before downstream processing.

The initial implementation adds a mapper from `ReceiptAnalysisResponse` to UFR.
The UFR includes generic document identity, merchant/date/currency/amount
fields, optional payment and category fields, generic items, and processing
metadata containing source, confidence, quality score, and parser version.

The UFR is currently an internal pipeline object. It is not added to the
existing `ReceiptUploadResponse`, so current clients receive the same response
shape.

## Consequences

### Positive

- Downstream persistence and financial calculations can target one schema.
- New parsers can be added without changing every consumer.
- Parser provenance and quality information travel with each record.
- Existing receipt extraction and API behavior are preserved.

### Trade-offs

- A mapper layer is required for every new parser.
- Some document types will leave receipt-oriented fields such as `merchant` or
  `total_amount` unset when the source does not provide them.
- The public API may expose UFR fields in a later, separately versioned change
  if clients need them.

## Future extension path

Future parser-specific components should follow:

```text
Document Classifier
  → Document-Specific Parser
  → Document-Specific Mapper
  → UniversalFinancialRecord
  → Shared Downstream Consumers
```

Examples include `UtilityBillParser → UtilityBillToUFRMapper` and
`WalletParser → WalletToUFRMapper`.