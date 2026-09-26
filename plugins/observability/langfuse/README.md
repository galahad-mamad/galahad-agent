# Langfuse Observability Plugin

This plugin ships bundled with Galahad but is **opt-in** — it only loads when
you explicitly enable it.

## Enable

Pick one:

```bash
# Interactive: walks you through credentials + SDK install + enable
galahad tools  # → Langfuse Observability

# Manual
pip install langfuse
galahad plugins enable observability/langfuse
```

## Required credentials

Set these in `~/.galahad/.env` (or via `galahad tools`):

```bash
GALAHAD_LANGFUSE_PUBLIC_KEY=pk-lf-...
GALAHAD_LANGFUSE_SECRET_KEY=sk-lf-...
GALAHAD_LANGFUSE_BASE_URL=https://cloud.langfuse.com   # or your self-hosted URL
```

Without the SDK or credentials the hooks no-op silently — the plugin fails
open.

## Verify

```bash
galahad plugins list                 # observability/langfuse should show "enabled"
galahad chat -q "hello"              # then check Langfuse for a "Galahad turn" trace
```

## Optional tuning

```bash
GALAHAD_LANGFUSE_ENV=production       # environment tag
GALAHAD_LANGFUSE_RELEASE=v1.0.0       # release tag
GALAHAD_LANGFUSE_SAMPLE_RATE=0.5      # sample 50% of traces
GALAHAD_LANGFUSE_MAX_CHARS=12000      # max chars per field (default: 12000)
GALAHAD_LANGFUSE_DEBUG=true           # verbose plugin logging
```

## Disable

```bash
galahad plugins disable observability/langfuse
```
