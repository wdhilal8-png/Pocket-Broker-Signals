
import telebot
import requests
import pandas as pd
from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator

TOKEN = "8967836017:AAGICmD4p7ReIAZJYAf8cRhUFixngpBEkTU"
API_KEY = "bf1df7e642b94f189ff0272831717afb"

bot = telebot.TeleBot(TOKEN)

def get_signal(symbol):
    url = f"https://YOUR_API_URL?symbol={symbol}&interval=1m&apikey={API_KEY}"

    data = requests.get(url).json()

    closes = [float(c["close"]) for c in data["values"]]

    df = pd.DataFrame(closes, columns=["close"])

    ema9 = EMAIndicator(df["close"], 9).ema_indicator().iloc[-1]
    ema21 = EMAIndicator(df["close"], 21).ema_indicator().iloc[-1]
    rsi = RSIIndicator(df["close"], 14).rsi().iloc[-1]

    macd = MACD(df["close"])
    macd_line = macd.macd().iloc[-1]
    signal_line = macd.macd_signal().iloc[-1]

    if ema9 > ema21 and rsi > 55 and macd_line > signal_line:
        return "🟢 BUY"

    if ema9 < ema21 and rsi < 45 and macd_line < signal_line:
        return "🔴 SELL"

    return "🟡 WAIT"

@bot.message_handler(func=lambda m: True)
def reply(message):
    signal = get_signal(message.text.upper())
    bot.reply_to(message, signal)

print("Bot Running...")
bot.infinity_polling()
