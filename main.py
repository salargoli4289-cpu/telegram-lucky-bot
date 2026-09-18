import os
import random
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

players = {}
app = Flask(__name__)
application = None


def get_player(user_id):
    if user_id not in players:
        players[user_id] = {"points": 100}
    return players[user_id]


def menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎮 بازی", callback_data="play")],
        [InlineKeyboardButton("💰 موجودی", callback_data="balance")]
    ])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    player = get_player(update.effective_user.id)

    await update.message.reply_text(
        f"سلام 👋\n"
        f"به ربات ضریب شانسی خوش آمدی!\n\n"
        f"امتیاز شما: {player['points']}",
        reply_markup=menu()
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    player = get_player(query.from_user.id)

    if query.data == "balance":
        await query.edit_message_text(
            f"💰 موجودی شما:\n\nامتیاز: {player['points']}",
            reply_markup=menu()
        )

    elif query.data == "play":
        multiplier = round(random.uniform(1.00, 10.00), 2)

        if multiplier >= 2.00:
            player["points"] += 10
            result = "🎉 بردی! +10 امتیاز"
        else:
            player["points"] = max(0, player["points"] - 5)
            result = "😅 این بار باختی! -5 امتیاز"

        await query.edit_message_text(
            f"🎲 ضریب این دور: {multiplier}x\n\n"
            f"{result}\n"
            f"امتیاز فعلی: {player['points']}",
            reply_markup=menu()
        )


@app.route("/", methods=["GET"])
def home():
    return "Telegram Lucky Bot is running!"


@app.route("/webhook", methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    await application.process_update(update)
    return "OK"


async def setup():
    await application.bot.set_webhook(f"{WEBHOOK_URL}/webhook")


def main():
    global application

    if not TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN تنظیم نشده است")

    if not WEBHOOK_URL:
        raise RuntimeError("WEBHOOK_URL تنظیم نشده است")

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))

    import asyncio
    asyncio.run(application.initialize())
    asyncio.run(setup())


if __name__ == "__main__":
    main()
