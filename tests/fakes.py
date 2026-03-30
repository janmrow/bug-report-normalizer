from __future__ import annotations

from typing import Any


class FakeLLMClient:
    def __init__(self, response_text: str) -> None:
        self.response_text = response_text
        self.calls: list[dict[str, Any]] = []

    def generate_json(
        self,
        *,
        prompt: str,
        schema: dict[str, Any],
        system_prompt: str | None = None,
    ) -> str:
        self.calls.append(
            {
                "prompt": prompt,
                "schema": schema,
                "system_prompt": system_prompt,
            }
        )
        return self.response_text
