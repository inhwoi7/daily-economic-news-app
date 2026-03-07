import os
import google.generativeai as genai
from typing import List, Dict

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY")

if GEMINI_API_KEY != "YOUR_GEMINI_API_KEY":
    genai.configure(api_key=GEMINI_API_KEY)
    _model = genai.GenerativeModel('gemini-pro')
else:
    print("Warning: GEMINI_API_KEY is not set. LLM summarization will use dummy data.")
    _model = None

def summarize_news_articles(articles: List[Dict]) -> List[Dict]:
    """Summarizes a list of news articles using the Gemini API."""
    if not _model:
        return [
            {"title": article.get("title"), "summary": f"Dummy summary for: {article.get('title')}", "url": article.get('url')}
            for article in articles
        ]

    summarized_articles = []
    for article in articles:
        title = article.get("title", "")
        description = article.get("description", "")
        url = article.get("url", "")
        
        prompt = f"""
Please summarize the following news article, focusing on its economic and social impact, especially concerning the stock market.
Provide a concise summary, ideally 2-3 sentences.

Title: {title}
Description: {description}
URL: {url}

Summary:
"""
        try:
            response = _model.generate_content(prompt)
            summary = response.text
            summarized_articles.append({"title": title, "summary": summary, "url": url})
        except Exception as e:
            print(f"Error summarizing article '{title}': {e}")
            summarized_articles.append({"title": title, "summary": description, "url": url}) # Fallback to description
    return summarized_articles

if __name__ == "__main__":
    dummy_articles = [
        {"title": "Global Markets Rise on Strong Earnings", "description": "Major stock indices worldwide saw gains today following better-than-expected corporate earnings reports from technology giants.", "url": "http://example.com/global-earnings"},
        {"title": "한국 경제, 반도체 수출 호조로 회복세", "description": "대한민국 경제가 반도체 수출 증가에 힘입어 회복세를 보이고 있으며, 이는 주식 시장에도 긍정적인 영향을 미칠 것으로 예상됩니다.", "url": "http://example.com/korean-economy"},
        {"title": "Oil Prices Surge Amid Geopolitical Tensions", "description": "Crude oil prices jumped significantly as new geopolitical tensions in the Middle East raised concerns about supply disruptions.", "url": "http://example.com/oil-prices"},
    ]
    
    print("Summarizing dummy articles...")
    summaries = summarize_news_articles(dummy_articles)
    for s in summaries:
        print(f"Title: {s['title']}
Summary: {s['summary']}
URL: {s['url']}
---")
