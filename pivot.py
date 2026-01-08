import streamlit as st
import ccxt
import pandas as pd

st.set_page_config(
    page_title="OKX Pivot S2 / S3 Scanner",
    layout="wide"
)

st.title("📉 OKX Pivot S2 / S3 Tarayıcı (1 Saatlik)")
st.caption("Standart Pivot noktalarına göre destek bölgesi filtreleme")

TIMEFRAME = "1h"
LIMIT = 10

LOW_PCT = st.slider("Alt tolerans (%)", 0.5, 3.0, 1.0) / 100
HIGH_PCT = st.slider("Üst tolerans (%)", 1.0, 5.0, 3.0) / 100

@st.cache_data(ttl=300)
def get_symbols():
    exchange = ccxt.okx({'enableRateLimit': True})
    markets = exchange.load_markets()
    return [
        s for s in markets
        if s.endswith('/USDT') and markets[s]['active']
    ]

def in_percent_range(price, level, low, high):
    diff = abs(price - level) / level
    return diff <= high

def scan():
    exchange = ccxt.okx({'enableRateLimit': True})
    rows = []

    for symbol in get_symbols():
        try:
            ohlcv = exchange.fetch_ohlcv(symbol, TIMEFRAME, limit=LIMIT)
            df = pd.DataFrame(
                ohlcv,
                columns=['time','open','high','low','close','volume']
            )

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
                rows.append({
                    "Coin": symbol,
                    "Close": round(price, 4),
                    "S2": round(s2, 4),
                    "S3": round(s3, 4),
                    "Mesafe %": round(abs(price - min(s2, s3)) / price * 100, 2)
                })

        except:
            continue

    return pd.DataFrame(rows)

# 🔘 TARAYI BAŞLAT BUTONU
if st.button("🚀 Taramayı Başlat"):
    with st.spinner("OKX verileri taranıyor..."):
        result = scan()

    if result.empty:
        st.warning("Uygun coin bulunamadı.")
    else:
        st.success(f"{len(result)} coin bulundu")
        st.dataframe(
            result.sort_values("Mesafe %"),
            use_container_width=True
        )

st.markdown("---")
st.caption("⚠️ Yatırım tavsiyesi değildir.")
