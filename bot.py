import json
import os
import time
import requests

TELEGRAM_TOKEN = "8748765412:AAG030Thdv4jFUcZ2LUT-Hso56pa2ldtF_s"
CHAT_ID = "1991436401"
CACHE_FILE = "prices_cache.json"
THRESHOLD_PERCENT = 0.1

# إضافة Headers عشان الـ API ما يحظر خوادم غيتهاب
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
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
  # المحاولة الأولى عبر CoinCap
  try:
    url = "https://api.coincap.io/v2/assets?limit=100"
    res = requests.get(url, headers=HEADERS, timeout=10)
    print(f"CoinCap Status Code: {res.status_code}")
    if res.status_code == 200:
      data = res.json().get("data", [])
      if data:
        return {
            coin["symbol"].upper(): float(coin["priceUsd"]) for coin in data
        }
  except Exception as e:
    print(f"خطأ في الاتصال بـ CoinCap: {e}")

  # المحاولة الثانية عبر Binance كبديل
  try:
    url = "https://api.binance.com/api/v3/ticker/price"
    res = requests.get(url, headers=HEADERS, timeout=10)
    print(f"Binance Status Code: {res.status_code}")
    if res.status_code == 200:
      data = res.json()
      prices = {}
      for coin in data:
        symbol = coin["symbol"]
        if symbol.endswith("USDT"):
          prices[symbol.replace("USDT", "")] = float(coin["price"])
      if prices:
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
    print("❌ فشل جلب الأسعار من جميع المصادر!")
    return

  print(f"✅ تم جلب بنجاح {len(new_prices)} عملة.")

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

  # حفظ الأسعار الجديدة في الملف
  with open(CACHE_FILE, "w") as f:
    json.dump(new_prices, f, indent=4)
  print(f"تم كتابة الأسعار في ملف {CACHE_FILE}")

  if alerts:
    msg = (
        "🚨 **تنبيه حركة الأسعار (بنسبة 0.1% أو أكثر)**\n\n"
        + "\n\n".join(alerts[:15])
    )
    send_telegram_message(msg)


if __name__ == "__main__":
  check_price_spikes()
