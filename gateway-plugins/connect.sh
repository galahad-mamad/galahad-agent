#!/bin/bash
# Galahad Agent — Easy Messenger Connect
# راهنمای تصویری ساده برای وصل کردن تلگرام / واتساپ / دیسکورد
# Usage: bash connect.sh [telegram|whatsapp|discord]

GREEN="\033[32m"; BOLD="\033[1m"; DIM="\033[2m"; RESET="\033[0m"
MSG="$1"

show_telegram() {
  echo -e "${BOLD}📱 اتصال تلگرام${RESET}"
  echo ""
  echo "  ۱. در تلگرام بروید: ${GREEN}@BotFather${RESET}"
  echo "  ۲. پیام بفرستید: ${GREEN}/newbot${RESET}"
  echo "  ۳. یک نام و یک username (انگلیسی، آخرش bot) بدهید"
  echo "  ۴. توکن (مثل 123456:ABC-DEF...) را کپی کنید"
  echo ""
  read -rp "توکن ربات را بچسبانید: " TOKEN
  if [ -z "$TOKEN" ]; then echo "❌ توکن خالی بود"; exit 1; fi

  ENVFILE="${GALAHAD_HOME:-$HOME/.galahad}/.env"
  mkdir -p "$(dirname "$ENVFILE")"
  if [ -f "$ENVFILE" ]; then sed -i.bak '/^TELEGRAM_BOT_TOKEN=/d' "$ENVFILE"; fi
  echo "TELEGRAM_BOT_TOKEN=$TOKEN" >> "$ENVFILE"

  if command -v galahad >/dev/null 2>&1; then
    galahad gateway setup telegram 2>/dev/null || true
    galahad gateway restart 2>/dev/null || galahad gateway start 2>/dev/null || true
  fi
  echo -e "  ${GREEN}✅ تلگرام بسته شد!${RESET} از این به بعد گلهاد در تلگرام در دسترس است."
}

show_whatsapp() {
  echo -e "${BOLD}💬 اتصال واتساپ (Baileys / QR)${RESET}"
  echo ""
  echo "  ۱. عدد را انتخاب کنید:"
  echo "     1) واتساپ شخصی (QR اسکن — Baileys)"
  echo "     2) واتساپ بیزینس API (توکن متا)"
  echo ""
  read -rp "انتخاب [1]: " CHOICE
  ENVFILE="${GALAHAD_HOME:-$HOME/.galahad}/.env"
  mkdir -p "$(dirname "$ENVFILE")"
  if [ "${CHOICE:-1}" = "2" ]; then
    read -rp "WhatsApp Business Token: " TOKEN
    sed -i.bak '/^WHATSAPP_/d' "$ENVFILE" 2>/dev/null
    echo "WHATSAPP_MODE=business" >> "$ENVFILE"
    echo "WHATSAPP_TOKEN=$TOKEN" >> "$ENVFILE"
    echo "  ✅ ذخیره شد"
  else
    sed -i.bak '/^WHATSAPP_/d' "$ENVFILE" 2>/dev/null
    echo "WHATSAPP_MODE=baileys" >> "$ENVFILE"
    echo "  QR اسکن: ${BOLD}galahad gateway run${RESET} — کد QR نمایش داده می‌شود، با واتساپ موبایل اسکن کنید"
    command -v galahad >/dev/null 2>&1 && galahad gateway run &
  fi
}

show_discord() {
  echo -e "${BOLD}🎮 اتصال دیسکورد${RESET}"
  echo ""
  echo "  ۱. بروید: https://discord.com/developers/applications"
  echo "  ۲. ${GREEN}New Application${RESET} → تب ${GREEN}Bot${RESET} → ${GREEN}Reset Token${RESET} → کپی"
  echo "  ۳. در ${GREEN}Bot${RESET} گزینه ${GREEN}Message Content Intent${RESET} را روشن کنید"
  echo ""
  read -rp "توکن بات: " TOKEN
  ENVFILE="${GALAHAD_HOME:-$HOME/.galahad}/.env"
  mkdir -p "$(dirname "$ENVFILE")"
  [ -f "$ENVFILE" ] && sed -i.bak '/^DISCORD_BOT_TOKEN=/d' "$ENVFILE"
  echo "DISCORD_BOT_TOKEN=$TOKEN" >> "$ENVFILE"
  command -v galahad >/dev/null 2>&1 && (galahad gateway restart 2>/dev/null || galahad gateway start 2>/dev/null || true)
  echo -e "  ${GREEN}✅ دیسکورد بسته شد${RESET}"
}

case "${MSG,,}" in
  telegram|tg)   show_telegram ;;
  whatsapp|wa)   show_whatsapp ;;
  discord|dc)    show_discord ;;
  *)
    echo -e "${BOLD}🛡️  اتصال پیام‌رسان به گلهاد${RESET}"
    echo ""
    echo "  1) 📱 تلگرام  — ساده‌ترین: ۲ دقیقه"
    echo "  2) 💬 واتساپ"
    echo "  3) 🎮 دیسکورد"
    echo ""
    read -rp "شماره: " CH
    case "$CH" in
      1) show_telegram ;; 2) show_whatsapp ;; 3) show_discord ;;
      *) echo "❌ نامعتبر" ;;
    esac ;;
esac