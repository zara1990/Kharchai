---
name: Confidence scoring
description: Deterministic confidence and review decisions for generated UFRs.
---

Confidence is calculated after UFR creation, not by the LLM. The score combines
image quality, required-field completeness, validation success, and parser
confidence using fixed weights, then derives a level and review decision.

**Why:** Downstream review routing needs a reproducible signal independent of
model self-assessment while preserving the existing upload response contract.

**How to apply:** Keep confidence enrichment internal to UFR metadata. Treat a
failed quality report as zero quality evidence; missing downstream evidence
must not be treated as success.