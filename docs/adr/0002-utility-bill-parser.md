# ADR-0002: Implement Pakistani Utility Bill Parser MVP

- **Status:** Accepted
- **Date:** 2026-08-02

## Context

KharchAI's financial pipeline supported receipt extraction and had a
utility-bill parser placeholder. Pakistani electricity and gas bills contain
different fields from receipts, including provider, consumer number, billing
period, issue date, and due date. The public upload response is already
consumed by clients and cannot change in this milestone.

## Decision

Add a dedicated `UtilityBillAnalysisService` using OpenAI Vision with a
utility-specific JSON-only prompt. It returns nullable structured fields and
does not modify `ReceiptAnalysisService` or its prompt.

When the classifier returns `utility_bill`, the pipeline:

```text
Utility Bill Image
  → UtilityBillAnalysisService
  → Utility Field Validation
  → UtilityBill → UFR Mapper
  → Existing ReceiptUploadResponse compatibility projection
```

Utility details not represented by the unchanged public response are retained
in the internal UFR, including consumer number, billing period, issue date, and
due date.

## Consequences

### Positive

- Electricity and gas bills share one parser contract.
- Missing or unreadable fields become null values and do not crash parsing.
- Utility bills now use the same UFR and pipeline as receipts.
- Existing receipt extraction, API fields, and Swagger remain unchanged.

### Trade-offs

- The classifier uses a conservative visual heuristic until OCR or a trained
  document classifier is introduced.
- The public response is a compatibility projection and does not expose all
  utility-specific fields.
- Provider-specific edge cases may require future extraction refinements.

## Future extension path

Provider-specific improvements can be added inside the utility parser or as
post-extraction normalizers without changing the pipeline or UFR boundary.
Future public exposure of utility-specific fields should use a separately
versioned API contract.