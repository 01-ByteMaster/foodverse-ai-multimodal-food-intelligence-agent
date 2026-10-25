"""Tiny JSON-file history store (no database needed)."""
import json, threading, time, uuid
from pathlib import Path

FILE = Path(__file__).resolve().parent.parent / "data" / "history.json"
_lock = threading.Lock()


def _read():
    try:
        return json.loads(FILE.read_text())
    except Exception:
        return []


def add(kind: str, title: str, detail: str, mode: str):
    with _lock:
        items = _read()
        items.insert(0, {"id": uuid.uuid4().hex[:8], "kind": kind, "title": title,
                         "detail": detail, "mode": mode, "ts": int(time.time())})
        try:
            FILE.parent.mkdir(exist_ok=True)
            FILE.write_text(json.dumps(items[:50], indent=1))
        except OSError:
            pass  # read-only filesystems: history is best-effort


def list_all():
    with _lock:
        return _read()


def clear():
    with _lock:
        try:
            FILE.write_text("[]")
        except OSError:
            pass
