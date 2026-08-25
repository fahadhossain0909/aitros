"""Retry scheduling primitives."""

from __future__ import annotations

import random

from .models import RetryPolicy, RetryStrategy


class RetryManager:
    """Calculates bounded retry delays without owning queue infrastructure."""

    def __init__(self, policy: RetryPolicy) -> None:
        self.policy = policy

    def can_retry(self, attempt: int) -> bool:
        return 1 <= attempt <= self.policy.max_retries

    def delay_seconds(self, attempt: int) -> float:
        if attempt < 1:
            raise ValueError("attempt must be >= 1")
        base = self.policy.initial_delay_ms
        if self.policy.strategy is RetryStrategy.FIXED:
            delay = base
        elif self.policy.strategy is RetryStrategy.LINEAR:
            delay = base * attempt
        else:
            delay = base * (2 ** (attempt - 1))
        delay = min(delay, self.policy.max_delay_ms)
        if self.policy.strategy is RetryStrategy.EXPONENTIAL_JITTER:
            delay = random.uniform(0, delay)
        return delay / 1000
