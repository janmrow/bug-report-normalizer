from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class EnvironmentInfo(BaseModel):
    environment_name: str | None = None
    browser: str | None = None
    operating_system: str | None = None
    device: str | None = None

    @field_validator("environment_name", "browser", "operating_system", "device")
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None

        normalized = value.strip()
        return normalized or None


class BugReportDraft(BaseModel):
    title: str
    summary: str
    observed_behavior: str | None = None
    steps_to_reproduce: list[str] = Field(default_factory=list)
    environment: EnvironmentInfo = Field(default_factory=EnvironmentInfo)
    missing_information: list[str] = Field(default_factory=list)

    @field_validator("title", "summary", "observed_behavior")
    @classmethod
    def normalize_text_fields(cls, value: str | None) -> str | None:
        if value is None:
            return None

        normalized = value.strip()
        if not normalized:
            raise ValueError("Text fields must not be empty.")
        return normalized

    @field_validator("steps_to_reproduce", "missing_information")
    @classmethod
    def normalize_string_lists(cls, value: list[str]) -> list[str]:
        normalized_items: list[str] = []

        for item in value:
            stripped = item.strip()
            if not stripped:
                raise ValueError("List items must not be empty.")
            normalized_items.append(stripped)

        return normalized_items
