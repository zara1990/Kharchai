# ADR-0007: Add Deterministic Field-Level Review Hints

- **Status:** Accepted
- **Date:** 2026-08-04

## Context

The confidence engine identifies whether a generated UFR should be reviewed,
but a reviewer also needs to know what to inspect. The explanation must be
deterministic, field-level, and independent of the LLM.

The existing upload response is public and must remain unchanged. Review
information belongs in the internal UFR metadata alongside confidence.

## Decision

Add `ReviewHintService` and run it in a `ReviewHintsStage` immediately after
the confidence stage:

```text
UFR → ConfidenceStage → ReviewHintsStage → existing upload response
```

Each hint has this shape:

```json
{
  "field": "merchant_name",
  "message": "Merchant name could not be identified."
}
```

The service checks:

- Missing merchant name
- Missing purchase date
- Missing total amount
- Total validation mismatch
- Low or failed image quality
- Missing utility consumer number, billing period, or due date
- Missing wallet transaction reference or direction

Hints are stored in `UniversalFinancialRecordMetadata.review_hints`. When all
required fields and quality/validation checks are clean, the list is empty,
including for HIGH-confidence records.

## Consequences

### Positive

- Reviewers receive actionable explanations instead of only a boolean decision.
- Rules are reproducible and do not consume model calls.
- Utility and wallet metadata remain supported without changing the generic UFR
  shape or public upload response.

### Limitations

- Hint rules are MVP heuristics and do not assess semantic correctness beyond
  existing parser and validation outputs.
- The current upload endpoint does not expose UFR metadata; downstream
  internal consumers can use it without an API migration.