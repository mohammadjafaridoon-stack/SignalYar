import os
import requests
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

SYMBOL = "BTCUSDT"
TIMEFRAME = "15m"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام! به SignalYar خوش آمدی. 🤖\n\n"
        "دستورها:\n"
        "/signal - بررسی بازار و دریافت وضعیت\n"
        "/help - راهنما\n\n"
        "ربات معامله خودکار انجام نمی‌دهد."
    )


def get_market_data():
    url = "https://api.binance.com/api/v3/klines"

    response = requests.get(
        url,
        params={
            "symbol": SYMBOL,
            "interval": TIMEFRAME,
            "limit": 50,
        },
        timeout=15,
    )
    response.raise_for_status()

    candles = response.json()

    closes = [float(candle[4]) for candle in candles]
    price = closes[-1]

    sma_short = sum(closes[-7:]) / 7
    sma_long = sum(closes[-25:]) / 25

    return price, sma_short, sma_long


async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        price, sma_short, sma_long = get_market_data()

        if sma_short > sma_long and price > sma_short:
            status = "🟢 تمایل صعودی اولیه"
            direction = "لانگ؛ فقط در صورت تأیید بیشتر"
        elif sma_short < sma_long and price < sma_short:
            status = "🔴 تمایل نزولی اولیه"
            direction = "شورت؛ فقط در صورت تأیید بیشتر"
        else:
            status = "🟡 وضعیت نامشخص"
            direction = "فعلاً ورود تأیید نشده"

        message = (
            f"📊 SignalYar | {SYMBOL}\n"
            f"⏱ تایم‌فریم: {TIMEFRAME}\n\n"
            f"💰 قیمت فعلی: {price:,.2f} USDT\n"
            f"📈 میانگین کوتاه: {sma_short:,.2f}\n"
            f"📉 میانگین بلند: {sma_long:,.2f}\n\n"
            f"📍 وضعیت: {status}\n"
            f"🔎 بررسی جهت: {direction}\n\n"
            "⚠️ تحلیل اولیه است، نه سیگنال قطعی.\n"
            "حد ضرر و حد سود قبل از معامله باید جداگانه بررسی شوند."
        )

        await update.message.reply_text(message)

    except Exception:
        await update.message.reply_text(
            "❌ دریافت اطلاعات بازار ناموفق بود.\n"
            "لطفاً کمی بعد دوباره تلاش کن."
        )


async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    await update.message.reply_text(
        "راهنمای SignalYar\n\n"
        "/start - شروع ربات\n"
        "/signal - بررسی بازار در تایم‌فریم ۱۵ دقیقه\n"
        "/help - نمایش راهنما\n\n"
        "این ربات معامله خودکار انجام نمی‌دهد.\n"
        "نتیجه تحلیل تضمین‌کننده سود نیست."
    )


def main():
    if not TOKEN:
        raise RuntimeError(
            "متغیر TELEGRAM_BOT_TOKEN در GitHub Secrets تنظیم نشده است."
        )

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("signal", signal))
    app.add_handler(CommandHandler("help", help_command))

    app.run_polling()


if __name__ == "__main__":
    main()
