import os
import requests
from typing import List, Dict, Optional

# Placeholder for LLM service (e.g., Gemini, GPT-4, or a local model)
# For this example, we'll use a placeholder logic that simulates summarization.
# In a real app, you'd call an API like Google Gemini or OpenAI.

def summarize_news(articles: List[Dict]) -> str:
    """
    Simulates summarizing a list of news articles using an LLM.
    In production, this would call an actual LLM API.
    """
    if not articles:
        return "No news articles found to summarize."

    summary_prompt = "Summarize the following economic news articles:\n"
    for article in articles:
        summary_prompt += f"- {article.get('title')}: {article.get('description')}\n"

    # Simulate an LLM response
    simulated_summary = f"Daily Economic Summary based on {len(articles)} articles:\n"
    simulated_summary += "The markets are showing mixed signals today. Major indices are responding to recent economic data releases. "
    simulated_summary += "Key takeaways include a focus on inflation trends and central bank policy expectations."
    
    return simulated_summary

def summarize_news_articles(articles: List[Dict]) -> List[Dict]:
    """
    Summarizes each article individually. In a real app, this could also be done
    in bulk to save tokens.
    """
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY")
    
    summarized_articles = []
    for article in articles:
        # For simplicity, we'll just add a 'summary' field.
        # In a real app, you'd call Gemini/OpenAI here.
        article_with_summary = article.copy()
        if GEMINI_API_KEY == "YOUR_GEMINI_API_KEY":
            article_with_summary['summary'] = (article.get('description') or "No description available.")[:200] + "..."
        else:
            # Here you could call get_gemini_summary for each or once for all
            article_with_summary['summary'] = get_gemini_summary([article], GEMINI_API_KEY)
        summarized_articles.append(article_with_summary)
    
    return summarized_articles

def get_gemini_summary(articles: List[Dict], api_key: str) -> Optional[str]:
    """
    Example of how you might actually call the Gemini API for summarization.
    """
    if not api_key or api_key == "YOUR_GEMINI_API_KEY":
        return summarize_news(articles) # Fallback to simulated summary

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
    
    prompt_text = "Summarize these news articles concisely for an economic briefing:\n"
    for a in articles:
        prompt_text += f"Title: {a.get('title')}\nDescription: {a.get('description')}\n\n"

    payload = {
        "contents": [{
            "parts": [{"text": prompt_text}]
        }]
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        result = response.json()
        return result['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return summarize_news(articles) # Fallback

if __name__ == "__main__":
    test_articles = [
        {"title": "Fed keeps rates steady", "description": "The Federal Reserve announced it will maintain current interest rates."},
        {"title": "Tech stocks rally", "description": "Major technology companies saw significant gains in today's trading session."}
    ]
    print("Generating summary...")
    summary = summarize_news(test_articles)
    print(summary)
