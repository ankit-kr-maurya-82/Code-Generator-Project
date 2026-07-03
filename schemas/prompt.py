from typing import List

from pydantic import BaseModel, Field


class Prompt(BaseModel):
    prompt: str = Field(default="")
    file_name: str | None = Field(default=None, max_length=255)
    file_content: str | None = Field(default=None, max_length=120_000)
    files: List[dict] | None = Field(default=None)

    model_config = {
        "extra": "ignore",
    }
