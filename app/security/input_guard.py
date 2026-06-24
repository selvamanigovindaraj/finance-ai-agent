from __future__ import annotations

import asyncio
import re

from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

from app.models import ChatRequest, Message, Role

_PII_ENTITIES = ["PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER", "CREDIT_CARD", "IBAN_CODE"]

_INJECTION_PATTERNS: list[re.Pattern[str]] = [
    re.compile(p, re.IGNORECASE)
    for p in [
        r"ignore\s+(all\s+)?previous\s+instructions",
        r"forget\s+(all\s+)?your\s+instructions",
        r"disregard\s+(your|all|previous)",
        r"you\s+are\s+now\s+",
        r"from\s+now\s+on\s+(you|act|ignore)",
        r"do\s+anything\s+now",
        r"\bdan\b",
        r"\bjailbreak\b",
        r"pretend\s+(you\s+are|to\s+be)",
        r"roleplay\s+as",
        r"act\s+as\s+if\s+you",
        r"new\s+persona",
    ]
]


class PromptInjectionError(ValueError):
    """Raised when a user message contains a known prompt-injection pattern."""


class InputGuard:
    """Validates and sanitises incoming user messages before processing."""

    def __init__(self) -> None:
        self._analyzer = AnalyzerEngine()
        self._anonymizer = AnonymizerEngine()  # type: ignore[no-untyped-call]

    async def check(self, request: ChatRequest) -> ChatRequest:
        """Redact PII from user messages and return the sanitised request."""
        sanitised: list[Message] = []
        for msg in request.messages:
            if msg.role == Role.user:
                self._check_injection(msg.content)
                clean = await asyncio.to_thread(self._sanitise, msg.content)
                sanitised.append(Message(role=msg.role, content=clean))
            else:
                sanitised.append(msg)
        return ChatRequest(
            messages=sanitised,
            session_id=request.session_id,
            stream=request.stream,
        )

    def _sanitise(self, text: str) -> str:
        """Replace PII entities with typed placeholders."""
        results = self._analyzer.analyze(text=text, entities=_PII_ENTITIES, language="en")
        anonymized = self._anonymizer.anonymize(
            text=text,
            analyzer_results=results,  # type: ignore[arg-type]
            operators={
                entity: OperatorConfig("replace", {"new_value": f"<{entity}>"})
                for entity in _PII_ENTITIES
            },
        )
        return anonymized.text

    def _check_injection(self, text: str) -> None:
        """Raise PromptInjectionError if the message matches a known injection pattern."""
        for pattern in _INJECTION_PATTERNS:
            if pattern.search(text):
                raise PromptInjectionError(f"Prompt injection detected: {pattern.pattern!r}")

    def _check_length(self, _text: str) -> None:
        """Raise if the message exceeds the allowed token budget."""
        raise NotImplementedError


_instance: InputGuard | None = None


def get_input_guard() -> InputGuard:
    """Return the process-wide InputGuard singleton (lazy init)."""
    global _instance
    if _instance is None:
        _instance = InputGuard()
    return _instance
