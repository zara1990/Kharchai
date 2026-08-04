---
name: Parser registry
description: Convention for adding document parsers to the financial pipeline.
---

The financial pipeline uses a centralized parser registry. New document types
should be registered there instead of adding selection branches to pipeline
stages.

**Why:** Centralized resolution keeps parser selection inspectable and lets
future document support be added without changing orchestration logic. Parser
specific compatibility adapters also preserve the existing upload response.

**How to apply:** Register the parser with its document type. Provide
normalization and legacy-response adapters when its output differs from the
current receipt-compatible boundary. Map complete parser output into the UFR
downstream; keep document-specific fields in UFR item metadata when the generic
record has no dedicated field.