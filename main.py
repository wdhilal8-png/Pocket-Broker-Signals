import telebot
import requests
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator

TOKEN = "8967836017:AAGICmD4p7ReIAZJYAf8cRhUFixngpBEkTU"
SSID= "po_uuid=a08b3779-b903-4b4a-87d6-2dc485a98155; lang=ar; loggedIn=1; no-login-captcha=1; is_pwa=0; hb9prtcp_m=1; _ga=GA1.1.267285269.1778074238; _scid=srF2u3Kf2264vDTTxKVwfY_GMjB8SNsO; lo_src=unknown; lo_uid=1778074238522-s6jm6k91vc; _tt_enable_cookie=1; _ttp=01KQYQQG1E11GKW73ZQX18NRDE_.tt.1; afUserId=42e64f0c-a636-4424-8cf0-d6e2f4ffc4c4-p; autologin=a%3A2%3A%7Bs%3A6%3A%22key_id%22%3Bs%3A16%3A%22de2c97f09d80ab2b%22%3Bs%3A7%3A%22user_id%22%3Bs%3A9%3A%22118530970%22%3B%7D; _uetvid=c502e080494f11f1ac894f1c4f14eedd; _sctr=1%7C1779919200000; _gcl_au=1.1.486531124.1778074237.1569718260.1780336637.1780336638; _scid_r=wzF2u3Kf2264vDTTxKVwfY_GMjB8SNsOj52N4Q; _ga_8D1Z2CLK9Z=GS2.1.s1780488278$o76$g1$t1780489460$j60$l0$h0$dAZz7St6egp9goAgHCbin9nij6UyqmcoP3A; ttcsid=1780488280467::pLz0gJhYKDDMbGP0k9ng.59.1780489555827.0::1.1178567.1181705::1275354.108.716.1238::0.0.0; ttcsid_CPC6SBRC77U2IO5KPOI0=1780488280464::-Cpr3QaXbpPgqOrc3i0H.59.1780489555828.1; ttcsid_D54NB53C77U5DJL508B0=1780488280477::4sx66JGmRRIKOXeReGlE.59.1780489555828.1; is_hidden_formula1_promocodes_modal=1; mv2i=1; referer=https%3A%2F%2Fwww.google.com%2F; ci_session=a%3A4%3A%7Bs%3A10%3A%22session_id%22%3Bs%3A32%3A%22d9249aad39b0f4e432efcc8d592ccd32%22%3Bs%3A10%3A%22ip_address%22%3Bs%3A14%3A%22154.100.34.197%22%3Bs%3A10%3A%22user_agent%22%3Bs%3A101%3A%22Mozilla%2F5.0%20%28X11%3B%20Linux%20x86_64%29%20AppleWebKit%2F537.36%20%28KHTML%2C%20like%20Gecko%29%20Chrome%2F143.0.0.0%20Safari%2F537.36%22%3Bs%3A13%3A%22last_activity%22%3Bi%3A1781795616%3B%7D23db1d140ed7cb008070c3012edc12ee; be_chart-1=expanded; cm_chart-1=0; hutlm12=1; pageview_id=1782332918738203; zoom-width=[[1%2C2%2C0.2]]'
﻿"

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
