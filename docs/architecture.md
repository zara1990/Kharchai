# KharchAI — Planned Architecture

> **Note:** This documents the intended architecture. Some downstream
> components remain future milestones.

## High-Level Data Flow

```
Android Expo App
  → FastAPI Backend
    → OpenAI Multimodal AI
      → Structured JSON
        → Validation
          → Supabase
            → Financial Calculations
              → AI Financial Reasoning
                → Android App
```

## Components

| Component | Status |
|---|---|
| Android Expo App | Not implemented |
| FastAPI Backend | ✅ Implemented through ReviewResponse pipeline |
| OpenAI Multimodal AI | ✅ Implemented for current parsers |
| Structured JSON response parsing | ✅ Implemented |
| Validation layer | ✅ Implemented |
| Supabase foundation | ✅ Client configuration and initial schema |
| Financial Calculations | Not implemented |
| AI Financial Reasoning | Not implemented |

## Supabase foundation

Supabase is a backend-only persistence dependency. The server-side client reads
these environment values:

- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`

The service-role key must remain server-side and must never be placed in
Android code or returned by an API. The initial UFR-oriented schema is located
at
`supabase/migrations/20260811000000_create_financial_records.sql`.

The foundation is complete, but the reviewed-record save endpoint has not been
implemented yet.
