# ADR-0008: Add the Review Response Builder

- **Status:** Accepted
- **Date:** 2026-08-11

## Context

The Android Review Screen needs a stable response containing editable extracted
fields, line items, validation warnings, deterministic review hints, confidence,
and processing metadata. The existing upload boundary was shaped around
`ReceiptUploadResponse`, which does not expose the generic UFR or the
document-specific fields needed by utility bills and wallet screenshots.

The existing receipt-shaped fields are already consumed by clients and must
remain available. Parser, validation, UFR, confidence, and review-hint logic
should not be duplicated or moved into the route.

## Decision

Add a typed `ReviewResponse` schema and a `ReviewResponseBuilder` that runs
after the existing processing stages:

```text
quality → classification → parser → validation → UFR
        → confidence → review hints → ReviewResponseBuilder
```

The builder is a response-shaping service only. It receives the completed UFR
and pipeline reports, exposes generic and document-specific editable fields,
copies UFR items and review information, and includes processing metadata. It
does not invoke an LLM, parser, validator, or persistence layer.

The public upload endpoint returns `ReviewResponse`. The legacy fields
`status`, `quality`, `validation`, and `receipt` remain embedded in it so
existing clients can continue consuming their established data.

## Consequences

### Positive

- The Android Review Screen receives one typed, document-agnostic response.
- Editable fields carry the same deterministic confidence produced by the
  backend scoring stage.
- Utility-bill and wallet-specific fields are available without changing the
  generic UFR shape.
- Existing receipt response data remains available during client migration.
- Response construction is isolated from parser and validation architecture.

### Limitations

- The response is still built per upload and is not persisted.
- The original image reference currently uses the uploaded filename; durable
  object storage references are deferred to a later milestone.
- The Android UI and human-review save endpoint are not part of this decision.