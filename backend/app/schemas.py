from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class WikiSummary(BaseModel):
    slug: str
    title: str
    description: str


class WikiDocument(WikiSummary):
    type: str
    body: str
    sources: list[str] = Field(default_factory=list)


class BabyInfo(BaseModel):
    name: str | None = Field(default=None, max_length=100)
    birth_date: date | None = None
    notes: str | None = Field(default=None, max_length=2000)

    @field_validator("birth_date", mode="before")
    @classmethod
    def empty_birth_date_is_unset(cls, value: object) -> object:
        return None if value == "" else value


class ChatRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=4000)
    baby_info: BabyInfo = Field(default_factory=BabyInfo)

    @field_validator("prompt")
    @classmethod
    def prompt_must_not_be_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("prompt must not be blank")
        return stripped


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    chat_mode: Literal["offline", "configured"]
