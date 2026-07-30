import os

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/debug", tags=["Debug"])


@router.get(
    "/openai",
    summary="Check OpenAI API key presence",
    description="Returns whether OPENAI_API_KEY is set in the environment. Never exposes the key value.",
)
def check_openai_key():
    key_found = bool(os.environ.get("OPENAI_API_KEY"))
    return {"openai_key_found": key_found}
