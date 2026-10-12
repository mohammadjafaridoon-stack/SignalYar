
import os
import requests
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام! به SignalYar خوش آمدی.\n\n"
        "/signal - دریافت وضعیت آزمایشی بازار\n"
        "/help - راهنما\n\n"
        "این نسخه هنوز سیگنال واقعی تولید نمی‌کند."
    )


async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        url = (
            "https://api.binance.com/api/v3/ticker/price"
            "?symbol=BTCUSDT"
        )
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        price = float(response.json()["price"])

        message = (
            "📊 SignalYar | BTC/USDT\n\n"
            f"💰 قیمت فعلی: {price:,.2f} USDT\n\n"
            "⏳ وضعیت: در انتظار تأیید\n"
            "🟢 ورود لانگ: تأیید نشده\n"
            "🔴 ورود شورت: تأیید نشده\n\n"
            "این پیام سیگنال ورود نیست."
        )
        await update.message.reply_text(message)

    except Exception:
        await update.message.reply_text(
            "دریافت قیمت ناموفق بود. دوباره تلاش کن."
        )


async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        "دستورها:\n"
        "/start - شروع\n"
        "/signal - بررسی قیمت بیت‌کوین\n"
        "/help - راهنما\n\n"
        "ربات معامله خودکار انجام نمی‌دهد."
    )


def main():
    if not TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN تنظیم نشده است.")

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("signal", signal))
    app.add_handler(CommandHandler("help", help_command))
    app.run_polling()


if __name__ == "__main__":
    main()
