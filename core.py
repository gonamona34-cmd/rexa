import os
import asyncio
from datetime import datetime, time
import random

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# =========================
# CONFIG (через env)
# =========================
BOT_TOKEN = os.getenv("8772435599:AAGR0vhjgaeTYZwK52OlYZPWbauQZ_n-WQE")
ADMIN_CHAT_ID = int(os.getenv("822993796", "0"))

REPORT_TIME = time(22, 0)  # 22:00

# =========================
# RANDOM PHRASES
# =========================
PHRASES = [
    "🧘 Спокій приходить тоді, коли все має свій ритм",
    "🌊 Потік рухається, навіть якщо ти цього не бачиш",
    "🔥 Якщо є напруга — є і розвиток",
    "⚡ Система стабільна — це теж форма сили",
    "🌿 Маленькі процеси створюють великі результати",
    "☯️ Баланс тримає систему в гармонії",
    "🧠 Контроль — це уважність до моменту",
    "🚀 Рух вперед — навіть у тиші",
    "🌙 Ніч не зупиняє систему, а лише змінює ритм",
    "🔁 Повторення створює стабільність",
]

# =========================
# CORE STATUS
# =========================
async def send_daily_report(app):
    while True:
        now = datetime.now()
        target = datetime.combine(now.date(), REPORT_TIME)

        if now > target:
            target = datetime.combine(now.date(), REPORT_TIME)
            target = target.replace(day=now.day + 1)

        await asyncio.sleep((target - now).seconds)

        phrase = random.choice(PHRASES)

        text = (
            "🟢 CORE STATUS: ALIVE\n"
            f"⏰ Time: {datetime.now().strftime('%H:%M:%S')}\n\n"
            f"{phrase}"
        )

        await app.bot.send_message(chat_id=ADMIN_CHAT_ID, text=text)


# =========================
# COMMANDS
# =========================
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🟢 Ядро дихає стабільно\n"
        f"⏰ Час: {datetime.now().strftime('%H:%M:%S')}\n"
        "✨ Потік рівний і контроль збережено"
    )
    await update.message.reply_text(text)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 Ядро активне. Система під контролем.")


# =========================
# MAIN
# =========================
async def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))

    # запуск фонової задачі
    asyncio.create_task(send_daily_report(app))

    print("🟢 CORE STARTED")

    await app.run_polling()


if __name__ == "__main__":
    asyncio.run(main())
