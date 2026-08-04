---
name: Review hints
description: Deterministic field-level review explanations attached to UFR metadata.
---

Review hints run after confidence scoring and explain missing fields, quality
problems, and validation mismatches with stable `{field, message}` entries.

**Why:** A review decision is more useful when downstream reviewers can see
which extracted field or evidence needs attention, without exposing or changing
the existing upload response.

**How to apply:** Keep the service deterministic and parser-aware through UFR
top-level fields and item metadata. Store hints in UFR metadata only; preserve
the public response schema.