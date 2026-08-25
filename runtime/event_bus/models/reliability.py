"""Reliability models for retry, replay and dead-letter processing."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from uuid import UUID


class RetryStrategy(StrEnum):
    FIXED = "fixed"
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    EXPONENTIAL_JITTER = "exponential_jitter"


@dataclass(frozen=True, slots=True)
class RetryPolicy:
    max_retries: int = 5
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_JITTER
    initial_delay_ms: int = 500
    max_delay_ms: int = 30_000
    max_retry_duration_seconds: int | None = None

    def __post_init__(self) -> None:
        if self.max_retries < 0:
            raise ValueError("max_retries must be non-negative")
        if self.initial_delay_ms <= 0:
            raise ValueError("initial_delay_ms must be positive")
        if self.max_delay_ms < self.initial_delay_ms:
            raise ValueError("max_delay_ms must be >= initial_delay_ms")
        if (
            self.max_retry_duration_seconds is not None
            and self.max_retry_duration_seconds <= 0
        ):
            raise ValueError("max_retry_duration_seconds must be positive")


@dataclass(frozen=True, slots=True)
class RetryContext:
    event_id: UUID
    attempt: int
    scheduled_at: datetime
    reason: str

    def __post_init__(self) -> None:
        if self.attempt < 1:
            raise ValueError("retry attempt must be >= 1")
        if self.scheduled_at.tzinfo is None:
            raise ValueError("scheduled_at must be timezone-aware")
        if not self.reason.strip():
            raise ValueError("retry reason must not be empty")


@dataclass(frozen=True, slots=True)
class ReplayContext:
    replay_id: UUID
    original_event_id: UUID
    requested_by: str
    reason: str
    requested_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def __post_init__(self) -> None:
        if not self.requested_by.strip():
            raise ValueError("requested_by must not be empty")
        if not self.reason.strip():
            raise ValueError("replay reason must not be empty")
        if self.requested_at.tzinfo is None:
            raise ValueError("requested_at must be timezone-aware")


@dataclass(frozen=True, slots=True)
class DeadLetterRecord:
    event_id: UUID
    reason: str
    failed_at: datetime
    attempts: int
    last_error_code: str | None = None
    last_error_message: str | None = None

    def __post_init__(self) -> None:
        if not self.reason.strip():
            raise ValueError("DLQ reason must not be empty")
        if self.attempts < 1:
            raise ValueError("DLQ attempts must be >= 1")
        if self.failed_at.tzinfo is None:
            raise ValueError("failed_at must be timezone-aware")
