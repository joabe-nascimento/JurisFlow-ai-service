"""Contador persistente de tokens consumidos pelo LLM (Azure OpenAI, etc.)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any

_lock = Lock()
_file = Path(__file__).resolve().parent.parent.parent / "var" / "llm_usage.json"


def _empty() -> dict[str, Any]:
    return {
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0,
        "requests": 0,
        "by_day": {},
        "last_request_at": None,
        "provider": "",
        "model": "",
    }


def _load() -> dict[str, Any]:
    if not _file.exists():
        return _empty()
    try:
        data = json.loads(_file.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return {**_empty(), **data}
    except (json.JSONDecodeError, OSError):
        pass
    return _empty()


def _save(data: dict[str, Any]) -> None:
    _file.parent.mkdir(parents=True, exist_ok=True)
    _file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def extract_usage_from_message(message: Any) -> dict[str, int]:
    """Extrai usage de AIMessage (LangChain + Azure OpenAI)."""
    meta = getattr(message, "response_metadata", None) or {}
    if not isinstance(meta, dict):
        meta = {}

    usage = meta.get("token_usage") or meta.get("usage") or {}
    if not isinstance(usage, dict):
        usage = {}

    prompt = int(usage.get("prompt_tokens") or usage.get("input_tokens") or 0)
    completion = int(usage.get("completion_tokens") or usage.get("output_tokens") or 0)
    total = int(usage.get("total_tokens") or (prompt + completion))

    return {
        "prompt_tokens": prompt,
        "completion_tokens": completion,
        "total_tokens": total,
    }


def record(
    usage: dict[str, int],
    *,
    source: str = "chat",
    provider: str = "",
    model: str = "",
) -> None:
    prompt = int(usage.get("prompt_tokens") or 0)
    completion = int(usage.get("completion_tokens") or 0)
    total = int(usage.get("total_tokens") or (prompt + completion))
    if total <= 0 and prompt <= 0 and completion <= 0:
        return

    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    now = datetime.now(timezone.utc).isoformat()

    with _lock:
        data = _load()
        data["prompt_tokens"] += prompt
        data["completion_tokens"] += completion
        data["total_tokens"] += total
        data["requests"] += 1
        data["last_request_at"] = now
        if provider:
            data["provider"] = provider
        if model:
            data["model"] = model

        by_day = data.setdefault("by_day", {})
        if not isinstance(by_day, dict):
            by_day = {}
            data["by_day"] = by_day

        day_row = by_day.get(day) or {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "requests": 0,
        }
        day_row["prompt_tokens"] += prompt
        day_row["completion_tokens"] += completion
        day_row["total_tokens"] += total
        day_row["requests"] += 1
        by_day[day] = day_row

        _save(data)


def get_summary() -> dict[str, Any]:
    with _lock:
        data = _load()

    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    month = day[:7]
    by_day = data.get("by_day") if isinstance(data.get("by_day"), dict) else {}

    today = by_day.get(day) or _empty()
    month_totals = _empty()
    for key, row in by_day.items():
        if not str(key).startswith(month):
            continue
        if not isinstance(row, dict):
            continue
        month_totals["prompt_tokens"] += int(row.get("prompt_tokens") or 0)
        month_totals["completion_tokens"] += int(row.get("completion_tokens") or 0)
        month_totals["total_tokens"] += int(row.get("total_tokens") or 0)
        month_totals["requests"] += int(row.get("requests") or 0)

    return {
        "provider": data.get("provider") or "",
        "model": data.get("model") or "",
        "lifetime": {
            "prompt_tokens": int(data.get("prompt_tokens") or 0),
            "completion_tokens": int(data.get("completion_tokens") or 0),
            "total_tokens": int(data.get("total_tokens") or 0),
            "requests": int(data.get("requests") or 0),
        },
        "today": {
            "prompt_tokens": int(today.get("prompt_tokens") or 0),
            "completion_tokens": int(today.get("completion_tokens") or 0),
            "total_tokens": int(today.get("total_tokens") or 0),
            "requests": int(today.get("requests") or 0),
        },
        "month": {
            "prompt_tokens": int(month_totals["prompt_tokens"]),
            "completion_tokens": int(month_totals["completion_tokens"]),
            "total_tokens": int(month_totals["total_tokens"]),
            "requests": int(month_totals["requests"]),
        },
        "last_request_at": data.get("last_request_at"),
    }
