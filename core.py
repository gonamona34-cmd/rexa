import requests
import time
import os
import traceback
import random
from datetime import datetime

# =========================
# CONFIG
# =========================
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "0"))

# =========================
# STATE
# =========================
last_offset = None

# модулі heartbeat
modules_heartbeat = {}
MODULE_TIMEOUT = 60  # сек

# статистика
warnings_count = 0
critical_count = 0

# =========================
# QUOTES
# =========================
QUOTES = [
    "🔥 Система росте через рух.",
    "⚡ Контроль створює спокій.",
    "🌱 Маленькі кроки формують силу.",
    "🚀 Ядро тримає баланс.",
    "💡 Світ стає яснішим через дію."
]

# =========================
# TELEGRAM
# =========================
def tg_send(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    requests.post(url, json={
        "chat_id": ADMIN_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }, timeout=10)


def get_updates(offset=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"

    params = {"timeout": 25}
    if offset:
        params["offset"] = offset

    return requests.get(url, params=params, timeout=30).json()

# =========================
# HEARTBEAT SYSTEM
# =========================
def module_heartbeat(module_name):
    modules_heartbeat[module_name] = time.time()


def check_modules():
    now = time.time()

    for module, last in modules_heartbeat.items():
        if now - last > MODULE_TIMEOUT:
            log_warning(f"Модуль {module} без heartbeat")


# =========================
# LOGGING
# =========================
def log_warning(text):
    global warnings_count
    warnings_count += 1

    tg_send(f"⚠️ <b>WARNING</b>\n{text}\n\n💡 {random.choice(QUOTES)}")


def log_critical(text):
    global critical_count
    critical_count += 1

    tg_send(f"🔴 <b>CRITICAL</b>\n{text}\n\n🔥 {random.choice(QUOTES)}")


# =========================
# REPORT
# =========================
def send_status():
    quote = random.choice(QUOTES)

    modules_status = ""

    now = time.time()

    for module, last in modules_heartbeat.items():
        status = "🟢"
        if now - last > MODULE_TIMEOUT:
            status = "🔴"

        modules_status += f"{status} {module}\n"

    text = f"""
📊 СИСТЕМНИЙ ЗВІТ

⚡ Heartbeat системи: активний

📦 Модулі:
{modules_status}

⚠️ Warnings: {warnings_count}
❗ Critical: {critical_count}

💡 <i>{quote}</i>
"""

    tg_send(text)


# =========================
# HANDLER
# =========================
def handle_message(message):
    text = message.get("text", "")

    if text == "/status":
        send_status()

    elif text == "/ping":
        tg_send("🏓 pong")

    elif text.startswith("/hb"):
        # /hb module_name
        parts = text.split()
        if len(parts) > 1:
            module_heartbeat(parts[1])
            tg_send(f"🟢 Heartbeat від {parts[1]}")

    else:
        tg_send(f"📩 {text}")


# =========================
# MAIN LOOP
# =========================
def main():
    global last_offset

    tg_send("🚀 Ядро 2.0 запущене")

    while True:
        try:
            data = get_updates(last_offset)

            for update in data.get("result", []):
                last_offset = update["update_id"] + 1

                if "message" in update:
                    handle_message(update["message"])

            check_modules()

        except Exception:
            err = traceback.format_exc()
            log_critical(err)
            time.sleep(5)

        time.sleep(1)


if __name__ == "__main__":
    main()
