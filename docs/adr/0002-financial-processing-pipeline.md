# ADR-0002: Adopt a Reusable Financial Document Processing Pipeline

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

Receipt parsing dispatches to the existing receipt analysis service. A
utility-bill parser entry is registered as a placeholder so its implementation
can be added without changing orchestration.

## Consequences

### Positive

- Processing order is explicit and reusable.
- Stages share state through one context instead of many independent arguments.
- Future document parsers can be registered without expanding route logic.
- Existing API behavior remains stable.
- Stage results provide a consistent place for warnings, errors, and payloads.

### Trade-offs

- The pipeline adds several small coordination classes.
- The current route still keeps its existing MIME-type request gate.
- Utility bills remain a placeholder until a dedicated parser is implemented.

## Future extension path

When a new document type is supported:

1. Add its parser to `ParserStage`.
2. Reuse or add a document-specific normalization adapter.
3. Map the parser output to `UniversalFinancialRecord` in `UFRStage`.
4. Preserve the shared validation and response boundary unless a later
   milestone explicitly changes the public API.