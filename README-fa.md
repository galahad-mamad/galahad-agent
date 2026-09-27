# گلهاد ایجنت ⚔ — راهنمای فارسی

**ایجنت هوش مصنوعی خودبهبودیاب که کامل به فارسی کار می‌کند.**

## نصب

```bash
git clone https://github.com/galahad-mamad/galahad-agent.git
cd galahad-agent
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
galahad setup
```

### نصب روی اندروید (Termux) 📱

راهنمای کامل و گام‌به‌گام فارسی: **[docs/termux-fa.md](docs/termux-fa.md)**

خلاصه:

```bash
pkg update -y && pkg install -y git python clang rust make pkg-config libffi openssl nodejs ripgrep ffmpeg
git clone https://github.com/galahad-mamad/galahad-agent.git
cd galahad-agent
python -m venv venv && source venv/bin/activate
export ANDROID_API_LEVEL="$(getprop ro.build.version.sdk)"
python -m pip install -e '.[termux]' -c constraints-termux.txt
ln -sf "$PWD/venv/bin/galahad" "$PREFIX/bin/galahad"
galahad
```

ویزارد وب فارسی (تنظیم مدل، تلگرام، واتساپ، دیسکورد):

```bash
python3 tools-galahad/setup_wizard.py
```

## دستورات اسلش ویژه

| دستور | کار |
|---|---|
| `/recap` | خلاصه‌ی آنی همان سشن (تعداد پیام، ابزارها، فایل‌های دست‌خورده) — بدون فراخوانی مدل، آفلاین |
| `/pocket` | جیب همیشه‌زنده برای تکه‌متن‌ها: `/pocket save wifi-hotel "رمز: …" #سفر` · `/pocket search wifi` · `/pocket get wifi-hotel` (کپی خودکار کلیپ‌بورد، سازگار با ترموکس) |
| `/later` | یادآوری طبیعی: `/later 30m استراحت` یا `/later every 2h چک کردن بیلد` |

## اتصال پیام‌رسان‌ها (راهنمای تصویری فارسی)

```bash
bash gateway-plugins/connect.sh telegram
bash gateway-plugins/connect.sh whatsapp
bash gateway-plugins/connect.sh discord
```

## پلاگین‌های دسکتاپ

پوشه `desktop-plugins/` را به `~/.galahad/desktop-plugins/` کپی کنید؛
اپ دسکتاپ گلهاد آن‌ها را خودکار بارگذاری می‌کند:

- **galahad-model-switcher** — سوئیچ سریع مدل با پریست پروایدرهای رایگان
- **galahad-persian-rtl** — راست‌به‌چپ خودکار برای متون فارسی
- **galahad-session-dashboard** — داشبورد زنده سشن، مدل، پروفایل
- **galahad-skill-manager** — مدیریت و مرور اسکیل‌ها

## اسکین فارسی

```bash
cp skins/galahad.yaml ~/.galahad/skins/
galahad config set display.skin galahad
```

## اسکیل‌های آماده

- `galahad-tutor` — معلم خصوصی فارسی‌زبان
- `galahad-mobile-repair` — راهنمای تعمیر موبایل

## ابزارهای فارسی (plugins-custom)

- `everyday.py` — کارهای روزمره (نماز، تقویم شمسی، قیمت ارز/طلا)
- `mobile_repair.py` — دیتابیس عیب‌یاری موبایل

## دستورهای اصلی

| دستور | کار |
|---|---|
| `galahad` | چت تعاملی TUI |
| `galahad setup` | تنظیم اولیه |
| `galahad gateway run` | اجرای گیت‌وی (تلگرام/واتساپ/…) |
| `galahad model` | عوض کردن مدل |
| `galahad status` | وضعیت |
| `galahad cron` | کارهای زمان‌بندی‌شده |

مخزن_home: `~/.galahad/` (با متغیر `GALAHAD_HOME` قابل تغییر است).
