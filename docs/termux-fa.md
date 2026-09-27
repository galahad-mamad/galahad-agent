# راهنمای نصب گلاهد ایجنت روی اندروید (Termux)

ایجنت گلاهد مستقیم روی گوشی اندرویدی با [Termux](https://termux.dev) اجرا می‌شه. این راهنمای رسمی فارسیه؛ نسخه‌ی انگلیسی: [`website/docs/getting-started/termux.md`](../website/docs/getting-started/termux.md)

> ⚠️ ترموکس پلتفرم سطح ۲ هست — یعنی نصب روی اندروید پشتیبانی best-effort داره و ممکنه بعضی قابلیت‌ها (مرورگر، صدا، داکر) کار نکنن. ولی به‌عنوان CLI کامل روی گوشی کار می‌کنه.

## چی نصب می‌شه و چی نه؟

✅ پشتیبانی‌شده در مسیر تست‌شده:
- CLI کامل گلاهد + چت تعاملی
- کران (job زمان‌بندی‌شده)
- ترمینال پس‌زمینه / PTY
- گیت‌وی تلگرام (اجرای دستی/بهترین‌تلاش در پس‌زمینه)
- MCP و حافظه Honcho

❌ فعلاً پشتیبانی نمی‌شه:
- `.[all]` کامل (اکسترای voice به `ctranslate2` نیاز داره که برای اندروید build نداره)
- راه‌اندازی خودکار مرورگر / Playwright
- ایزولاسیون داکری
- اندروید ممکنه پروسه‌های پس‌زمینه رو بخوابونه — موندگاری گیت‌وی تضمینی نیست

---

## روش ۱ — نصب تک‌دستی (توصیه‌شده، کامل و قابل‌عیب‌یابی)

### ۱. ترموکس رو از F-Droid نصب کن

از **گوگل‌پلی نصب نکن** (نسخه‌ی پلی‌استور قدیمی و قطع‌شده‌ست). این آدرس F-Droid:

```
https://f-droid.org/packages/com.termux/
```

### ۲. آپدیت پکیج‌ها + نصب ابزارهای سیستمی

```bash
pkg update -y
pkg install -y git python clang rust make pkg-config libffi openssl nodejs ripgrep ffmpeg
```

| پکیج | چرا لازمه |
|---|---|
| python | خود رانتایم + venv |
| git | گرفتن ریپو |
| clang rust make pkg-config libffi openssl | build کردن چند وابستگی پایتون روی اندروید |
| nodejs | ابزار مرورگر/آزمایشی (اختیاری) |
| ripgrep | جستجوی سریع فایل |
| ffmpeg | تبدیل مدیا / TTS |

### ۳. گرفتن ریپو

```bash
git clone https://github.com/galahad-mamad/galahad-agent.git
cd galahad-agent
```

### ۴. ساخت محیط مجازی (مهم‌ترین مرحله)

```bash
python -m venv venv
source venv/bin/activate
export ANDROID_API_LEVEL="$(getprop ro.build.version.sdk)"
python -m pip install --upgrade pip setuptools wheel
```

> 🔑 `ANDROID_API_LEVEL` رو حتماً ست کن — پکیج‌های Rust مثل `jiter` بدون این متغیر build نمی‌شن.

### ۵. نصب باندل تست‌شده‌ی ترموکس

```bash
python -m pip install -e '.[termux]' -c constraints-termux.txt
```

اگه فقط هسته‌ی حداقلی می‌خوای:

```bash
python -m pip install -e '.' -c constraints-termux.txt
```

### ۶. گذاشتن `galahad` روی PATH ترموکس

```bash
ln -sf "$PWD/venv/bin/galahad" "$PREFIX/bin/galahad"
```

بعد از این، تو هر shell جدیدی `galahad` در دسترسه و لازم نیست venv رو دوباره activate کنی.

### ۷. تست و اجرا

```bash
galahad version
galahad doctor
galahad
```

---

## روش ۲ — اسکرپت نصب خودکار

```bash
pkg install -y curl
curl -fsSL https://raw.githubusercontent.com/galahad-mamad/galahad-agent/main/scripts/install.sh | bash
```

اسکرپت روی ترموکس خودکار:
- با `pkg` پکیج‌های سیستمی رو می‌گیره
- venv با `python -m venv` می‌سازه
- اول `.[termux-all]` و بعد `.[termux]` و آخر base رو تست می‌کنه
- `galahad` رو توی `$PREFIX/bin` لینک می‌کنه
- bootstrapp مرورگر/واتساپ رو رد می‌کنه (تست‌نشده روی اندروید)

---

## تنظیمات بعد از نصب

```bash
galahad model      # انتخاب پروایدر و مدل
galahad setup      # ویزارد کامل تنظیمات
```

یا کلید API رو مستقیم در `~/.galahad/.env` بذار.

### اتصال ربات تلگرام روی گوشی

```bash
bash gateway-plugins/connect.sh
```

اسکریپت ازت توکن ربات می‌خواد و فایل env رو پر می‌کنه. بعد:

```bash
galahad gateway
```

> ⚠️ اندروید ممکنه حین خواب بودن، ترموکس رو متوقف کنه. برای ران طولانی‌مدت:
> **تنظیمات باتری → اپ Termux → بدون محدودیت (Unrestricted)**
> و گزینه‌ی wake-lock ترموکس (`termux-wake-lock`) رو بزن.

---

## عیب‌یابی

**خطای «No solution found» برای `.[all]`:**
مسیر تست‌شده‌ی ترموکس رو بزن: `pip install -e '.[termux]' -c constraints-termux.txt` (مشکل از اکسترای voice هست).

**خطای `uv pip install`:**
روی اندروید `uv` جواب نمی‌ده؛ از venv استاندارد + pip استفاده کن (روش ۱).

**خطای `jiter` / `maturin` / ANDROID_API_LEVEL:**
```bash
export ANDROID_API_LEVEL="$(getprop ro.build.version.sdk)"
```
بعد دوباره pip install کن.

**`galahad doctor` میگه ripgrep یا node نیست:**
```bash
pkg install ripgrep nodejs
```

**خطای build هنگام pip install:**
```bash
pkg install clang rust make pkg-config libffi openssl
```
و دوباره نصب رو تکرار کن.

**کند بودن pip:**
```bash
pip config set global.index-url https://pypi.org/simple
```

---

## آپدیت نسخه روی ترموکس

```bash
cd galahad-agent
source venv/bin/activate
git pull
python -m pip install -e '.[termux]' -c constraints-termux.txt
```

## غیرفعال‌سازی/حذف

```bash
rm "$PREFIX/bin/galahad"
rm -rf ~/.galahad galahad-agent
```

---

## محدودیت‌های شناخته‌شده روی گوشی

- داکر در دسترس نیست
- تبدیل گفتار به نوشتار محلی (`faster-whisper`) در مسیر تست‌شده نیست
- ابزار مرورگر عمداً در نصب فعال نمی‌شه (آزمایشی محسوب می‌شه)
- فقط باندل‌های `.[termux]` و `.[termux-all]` رسماً تست شدن

اگه مشکل اندروید-اختصاصی جدیدی دیدی، توی GitHub issue بزن با این اطلاعات:
نسخه اندروید، خروجی `termux-info`، `python --version`، `galahad doctor` و متن کامل خطا.
