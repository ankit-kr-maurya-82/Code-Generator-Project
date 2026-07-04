from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime


class HistoryItem(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    prompt: str
    response: str
    created_at: float = Field(default_factory=lambda: datetime.utcnow().timestamp())
