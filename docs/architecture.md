# KharchAI — Planned Architecture

> **Note:** This documents the intended end-state architecture.  
> Most components listed below are **NOT implemented yet**.  
> The current milestone only establishes the FastAPI backend foundation.

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
| FastAPI Backend | ✅ Milestone 1 — foundation only |
| OpenAI Multimodal AI | Not implemented |
| Structured JSON response parsing | Not implemented |
| Validation layer | Not implemented |
| Supabase (database) | Not implemented |
| Financial Calculations | Not implemented |
| AI Financial Reasoning | Not implemented |
