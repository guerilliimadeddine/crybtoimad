import json
import os
import requests

# بيانات تيليجرام الخاصة بك
TELEGRAM_TOKEN = "8748765412:AAG030Thdv4jFUcZ2LUT-Hso56pa2ldtF_s"
CHAT_ID = "1991436401"

CACHE_FILE = "prices_cache.json"
THRESHOLD_PERCENT = 1.0  # نسبة التغير المطلوبة للتنبيه (1%)


def send_telegram_message(message):
  url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
  payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
  try:
    requests.post(url, json=payload, timeout=10)
  except Exception as e:
    print(f"خطأ في إرسال الرسالة: {e}")


def check_price_spikes():
  # 1. قراءة الأسعار السابقة من الـ Cache إذا كانت موجودة
  old_prices = {}
  if os.path.exists(CACHE_FILE):
    try:
      with open(CACHE_FILE, "r") as f:
        old_prices = json.load(f)
      print("تم تحميل الأسعار السابقة بنجاح.")
    except Exception as e:
      print(f"فشل قراءة ملف الـ Cache: {e}")

  try:
    # 2. جلب الأسعار الحالية لأعلى 100 عملة من CoinCap
    url = "https://api.coincap.io/v2/assets?limit=100"
    response = requests.get(url, timeout=15)
    if response.status_code != 200:
      print(f"خطأ في الاتصال بالمصدر: {response.status_code}")
      return

    coins = response.json().get("data", [])
    new_prices = {}
    alerts = []

    # 3. مقارنة السعر الجديد بالسعر القديم لكل عملة
    for coin in coins:
      symbol = coin.get("symbol", "").upper()
      name = coin.get("name", "")
      price = float(coin.get("priceUsd", 0))
      new_prices[symbol] = price

      if symbol in old_prices:
        old_price = old_prices[symbol]
        if old_price > 0:
          change_pct = ((price - old_price) / old_price) * 100

          # إذا كانت نسبة التغير 1% أو أكثر (صعوداً أو هبوطاً)
          if abs(change_pct) >= THRESHOLD_PERCENT:
            direction = "🚀 صعود" if change_pct > 0 else "🔻 هبوط"
            emoji = "🟢" if change_pct > 0 else "🔴"
            alerts.append(
                f"{emoji} **{name} ({symbol})**: {direction} بنسبة"
                f" `{change_pct:+.2f}%`\nالسعر الحالي: `${price:,.4f}` (السعر"
                f" السابق: `${old_price:,.4f}`)"
            )

    # 4. حفظ الأسعار الجديدة في ملف الـ Cache للدورة القادمة
    with open(CACHE_FILE, "w") as f:
      json.dump(new_prices, f)
    print("تم تحديث ملف الأسعار للدورة القادمة.")

    # 5. إرسال الإشعار على تيليجرام إذا توفرت تنبيهات
    if alerts:
      msg = (
          "🚨 **تنبيه حركة الأسعار (خلال الدورة الأخيرة)**\n\n"
          + "\n\n".join(alerts)
      )
      send_telegram_message(msg)
      print("تم إرسال التنبيهات بنجاح.")
    else:
      print("لا توجد تغيرات بنسبة 1% أو أكثر في هذه الدورة.")

  except Exception as e:
    print(f"حدث خطأ أثناء تشغيل السكربت: {e}")


if __name__ == "__main__":
  check_price_spikes()
