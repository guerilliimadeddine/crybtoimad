import json
import os
import requests

TELEGRAM_TOKEN = "8748765412:AAG030Thdv4jFUcZ2LUT-Hso56pa2ldtF_s"
CHAT_ID = "1991436401"
CACHE_FILE = "prices_cache.json"
THRESHOLD_PERCENT = 0.1

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
  # استخدام Binance API المباشر (سريع، مجاني، ولا يحظر سيرفرات غيتهاب)
  url = "https://api.binance.com/api/v3/ticker/price"
  try:
    res = requests.get(url, headers=HEADERS, timeout=15)
    print(f"Binance Status Code: {res.status_code}")
    if res.status_code == 200:
      data = res.json()
      prices = {}
      for coin in data:
        symbol = coin.get("symbol", "")
        # نأخذ العملات المرتبطة بـ USDT لجلب كل العملات الكبرى والمعروفة
        if symbol.endswith("USDT"):
          clean_symbol = symbol.replace("USDT", "")
          price = float(coin.get("price", 0))
          if price > 0:
            prices[clean_symbol] = price

      if prices:
        print(f"✅ تم بنجاح جلب {len(prices)} عملة من Binance.")
        return prices
  except Exception as e:
    print(f"خطأ في الاتصال بـ Binance: {e}")

  return {}


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

  print(f"إجمالي العملات المخزنة حالياً: {len(new_prices)}")

  alerts = []
  if old_prices:
    for symbol, price in new_prices.items():
      if symbol in old_prices:
        old_price = old_prices[symbol]
        if old_price > 0:
          change_pct = ((price - old_price) / old_price) * 100
          if abs(change_pct) >= THRESHOLD_PERCENT:
            direction = "🚀 صعود" if change_pct > 0 else "🔻 هبوط"
            emoji = "🟢" if change_pct > 0 else "🔴"
            alerts.append(
                f"{emoji} **{symbol}**: {direction} بنسبة `{change_pct:+.2f}%`\nالسعر"
                f" الحالي: `${price:,.4f}`"
            )

  # حفظ الأسعار الجديدة ليرفعها الـ Git تلقائياً
  with open(CACHE_FILE, "w") as f:
    json.dump(new_prices, f, indent=4)
  print(f"تم تحديث وحفظ ملف {CACHE_FILE}")

  if alerts:
    msg = (
        "🚨 **تنبيه حركة الأسعار (بنسبة 0.1% أو أكثر)**\n\n"
        + "\n\n".join(alerts[:15])
    )
    send_telegram_message(msg)


if __name__ == "__main__":
  check_price_spikes()
