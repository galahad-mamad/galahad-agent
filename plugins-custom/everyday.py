"""
Galahad Agent — Everyday Utility Tools
روزمره: reminders, notes, weather, currency, translation, file organization.
"""
import json
import os
import re
import subprocess
import datetime
from pathlib import Path
from tools.registry import registry

GALAHAD_HOME = Path(os.environ.get("GALAHAD_HOME", Path.home() / ".galahad"))
GALAHAD_HOME.mkdir(parents=True, exist_ok=True)

NOTES_FILE = GALAHAD_HOME / "notes.json"
REMINDERS_FILE = GALAHAD_HOME / "reminders.json"


def _load(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _save(path: Path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


# ---------- NOTES ----------

def save_note(args: dict, **kw) -> str:
    """Save a quick note with tags."""
    text = args.get("text", "").strip()
    tags = args.get("tags", [])
    if not text:
        return json.dumps({"error": "text required"})
    notes = _load(NOTES_FILE, [])
    note = {
        "id": len(notes) + 1,
        "text": text,
        "tags": tags,
        "created": datetime.datetime.now().isoformat(),
    }
    notes.append(note)
    _save(NOTES_FILE, notes)
    return json.dumps({"success": True, "note_id": note["id"]})


def search_notes(args: dict, **kw) -> str:
    """Search notes by keyword or tag."""
    query = args.get("query", "").lower()
    tag = args.get("tag", "")
    notes = _load(NOTES_FILE, [])
    results = [
        n for n in notes
        if (not query or query in n["text"].lower())
        and (not tag or tag in n.get("tags", []))
    ]
    return json.dumps({"notes": results[-50:], "count": len(results)})


def delete_note(args: dict, **kw) -> str:
    """Delete a note by id."""
    note_id = args.get("note_id")
    notes = _load(NOTES_FILE, [])
    before = len(notes)
    notes = [n for n in notes if n["id"] != note_id]
    _save(NOTES_FILE, notes)
    return json.dumps({"success": len(notes) < before})


# ---------- REMINDERS ----------

def add_reminder(args: dict, **kw) -> str:
    """Add a reminder with optional due date/time."""
    text = args.get("text", "").strip()
    due = args.get("due", "")  # ISO: 2026-09-27T14:00
    if not text:
        return json.dumps({"error": "text required"})
    reminders = _load(REMINDERS_FILE, [])
    reminder = {
        "id": max([r["id"] for r in reminders], default=0) + 1,
        "text": text,
        "due": due,
        "done": False,
        "created": datetime.datetime.now().isoformat(),
    }
    reminders.append(reminder)
    _save(REMINDERS_FILE, reminders)
    return json.dumps({"success": True, "reminder_id": reminder["id"]})


def list_reminders(args: dict, **kw) -> str:
    """List pending reminders, overdue first."""
    reminders = _load(REMINDERS_FILE, [])
    now = datetime.datetime.now()
    pending = []
    for r in reminders:
        if r.get("done"):
            continue
        overdue = False
        if r.get("due"):
            try:
                overdue = datetime.datetime.fromisoformat(r["due"]) < now
            except Exception:
                pass
        r2 = dict(r)
        r2["overdue"] = overdue
        pending.append(r2)
    pending.sort(key=lambda r: (not r["overdue"], r.get("due") or "9999"))
    return json.dumps({"reminders": pending, "count": len(pending)})


def complete_reminder(args: dict, **kw) -> str:
    """Mark a reminder as done."""
    rid = args.get("reminder_id")
    reminders = _load(REMINDERS_FILE, [])
    for r in reminders:
        if r["id"] == rid:
            r["done"] = True
            r["completed"] = datetime.datetime.now().isoformat()
    _save(REMINDERS_FILE, reminders)
    return json.dumps({"success": True})


# ---------- WEATHER (wttr.in, free, no key) ----------

def get_weather(args: dict, **kw) -> str:
    """Get current weather for a city (free, no API key)."""
    city = args.get("city", "Tehran")
    try:
        result = subprocess.run(
            ["curl", "-s", "--max-time", "15", f"https://wttr.in/{city}?format=j1"],
            capture_output=True, text=True, timeout=20,
        )
        if result.returncode != 0 or not result.stdout.strip():
            return json.dumps({"error": "weather fetch failed"})
        data = json.loads(result.stdout)
        cur = data["current_condition"][0]
        today = data["weather"][0]
        return json.dumps({
            "city": city,
            "temp_c": cur["temp_C"],
            "feels_like_c": cur["FeelsLikeC"],
            "humidity": cur["humidity"],
            "condition": cur["weatherDesc"][0]["value"],
            "wind_kmph": cur["windspeedKmph"],
            "today_min": today["mintempC"],
            "today_max": today["maxtempC"],
        })
    except Exception as e:
        return json.dumps({"error": str(e)})


# ---------- CURRENCY (free exchange API) ----------

def currency_convert(args: dict, **kw) -> str:
    """Convert currency amounts. Supports IRT (تومان), USD, EUR, AED, etc."""
    amount = args.get("amount", 1)
    frm = args.get("from", "USD").upper()
    to = args.get("to", "IRT").upper()
    # Toman handling: API has IRR, toman = IRR/10
    api_from, api_to = ("IRR" if frm == "IRT" else frm), ("IRR" if to == "IRT" else to)
    try:
        result = subprocess.run(
            ["curl", "-s", "--max-time", "15", f"https://open.er-api.com/v6/latest/{api_from}"],
            capture_output=True, text=True, timeout=20,
        )
        data = json.loads(result.stdout)
        rate = data["rates"].get(api_to)
        if rate is None:
            return json.dumps({"error": f"currency {api_to} not supported"})
        value = float(amount) * rate
        if to == "IRT":
            value /= 10  # IRR -> toman
        if frm == "IRT":
            value = float(amount) * 10 * rate
        return json.dumps({"amount": float(amount), "from": frm, "to": to, "result": round(value, 4), "rate": rate})
    except Exception as e:
        return json.dumps({"error": str(e)})


# ---------- FILE ORGANIZER ----------

EXT_GROUPS = {
    "images": [".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".svg", ".heic"],
    "videos": [".mp4", ".mkv", ".avi", ".mov", ".webm", ".flv"],
    "audio": [".mp3", ".wav", ".ogg", ".flac", ".m4a", ".aac"],
    "documents": [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt", ".md", ".csv"],
    "archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"],
    "code": [".py", ".js", ".ts", ".html", ".css", ".json", ".yaml", ".yml", ".sh", ".bat"],
    "executables": [".exe", ".msi", ".apk", ".deb", ".AppImage", ".dmg"],
}


def organize_files(args: dict, **kw) -> str:
    """Sort a folder's files into category subfolders (photos, videos, docs...)."""
    folder = args.get("folder", str(Path.home() / "Downloads"))
    dry_run = args.get("dry_run", True)
    folder_path = Path(folder).expanduser()
    if not folder_path.exists():
        return json.dumps({"error": f"folder not found: {folder}"})

    moved = []
    for f in folder_path.iterdir():
        if not f.is_file() or f.name.startswith("."):
            continue
        ext = f.suffix.lower()
        category = next((cat for cat, exts in EXT_GROUPS.items() if ext in exts), "other")
        target_dir = folder_path / category
        target = target_dir / f.name
        if not dry_run:
            target_dir.mkdir(exist_ok=True)
            f.rename(target)
        moved.append({"file": f.name, "category": category})

    return json.dumps({
        "folder": str(folder_path),
        "dry_run": dry_run,
        "files_to_organize": len(moved),
        "preview": moved[:30],
        "hint": "dry_run=false را برای انجام واقعی صدا بزن" if dry_run else None,
    })


# ---------- SCREENSHOT (Windows + Linux) ----------

def take_screenshot(args: dict, **kw) -> str:
    """Capture a screenshot of the desktop."""
    out_dir = GALAHAD_HOME / "screenshots"
    out_dir.mkdir(exist_ok=True)
    name = out_dir / f"screenshot_{datetime.datetime.now():%Y%m%d_%H%M%S}.png"
    import platform
    try:
        if platform.system() == "Windows":
            # Use PowerShell + .NET
            ps = (
                "Add-Type -AssemblyName System.Windows.Forms,System.Drawing;"
                "$b=[System.Windows.Forms.Screen]::PrimaryScreen.Bounds;"
                "$bmp=New-Object System.Drawing.Bitmap $b.Width,$b.Height;"
                f"$g=[System.Drawing.Graphics]::FromImage($bmp);$g.CopyFromScreen($b.Location,[System.Drawing.Point]::Empty,$b.Size);"
                f"$bmp.Save('{str(name)}');$g.Dispose();$bmp.Dispose()"
            )
            subprocess.run(["powershell", "-NoProfile", "-Command", ps], timeout=30, check=True)
        elif platform.system() == "Darwin":
            subprocess.run(["screencapture", "-x", str(name)], timeout=30, check=True)
        else:
            for cmd in (["grim", str(name)], ["spectacle", "-b", "-n", "-o", str(name)], ["gnome-screenshot", "-f", str(name)]):
                try:
                    subprocess.run(cmd, timeout=30, check=True)
                    break
                except (FileNotFoundError, subprocess.CalledProcessError):
                    continue
            else:
                return json.dumps({"error": "no screenshot tool found (grim/spectacle/gnome-screenshot)"})
        return json.dumps({"success": True, "path": str(name)})
    except Exception as e:
        return json.dumps({"error": str(e)})


# ---------- REGISTRATION ----------

TOOL_SPECS = [
    ("save_note", "Save a quick personal note with optional tags",
     {"text": {"type": "string"}, "tags": {"type": "array", "items": {"type": "string"}}}, ["text"]),
    ("search_notes", "Search personal notes by keyword or tag",
     {"query": {"type": "string"}, "tag": {"type": "string"}}, []),
    ("delete_note", "Delete a note by id", {"note_id": {"type": "integer"}}, ["note_id"]),
    ("add_reminder", "Add a reminder with optional due date (ISO format)",
     {"text": {"type": "string"}, "due": {"type": "string"}}, ["text"]),
    ("list_reminders", "List pending reminders (overdue first)", {}, []),
    ("complete_reminder", "Mark a reminder as done", {"reminder_id": {"type": "integer"}}, ["reminder_id"]),
    ("get_weather", "Current weather for a city — free, no API key (wttr.in)",
     {"city": {"type": "string", "default": "Tehran"}}, []),
    ("currency_convert", "Convert currency amounts incl. IRT (تومان), USD, EUR, AED, GBP — free API",
     {"amount": {"type": "number"}, "from": {"type": "string"}, "to": {"type": "string"}}, ["amount", "from", "to"]),
    ("organize_files", "Sort a folder's files into category subfolders (images/videos/docs/audio/archives/code). Default dry_run=true",
     {"folder": {"type": "string"}, "dry_run": {"type": "boolean", "default": True}}, []),
    ("take_screenshot", "Capture a desktop screenshot (Windows/macOS/Linux)", {}, []),
]

_g = globals()
for _name, _desc, _props, _req in TOOL_SPECS:
    registry.register(
        name=_name,
        toolset="everyday",
        schema={
            "name": _name,
            "description": (_desc + ". " + " / ".join(f"{k}: {v.get('type', 'any')}" for k, v in _props.items())).strip(),
            "parameters": {"type": "object", "properties": _props, "required": _req},
        },
        handler=lambda args, _f=_g[_name], **kw: _f(args, **kw),
    )