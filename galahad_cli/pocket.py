"""Pocket — a persistent personal clipboard bank for Galahad Agent.

Unlike the conversation itself, pocket entries survive across sessions and
are searchable.  Think: "save this SSH one-liner / regex / promo code /
whatsapp template forever, find it later from any session".

Storage: ~/.galahad/pocket.json  — plain JSON, zero dependencies, safe to
back up or sync by hand.
"""
from __future__ import annotations

import json
import os
import re
import time
from typing import Any, Dict, List, Optional

_MAX_ENTRIES = 500
_MAX_SNIPPET = 20000


def _pocket_path() -> str:
    home = os.environ.get("GALAHAD_HOME") or os.path.join(os.path.expanduser("~"), ".galahad")
    return os.path.join(home, "pocket.json")


def _load() -> List[Dict[str, Any]]:
    try:
        with open(_pocket_path(), encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (OSError, ValueError):
        return []


def _save(entries: List[Dict[str, Any]]) -> None:
    path = _pocket_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


def save(name: str, text: str, tags: str = "") -> Dict[str, Any]:
    """Save (or overwrite) a named snippet. Returns the stored entry."""
    name = (name or "").strip()
    text = (text or "").strip()
    if not name:
        raise ValueError("pocket entry needs a name")
    if not text:
        raise ValueError("pocket entry needs content")
    if len(text) > _MAX_SNIPPET:
        text = text[:_MAX_SNIPPET] + "\n…[truncated]"
    entries = _load()
    entry = {
        "name": name,
        "text": text,
        "tags": [t.strip().lower() for t in tags.split(",") if t.strip()],
        "created": time.time(),
        "hits": 0,
    }
    entries = [e for e in entries if e.get("name") != name]
    entries.append(entry)
    if len(entries) > _MAX_ENTRIES:
        entries = entries[-_MAX_ENTRIES:]
    _save(entries)
    return entry


def get(name: str) -> Optional[Dict[str, Any]]:
    """Exact name match (case-insensitive); increments hit counter."""
    entries = _load()
    needle = (name or "").strip().lower()
    for e in entries:
        if e.get("name", "").lower() == needle:
            e["hits"] = int(e.get("hits", 0)) + 1
            e["last_used"] = time.time()
            _save(entries)
            return e
    return None


def search(query: str) -> List[Dict[str, Any]]:
    """Substring search across name, text and tags."""
    q = (query or "").strip().lower()
    if not q:
        return []
    out = []
    for e in _load():
        hay = (e.get("name", "") + " " + e.get("text", "")[:500] + " " + " ".join(e.get("tags", []))).lower()
        if q in hay:
            out.append(e)
    out.sort(key=lambda e: (-int(e.get("hits", 0)), e.get("name", "")))
    return out[:15]


def delete(name: str) -> bool:
    entries = _load()
    needle = (name or "").strip().lower()
    kept = [e for e in entries if e.get("name", "").lower() != needle]
    if len(kept) == len(entries):
        return False
    _save(kept)
    return True


def list_entries() -> List[Dict[str, Any]]:
    entries = list(_load())
    entries.sort(key=lambda e: e.get("name", "").lower())
    return entries


def recent(n: int = 5) -> List[Dict[str, Any]]:
    entries = _load()
    entries.sort(key=lambda e: e.get("last_used") or e.get("created", 0), reverse=True)
    return entries[:n]
