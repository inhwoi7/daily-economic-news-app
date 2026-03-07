from typing import List, Dict
from datetime import datetime

import news_fetcher
import financial_data_fetcher
import llm_summarizer
import models

def build_daily_email_content(user_id: int, user_email: str, db) -> str:
    """
    Builds the HTML content for the daily economic news email based on user preferences.
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return "<p>User not found.</p>"

    # Fetch preferences
    preferences = db.query(models.Preference).filter(models.Preference.owner_id == user_id).first()
    news_sources = db.query(models.NewsSource).filter(models.NewsSource.owner_id == user_id, models.NewsSource.is_active == True).all()
    stocks = db.query(models.Stock).filter(models.Stock.owner_id == user_id, models.Stock.is_active == True).all()
    currencies = db.query(models.Currency).filter(models.Currency.owner_id == user_id, models.Currency.is_active == True).all()

    email_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ width: 80%; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }}
            h2 {{ color: #0056b3; }}
            h3 {{ color: #0056b3; border-bottom: 1px solid #eee; padding-bottom: 5px; }}
            .news-article {{ margin-bottom: 15px; padding-bottom: 15px; border-bottom: 1px dashed #eee; }}
            .news-article:last-child {{ border-bottom: none; }}
            .stock-info, .currency-info {{ background-color: #f9f9f9; padding: 10px; border-left: 3px solid #0056b3; margin-bottom: 10px; }}
            .disclaimer {{ font-size: 0.8em; color: #777; margin-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Daily Economic News Summary - {datetime.now().strftime('%Y-%m-%d %H:%M')}</h2>
            
            <h3>Global News</h3>
    """
    global_articles_raw = news_fetcher.fetch_global_news(query="economy stock market", page_size=5) # Example query
    global_summaries = llm_summarizer.summarize_news_articles(global_articles_raw)
    
    if global_summaries:
        for article in global_summaries:
            email_content += f"""
            <div class="news-article">
                <strong><a href="{article.get('url', '#')}">{article.get('title', 'N/A')}</a></strong>
                <p>{article.get('summary', 'No summary available.')}</p>
            </div>
            """
    else:
        email_content += "<p>No global news available.</p>"

    email_content += """
            <h3>South Korean News</h3>
    """
    korean_articles_raw = news_fetcher.fetch_korean_news(query="경제 주식", page_size=5) # Example query
    korean_summaries = llm_summarizer.summarize_news_articles(korean_articles_raw)

    if korean_summaries:
        for article in korean_summaries:
            email_content += f"""
            <div class="news-article">
                <strong><a href="{article.get('url', '#')}">{article.get('title', 'N/A')}</a></strong>
                <p>{article.get('summary', 'No summary available.')}</p>
            </div>
            """
    else:
        email_content += "<p>No South Korean news available.</p>"

    # --- Financial Data ---
    email_content += """
            <h3>Market Data</h3>
    """

    if stocks:
        email_content += "<h4>Stocks:</h4>"
        for stock in stocks:
            stock_data = financial_data_fetcher.fetch_stock_quote(stock.symbol)
            if stock_data:
                email_content += f"""
                <div class="stock-info">
                    <strong>{stock_data.get('symbol', 'N/A')}</strong>: ${stock_data.get('price', 'N/A'):.2f} 
                    ({stock_data.get('change', 0):+.2f}, {stock_data.get('change_percent', 'N/A')})
                </div>
                """
            else:
                email_content += f"<p>Could not fetch data for stock: {stock.symbol}</p>"
    else:
        email_content += "<p>No stocks configured.</p>"

    if currencies:
        email_content += "<h4>Exchange Rates:</h4>"
        for currency in currencies:
            # Assuming currency.symbol is like "USD/KRW"
            from_cur, to_cur = currency.symbol.split('/') if '/' in currency.symbol else (None, None)
            if from_cur and to_cur:
                currency_data = financial_data_fetcher.fetch_exchange_rate(from_cur, to_cur)
                if currency_data:
                    email_content += f"""
                    <div class="currency-info">
                        <strong>{currency_data.get('from_currency', 'N/A')}/{currency_data.get('to_currency', 'N/A')}</strong>: {currency_data.get('exchange_rate', 'N/A'):.2f}
                    </div>
                    """
                else:
                    email_content += f"<p>Could not fetch data for currency: {currency.symbol}</p>"
            else:
                email_content += f"<p>Invalid currency symbol: {currency.symbol}</p>"
    else:
        email_content += "<p>No currencies configured.</p>"

    email_content += """
            <div class="disclaimer">
                <p>This email is for informational purposes only and not financial advice.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return email_content
