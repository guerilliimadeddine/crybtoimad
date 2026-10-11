import json
import os
import time
import requests

TELEGRAM_TOKEN = "8748765412:AAG030Thdv4jFUcZ2LUT-Hso56pa2ldtF_s"
CHAT_ID = "1991436401"
CACHE_FILE = "prices_cache.json"
HEARTBEAT_FILE = "heartbeat_cache.json"  # ملف لتتبع وقت آخر رسالة دورية للبيتكوين

MIN_PRICE_FILTER = 0.0001

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
        " like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}


def send_telegram_message(message):
  url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
  payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
  try:
    requests.post(url, json=payload, timeout=10)
  except Exception as e:
    print(f"خطأ في إرسال الرسالة: {e}")


def calculate_rsi_history(closes, period=14):
  """حساب RSI الحالي والسابق للتأكد من أنه في حالة صعود"""
  if len(closes) < period + 2:
    return 50.0, 50.0

  rsis = []
  for idx in range(period + 1, len(closes) + 1):
    sub_closes = closes[:idx]
    gains, losses = [], []
    for i in range(1, len(sub_closes)):
      diff = sub_closes[i] - sub_closes[i - 1]
      if diff >= 0:
        gains.append(diff)
        losses.append(0)
      else:
        gains.append(0)
        losses.append(abs(diff))

    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period

    if avg_loss == 0:
      rsis.append(100.0)
    else:
      rs = avg_gain / avg_loss
      rsis.append(100 - (100 / (1 + rs)))

  return rsis[-1], rsis[-2]


def fetch_advanced_strategy(symbol):
  """جلب البيانات الشمعية وحساب MA 99, المقاومة, و RSI"""
  url = f"https://api.binance.com/api/v3/klines?symbol={symbol}USDT&interval=1h&limit=110"
  try:
    res = requests.get(url, headers=HEADERS, timeout=6)
    if res.status_code == 200:
      data = res.json()
      closes = [float(candle[4]) for candle in data]
      highs = [float(candle[2]) for candle in data]
      lows = [float(candle[3]) for candle in data]

      if len(closes) >= 99:
        current_price = closes[-1]
        rsi_current, rsi_prev = calculate_rsi_history(closes, 14)
        ma_99 = sum(closes[-99:]) / 99
        resistance = max(highs[-40:])
        support = min(lows[-40:])

        return {
            "price": current_price,
            "rsi_current": rsi_current,
            "rsi_prev": rsi_prev,
            "resistance": resistance,
            "support": support,
            "ma_99": ma_99,
        }
  except Exception:
    pass
  return None


def check_heartbeat(btc_price):
  """إرسال رسالة اطمئنان وسعر البيتكوين كل 30 دقيقة تقريباً"""
  current_time = time.time()
  last_time = 0

  if os.path.exists(HEARTBEAT_FILE):
    try:
      with open(HEARTBEAT_FILE, "r") as f:
        data = json.load(f)
        last_time = data.get("last_sent", 0)
    except Exception:
      pass

  # 30 دقيقة = 1800 ثانية
  if current_time - last_time >= 1800:
    heartbeat_msg = (
        f"🟢 **البوت يعمل بنجاح (فحص دوري)**\n"
        f"👑 **سعر البيتكوين (BTC)**: `${btc_price:,.2f}`\n"
        f"⚡ *النظام متصل ويراقب السوق بدقة.*"
    )
    send_telegram_message(heartbeat_msg)

    # تحديث وقت آخر رسالة
    with open(HEARTBEAT_FILE, "w") as f:
      json.dump({"last_sent": current_time}, f)


def check_strategy_signals():
  symbols = [
      "BTC",
      "ETH",
      "BNB",
      "SOL",
      "XRP",
      "ADA",
      "DOGE",
      "AVAX",
      "TRX",
      "LINK",
      "DOT",
      "UNI",
      "LTC",
      "NEAR",
      "APT",
      "ATOM",
      "XLM",
      "FIL",
      "HBAR",
      "RENDER",
      "SUI",
      "PEPE",
      "SHIB",
      "ICP",
      "ARB",
      "OP",
      "INJ",
      "TIA",
      "GRT",
      "STX",
      "IMX",
      "MKR",
      "ALGO",
      "RUNE",
      "FET",
      "THETA",
      "FLOKI",
      "WIF",
      "BONK",
      "SNX",
      "AAVE",
      "FTM",
      "FLOW",
      "SEI",
      "EGLD",
      "QNT",
      "CHZ",
      "CRV",
      "SAND",
      "MANA",
      "AXS",
      "GALA",
      "ENJ",
      "BAT",
      "ZIL",
      "KAVA",
      "ROSE",
      "AR",
      "LDO",
      "SSV",
      "DYDX",
      "BLUR",
      "PORTAL",
      "PIXEL",
      "PENDLE",
      "IOST",
      "ONE",
      "ZRX",
      "COMP",
      "SUSHI",
      "YFI",
      "BAL",
      "OCEAN",
      "AGIX",
      "JASMY",
      "CKB",
      "SC",
      "DGB",
      "RVN",
      "IO",
      "BCH",
      "ETC",
      "XMR",
      "ZEC",
      "DASH",
      "NEO",
      "EOS",
      "XTZ",
      "KSM",
      "ONT",
      "ICX",
      "QTUM",
      "WAVES",
      "OMG",
      "NEXO",
      "HOT",
      "PAXG",
      "KNC",
      "ANKR",
      "POL",
      "ORDI",
      "SATS",
      "RATS",
      "BOME",
      "MEME",
      "ZEUS",
      "TNSR",
      "SAGA",
      "OMNI",
      "REZ",
      "BB",
      "NOT",
      "LISTA",
      "ZK",
      "ZRO",
      "BLUM",
      "DOGS",
      "CATI",
      "HMSTR",
      "EIGEN",
      "SCR",
      "GOAT",
      "PENGU",
      "PNUT",
      "LUCE",
      "ACT",
      "CHILLGUY",
      "JUP",
      "PYTH",
      "W",
      "JTO",
      "MANTA",
      "ALT",
      "XAI",
      "ACE",
      "NFP",
      "AI",
      "XEM",
      "LSK",
      "ARDR",
      "ZEN",
      "XVG",
      "SYS",
      "FUN",
      "STORJ",
      "ANT",
      "RLC",
      "CVC",
      "LOOM",
      "SNT",
      "POWR",
      "BLZ",
  ]

  alerts = []
  btc_current_price = 0

  for sym in symbols:
    data = fetch_advanced_strategy(sym)
    if data and data["price"] >= MIN_PRICE_FILTER:
      price = data["price"]

      # حفظ سعر البيتكوين لاستخدامه في رسالة الاطمئنان
      if sym == "BTC":
        btc_current_price = price

      resistance = data["resistance"]
      rsi_curr = data["rsi_current"]
      rsi_prev = data["rsi_prev"]
      ma_99 = data["ma_99"]

      # الشروط الاستراتيجية
      is_near_resistance = price >= (resistance * 0.99)
      is_rsi_rising = rsi_curr > rsi_prev
      is_above_ma99 = price > ma_99

      if is_near_resistance and is_rsi_rising and is_above_ma99:
        alert_msg = (
            f"🎯 **فرصة اختراق مؤكدة (شروط مطابقة)**\n"
            f"🟢 **العملة**: `{sym}`\n"
            f"💵 السعر الحالي: `${price:,.4f}`\n"
            f"⚔️ خط المقاومة: `${resistance:,.4f}`\n"
            f"📈 **MA 99**: `${ma_99:,.4f}` (السعر فوق المتوسط)\n"
            f"📊 **RSI الصاعد**: `{rsi_curr:.1f}` (كان `{rsi_prev:.1f}` ↗️)\n"
            f"🛡️ الدعم القريب: `${data['support']:,.4f}`"
        )
        alerts.append(alert_msg)

  # فحص إرسال رسالة الاطمئنان الدورية للبيتكوين كل نصف ساعة
  if btc_current_price > 0:
    check_heartbeat(btc_current_price)

  # إرسال تنبيهات الصفقات إذا وجدت
  if alerts:
    for msg in alerts:
      send_telegram_message(msg)
      print("تم إرسال إشارة استراتيجية متقدمة بنجاح.")
  else:
    print(
        "لا توجد عملات تطابق شروط المقاومة + صعود RSI + فوق MA 99 في هذه"
        " الدورة."
    )


if __name__ == "__main__":
  check_strategy_signals()
