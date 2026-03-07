# Daily Economic News App

This application is a personalized daily economic news summary service. It allows users to register, log in, set preferences for news sources, stocks, and currencies, and receive daily email summaries.

## Features

*   **User Authentication:** Register and log in with username, password, and email.
*   **Customizable Preferences:** Manage desired news sources, stocks, currencies, and email delivery time via a web interface.
*   **Automated Email Delivery:** Receive daily email summaries of economic news and market data at a specified time.
*   **News Summarization:** Utilizes the Gemini API for concise news summarization.
*   **Financial Data Integration:** Fetches real-time stock quotes and exchange rates from Alpha Vantage.

## Project Structure

```
daily-economic-news-app/
├── main.py                 # FastAPI application with API endpoints and scheduler
├── auth.py                 # Authentication utilities (password hashing, JWT)
├── database.py             # SQLAlchemy setup for SQLite database
├── models.py               # SQLAlchemy models for User, Preference, NewsSource, Stock, Currency
├── news_fetcher.py         # Functions to fetch news from NewsAPI.org and placeholder for Korean news
├── financial_data_fetcher.py # Functions to fetch financial data from Alpha Vantage
├── llm_summarizer.py       # Functions to summarize news using Gemini API
├── email_builder.py        # Logic to build HTML email content
├── send_email.py           # Functions to send emails using Gmail API
├── venv/                   # Python virtual environment
└── static/
    ├── index.html          # Frontend HTML for login, registration, and dashboard
    ├── style.css           # Frontend styling
    └── app.js              # Frontend JavaScript logic
```

## Setup and Running the Application

Follow these steps to set up and run the Daily Economic News App:

### 1. Navigate to the Project Directory

Open your terminal and change to the `daily-economic-news-app` directory:

```bash
cd daily-economic-news-app
```

### 2. Activate Virtual Environment

Activate the Python virtual environment to ensure all dependencies are used:

```bash
source venv/bin/activate
```

### 3. Set Environment Variables for API Keys

The application requires several API keys for various services. Set these as environment variables. You can either `export` them in your terminal session (they will be active until you close the terminal) or add them to a `.env` file and use a library like `python-dotenv` (not included in this project) to load them automatically.

*   **`SECRET_KEY` (for JWT in `auth.py`):**
    This is a secure key used for signing JWT tokens. Generate a strong random key and set it.
    ```bash
    export SECRET_KEY=$(python -c 'import os; print(os.urandom(24).hex())')
    ```
    *(Note: The `auth.py` file has been updated to use `os.getenv("SECRET_KEY", "your-super-secret-key")`. Make sure to replace `"your-super-secret-key"` with your actual generated key or ensure the environment variable is set.)*

*   **`NEWS_API_KEY` (for NewsAPI.org in `news_fetcher.py`):**
    1.  Register at [NewsAPI.org](https://newsapi.org/) to get your API key.
    2.  Set the environment variable:
        ```bash
        export NEWS_API_KEY="YOUR_NEWS_API_KEY"
        ```

*   **`ALPHA_VANTAGE_API_KEY` (for Alpha Vantage in `financial_data_fetcher.py`):**
    1.  Register at [Alpha Vantage](https://www.alphavantage.co/) to get your API key.
    2.  Set the environment variable:
        ```bash
        export ALPHA_VANTAGE_API_KEY="YOUR_ALPHA_VANTAGE_API_KEY"
        ```

*   **`GEMINI_API_KEY` (for Gemini API in `llm_summarizer.py`):**
    1.  Obtain your Gemini API key from [Google AI Studio](https://aistudio.google.com/).
    2.  Set the environment variable:
        ```bash
        export GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
        ```

### 4. Configure Gmail API (`credentials.json`)

To enable the application to send emails via Gmail:

1.  **Go to Google Cloud Console:** [console.cloud.google.com](https://console.cloud.google.com/)
2.  **Create or Select a Project.**
3.  **Enable Gmail API:** Navigate to "APIs & Services" > "Library", search for "Gmail API", and enable it.
4.  **Configure OAuth Consent Screen:** Go to "APIs & Services" > "OAuth consent screen".
    *   Choose "External" user type.
    *   Fill in required app information (app name, user support email, developer contact information).
5.  **Create Credentials:** Go to "APIs & Services" > "Credentials".
    *   Click "CREATE CREDENTIALS" > "OAuth client ID".
    *   Select "Desktop app" as the Application type and give it a name.
    *   Click "DOWNLOAD JSON" to download your `credentials.json` file.
    *   **Place this `credentials.json` file directly inside your `daily-economic-news-app` directory.**
6.  **First Run Authorization:** The first time the application attempts to send an email, a browser window will open, prompting you to log in with your Google account and grant the app permission to send emails. After authorization, a `token.json` file will be automatically created in the `daily-economic-news-app` directory, storing your credentials for future use.

### 5. Run the FastAPI Backend

With all API keys and `credentials.json` in place, run the FastAPI application:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```
The server will run in the foreground. You will see logs in your terminal. You can stop it by pressing `CTRL+C`.

### 6. Access the Web Interface

Once the backend is running, open your web browser and navigate to:

```
http://127.0.0.1:8000/
```

You can now:
*   **Register** a new user with a valid email address.
*   **Log in** with your new credentials.
*   **Manage your preferences** on the dashboard, including:
    *   Setting your preferred daily email time.
    *   Adding and removing stocks to track (e.g., `AAPL`, `005930.KS` for Samsung Electronics).
    *   Adding and removing currency pairs to track (e.g., `USD/KRW`, `EUR/USD`).
*   **Manually trigger** an email by clicking "Send Daily Email Now" to test the email delivery immediately. Check the registered email inbox for the summary.

## Verification of Application Functionality

To confirm the application is fully functional:

1.  **Backend Startup:** Ensure the `uvicorn` server starts without critical errors and displays `INFO: Uvicorn running on http://0.0.0.0:8000`.
2.  **User Registration & Login:** Successfully register a new user and then log in using the web interface.
3.  **Preference Management:**
    *   Set an email time and save it.
    *   Add at least one stock and one currency. Ensure they appear in the lists.
    *   (Optional) Remove an item and confirm it disappears.
4.  **Manual Email Test:**
    *   Click the "Send Daily Email Now" button.
    *   Observe the `uvicorn` terminal for logs indicating email sending attempts.
    *   **Crucially, check the email inbox of the user you registered.** A summary email containing news, stock, and currency information should arrive. If not, check the terminal logs for errors related to Gmail API or data fetching.
5.  **Scheduled Email Check (Background):**
    *   Keep the `uvicorn` server running.
    *   In the terminal logs, you should see messages like `Running scheduled email task for X users.` approximately every minute.
    *   At the minute mark matching the email time you set in your preferences (e.g., if you set 08:10, and the current time hits HH:10), you should see logs indicating an email is being sent to your registered email address.

By successfully completing these steps, you can confirm that your personalized daily economic news app is fully operational.
