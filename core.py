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

modules_heartbeat = {}
MODULE_TIMEOUT = 60

warnings_count = 0
critical_count = 0

# =========================
# QUOTES
# =========================
QUOTES = [
    "🔥 Система росте через рух",
    "⚡ Контроль створює спокій",
    "🌱 Кожен крок формує силу",
    "🚀 Ядро тримає баланс",
    "💡 Світ стає яснішим через дію"
]

# =========================
# TELEGRAM
# =========================
def tg_send(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    try:
        requests.post(url, json={
            "chat_id": ADMIN_CHAT_ID,
            "text": text,
            "parse_mode": "HTML"
        }, timeout=10)
    except Exception as e:
        print("Telegram error:", e)


def get_updates(offset=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"

    params = {"timeout": 25}
    if offset:
        params["offset"] = offset

    return requests.get(url, params=params, timeout=30).json()

# =========================
# MODULES HEARTBEAT
# =========================
def module_heartbeat(name):
    modules_heartbeat[name] = time.time()


def check_modules():
    now = time.time()

    for name, last in modules_heartbeat.items():
        if now - last > MODULE_TIMEOUT:
            log_warning(f"Модуль '{name}' без heartbeat")


# =========================
# LOGS
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
# STATUS
# =========================
def send_status():
    now = time.time()

    modules_text = ""

    for name, last in modules_heartbeat.items():
        status = "🟢"
        if now - last > MODULE_TIMEOUT:
            status = "🔴"

        modules_text += f"{status} {name}\n"

    text = f"""
📊 <b>СИСТЕМНИЙ ЗВІТ</b>

⚡ Heartbeat: активний

📦 Модулі:
{modules_text if modules_text else '—'}

⚠️ Warnings: {warnings_count}
❗ Critical: {critical_count}

💡 <i>{random.choice(QUOTES)}</i>
"""

    tg_send(text)


# =========================
# HANDLER
# =========================
def handle_message(message):
    text = message.get("text", "")

    # лог тільки в консоль
    print(f"MSG: {text}")

    # команди
    if text == "/start":
        tg_send("🚀 Ядро активовано")

    elif text == "/status":
        send_status()

    elif text == "/ping":
        tg_send("🏓 pong")

    elif text.startswith("/hb"):
        parts = text.split()
        if len(parts) > 1:
            module_heartbeat(parts[1])
            tg_send(f"🟢 Heartbeat: {parts[1]}")

# =========================
# MAIN LOOP
# =========================
def main():
    global last_offset

    tg_send("🚀 Ядро запущене")

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
