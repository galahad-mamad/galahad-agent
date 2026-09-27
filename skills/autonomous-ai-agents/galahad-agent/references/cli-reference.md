# Galahad CLI Reference

Live sources when anything looks stale: `galahad --help`, `galahad <command> --help`,
https://github.com/galahad-mamad/galahad-agent/tree/main/website/docs/reference/cli-commands

### Global Flags

```
galahad [flags] [command]        (no subcommand = interactive chat)

  --version, -V             Show version
  -z, --oneshot PROMPT      One-shot: print ONLY the final response (for scripts/pipes)
  -m MODEL  --provider P    Model/provider override for this invocation
  -t, --toolsets LIST       Comma-separated toolsets for this invocation
  --resume, -r SESSION      Resume session by ID or title
  --continue, -c [NAME]     Resume by name, or most recent session
  --worktree, -w            Isolated git worktree mode (parallel agents)
  --skills, -s SKILL        Preload skills (comma-separate or repeat)
  --profile, -p NAME        Use a named profile
  --yolo                    Skip dangerous command approval
  --tui / --cli             Force the Ink TUI / classic REPL
  --ignore-rules            Skip AGENTS.md/SOUL.md/memory/skill injection
  --safe-mode               Disable ALL customizations (troubleshooting)
  --pass-session-id         Include session ID in system prompt
```

### Chat

```
galahad chat [flags]
  -q, --query TEXT          Single query, non-interactive
  --image PATH              Attach a local image to a single query
  -Q, --quiet               Suppress banner, spinner, tool previews
  --checkpoints             Enable filesystem checkpoints (/rollback)
  --max-turns N             Cap tool-calling iterations
  --source TAG              Session source tag (default: cli)
```
(plus the global flags above)

### Configuration

```
galahad setup [section]      Wizard (model|tts|terminal|gateway|tools|agent)
galahad model                Interactive model/provider picker
galahad fallback [add|remove|list]  Fallback provider chain
galahad config [show|edit|get|set|unset|path|env-path|check|migrate]
galahad login / logout       OAuth sign-in / clear stored auth
galahad doctor [--fix]       Check dependencies and config
galahad status [--all]       Component status
```

### Tools & Skills

```
galahad tools [list|enable NAME|disable NAME]   Per-platform toolsets (curses UI with no args)

galahad skills list|browse|search QUERY|inspect ID
galahad skills install ID    Hub identifier OR a direct https://…/SKILL.md URL
galahad skills config        Enable/disable skills per platform
galahad skills check|update|uninstall|publish PATH
galahad skills tap add REPO  Add a GitHub repo as a skill source
galahad bundles              Skill bundles (one /<name> alias loads several skills)
```

### MCP Servers

```
galahad mcp add NAME (--url or --command) | remove | list | test NAME
galahad mcp catalog | install NAME     Curated catalog install
galahad mcp configure NAME             Toggle tool selection
galahad mcp serve                      Run Galahad as an MCP server
```
Details (transport, tool discovery, catalog): `references/native-mcp.md`.

### Gateway (Messaging Platforms)

```
galahad gateway run|install|start|stop|restart|status|setup
```

20+ platforms: Telegram, Discord, Slack, WhatsApp (Baileys + Business Cloud API), iMessage (Photon — `galahad photon setup`), Signal, Email, SMS, Matrix, Mattermost, Teams, LINE, SimpleX, ntfy, Google Chat, Home Assistant, DingTalk, Feishu, WeCom, Weixin, API Server, Webhooks. Open WebUI connects via the API Server adapter. Most adapters ship under `plugins/platforms/`.
Docs: https://github.com/galahad-mamad/galahad-agent/tree/main/website/docs/user-guide/messaging/

### Sessions

```
galahad sessions list|browse|rename ID TITLE|delete ID|export OUT|prune|stats
```

### Cron / Webhooks

```
galahad cron list|create SCHED|edit ID|pause|resume|run ID|remove|status
    Schedules: '30m', 'every 2h', '0 9 * * *', ISO timestamp
galahad webhook subscribe NAME|list|remove NAME|test NAME
```
Webhook payloads/routes: `references/webhooks.md`.

### Profiles

```
galahad profile list|create NAME (--clone|--clone-all|--clone-from)|use|show|delete
galahad profile rename A B | alias NAME | export NAME | import FILE
```

### Credentials & Pools

```
galahad auth                 Interactive credential manager
galahad auth add [PROVIDER]  Add OAuth or API-key credential (galahad, openai-codex, qwen-oauth, …)
galahad auth list|remove P IDX|reset PROVIDER|status
```
Multiple credentials per provider form a pool that rotates automatically and skips exhausted keys.

### Other

```
galahad desktop / gui        Native desktop app
galahad dashboard            Web admin panel + embedded chat (--stop / --status)
galahad proxy                OpenAI-compatible local proxy backed by an OAuth provider
galahad portal               Quick setup / sign in via Galahad Portal
galahad kanban <verb>        Multi-agent work-queue board
galahad project              Named multi-folder workspaces
galahad skin list|use|set    Switch/tweak skins (see references/themes.md)
galahad pets <verb>          Pet mascots (see references/petdex.md)
galahad memory setup|status|off|reset   Memory provider
galahad secrets bitwarden|onepassword   External secret stores
galahad moa                  Mixture-of-Agents slots
galahad hooks / security / backup / import / checkpoints / console
galahad logs [-f] [errors]   View agent/error logs
galahad send                 One-off message through a gateway platform
galahad pairing / plugins / insights / journey / computer-use
galahad acp                  ACP server (IDE integration)
galahad completion bash|zsh|fish
galahad update / uninstall / claw migrate
```

Plugin- and provider-supplied subcommands (e.g. `galahad photon setup`) only appear once their plugin is installed/active.

### Where to Find Things

| Looking for... | Location |
|---|---|
| Config options | `galahad config edit` · [Configuration docs](https://github.com/galahad-mamad/galahad-agent/tree/main/website/docs/user-guide/configuration) |
| Tools / toolsets | `galahad tools list` · [Tools reference](https://github.com/galahad-mamad/galahad-agent/tree/main/website/docs/reference/tools-reference) |
| Skills catalog | `galahad skills browse` · [Skills catalog](https://github.com/galahad-mamad/galahad-agent/tree/main/website/docs/reference/skills-catalog) |
| Provider setup | `galahad model` · [Providers guide](https://github.com/galahad-mamad/galahad-agent/tree/main/website/docs/integrations/providers) |
| Env variables | `galahad config env-path` · [Env vars reference](https://github.com/galahad-mamad/galahad-agent/tree/main/website/docs/reference/environment-variables) |
| Gateway logs | `~/.galahad/logs/gateway.log` (or `galahad logs`) |
| Sessions | `galahad sessions browse` (reads state.db) |
