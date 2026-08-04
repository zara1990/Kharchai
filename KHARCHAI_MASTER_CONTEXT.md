# KharchAI Master Context

## Project

KharchAI is an AI-powered financial copilot for Pakistan. The backend is a
Python 3.11 FastAPI service in `backend/`; the Android Expo application is
planned for a later milestone.

## Current backend pipeline

```text
Upload
  → FinancialPipeline
      → Image Quality Stage
      → Classifier Stage
      → Parser Stage
          → Parser Registry
              → ReceiptAnalysisService
              → UtilityBillAnalysisService
      → Validation Stage
      → UFR Stage
  → Existing ReceiptUploadResponse
```

Receipt extraction and the public receipt response remain unchanged.

The route is intentionally limited to request handling: MIME validation, byte
reading, context creation, and returning the pipeline result. Business logic
lives in the reusable pipeline stages.

The parser stage now dispatches `document_type="utility_bill"` to
`UtilityBillAnalysisService`. Its structured utility output is validated,
projected into the unchanged legacy response shape, and mapped into the UFR.

Parser selection is centralized in `ParserRegistry`. New document parsers are
registered there rather than adding document-type branches to the pipeline.

## Universal Financial Record foundation

`UniversalFinancialRecord` is the canonical internal representation for
financial documents. The current receipt adapter maps
`ReceiptAnalysisResponse` into a UFR after normalization. The UFR is internal
for now and is not added to the existing upload response, preventing a breaking
API change.

The UFR supports:

- receipts
- Pakistani utility bills (electricity and gas MVP)
- future wallet screenshots
- future bank statements

Future document-specific parsers should produce their own extraction output and
map it into the same UFR schema before persistence, calculations, or financial
reasoning.

## Workflow conventions

- Inspect the repository before every milestone change.
- Implement one explicit milestone at a time.
- Preserve working behavior and existing API contracts unless a milestone
  explicitly changes them.
- Do not add Supabase, authentication, mobile, dashboards, or other future
  scope without an explicit milestone.