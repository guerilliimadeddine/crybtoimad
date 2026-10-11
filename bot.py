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
  # قائمة موسعة تضم 200 عملة رقمية
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
      "USDC",
      "USDT",
      "DAI",
      "FDUSD",
      "TUSD",
      "PYUSD",
      "JUP",
      "PYTH",
      "W",
      "JTO",
      "MANTA",
      "ALT",
      "PIXEL",
      "PORTAL",
      "XAI",
      "ACE",
      "NFP",
      "AI",
      "XEM",
      "LSK",
      "ARDR",
      "STRAT",
      "BTS",
      "PIVX",
      "ZEN",
      "XVG",
      "SYS",
      "FUN",
      "STORJ",
      "GNT",
      "ANT",
      "RLC",
      "CVC",
      "LOOM",
      "SNT",
      "POWR",
      "MAN",
      "DNT",
      "REQ",
      "RDN",
      "XRP",
      "POLY",
      "GTO",
      "OST",
      "CDT",
      "OCN",
      "BNT",
      "QSP",
      "XZC",
      "DATA",
      "STORM",
      "MFT",
      "ADD",
      "VTHO",
      "GO",
      "TNB",
      "NAV",
      "EDO",
      "CLN",
      "WPR",
      "VIB",
      "PIVX",
      "IOST",
      "BLZ",
      "SYS",
      "HOT",
      "QLC",
      "NPXS",
      "KEY",
      "DOCK",
      "MITH",
      "MCO",
      "STPT",
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
        if price > 0:
          prices[sym] = price
    except Exception:
      pass

  if prices:
    print(f"✅ تم بنجاح جلب {len(prices)} عملة من Coinbase.")
    return prices

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
