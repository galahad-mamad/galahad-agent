<p align="center">
  <img src="assets/banner.png" alt="Galahad Agent" width="100%">
</p>

# Galahad Agent ⚔
<p align="center">
  <a href="https://instagram.com/galahad_mamad"><img src="https://img.shields.io/badge/Instagram-@galahad__mamad-E4405F?style=for-the-badge&logo=instagram&logoColor=white" alt="Instagram"></a>
  <a href="https://github.com/galahad-mamad/galahad-agent/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License: MIT"></a>
</p>

**A terminal-native AI agent that keeps what it learns.** Galahad runs in your shell, remembers the work it has done, and turns repeated friction into reusable skills — no cloud lock-in, no phone-home. Bring any model endpoint you like: OpenRouter, OpenAI, Anthropic, Gemini, or a local llama.cpp / vLLM / Ollama server.

## Why Galahad

- **Skills from experience** — repeated workflows get written up as playbooks it reuses in later sessions.
- **Your machine, your keys** — everything (config, sessions, memory) lives under `~/.galahad`. Nothing leaves except the API calls you authorize.
- **Works where you work** — interactive TUI, one-shot scripts, cron jobs, a Web API server, and a messaging gateway (Telegram, Discord, Slack, WhatsApp, Matrix, email, and more).
- **Model-agnostic** — 40+ providers; swap mid-session with `galahad model`. Local endpoints are first-class.
- **Tooling built in** — terminal, file editing, browser automation, image gen, TTS, web search, subagent delegation, scheduled jobs.

## Install

```bash
git clone https://github.com/galahad-mamad/galahad-agent.git
cd galahad-agent
python3 -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .
```

Requires Python 3.11+. Then:
```bash
galahad setup     # first-run wizard: provider, tools, messaging
galahad           # start chatting
```

Persian quick-start: **[README-fa.md](README-fa.md)** · راهنمای اتصال ربات تلگرام: [`gateway-plugins/connect.sh`](gateway-plugins/connect.sh)

## First commands

| Command | What it does |
|---|---|
| `galahad` | Interactive chat (TUI) |
| `galahad model` | Pick provider + model |
| `galahad -z "prompt"` | One-shot, no chat UI |
| `galahad gateway` | Bridge your agents into Telegram/Discord/… |
| `galahad setup wizard` extras | `python tools-galahad/setup_wizard.py` — Persian web wizard |
| `galahad doctor` | Health check |
| `galahad cron` | Scheduled autonomous jobs |

## Customize the look

The default theme is teal/steel. The theme engine drives CLI, TUI, and desktop from one YAML file:

```bash
cp skins/galahad.yaml ~/.galahad/skins/
galahad config set display.skin galahad   # forest-green variant
```

Skills (playbooks), plugins, and the messaging gateway are documented inline: `galahad skills`, `galahad plugins`, `galahad gateway --help`.

## Repository map

| Path | Contents |
|---|---|
| `galahad_cli/` | CLI + TUI + setup wizard |
| `agent/` | Agent loop, memory, skills engine |
| `gateway/` | Messaging platform adapters |
| `tools/` | Built-in tools (browser, terminal, tts, …) |
| `skills/` | Bundled skill library |
| `ui-tui/` · `tui_gateway/` | React/Ink terminal UI + its gateway |
| `web/` | Web dashboard |
| `desktop-plugins/` | Desktop app plugins (model switcher, Persian RTL, session dashboard, skill manager) |
| `tools-galahad/setup_wizard.py` | Persian web setup wizard |
| `locales/` | Runtime i18n |

## Privacy

No telemetry. No account required. Credentials go to `~/.galahad/.env`; sessions to `~/.galahad/sessions.db`. Delete the folder and it's like it was never installed.

---

Built by [galahad_mamad](https://instagram.com/galahad_mamad). MIT licensed.
