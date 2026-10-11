import json
import os
import requests

TELEGRAM_TOKEN = "8748765412:AAG030Thdv4jFUcZ2LUT-Hso56pa2ldtF_s"
CHAT_ID = "1991436401"
PRICES_FILE = "prices.json"


def send_telegram_message(message):
  url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
  payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
  try:
    requests.post(url, json=payload, timeout=10)
  except Exception as e:
    print(f"خطأ في إرسال الرسالة: {e}")


def load_prices():
  if os.path.exists(PRICES_FILE):
    try:
      with open(PRICES_FILE, "r") as f:
        return json.load(f)
    except:
      return {}
  return {}


def save_prices(prices):
  with open(PRICES_FILE, "w") as f:
    json.dump(prices, f, indent=4)


def check_market():
  try:
    url = "https://api.coincap.io/v2/assets?limit=100"
    response = requests.get(url, timeout=15)
    if response.status_code != 200:
      print(f"خطأ في جلب البيانات: {response.status_code}")
      return

    data = response.json()
    coins = data.get("data", [])
    previous_prices = load_prices()
    current_prices = {}
    significant_changes = []

    for coin in coins:
      symbol = coin.get("symbol", "").upper()
      name = coin.get("name", "")
      current_price = float(coin.get("priceUsd", 0))
      current_prices[symbol] = current_price

      if symbol not in previous_prices:
        continue

      old_price = previous_prices[symbol]
      change_pct = ((current_price - old_price) / old_price) * 100

      if abs(change_pct) >= 0.1:
        direction = "🚀 صعود" if change_pct > 0 else "🔻 هبوط"
        significant_changes.append(
            f"• **{name} ({symbol})**: {direction} `{change_pct:.2f}%` | السعر:"
            f" `${current_price:,.4f}`"
        )

    # حفظ الأسعار الجديدة للمقارنة في المرة القادمة
    save_prices(current_prices)

    if significant_changes:
      msg = (
          "📊 **تقرير حركة السوق (تغيرات بنسبة 0.1% فأكثر)**\n\n"
          + "\n".join(significant_changes[:15])
      )
      send_telegram_message(msg)
      print("تم رصد وإرسال التغيرات بنجاح.")
    else:
      print("تم الفحص بنجاح، ولم تتجاوز أي عملة نسبة 0.1% حالياً.")

  except Exception as e:
    print(f"حدث خطأ أثناء فحص السوق: {e}")


if __name__ == "__main__":
  check_market()
