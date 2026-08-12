"""Schemas for the reviewed financial-record persistence endpoint."""

from pydantic import BaseModel


class FinancialRecordSaveResponse(BaseModel):
    """Small deterministic response returned after a successful save."""

    saved: bool
    record_id: str
    document_type: str