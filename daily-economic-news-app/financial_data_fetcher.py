import os
import requests
from typing import Dict, Optional

ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "YOUR_ALPHA_VANTAGE_API_KEY")

def fetch_stock_quote(symbol: str) -> Optional[Dict]:
    """Fetches the latest stock quote for a given symbol using Alpha Vantage."""
    if ALPHA_VANTAGE_API_KEY == "YOUR_ALPHA_VANTAGE_API_KEY":
        print(f"Warning: ALPHA_VANTAGE_API_KEY is not set. Using dummy data for stock: {symbol}.")
        return {
            "symbol": symbol,
            "price": 100.00,
            "change": 1.50,
            "change_percent": "1.52%",
            "timestamp": "2026-03-07 10:00:00"
        }

    url = "https://www.alphavantage.co/query"
    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": symbol,
        "apikey": ALPHA_VANTAGE_API_KEY
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        if "Global Quote" in data:
            quote = data["Global Quote"]
            return {
                "symbol": quote.get("01. symbol"),
                "price": float(quote.get("05. price")),
                "change": float(quote.get("09. change")),
                "change_percent": quote.get("10. change percent"),
                "timestamp": quote.get("07. latest trading day") # This is not exact timestamp, but latest trading day
            }
        else:
            print(f"Error fetching stock quote for {symbol}: {data.get('Note', 'Unknown error')}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching stock quote for {symbol}: {e}")
        return None

def fetch_exchange_rate(from_currency: str, to_currency: str) -> Optional[Dict]:
    """Fetches the exchange rate between two currencies using Alpha Vantage."""
    if ALPHA_VANTAGE_API_KEY == "YOUR_ALPHA_VANTAGE_API_KEY":
        print(f"Warning: ALPHA_VANTAGE_API_KEY is not set. Using dummy data for exchange rate: {from_currency}/{to_currency}.")
        return {
            "from_currency": from_currency,
            "to_currency": to_currency,
            "exchange_rate": 1.10 if from_currency == "USD" and to_currency == "EUR" else 1300.00,
            "timestamp": "2026-03-07 10:00:00"
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
        if "Realtime Currency Exchange Rate" in data:
            rate_data = data["Realtime Currency Exchange Rate"]
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

    print("
Fetching exchange rate for USD/KRW...")
    usd_krw_rate = fetch_exchange_rate("USD", "KRW")
    if usd_krw_rate:
        print(usd_krw_rate)
