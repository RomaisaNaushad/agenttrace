import yfinance as yf

tickers = ["META", "NVDA", "MDB"]

for t in tickers:
    print(f"\n--- {t} ---")
    hist = yf.Ticker(t).history(period="3mo")
    print(hist[["Close"]].tail(15))