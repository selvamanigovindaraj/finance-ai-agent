from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any


class Tracer:
    """OpenTelemetry-compatible tracer for agent pipeline steps."""

    def __init__(self, service_name: str = "ai-agent") -> None:
        self.service_name = service_name

    @asynccontextmanager
    async def span(self, name: str, **attributes: Any) -> AsyncIterator[None]:
        """Context manager that wraps a pipeline step in a trace span."""
        raise NotImplementedError
        yield  # noqa: RET504 — unreachable yield satisfies type checker

    def record_event(self, name: str, payload: dict[str, Any]) -> None:
        """Attach a named event to the current active span."""
        raise NotImplementedError


tracer = Tracer()
