"""Low-frequency HTTP helpers shared by collection scripts."""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import requests


USER_AGENT = (
    "HanwhaEaglesDataCenter/0.1 "
    "(+https://github.com/robinho0329/hanwha-eagles-dashboard; research dashboard)"
)


@dataclass(frozen=True)
class FetchResult:
    url: str
    status_code: int
    content_type: str
    body: bytes
    fetched_at: str
    sha256: str


def fetch(url: str, attempts: int = 3, timeout: int = 30) -> FetchResult:
    """GET once per attempt; retry connection/5xx only with exponential backoff."""
    headers = {"User-Agent": USER_AGENT, "Accept-Language": "ko-KR,ko;q=0.9"}
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            if 400 <= response.status_code < 500:
                response.raise_for_status()
            if response.status_code >= 500:
                raise requests.HTTPError(f"server returned {response.status_code}")
            body = response.content
            return FetchResult(
                url=response.url,
                status_code=response.status_code,
                content_type=response.headers.get("content-type", ""),
                body=body,
                fetched_at=datetime.now(timezone.utc).isoformat(),
                sha256=hashlib.sha256(body).hexdigest(),
            )
        except (requests.ConnectionError, requests.Timeout, requests.HTTPError) as exc:
            last_error = exc
            if isinstance(exc, requests.HTTPError) and getattr(exc.response, "status_code", 500) < 500:
                raise
            if attempt + 1 < attempts:
                time.sleep(2 ** (attempt + 1))
    raise RuntimeError(f"failed to fetch {url} after {attempts} attempts") from last_error


def save_raw(result: FetchResult, directory: Path, suffix: str = ".html") -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    stamp = result.fetched_at.replace(":", "").replace("+00:00", "Z").replace("-", "")
    target = directory / f"{stamp}{suffix}"
    target.write_bytes(result.body)
    return target
