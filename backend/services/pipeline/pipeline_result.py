"""Reusable result object returned by financial-document pipeline stages."""

from dataclasses import dataclass, field
from typing import Any, Optional

from fastapi import HTTPException


@dataclass
class PipelineResult:
    """Carries a stage outcome without passing loose values between stages."""

    success: bool
    stage_name: str
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    payload: Any = None
    http_status_code: Optional[int] = None

    @classmethod
    def ok(
        cls,
        stage_name: str,
        payload: Any = None,
        *,
        warnings: Optional[list[str]] = None,
    ) -> "PipelineResult":
        return cls(
            success=True,
            stage_name=stage_name,
            warnings=warnings or [],
            payload=payload,
        )

    @classmethod
    def fail(
        cls,
        stage_name: str,
        *,
        errors: Optional[list[str]] = None,
        payload: Any = None,
        http_status_code: Optional[int] = None,
    ) -> "PipelineResult":
        return cls(
            success=False,
            stage_name=stage_name,
            errors=errors or [],
            payload=payload,
            http_status_code=http_status_code,
        )

    def raise_for_http_error(self) -> None:
        """Translate a failed pipeline result into the existing HTTP error."""
        if self.success:
            return
        raise HTTPException(
            status_code=self.http_status_code or 500,
            detail=self.payload or {
                "error": "Financial document processing failed",
                "stage": self.stage_name,
                "errors": self.errors,
            },
        )