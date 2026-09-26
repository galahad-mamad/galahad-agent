#!/usr/bin/env python3
"""
Galahad Agent — Local Web Setup Wizard
اجرای: python setup_wizard.py
باز شدن مرورگر روی http://localhost:8765
STEP 1: زبان را انتخاب کنید / Choose your language / Pilih bahasa
STEP 2: یک ارائه‌دهنده رایگان + API key → config.yaml + .env ساخته می‌شود
STEP 3: پلگین‌های پیام‌رسان (تلگرام/واتساپ/دیسکورد) — فرم‌های ساده
"""
import json
import os
import sys
import webbrowser
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

GALAHAD_HOME = Path(os.environ.get("GALAHAD_HOME",
                     os.environ.get("GALAHAD_HOME", Path.home() / ".galahad")))
# Back-compat alias for internal functions
GALAHAD_HOME = GALAHAD_HOME

# Free providers — one API key and you're done
FREE_PROVIDERS = {
    "groq": {
        "name": "Groq", "base_url": "https://api.groq.com/openai/v1", "env": "GROQ_API_KEY",
        "signup": "https://console.groq.com/keys",
        "models": ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"],
        "note": "رایگان، سریع، ۱۴ هزار توکن در دقیقه",
    },
    "openrouter": {
        "name": "OpenRouter", "base_url": "https://openrouter.ai/api/v1", "env": "OPENROUTER_API_KEY",
        "signup": "https://openrouter.ai/keys",
        "models": ["meta-llama/llama-3.3-70b-instruct:free", "deepseek/deepseek-chat-v3.1:free", "google/gemini-2.0-flash-exp:free"],
        "note": "ده‌ها مدل رایگان با یک کلید",
    },
    "gemini": {
        "name": "Google Gemini", "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/", "env": "GOOGLE_API_KEY",
        "signup": "https://aistudio.google.com/apikey",
        "models": ["gemini-2.0-flash", "gemini-1.5-flash"],
        "note": "کلید رایگان گوگل، ۱۵ هزار درخواست روزانه",
    },
    "ollama": {
        "name": "Ollama (Local)", "base_url": "http://localhost:11434/v1", "env": None,
        "signup": "https://ollama.com/download",
        "models": ["llama3.1", "qwen2.5:14b", "deepseek-r1"],
        "note": "کاملاً آفلاین و رایگان — نیاز به نصب اولاما",
    },
    "mistral": {
        "name": "Mistral AI", "base_url": "https://api.mistral.ai/v1", "env": "MISTRAL_API_KEY",
        "signup": "https://console.mistral.ai/api-keys",
        "models": ["mistral-large-latest", "open-mistral-nemo"],
        "note": "مدل‌های اروپایی با کیفیت",
    },
    "huggingface": {
        "name": "HuggingFace", "base_url": "https://router.huggingface.co/v1", "env": "HF_TOKEN",
        "signup": "https://huggingface.co/settings/tokens",
        "models": ["meta-llama/Llama-3.3-70B-Instruct"],
        "note": "رایگان با محدودیت نرخ",
    },
}

MESSSENGERS = {
    "telegram": {"name": "Telegram", "howto_fa": "به @BotFather پیام بدهید، /newbot بزنید، توکن را کپی کنید", "field": "TELEGRAM_BOT_TOKEN"},
    "whatsapp": {"name": "WhatsApp", "howto_fa": "واتساپ بیزینس یا Baileys — کد QR با اسکن اتصال", "field": "WHATSASS_PHONE"},
    "discord": {"name": "Discord", "howto_fa": "discord.com/developers → New Application → Bot → Token", "field": "DISCORD_BOT_TOKEN"},
}

HTML = """<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="utf-8"><title>Galahad Agent — Setup</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
:root{--bg:#0d1b12;--panel:#061209;--line:#1a3a26;--green:#00e676;--green2:#00ff88;--text:#b8e6c8;--dim:#5a8a6a}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--text);font-family:Tahoma,'Segoe UI',sans-serif;min-height:100vh;padding:24px}
.wrap{max-width:760px;margin:0 auto}
h1{color:var(--green2);font-size:26px;margin-bottom:6px}
h1 span{color:var(--dim);font-size:14px;font-weight:normal}
.sub{color:var(--dim);margin-bottom:24px}
.steps{display:flex;gap:8px;margin-bottom:24px}
.step{flex:1;text-align:center;padding:10px;border-radius:8px;background:var(--panel);border:1px solid var(--line);color:var(--dim);font-size:13px;cursor:pointer}
.step.active{border-color:var(--green);color:var(--green2)}
.card{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:20px;margin-bottom:16px}
.prov{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px}
.pcard{border:1px solid var(--line);border-radius:10px;padding:14px;cursor:pointer;transition:.2s}
.pcard:hover{border-color:var(--green)}
.pcard.sel{border-color:var(--green2);box-shadow:0 0 0 1px var(--green2)}
.pname{color:var(--green2);font-weight:bold;font-size:15px}
.pnote{color:var(--dim);font-size:12px;margin:6px 0}
.models{font-family:monospace;font-size:11px;color:var(--text);background:var(--bg);padding:6px 8px;border-radius:6px;margin-top:8px}
a{color:var(--green)}
input,select{width:100%;padding:12px;border-radius:8px;border:1px solid var(--line);background:var(--bg);color:var(--text);font-size:14px;margin:8px 0}
input:focus{outline:none;border-color:var(--green)}
button{background:var(--green);color:var(--bg);border:none;padding:12px 24px;border-radius:8px;font-size:15px;font-weight:bold;cursor:pointer;width:100%}
button:hover{background:var(--green2)}
button.sec{background:transparent;border:1px solid var(--line);color:var(--text);font-weight:normal}
.ok{color:var(--green);text-align:center;padding:12px;font-size:15px}
.err{color:#ff4444;text-align:center;padding:8px}
.hidden{display:none}
label{color:var(--dim);font-size:13px}
.langbar{display:flex;gap:8px;justify-content:center;margin-bottom:20px}
.langbar button{width:auto;padding:6px 14px;font-size:13px}
</style>
</head>
<body>
<div class="wrap">
<h1>🛡️ Galahad Agent <span>Setup Wizard</span></h1>
<p class="sub" id="sub">نصب در ۳ مرحله — زبان، مدل، پیام‌رسان</p>

<div class="langbar">
<button class="sec" onclick="setLang('fa')">فارسی</button>
<button class="sec" onclick="setLang('en')">English</button>
</div>

<div class="steps">
<div class="step active" id="s1">۱. انتخاب مدل رایگان</div>
<div class="step" id="s2">۲. کلید API</div>
<div class="step" id="s3">۳. پیام‌رسان‌ها</div>
</div>

<div class="card" id="step1">
<h3 style="color:var(--green2);margin-bottom:12px">یک ارائه‌دهنده رایگان انتخاب کنید</h3>
<div class="prov" id="provGrid"></div>
<button style="margin-top:16px" onclick="goStep(2)">بعدی ←</button>
</div>

<div class="card hidden" id="step2">
<h3 style="color:var(--green2);margin-bottom:8px" id="selName"></h3>
<p class="sub">از لینک زیر کلید رایگان بگیرید و اینجا بچسبانید:<br>
<a id="signupLink" target="_blank" href="#"></a></p>
<label id="keyLabel">کلید API</label>
<input id="apiKey" type="password" placeholder="API Key...">
<button onclick="saveModel()">ذخیره و نصب مدل</button>
<div id="saveResult"></div>
<button class="sec" style="margin-top:10px" onclick="goStep(1)">→ مرحله قبل</button>
</div>

<div class="card hidden" id="step3">
<h3 style="color:var(--green2);margin-bottom:12px">وصل کردن پیام‌رسان‌ها (اختیاری)</h3>
<div id="messengerForms"></div>
<div id="msgResult"></div>
<button onclick="finish()">پایان — راه‌اندازی گلهاد</button>
</div>
</div>

<script>
const PROVIDERS = PROVIDERS_JSON;
const MSGS = MSGS_JSON;
let sel = null, lang = 'fa';

function renderProviders(){
  const g = document.getElementById('provGrid');
  g.innerHTML = Object.entries(PROVIDERS).map(([id,p])=>`
    <div class="pcard ${sel===id?'sel':''}" onclick="sel='${id}';renderProviders()">
      <div class="pname">${p.name}</div>
      <div class="pnote">${p.note}</div>
      <div class="models">${p.models.slice(0,2).join('<br>')}</div>
    </div>`).join('');
}

function goStep(n){
  [1,2,3].forEach(i=>{
    document.getElementById('step'+i).classList.toggle('hidden', i!==n);
    document.getElementById('s'+i).classList.toggle('active', i===n);
  });
  if(n===2 && sel){
    const p = PROVIDERS[sel];
    document.getElementById('selName').textContent = p.name;
    const a = document.getElementById('signupLink');
    a.href = p.signup; a.textContent = p.signup;
    document.getElementById('keyLabel').textContent = p.env ? 'کلید API:' : 'این گزینه کلید نمی‌خواهد — فقط دکمه را بزنید';
  }
}

async function saveModel(){
  const key = document.getElementById('apiKey').value.trim();
  const r = await fetch('/api/setup_model', {method:'POST', body: JSON.stringify({provider: sel, api_key: key})});
  const d = await r.json();
  document.getElementById('saveResult').innerHTML = d.ok
    ? `<div class="ok">✅ ${d.message}<br>مدل پیش‌فرض: ${d.model}</div>`
    : `<div class="err">❌ ${d.error}</div>`;
  if(d.ok) setTimeout(()=>goStep(3), 800);
}

function renderMessengers(){
  document.getElementById('messengerForms').innerHTML = Object.entries(MSGS).map(([id,m])=>`
    <div style="border:1px solid var(--line);border-radius:10px;padding:12px;margin-bottom:10px">
      <strong style="color:var(--green2)">${m.name}</strong>
      <div class="pnote">${m.howto}</div>
      <input id="msg_${id}" placeholder="${m.field}" ${m.field.includes('QR')?'disabled':''}>
    </div>`).join('');
}

async function finish(){
  const bodies = {};
  for(const id of Object.keys(MSGS)){
    const v = document.getElementById('msg_'+id)?.value.trim();
    if(v) bodies[id] = v;
  }
  const r = await fetch('/api/setup_messengers', {method:'POST', body: JSON.stringify(bodies)});
  const d = await r.json();
  document.getElementById('msgResult').innerHTML = `<div class="ok">✅ ${d.message}</div>`;
}

function setLang(l){
  lang = l;
  if(l==='en'){
    document.documentElement.dir='ltr'; document.documentElement.lang='en';
    document.getElementById('sub').textContent = 'Setup in 3 steps — model, key, messengers';
  } else {
    document.documentElement.dir='rtl'; document.documentElement.lang='fa';
    document.getElementById('sub').textContent = 'نصب در ۳ مرحله — مدل، کلید، پیام‌رسان';
  }
}

renderProviders();
renderMessengers();
</script>
</body>
</html>"""


def write_yaml_config(provider_id: str, model: str) -> None:
    """Merge model+display settings into config.yaml — NEVER clobbers user config."""
    cfg = GALAHAD_HOME / "config.yaml"
    cfg.parent.mkdir(parents=True, exist_ok=True)
    p = FREE_PROVIDERS[provider_id]
    try:
        import yaml
        data = {}
        if cfg.exists():
            data = yaml.safe_load(cfg.read_text(encoding="utf-8")) or {}
            backup = cfg.with_suffix(".yaml.bak")
            backup.write_text(cfg.read_text(encoding="utf-8"), encoding="utf-8")
        data.setdefault("model", {}).update({
            "default": model,
            "provider": provider_id,
            "base_url": p["base_url"],
        })
        data.setdefault("display", {}).update({"skin": "galahad"})
        cfg.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
                       encoding="utf-8")
    except ImportError:
        # No PyYAML — append-only merge: strip old model/display blocks, append new
        lines = []
        if cfg.exists():
            skip = False
            for line in cfg.read_text(encoding="utf-8").splitlines():
                if line and not line.startswith((" ", "#")):
                    skip = line.startswith(("model:", "display:"))
                if not skip:
                    lines.append(line)
        lines += [
            "model:",
            f"  default: {model}",
            f"  provider: {provider_id}",
            f"  base_url: {p['base_url']}",
            "display:",
            "  skin: galahad",
        ]
        cfg.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _merge_env(env_file: Path, updates: dict) -> None:
    """Update/append keys in .env, preserving comments and other lines."""
    env_file.parent.mkdir(parents=True, exist_ok=True)
    lines = env_file.read_text(encoding="utf-8").splitlines() if env_file.exists() else []
    remaining = dict(updates)
    out = []
    for line in lines:
        k = line.partition("=")[0].strip() if "=" in line else ""
        if k in remaining:
            out.append(f"{k}={remaining.pop(k)}")
        else:
            out.append(line)
    out += [f"{k}={v}" for k, v in remaining.items()]
    env_file.write_text("\n".join(out) + "\n", encoding="utf-8")


def write_env(provider_id: str, api_key: str) -> None:
    """Add/update the provider's key in .env without clobbering other keys."""
    env_file = GALAHAD_HOME / ".env"
    p = FREE_PROVIDERS[provider_id]
    updates = {}
    if p["env"]:
        updates[p["env"]] = api_key
    _merge_env(env_file, updates)


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json"):
        data = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", f"{ctype}; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            html = (HTML
                    .replace("PROVIDERS_JSON", json.dumps(FREE_PROVIDERS, ensure_ascii=False))
                    .replace("MSGS_JSON", json.dumps(MESSSENGERS, ensure_ascii=False)))
            self._send(200, html, "text/html")
        else:
            self._send(404, '{"error":"not found"}')

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        try:
            body = json.loads(self.rfile.read(length) or b"{}")
        except (ValueError, UnicodeDecodeError):
            return self._send(400, json.dumps({"error": "invalid JSON"}))

        if self.path == "/api/setup_model":
            if not isinstance(body, dict):
                return self._send(400, json.dumps({"error": "body must be an object"}))
            pid = body.get("provider", "")
            key = body.get("api_key", "")
            if pid not in FREE_PROVIDERS:
                return self._send(400, json.dumps({"error": "unknown provider"}))
            p = FREE_PROVIDERS[pid]
            if p["env"] and not key:
                return self._send(400, json.dumps({"error": "api_key required"}))
            write_yaml_config(pid, p["models"][0])
            write_env(pid, key)
            self._send(200, json.dumps({"ok": True, "model": p["models"][0],
                                        "message": "کانفیگ ذخیره شد"}))

        elif self.path == "/api/setup_messengers":
            if not isinstance(body, dict):
                return self._send(400, json.dumps({"error": "body must be an object"}))
            saved = []
            updates = {}
            for mid, value in body.items():
                if mid in MESSSENGERS and isinstance(value, str) and value.strip():
                    updates[MESSSENGERS[mid]["field"]] = value.strip()
                    saved.append(MESSSENGERS[mid]["name"])
            if updates:
                _merge_env(GALAHAD_HOME / ".env", updates)
            self._send(200, json.dumps({"message": f"پیام‌رسان‌ها ذخیره شدند: {', '.join(saved) or 'هیچکدام'} — با galahad gateway start فعال می‌شوند"}))
        else:
            self._send(404, '{"error":"not found"}')

    def log_message(self, *a):
        pass


def main():
    port = 8765
    if "--port" in sys.argv:
        try:
            port = int(sys.argv[sys.argv.index("--port") + 1])
        except (ValueError, IndexError):
            print("خطا: --port باید عدد باشد")
            sys.exit(1)
    url = f"http://localhost:{port}"
    print(f"🛡️  Galahad Setup Wizard: {url}")
    print("در حال باز شدن در مرورگر... / Opening browser...")
    try:
        webbrowser.open(url)
    except Exception:
        pass
    HTTPServer(("127.0.0.1", port), Handler).serve_forever()


if __name__ == "__main__":
    main()