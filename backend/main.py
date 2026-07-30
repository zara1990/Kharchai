from fastapi import FastAPI

from routes.receipt import router as receipt_router

app = FastAPI(
    title="KharchAI API",
    description="AI-powered financial copilot for Pakistan — backend API.",
    version="0.1.0",
)

app.include_router(receipt_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
