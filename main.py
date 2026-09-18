import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
players = {}

def get_player(user_id):
    if user_id not in players:
        players[user_id] = {"points": 100}
    return players[user_id]

def menu():
    keyboard = [
        [InlineKeyboardButton("🎮 بازی", callback_data="play")],
        [InlineKeyboardButton("💰 موجودی", callback_data="balance")]
    ]
    return InlineKeyboardMarkup(keyboard)

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
        return

    if query.data == "play":
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

def main():
    if not TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN تنظیم نشده است.")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
