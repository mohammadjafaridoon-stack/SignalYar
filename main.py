
import os
import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger("SignalYar")

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
SYMBOL = "BTCUSDT"
TIMEFRAME = "15m"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام! به SignalYar خوش آمدی 🤖\n\n"
        "/start - شروع ربات\n"
        "/signal - تحلیل بازار بیت‌کوین\n"
        "/help - راهنما\n\n"
        "ربات معامله خودکار انجام نمی‌دهد."
    )


def get_market_data():
    response = requests.get(
        "https://api.binance.com/api/v3/klines",
        params={
            "symbol": SYMBOL,
            "interval": TIMEFRAME,
            "limit": 50,
        },
        timeout=20,
    )
    response.raise_for_status()
    candles = response.json()

    if not isinstance(candles, list) or len(candles) < 25:
        raise ValueError("اطلاعات بازار کافی نیست.")

    closes = [float(candle[4]) for candle in candles]
    price = closes[-1]
    sma_short = sum(closes[-7:]) / 7
    sma_long = sum(closes[-25:]) / 25

    return price, sma_short, sma_long


async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ در حال بررسی بازار...")

    try:
        price, sma_short, sma_long = get_market_data()

        if sma_short > sma_long and price > sma_short:
            status = "🟢 تمایل صعودی اولیه"
            direction = "لانگ؛ نیازمند تأیید بیشتر"
        elif sma_short < sma_long and price < sma_short:
            status = "🔴 تمایل نزولی اولیه"
            direction = "شورت؛ نیازمند تأیید بیشتر"
        else:
            status = "🟡 وضعیت نامشخص"
            direction = "فعلاً ورود تأیید نشده"

        message = (
            f"📊 SignalYar | {SYMBOL}\n"
            f"⏱ تایم‌فریم: {TIMEFRAME}\n\n"
            f"💰 قیمت: {price:,.2f} USDT\n"
            f"📈 میانگین ۷ کندل: {sma_short:,.2f}\n"
            f"📉 میانگین ۲۵ کندل: {sma_long:,.2f}\n\n"
            f"📍 وضعیت: {status}\n"
            f"🔎 جهت احتمالی: {direction}\n\n"
            "⚠️ تحلیل اولیه است و سود را تضمین نمی‌کند.\n"
            "حد ضرر و حد سود باید جداگانه بررسی شوند."
        )
        await update.message.reply_text(message)

    except Exception as e:
        logger.exception("خطا در دریافت اطلاعات بازار")
        await update.message.reply_text(
            "❌ دریافت اطلاعات بازار ناموفق بود.\n"
            f"نوع خطا: {type(e).__name__}\n"
            "جزئیات در گزارش GitHub Actions ثبت شده است."
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📚 راهنمای SignalYar\n\n"
        "/start - شروع ربات\n"
        "/signal - تحلیل بیت‌کوین\n"
        "/help - راهنما\n\n"
        "تایم‌فریم: ۱۵ دقیقه\n"
        "ربات معامله خودکار انجام نمی‌دهد."
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

    logger.info("SignalYar در حال اجراست.")
    app.run_polling()


if __name__ == "__main__":
    main()
