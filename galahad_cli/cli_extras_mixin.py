"""CLIExtrasMixin — three flagship slash commands.

/recap    — instant local recap of the current session (no LLM call).
/pocket   — persistent cross-session snippet bank (save/get/search/copy).
/later    — natural-language reminder → one-shot background job.

All three are computed locally through existing engines (session_recap,
pocket store, cron scheduler), so they work offline, cost nothing, and
function on Termux the same as desktop.
"""
from __future__ import annotations

import time


class CLIExtrasMixin:
    # ───────────────────────────── /recap ─────────────────────────────
    def _handle_recap_command(self) -> None:
        try:
            from galahad_cli.session_recap import build_recap

            if not getattr(self, "conversation_history", None):
                print("  Nothing to recap yet — this session has no turns.")
                return
            recap = build_recap(list(self.conversation_history), platform="cli")
            print()
            print(recap)
            print()
        except Exception as exc:  # pragma: no cover - defensive
            print(f"  recap failed: {exc}")

    # ───────────────────────────── /pocket ────────────────────────────
    def _handle_pocket_command(self, cmd: str) -> None:
        from galahad_cli import pocket

        parts = cmd.split(None, 2)
        sub = parts[1].lower() if len(parts) > 1 else "list"

        if sub in ("save", "add"):
            if len(parts) < 3:
                print("  Usage: /pocket save <name> <text>")
                return
            rest = parts[2]
            # optional trailing #tags
            tags = ""
            if " #" in rest:
                head, tail = rest.rsplit(" #", 1)
                if " " not in tail.strip():
                    rest, tags = head.strip(), tail.strip()
            name, _, text = rest.partition(" ")
            if not text.strip():
                print("  Need content: /pocket save <name> <text>")
                return
            entry = pocket.save(name, text, tags)
            print(f"  Pocketed '{entry['name']}' ({len(entry['text'])} chars).")
        elif sub in ("get", "show", "open"):
            if len(parts) < 3:
                print("  Usage: /pocket get <name>")
                return
            entry = pocket.get(parts[2])
            if not entry:
                print(f"  Nothing in pocket named '{parts[2]}'. Try /pocket search {parts[2]}")
                return
            print()
            print(f"  ── {entry['name']} ──")
            for line in entry["text"].splitlines() or [""]:
                print(f"  {line}")
            print()
            if self._copy_to_clipboard(entry["text"]):
                print("  (copied to clipboard)")
        elif sub == "search":
            if len(parts) < 3:
                print("  Usage: /pocket search <query>")
                return
            hits = pocket.search(parts[2])
            if not hits:
                print("  No pocket entries match.")
                return
            print()
            for e in hits:
                first = e["text"].splitlines()[0][:60] if e.get("text") else ""
                tags = f" #{' #'.join(e['tags'])}" if e.get("tags") else ""
                print(f"  • {e['name']:<24} {first}{tags}")
            print(f"\n  /pocket get <name> to open.")
        elif sub == "delete":
            if len(parts) < 3 or not pocket.delete(parts[2]):
                print("  Usage: /pocket delete <name>")
                return
            print(f"  Deleted '{parts[2]}'.")
        else:  # list
            entries = pocket.list_entries()
            if not entries:
                print("  Pocket is empty. /pocket save <name> <text>")
                return
            print()
            for e in entries:
                tags = f" #{' #'.join(e['tags'])}" if e.get("tags") else ""
                print(f"  • {e['name']:<24} {int(e.get('hits', 0))} hits{tags}")
            print()

    @staticmethod
    def _copy_to_clipboard(text: str) -> bool:
        import subprocess, shutil
        for cmd in (["wl-copy"], ["xclip", "-selection", "clipboard"], ["pbcopy"]):
            if shutil.which(cmd[0]):
                try:
                    subprocess.run(cmd, input=text.encode("utf-8"), timeout=5, check=True)
                    return True
                except Exception:
                    pass
        # Termux: termux-api provides termux-clipboard-set
        if shutil.which("termux-clipboard-set"):
            try:
                subprocess.run(["termux-clipboard-set"], input=text.encode("utf-8"), timeout=5, check=True)
                return True
            except Exception:
                pass
        return False

    # ───────────────────────────── /later ─────────────────────────────
    def _handle_later_command(self, cmd: str) -> None:
        rest = cmd.split(None, 1)[1].strip() if " " in cmd else ""
        if not rest:
            print('  Usage: /later <when> <what>   e.g.  /later 30m stretch break')
            print('         /later every 2h check the build')
            return
        tokens = rest.split(None, 2)
        when, what = tokens[0], (tokens[1] if len(tokens) > 1 else "")
        # two-word schedules: "every 2h"
        if when.lower() == "every" and len(tokens) > 2:
            when, what = f"every {tokens[1]}", tokens[2]
        if not what:
            print("  What should I remind you about?  e.g. /later 1h call the host")
            return
        schedule = when
        try:
            from cron.jobs import parse_schedule
            sched = parse_schedule(when.lower())
        except Exception as exc:
            print(f"  Can't understand '{when}' ({exc}).")
            print("  Try: 15m 2h 45m  or  'every 2h'  or  a cron expr in quotes.")
            return
        if sched.get("kind") == "cron":
            schedule = when.lower()
        elif sched.get("kind") == "once":
            schedule = when.lower()
        try:
            import json as _json
            from tools.cronjob_tools import cronjob as cronjob_tool  # type: ignore
            result = _json.loads(cronjob_tool(
                action="create",
                schedule=schedule,
                prompt=(
                    "You are delivering a user-set reminder. The user asked "
                    f"at {time.strftime('%Y-%m-%d %H:%M')}: \"{what}\". "
                    "Send a short, friendly reminder message about it now."
                ),
                name=f"reminder: {what[:38]}",
                repeat=1 if sched.get("kind") == "once" else None,
            ))
            if not result.get("success", False):
                print(f"  Could not schedule the reminder: {result.get('error', 'unknown')}")
                return
            job = result.get("job") or {}
            job_id = job.get("job_id", "?")
            print(f"  ⏰ Later set — job {str(job_id)[:12]} · {schedule} · {what}")
        except Exception as exc:
            print(f"  Could not schedule the reminder: {exc}")
