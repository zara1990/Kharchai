# ADR-0003: Centralize Parser Selection with a Parser Registry

- **Status:** Accepted
- **Date:** 2026-08-02

## Context

The financial pipeline supported receipts and Pakistani utility bills, but
parser resolution and parser-specific compatibility adapters were owned by the
parser stage. Adding another document type would require editing stage
dispatch logic and could introduce branching changes to the pipeline.

The receipt and utility parser implementations are already working and must
not change. The upload response schema must also remain backward compatible.

## Decision

Introduce `ParserRegistry` as the single source of parser selection:

```text
receipt      → ReceiptAnalysisService
utility_bill → UtilityBillAnalysisService
```

`ParserStage` requests a registration from the registry, invokes the resolved
parser, and applies the registration's normalization and legacy-response
adapters. Unsupported document types return the existing controlled
`unsupported_document` HTTP 400 result instead of raising a lookup exception.

## How to register a new parser

Add one registration line to the registry:

```python
registry.register("wallet_screenshot", WalletParser())
```

If the parser needs document-specific normalization or a compatibility
projection, provide those adapters at registration time:

```python
registry.register(
    "wallet_screenshot",
    WalletParser(),
    normalize=wallet_normalize,
    to_legacy_response=wallet_to_legacy_response,
)
```

The parser service itself remains in its own module. Its extraction logic does
not move into the registry.

## Pipeline resolution

```text
Classifier
  → ParserStage
      → ParserRegistry.get_registration(document_type)
          → parser.process_bytes(...)
          → registered normalization adapter
          → registered legacy-response adapter
  → Validation
  → UFR
```

The current public `ReceiptUploadResponse` remains unchanged. Utility-specific
data continues to be retained internally through the existing UFR boundary.

## Consequences

### Positive

- Parser selection is centralized and easy to inspect.
- Future parser support requires registration instead of dispatch branches.
- Unsupported types are handled deterministically.
- Existing receipt and utility parser logic remains untouched.

### Trade-offs

- Parser registrations must provide adapters when their output is not already
  compatible with the legacy response boundary.
- The registry is an additional coordination layer in the pipeline.