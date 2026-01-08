import streamlit as st
import ccxt
import pandas as pd

st.set_page_config(page_title="OKX Pivot S2 / S3 Scanner", layout="wide")
st.title("📉 OKX Pivot S2 / S3 Tarayıcı (TradingView Uyumlu)")
st.caption("Classic Pivot – 1 Saatlik Grafik")

TIMEFRAME = "1h"
LIMIT = 10

LOW_PCT = st.slider("Alt tolerans (%)", 1.0, 3.0, 1.0) / 100
HIGH_PCT = st.slider("Üst tolerans (%)", 1.0, 5.0, 3.0) / 100

@st.cache_data(ttl=300)
def get_symbols():
    exchange = ccxt.okx({'enableRateLimit': True})
    markets = exchange.load_markets()
    return [s for s in markets if s.endswith('/USDT') and markets[s]['active']]

def calculate_classic_pivots(H, L, C):
    P = (H + L + C) / 3
    S2 = P - (H - L)
    S3 = L - 2 * (H - P)
    return S2, S3

def in_range(price, level, low, high):
    diff = abs(price - level) / level
    return diff <= high

def scan():
    exchange = ccxt.okx({'enableRateLimit': True})
    rows = []

    for symbol in get_symbols():
        try:
            ohlcv = exchange.fetch_ohlcv(symbol, TIMEFRAME, limit=LIMIT)
            df = pd.DataFrame(ohlcv, columns=['t','o','h','l','c','v'])

            prev = df.iloc[-2]   # Pivot hesabı
            last = df.iloc[-1]   # Fiyat kontrolü

            S2, S3 = calculate_classic_pivots(
                prev['h'], prev['l'], prev['c']
            )

            price = last['c']

            if in_range(price, S2, LOW_PCT, HIGH_PCT) or in_range(price, S3, LOW_PCT, HIGH_PCT):
                rows.append({
                    "Coin": symbol,
                    "Close": round(price, 4),
                    "S2": round(S2, 4),
                    "S3": round(S3, 4),
                    "Mesafe %": round(min(
                        abs(price - S2) / S2,
                        abs(price - S3) / S3
                    ) * 100, 2)
                })

        except:
            continue

    return pd.DataFrame(rows)

# 🔘 BUTON
if st.button("🚀 Taramayı Başlat"):
    with st.spinner("OKX taranıyor..."):
        result = scan()

    if result.empty:
        st.warning("Uygun coin bulunamadı.")
    else:
        st.success(f"{len(result)} coin bulundu")
        st.dataframe(
            result.sort_values("Mesafe %"),
            use_container_width=True
        )

st.caption("⚠️ TradingView Classic Pivot ile birebir uyumludur.")
