---
name: Supabase foundation
description: Persistence boundary and migration status for the KharchAI backend.
---

KharchAI uses a small server-only REST client configured by `SUPABASE_URL` and
`SUPABASE_SERVICE_ROLE_KEY`; the initial UFR-oriented schema is applied
separately from the checked-in SQL migration.

**Why:** The upload and ReviewResponse contracts must stay independent from
persistence, while privileged credentials must never reach Android or clients.

**How to apply:** Keep the client lazy and cached, use `financial_records` as
the canonical UFR storage shape, and do not add save behavior until its
dedicated milestone. Live API reachability does not mean the migration is
applied.