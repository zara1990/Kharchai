from fastapi import FastAPI

app = FastAPI(
    title="KharchAI API",
    description="AI-powered financial copilot for Pakistan — backend API.",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {"status": "ok"}
