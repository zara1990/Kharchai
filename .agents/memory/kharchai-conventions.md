---
name: KharchAI project conventions
description: Workflow rules and stack decisions for the KharchAI project.
---

# KharchAI Project Conventions

## Workflow rules
- Always inspect the repository before making any changes.
- Build one vertical slice at a time — wait for explicit milestone instructions.
- Never introduce dependencies not asked for in the milestone prompt.
- Never implement: OpenAI, Supabase, auth, dashboard, receipt AI, or mobile app until explicitly requested.

## Stack (confirmed)
- Backend: Python 3.11 + FastAPI + Uvicorn, located in `backend/`
- Mobile: Expo React Native (Android-first), future, will live in `mobile/`
- Backend runs on port 8000 via workflow named "Backend"

**Why:** User is using a controlled vibe-coding workflow and will provide each milestone prompt explicitly. Scope creep breaks their process.

**How to apply:** On every session, re-read the milestone prompt carefully. Do only what is listed. Stop after the milestone.
