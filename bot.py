import json
import os
import requests

TELEGRAM_TOKEN = "8748765412:AAG030Thdv4jFUcZ2LUT-Hso56pa2ldtF_s"
CHAT_ID = "1991436401"
CACHE_FILE = "prices_cache.json"

# === استراتيجية الشروط الاحترافية ===
THRESHOLD_PERCENT = 0.5  # رفعنا النسبة إلى 0.5% لتفادي الإزعاج والتركيز على الحركات الحقيقية القوية
MIN_PRICE_FILTER = (
    0.0001  # استبعاد العملات الرخيصة جداً (Scam/Dust) لتفادي التلاعب السعري
)

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


def fetch_crypto_prices():
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
  ]

  prices = {}
  for sym in symbols:
    try:
      res = requests.get(
          f"https://api.coinbase.com/v2/prices/{sym}-USD/spot",
          headers=HEADERS,
          timeout=3,
      )
      if res.status_code == 200:
        data = res.json()
        price = float(data.get("data", {}).get("amount", 0))
        if price >= MIN_PRICE_FILTER:
          prices[sym] = price
    except Exception:
      pass

  return prices


def check_price_spikes():
  old_prices = {}
  if os.path.exists(CACHE_FILE):
    try:
      with open(CACHE_FILE, "r") as f:
        old_prices = json.load(f)
    except Exception:
      old_prices = {}

  new_prices = fetch_crypto_prices()
  if not new_prices:
    print("❌ فشل جلب الأسعار تماماً!")
    return

  print(f"إجمالي العملات المفلترة والمخزنة: {len(new_prices)}")

  alerts = []
  if old_prices:
    for symbol, price in new_prices.items():
      if symbol in old_prices:
        old_price = old_prices[symbol]
        if old_price > 0:
          change_pct = ((price - old_price) / old_price) * 100

          # تطبيق الاستراتيجية الاحترافية: فلترة حسب النسبة المئوية
          if abs(change_pct) >= THRESHOLD_PERCENT:
            # تصنيف قوة الحركة (استراتيجية إضافية)
            if abs(change_pct) >= 2.0:
              status_icon = (
                  "🔥 **انفجار سعري قوي!**"
                  if change_pct > 0
                  else "💥 **انهيار حاد!**"
              )
            else:
              status_icon = "🚀 صعود ملحوظ" if change_pct > 0 else "🔻 هبوط ملحوظ"

            emoji = "🟢" if change_pct > 0 else "🔴"
            alerts.append(
                f"{emoji} {status_icon}\n🔹 **العملة**: `{symbol}`\n📊 التغير:"
                f" `{change_pct:+.2f}%`\n💵 السعر الحالي: `${price:,.4f}`"
            )

  # حفظ الأسعار الجديدة للمقارنة القادمة
  with open(CACHE_FILE, "w") as f:
    json.dump(new_prices, f, indent=4)
  print(f"تم تحديث وحفظ ملف {CACHE_FILE}")

  # إرسال التنبيهات مقسمة ومنظمة باحترافية
  if alerts:
    batch_size = 5  # جعل كل رسالة تحتوي على 5 تنبيهات واضحة ومركزة للتداول
    for i in range(0, len(alerts), batch_size):
      batch = alerts[i : i + batch_size]
      msg = (
          f"📊 **تقرير استراتيجية السوق (دفعة {i // batch_size + 1})**\n\n"
          + "\n\n-------------------\n\n".join(batch)
      )
      send_telegram_message(msg)


if __name__ == "__main__":
  check_price_spikes()
