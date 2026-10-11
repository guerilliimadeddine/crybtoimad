import json
import os
import requests

TELEGRAM_TOKEN = "8748765412:AAG030Thdv4jFUcZ2LUT-Hso56pa2ldtF_s"
CHAT_ID = "1991436401"
CACHE_FILE = "prices_cache.json"
THRESHOLD_PERCENT = 0.1

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
  # استخدام CoinGecko API (مجاني ولا يحظر خوادم غيتهاب غالباً)
  url = (
      "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,binancecoin,solana,ripple,cardano,dogecoin,avalanche-2,tron,chainlink,polkadot,polygon-ecosystem-token,uniswap,litecoin,near,aptos,cosmos,stellar,filecoin,hedera&vs_currencies=usd"
  )
  try:
    res = requests.get(url, headers=HEADERS, timeout=15)
    print(f"CoinGecko Status Code: {res.status_code}")
    if res.status_code == 200:
      data = res.json()
      prices = {}
      # ربط الأسماء برموزها المعروفة
      mapping = {
          "bitcoin": "BTC",
          "ethereum": "ETH",
          "binancecoin": "BNB",
          "solana": "SOL",
          "ripple": "XRP",
          "cardano": "ADA",
          "dogecoin": "DOGE",
          "avalanche-2": "AVAX",
          "tron": "TRX",
          "chainlink": "LINK",
          "polkadot": "DOT",
          "polygon-ecosystem-token": "POL",
          "uniswap": "UNI",
          "litecoin": "LTC",
          "near": "NEAR",
          "aptos": "APT",
          "cosmos": "ATOM",
          "stellar": "XLM",
          "filecoin": "FIL",
          "hedera": "HBAR",
      }
      for key, val in data.items():
        if key in mapping:
          prices[mapping[key]] = float(val["usd"])
      if prices:
        return prices
  except Exception as e:
    print(f"خطأ في الاتصال بـ CoinGecko: {e}")

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
    # كتابة ملف تجريبي لضمان أن الـ Git يعمل ولن يتوقف الملف فارغاً
    new_prices = {"TEST": 1.0}

  print(f"✅ تم جلب بنجاح {len(new_prices)} عملة.")

  alerts = []
  if old_prices:
    for symbol, price in new_prices.items():
      if symbol in old_prices:
        old_price = old_prices[symbol]
        if old_price > 0 and symbol != "TEST":
          change_pct = ((price - old_price) / old_price) * 100
          if abs(change_pct) >= THRESHOLD_PERCENT:
            direction = "🚀 صعود" if change_pct > 0 else "🔻 هبوط"
            emoji = "🟢" if change_pct > 0 else "🔴"
            alerts.append(
                f"{emoji} **{symbol}**: {direction} بنسبة `{change_pct:+.2f}%`\nالسعر"
                f" الحالي: `${price:,.4f}`"
            )

  # حفظ الأسعار الجديدة في الملف ليتغير محتواه ويستطيع الـ Git رفعه
  with open(CACHE_FILE, "w") as f:
    json.dump(new_prices, f, indent=4)
  print(f"تم تحديث وكتابة ملف {CACHE_FILE}")

  if alerts:
    msg = (
        "🚨 **تنبيه حركة الأسعار (بنسبة 0.1% أو أكثر)**\n\n"
        + "\n\n".join(alerts[:15])
    )
    send_telegram_message(msg)


if __name__ == "__main__":
  check_price_spikes()
