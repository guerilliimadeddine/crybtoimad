import json
import os
import subprocess
import time
import requests

TELEGRAM_TOKEN = "8748765412:AAG030Thdv4jFUcZ2LUT-Hso56pa2ldtF_s"
CHAT_ID = "1991436401"
CACHE_FILE = "prices_cache.json"
THRESHOLD_PERCENT = 0.1  # 0.1%


def send_telegram_message(message):
  url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
  payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
  try:
    requests.post(url, json=payload, timeout=10)
  except Exception as e:
    print(f"خطأ في إرسال الرسالة إلى تيليجرام: {e}")


def git_commit_and_push():
  try:
    subprocess.run(["git", "config", "--global", "user.name", "CryptoBot"])
    subprocess.run([
        "git",
        "config",
        "--global",
        "user.email",
        "bot@users.noreply.github.com",
    ])
    subprocess.run(["git", "add", CACHE_FILE])

    status = subprocess.run(
        ["git", "status", "--porcelain"], capture_output=True, text=True
    )
    if status.stdout.strip():
      subprocess.run([
          "git",
          "commit",
          "-m",
          "Update price cache [skip ci]",
      ])
      push_res = subprocess.run(
          ["git", "push", "origin", "HEAD"], capture_output=True, text=True
      )
      print(f"نتيجة الـ Push: {push_res.stdout} {push_res.stderr}")
    else:
      print("لا توجد تغييرات جديدة في الأسعار لحفظها.")
  except Exception as e:
    print(f"خطأ في الـ Git: {e}")


def fetch_crypto_prices():
  # محاولة أولى من CoinCap مع إمكانية المحاولة 3 مرات
  for attempt in range(3):
    try:
      url = "https://api.coincap.io/v2/assets?limit=100"
      res = requests.get(url, timeout=10)
      if res.status_code == 200:
        data = res.json().get("data", [])
        return {
            coin["symbol"].upper(): float(coin["priceUsd"]) for coin in data
        }
    except Exception as e:
      print(f"محاولة CoinCap رقم {attempt + 1} فشلت: {e}")
      time.sleep(2)

  # بديل مضمون في حال فشل CoinCap (استخدام Binance API)
  print("جاري التحويل إلى المصدر البديل (Binance API)...")
  try:
    url = "https://api.binance.com/api/v3/ticker/price"
    res = requests.get(url, timeout=10)
    if res.status_code == 200:
      data = res.json()
      prices = {}
      for coin in data:
        symbol = coin["symbol"]
        if symbol.endswith("USDT"):
          clean_symbol = symbol.replace("USDT", "")
          prices[clean_symbol] = float(coin["price"])
      return prices
  except Exception as e:
    print(f"فشل الاتصال بالمصدر البديل أيضاً: {e}")

  return {}


def check_price_spikes():
  old_prices = {}
  if os.path.exists(CACHE_FILE):
    try:
      with open(CACHE_FILE, "r") as f:
        old_prices = json.load(f)
      print(f"تم قراءة الأسعار القديمة. عدد العملات: {len(old_prices)}")
    except Exception as e:
      print(f"خطأ في قراءة الكاش: {e}")

  new_prices = fetch_crypto_prices()
  if not new_prices:
    print("لم نتمكن من جلب الأسعار الحالية بسبب انقطاع الخدمة من المصدر.")
    return

  alerts = []
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
              f" الحالي: `${price:,.4f}` (السابق: `${old_price:,.4f}`)"
          )

  # حفظ الأسعار الجديدة في ملف JSON
  with open(CACHE_FILE, "w") as f:
    json.dump(new_prices, f, indent=4)
  print("تم حفظ الأسعار الجديدة في ملف prices_cache.json")

  # رفع الملف إلى المستودع
  git_commit_and_push()

  # إرسال التنبيهات
  if alerts:
    msg = (
        "🚨 **تنبيه حركة الأسعار (بنسبة 0.1% أو أكثر)**\n\n"
        + "\n\n".join(alerts[:15])
    )
    send_telegram_message(msg)
  else:
    print("لا توجد تغيرات تتجاوز 0.1% مقارنة بالفحص السابق.")


if __name__ == "__main__":
  check_price_spikes()
