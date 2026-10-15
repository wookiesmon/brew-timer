"""Bounded exponential backoff for transient API failures.

Order *creation* is never retried here: a timeout can hide an order that was
accepted, so the engine records SUBMIT_UNKNOWN and looks the order up by its
client ID instead of resubmitting it.
"""
from __future__ import annotations

import logging
import random
import time
from typing import Callable, TypeVar

import requests

log = logging.getLogger("bot.retry")
T = TypeVar("T")


def is_transient(exc: BaseException) -> bool:
    if isinstance(exc, (requests.exceptions.ConnectionError, requests.exceptions.Timeout)):
        return True
    status = getattr(getattr(exc, "response", None), "status_code", None)
    if status is None:
        status = getattr(exc, "status_code", None)  # hyperliquid.utils.error.ClientError / ServerError
    return isinstance(status, int) and (status == 429 or status >= 500)


class Retrier:
    def __init__(self, max_retries: int = 4, base_delay: float = 1.0, max_delay: float = 30.0,
                 sleep: Callable[[float], None] = time.sleep):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.sleep = sleep

    def call(self, fn: Callable[..., T], *args, **kwargs) -> T:
        attempt = 0
        while True:
            try:
                return fn(*args, **kwargs)
            except Exception as exc:  # noqa: BLE001 - classified below
                if attempt >= self.max_retries or not is_transient(exc):
                    raise
                delay = min(self.max_delay, self.base_delay * (2 ** attempt)) * (0.8 + 0.4 * random.random())
                log.warning("transient API error (%s); retry %d/%d in %.1fs",
                            type(exc).__name__, attempt + 1, self.max_retries, delay)
                self.sleep(delay)
                attempt += 1
