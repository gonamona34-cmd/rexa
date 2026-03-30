import requests
import time
import os
import traceback

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


# =========================
# TELEGRAM
# =========================
def tg_send(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={
            "chat_id": ADMIN_CHAT_ID,
            "text": text
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
# LOGIC
# =========================
def handle_message(message):
    text = message.get("text", "")
    chat_id = message["chat"]["id"]

    if text == "/status":
        tg_send("🟢 Ядро працює стабільно")

    elif text == "/ping":
        tg_send("🏓 pong")

    else:
        tg_send(f"📩 Отримано: {text}")


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
            print(err)
            tg_send(f"⚠️ Помилка:\n{err}")
            time.sleep(5)

        time.sleep(1)


if __name__ == "__main__":
    main()
