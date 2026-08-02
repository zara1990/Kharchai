---
name: Universal Financial Record
description: Architectural decision for the shared internal financial-document representation.
---

# Universal Financial Record

KharchAI uses a Universal Financial Record as the canonical internal
representation across financial document types. Document-specific parsers
should map into the UFR before shared persistence, calculations, or reasoning.

**Why:** Receipt extraction already has a public client-facing contract, while
future utility bills, wallet screenshots, and bank statements will have
different parser-specific shapes. A shared internal record avoids coupling
downstream consumers to each parser and preserves backward compatibility.

**How to apply:** Add a document-specific parser and mapper that returns the
UFR. Keep the existing receipt upload response unchanged unless a later
milestone explicitly introduces a versioned public UFR response.