# ADR-0004: Adopt a Reusable Financial Document Processing Pipeline

- **Status:** Accepted
- **Date:** 2026-08-02

## Context

The receipt upload route previously coordinated quality checking, document
classification, extraction, normalization, validation, and UFR mapping itself.
That made the route the owner of business orchestration and made it harder to
reuse the same processing flow for utility bills, wallet screenshots, bank
statements, and other financial documents.

The current receipt API is already used by clients. This milestone must
preserve its response schema, Swagger contract, extraction prompt, and existing
quality and validation behavior.

## Decision

Introduce a reusable `FinancialPipeline` with a shared `PipelineContext` and
stage-specific `PipelineResult` objects. The pipeline executes:

```text
Quality → Classifier → Parser → Validation → UFR
```

The route remains responsible only for request handling: MIME validation,
reading the upload, creating the context, invoking the pipeline, and returning
the existing response. Existing services are reused inside stages rather than
duplicated.

Receipt parsing dispatches to the existing receipt analysis service. Utility
bill parsing dispatches to the dedicated utility-bill service.

## Consequences

- Processing order is explicit and reusable.
- Stages share state through one context instead of many independent arguments.
- Future document parsers can be registered without expanding route logic.
- Existing API behavior remains stable.