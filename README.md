# KharchAI

**KharchAI** is an AI-powered financial copilot for Pakistan.  
It helps users track expenses by analysing receipts and providing intelligent financial insights.

---

## Current Milestone: FastAPI Backend Foundation

The backend uses **Python + FastAPI**. This milestone establishes a clean, minimal API skeleton.  
Receipt AI and OpenAI integration are **not implemented yet**.

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

## What is NOT implemented yet

- Receipt image analysis
- OpenAI / multimodal AI integration
- Supabase / database
- Authentication
- Android mobile application
- Financial calculations / AI reasoning

See [`docs/architecture.md`](docs/architecture.md) for the planned architecture  
and [`docs/api-contract.md`](docs/api-contract.md) for future API contracts.
