import ccxt
import pandas as pd

# OKX bağlantısı
exchange = ccxt.okx({'enableRateLimit': True})

TIMEFRAME = '1h'
LIMIT = 10

LOW_PCT = 0.01   # %1
HIGH_PCT = 0.03  # %3

def in_percent_range(price, level, low=0.01, high=0.03):
    diff_pct = abs(price - level) / level
    return low <= diff_pct <= high or diff_pct < low

markets = exchange.load_markets()
symbols = [
    s for s in markets
    if s.endswith('/USDT') and markets[s]['active']
]

results = []

for symbol in symbols:
    try:
        ohlcv = exchange.fetch_ohlcv(
            symbol,
            timeframe=TIMEFRAME,
            limit=LIMIT
        )

        df = pd.DataFrame(
            ohlcv,
            columns=['time','open','high','low','close','volume']
        )

        # Önceki kapanmış mum
        prev = df.iloc[-2]
        last = df.iloc[-1]

        H, L, C = prev['high'], prev['low'], prev['close']

        pivot = (H + L + C) / 3
        s2 = pivot - (H - L)
        s3 = L - 2 * (H - pivot)

        price = last['close']

        if (
            in_percent_range(price, s2, LOW_PCT, HIGH_PCT)
            or in_percent_range(price, s3, LOW_PCT, HIGH_PCT)
        ):
            results.append({
                "Coin": symbol,
                "Close": round(price, 4),
                "S2": round(s2, 4),
                "S3": round(s3, 4)
            })

    except Exception:
        continue

# Sonuçlar
print("📉 1H Pivot S2 / S3 Bölgesindeki Coinler:\n")
for r in results:
    print(
        f"{r['Coin']} | Close: {r['Close']} | "
        f"S2: {r['S2']} | S3: {r['S3']}"
    )
