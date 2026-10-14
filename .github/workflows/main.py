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
BINANCE_URL = "https://api.binance.com/api/v3/klines"

def get_signal():
response = requests.get(
BINANCE_URL,
params={
"symbol": SYMBOL,
"interval": TIMEFRAME,
"limit": 30,
},
timeout=15,
)
response.raise_for_status()
candles = response.json()

if not isinstance(candles, list) or len(candles) < 21:
    raise ValueError("داده‌های بازار کافی نیست.")

closes = [float(candle[4]) for candle in candles[:-1]]

sma_short = sum(closes[-7:]) / 7
sma_long = sum(closes[-21:]) / 21
current_price = closes[-1]

if sma_short > sma_long:
    direction = "🟢 احتمال تمایل صعودی"
elif sma_short < sma_long:
    direction = "🔴 احتمال تمایل نزولی"
else:
    direction = "🟡 وضعیت خنثی"

return (
    "📊 سیگنال‌یار | تحلیل آزمایشی\n\n"
    f"💰 نماد: {SYMBOL}\n"
    f"⏱ تایم‌فریم: {TIMEFRAME}\n"
    f"💵 قیمت آخرین کندل بسته‌شده: {current_price:.2f} USDT\n\n"
    f"📈 میانگین ۷ کندل: {sma_short:.2f}\n"
    f"📉 میانگین ۲۱ کندل: {sma_long:.2f}\n\n"
    f"📍 نتیجه: {direction}\n\n"
    "⚠️ این تحلیل ساده و آموزشی است؛ "
    "تضمینی برای سود یا پیش‌بینی قطعی بازار نیست."
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
await update.effective_message.reply_text(
"سلام! 👋 به ربات SignalYar خوش آمدی.\n\n"
"برای دریافت تحلیل آزمایشی بیت‌کوین دستور زیر را بفرست:\n"
"/signal"
)

async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
message = await update.effective_message.reply_text(
"⏳ در حال دریافت اطلاعات بازار..."
)

try:
    result = await context.application.bot_data["signal_lock"].acquire()
    try:
        text = await __import__("asyncio").to_thread(get_signal)
    finally:
        context.application.bot_data["signal_lock"].release()

    await message.edit_text(text)

except requests.RequestException:
    logger.exception("Market request failed")
    await message.edit_text(
        "❌ دریافت اطلاعات بازار ناموفق بود. لطفاً بعداً دوباره تلاش کن."
    )
except Exception:
    logger.exception("Signal generation failed")
    await message.edit_text(
        "❌ هنگام تهیه تحلیل خطایی رخ داد. لطفاً دوباره تلاش کن."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
await update.effective_message.reply_text(
"دستورهای ربات:\n"
"/start - شروع\n"
"/signal - دریافت تحلیل بازار\n"
"/help - راهنما"
)

async def post_init(application: Application):
import asyncio
application.bot_data["signal_lock"] = asyncio.Lock()

def main():
if not TOKEN:
raise RuntimeError(
"متغیر TELEGRAM_BOT_TOKEN در GitHub Secrets تنظیم نشده است."
)

application = (
    Application.builder()
    .token(TOKEN)
    .post_init(post_init)
    .build()
)

application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("signal", signal))
application.add_handler(CommandHandler("help", help_command))

logger.info("SignalYar is starting")
application.run_polling(drop_pending_updates=True)

if name == "main":
main()
