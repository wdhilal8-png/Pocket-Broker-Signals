import telebot
import requests
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator

TOKEN = "8967836017:AAGICmD4p7ReIAZJYAf8cRhUFixngpBEkTU"
API_KEY = "23bdbe8662e241bd8024a39e8ddf534b"

bot = telebot.TeleBot(TOKEN)

def analyze_pair(pair):
    pair = pair.upper().replace(" ", "").replace("/", "").replace("OTC", "")

    symbol = pair[:3] + "/" + pair[3:]

    url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval=1min&outputsize=100&apikey={API_KEY}"

    response = requests.get(url)
    data = response.json()

    if "values" not in data:
        return "❌ الزوج غير موجود"

    closes = [float(x["close"]) for x in reversed(data["values"])]

    df = pd.DataFrame(closes, columns=["close"])

    rsi = RSIIndicator(df["close"], window=14).rsi().iloc[-1]
    ema9 = EMAIndicator(df["close"], window=9).ema_indicator().iloc[-1]
    ema21 = EMAIndicator(df["close"], window=21).ema_indicator().iloc[-1]

    if ema9 > ema21 and rsi > 55:
        signal = "📈 BUY"
    elif ema9 < ema21 and rsi < 45:
        signal = "📉 SELL"
    else:
        signal = "⏳ WAIT"

    return f"""
📊 {pair}

{signal}

RSI: {round(rsi,2)}

EMA9 : {round(ema9,5)}
EMA21: {round(ema21,5)}

⌛ مدة الصفقة: 1 دقيقة
"""

@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(message, "أرسل الزوج مثل:\nEURUSD\nGBPUSD\nUSDJPY")

@bot.message_handler(func=lambda m: True)
def reply(message):
    result = analyze_pair(message.text)
    bot.reply_to(message, result)

print("Bot Running...")
bot.infinity_polling(skip_pending=True)
