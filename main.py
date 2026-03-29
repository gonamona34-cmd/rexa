import time
import threading
import sys
from datetime import datetime

# ===================== CONFIG =====================
MODULES = [
    "catalog_tg",
    "buy_box",
    "telegram_core",
    "ext_module"
]

HEARTBEAT_OK = 180      # 3 хв
DEGRADED_TIME = 220     # ~3:40
DOWN_TIME = 240         # 4 хв

CHECK_INTERVAL = 10     # перевірка кожні 10 сек


# ===================== LOGGER =====================
class Logger:
    def log(self, module, status, message):
        print(f"[{datetime.now()}] {module} | {status} | {message}")


# ===================== TELEGRAM =====================
class Telegram:
    def send_red(self, text):
        print("🔴", text)

    def send_green(self, text):
        print("🟢", text)

    def send_status(self, text):
        print(text)


# ===================== CORE =====================
class Core:
    def __init__(self):
        self.logger = Logger()
        self.telegram = Telegram()

        self.modules = MODULES

        self.last_seen = {m: time.time() for m in self.modules}
        self.status = {m: "OK" for m in self.modules}

        self.start_time = time.time()

    def heartbeat(self, module):
        now = time.time()
        prev = self.status[module]

        self.last_seen[module] = now

        if prev == "DOWN":
            self.status[module] = "OK"
            self.telegram.send_green(f"{module} відновився")

        else:
            self.status[module] = "OK"

    def check(self):
        now = time.time()

        for m in self.modules:
            diff = now - self.last_seen[m]
            prev = self.status[m]

            # DEGRADED (один раз)
            if DEGRADED_TIME < diff < DOWN_TIME and prev == "OK":
                self.status[m] = "DEGRADED"
                self.logger.log(m, "DEGRADED", f"{int(diff)} сек без heartbeat")

            # DOWN (один раз)
            if diff >= DOWN_TIME and prev != "DOWN":
                self.status[m] = "DOWN"
                self.logger.log(m, "DOWN", f"{int(diff)} сек без heartbeat")
                self.telegram.send_red(f"{m} впав ({int(diff)} сек)")

    def build_status(self):
        lines = []

        for m in self.modules:
            diff = int(time.time() - self.last_seen[m])

            if self.status[m] == "OK":
                icon = "🟢"
            elif self.status[m] == "DEGRADED":
                icon = "🟡"
            else:
                icon = "🔴"

            lines.append(f"{icon} {m} — {diff} сек")

        uptime = int(time.time() - self.start_time)

        return f"""
✨ Система дихає

{chr(10).join(lines)}

⏱ Аптайм: {uptime} сек
🌿 Рух = життя
"""

    def restart(self):
        print("♻️ Перезапуск...")
        sys.exit()


# ===================== LOOP =====================
core = Core()

def core_loop():
    while True:
        core.check()
        time.sleep(CHECK_INTERVAL)


# ===================== TEST MODULE =====================
def simulate_modules():
    while True:
        core.heartbeat("catalog_tg")
        time.sleep(60)


# ===================== RUN =====================
threading.Thread(target=core_loop).start()
threading.Thread(target=simulate_modules).start()

# тест команди
while True:
    cmd = input()

    if cmd == "status":
        print(core.build_status())

    if cmd == "restart":
        core.restart()
