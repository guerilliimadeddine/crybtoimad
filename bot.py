import json
import os
import subprocess
import requests

TELEGRAM_TOKEN = "8748765412:AA6030Thdv4jFUcZ2LUT-Hso56pa2lDtF_s"
CHAT_ID = "1991436401"
CACHE_FILE = "prices_cache.json"
THRESHOLD_PERCENT = 0.1  # تم تعديل النسبة لتصبح 0.1%


def send_telegram_message(message):
  url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
  payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
  try:
    requests.post(url, json=payload, timeout=10)
  except Exception as e:
    print(f"خطأ في إرسال الرسالة: {e}")


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
    subprocess.run(["git", "commit", "-m", "Update price cache [skip ci]"])
    subprocess.run(["git", "push"])
    print("تم تحديث وحفظ الملف في المستودع بنجاح.")
  except Exception as e:
    print(f"خطأ أثناء تحديث الـ Git: {e}")


def check_price_spikes():
  old_prices = {}
  if os.path.exists(CACHE_FILE):
    try:
      with open(CACHE_FILE, "r") as f:
        old_prices = json.load(f)
    except Exception:
      old_prices = {}

  try:
    url = "https://api.coincap.io/v2/assets?limit=100"
    response = requests.get(url, timeout=15)
    if response.status_code != 200:
      return

    coins = response.json().get("data", [])
    new_prices = {}
    alerts = []

    for coin in coins:
      symbol = coin.get("symbol", "").upper()
      name = coin.get("name", "")
      price = float(coin.get("priceUsd", 0))
      new_prices[symbol] = price

      if symbol in old_prices:
        old_price = old_prices[symbol]
        if old_price > 0:
          change_pct = ((price - old_price) / old_price) * 100
          # التحقق مما إذا تجاوز التغير النسبة الجديدة 0.1%
          if abs(change_pct) >= THRESHOLD_PERCENT:
            direction = "🚀 صعود" if change_pct > 0 else "🔻 هبوط"
            emoji = "🟢" if change_pct > 0 else "🔴"
            alerts.append(
                f"{emoji} **{name} ({symbol})**: {direction} بنسبة"
                f" `{change_pct:+.2f}%`\nالسعر الحالي: `${price:,.4f}`"
            )

    # حفظ الأسعار الجديدة محلياً
    with open(CACHE_FILE, "w") as f:
      json.dump(new_prices, f, indent=4)

    # رفع الملف المحدث تلقائياً إلى المستودع
    git_commit_and_push()

    if alerts:
      msg = (
          "🚨 **تنبيه حركة الأسعار (بنسبة 0.1% أو أكثر)**\n\n"
          + "\n\n".join(alerts)
      )
      send_telegram_message(msg)

  except Exception as e:
    print(f"حدث خطأ: {e}")


if __name__ == "__main__":
  check_price_spikes()
