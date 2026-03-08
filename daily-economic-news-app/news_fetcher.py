import os
import requests
from typing import List, Dict

NEWS_API_KEY = os.getenv("NEWS_API_KEY", "YOUR_NEWS_API_KEY") 

def fetch_global_news(query: str = "economy stock market", language: str = "en", page_size: int = 10) -> List[Dict]:
    """Fetches global news articles using NewsAPI.org."""
    if NEWS_API_KEY == "YOUR_NEWS_API_KEY":
        print("Warning: NEWS_API_KEY is not set. Using dummy data for global news.")
        return [
            {"title": "Dummy Global News 1", "description": "This is a dummy global news article about the economy.", "url": "http://example.com/global1"},
            {"title": "Dummy Global News 2", "description": "Another dummy global news article on the stock market.", "url": "http://example.com/global2"},
        ]
    
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "language": language,
        "pageSize": page_size,
        "apiKey": NEWS_API_KEY,
        "sortBy": "publishedAt"
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status() # Raise an exception for HTTP errors
        articles = response.json().get("articles", [])
        return [{"title": a.get("title"), "description": a.get("description"), "url": a.get("url")} for a in articles]
    except requests.exceptions.RequestException as e:
        print(f"Error fetching global news: {e}")
        return []

def fetch_korean_news(query: str = "경제 주식", page_size: int = 10) -> List[Dict]:
    """
    Placeholder function for fetching South Korean news.
    """
    print("Warning: Using dummy data for Korean news.")
    return [
        {"title": "더미 한국 뉴스 1", "description": "한국 경제 관련 더미 뉴스입니다.", "url": "http://example.com/korean1"},
        {"title": "더미 한국 뉴스 2", "description": "한국 주식 시장 관련 더미 뉴스입니다.", "url": "http://example.com/korean2"},
    ]

if __name__ == "__main__":
    print("Fetching global news...")
    global_articles = fetch_global_news()
    for article in global_articles:
        print(f"Title: {article['title']}")
        print(f"Description: {article['description']}")
        print(f"URL: {article['url']}")
        print("---")

    print("\nFetching Korean news (dummy data)...")
    korean_articles = fetch_korean_news()
    for article in korean_articles:
        print(f"Title: {article['title']}")
        print(f"Description: {article['description']}")
        print(f"URL: {article['url']}")
        print("---")
