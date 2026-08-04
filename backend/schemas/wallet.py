"""Strongly typed output schema for wallet screenshot extraction."""

from typing import Optional

from pydantic import BaseModel


class WalletAnalysisResponse(BaseModel):
    """Structured EasyPaisa/JazzCash transaction extraction result."""

    status: str
    filename: str
    content_type: str
    size_bytes: int
    message: str

    wallet_name: Optional[str] = None
    transaction_type: Optional[str] = None
    amount: Optional[float] = None
    currency: Optional[str] = None
    counterparty: Optional[str] = None
    transaction_date: Optional[str] = None
    transaction_time: Optional[str] = None
    transaction_reference: Optional[str] = None