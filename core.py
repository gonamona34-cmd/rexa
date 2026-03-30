import requests
import time
import os
import traceback
import random

# =========================
# CONFIG
# =========================
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "0"))

# =========================
# STATE
# =========================
last_offset = None
last_heartbeat = time.time()
is_degraded = False

warnings_count = 0
critical_count = 0

# =========================
# QUOTES
# =========================
QUOTES = [
    "💡 Світ створюється діями, а не очікуванням.",
    "⚡ Система росте там, де є рух.",
    "🔥 Кожен збій — це крок до сили.",
    "🌱 Маленькі рішення будують великі системи.",
    "🚀 Контроль — це спокій у хаосі."
]

# =========================
# TELEGRAM
# =========================
def tg_send(text, reply_markup=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": ADMIN_CHAT_ID,
        "text": text
    }

    if reply_markup:
        payload["reply_markup"] = reply_markup

    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print("Telegram error:", e)


def get_updates(offset=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"

    params = {"timeout": 25}
    if offset:
        params["offset"] = offset

    return requests.get(url, params=params, timeout=30).json()


# =========================
# BUTTON
# =========================
def get_keyboard():
    return {
        "keyboard": [
            [{"text": "📊 Статус"}]
        ],
        "resize_keyboard": True
    }


# =========================
# REPORT
# =========================
def send_status_report():
    quote = random.choice(QUOTES)

    text = f"""
📊 <b>ЗВІТ СИСТЕМИ</b>

🟢 Heartbeat: активний
⚠️ Warnings: {warnings_count}
❗ Critical: {critical_count}

{quote}
"""

    tg_send(text)


# =========================
# LOGGING
# =========================
def log_warning(text):
    global warnings_count
    warnings_count += 1

    tg_send(f"⚠️ WARNING\n\n{text}\n\n💡 {random.choice(QUOTES)}")


def log_critical(text):
    global critical_count
    critical_count += 1

    tg_send(f"🔴 CRITICAL\n\n{text}\n\n🔥 {random.choice(QUOTES)}")


# =========================
# HANDLER
# =========================
def handle_message(message):
    text = message.get("text", "")

    # команда /status
    if text == "/status" or text == "📊 Статус":
        send_status_report()

    elif text == "/ping":
        tg_send("🏓 pong")

    elif text == "/start":
        tg_send("🚀 Система активована", reply_markup=get_keyboard())

    else:
        tg_send(f"📩 {text}")


# =========================
# HEALTH
# =========================
def heartbeat():
    global last_heartbeat, is_degraded

    last_heartbeat = time.time()

    if is_degraded:
        tg_send("🟢 Система відновилась")
        is_degraded = False


def check_health():
    global is_degraded

    if time.time() - last_heartbeat > 60:
        if not is_degraded:
            tg_send("🔴 Втрата heartbeat")
            is_degraded = True


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

            heartbeat()
            check_health()

        except Exception:
            err = traceback.format_exc()

            # трактуємо як critical
            log_critical(err)

            time.sleep(5)

        time.sleep(1)


if __name__ == "__main__":
    main()
