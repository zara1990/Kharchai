# KharchAI

**KharchAI** is an AI-powered financial copilot for Pakistan.  
It helps users track expenses by analysing receipts and providing intelligent financial insights.

---

## Current Milestone: Supabase Foundation

The backend uses **Python + FastAPI** and now has a server-side Supabase
foundation for the existing Universal Financial Record pipeline. The reviewed
record save endpoint is intentionally deferred to a later milestone.

---

## Project Structure

```
backend/        # Python FastAPI backend
  main.py       # Application entry point
  routes/       # API route modules (future)
  services/     # Business logic (future)
  models/       # Data models (future)
  schemas/      # Pydantic schemas (future)
  utils/        # Utility helpers (future)
docs/           # Architecture and API documentation
mobile/         # Expo React Native Android app (future milestone)
```

---

## Running the Backend

From the project root:

```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

---

## Testing GET /health

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{"status": "ok"}
```

---

## Interactive API Documentation

Once the backend is running, open:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## Supabase configuration

The backend requires these server-side environment values:

```text
SUPABASE_URL
SUPABASE_SERVICE_ROLE_KEY
```

Never expose `SUPABASE_SERVICE_ROLE_KEY` to Android or API clients. Apply the
initial database schema from
[`supabase/migrations/20260811000000_create_financial_records.sql`](supabase/migrations/20260811000000_create_financial_records.sql).

## What is NOT implemented yet

- Receipt image analysis
- OpenAI / multimodal AI integration
- Reviewed-record save endpoint
- Authentication
- Android mobile application
- Financial calculations / AI reasoning

See [`docs/architecture.md`](docs/architecture.md) for the planned architecture  
and [`docs/api-contract.md`](docs/api-contract.md) for future API contracts.
