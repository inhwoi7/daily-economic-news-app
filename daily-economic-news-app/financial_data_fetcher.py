import os
import requests
import yfinance as yf
from typing import Dict, Optional

# Alpha Vantage API Key (Get a free one at https://www.alphavantage.co/support/#api-key)
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "YOUR_ALPHA_VANTAGE_API_KEY")

def fetch_stock_quote(symbol: str) -> Optional[Dict]:
    """Fetches a current stock quote for a given ticker symbol using yfinance."""
    try:
        ticker = yf.Ticker(symbol)
        # Fetching 2 days to calculate change from previous close
        hist = ticker.history(period="2d")
        if not hist.empty:
            info = hist.iloc[-1]
            prev_close = hist.iloc[-2]["Close"] if len(hist) > 1 else info["Open"]
            change = info["Close"] - prev_close
            change_percent = (change / prev_close) * 100 if prev_close != 0 else 0
            return {
                "symbol": symbol,
                "price": float(info["Close"]),
                "change": float(change),
                "change_percent": f"{change_percent:.2f}%",
                "currency": "USD" 
            }
        else:
            print(f"No price data found for {symbol} with yfinance.")
            return None
    except Exception as e:
        print(f"Error fetching stock quote for {symbol} with yfinance: {e}")
        return None

def fetch_exchange_rate(from_currency: str = "USD", to_currency: str = "KRW") -> Optional[Dict]:
    """Fetches the current exchange rate between two currencies using Alpha Vantage."""
    if ALPHA_VANTAGE_API_KEY == "YOUR_ALPHA_VANTAGE_API_KEY":
        print("Warning: ALPHA_VANTAGE_API_KEY is not set. Using dummy data for exchange rate.")
        return {
            "from_currency": from_currency,
            "to_currency": to_currency,
            "exchange_rate": 1350.0, # Dummy rate
            "timestamp": "2024-05-20 00:00:00"
        }

    url = "https://www.alphavantage.co/query"
    params = {
        "function": "CURRENCY_EXCHANGE_RATE",
        "from_currency": from_currency,
        "to_currency": to_currency,
        "apikey": ALPHA_VANTAGE_API_KEY
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        rate_data = data.get("Realtime Currency Exchange Rate")
        if rate_data:
            return {
                "from_currency": rate_data.get("1. From_Currency Code"),
                "to_currency": rate_data.get("3. To_Currency Code"),
                "exchange_rate": float(rate_data.get("5. Exchange Rate")),
                "timestamp": rate_data.get("6. Last Refreshed")
            }
        else:
            print(f"Error fetching exchange rate for {from_currency}/{to_currency}: {data.get('Note', 'Unknown error')}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching exchange rate for {from_currency}/{to_currency}: {e}")
        return None

if __name__ == "__main__":
    print("Fetching stock quote for AAPL...")
    aapl_quote = fetch_stock_quote("AAPL")
    if aapl_quote:
        print(aapl_quote)

    print("\nFetching exchange rate for USD/KRW...")
    usd_krw_rate = fetch_exchange_rate("USD", "KRW")
    if usd_krw_rate:
        print(usd_krw_rate)
