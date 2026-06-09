import os
import json
import requests
import yfinance as yf
import pandas as pd
from prophet import Prophet
from dotenv import load_dotenv
from supabase import create_client
load_dotenv()

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GROQ_API_KEY   = os.getenv("GROQ_API_KEY")   # free at console.groq.com

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"
GEMINI_MODELS   = ["gemini-2.0-flash", "gemini-2.0-flash-lite"]

GROQ_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "mixtral-8x7b-32768",
]



def _call_gemini(model: str, system_prompt: str, user_prompt: str, max_tokens=300) -> str:
    url = f"{GEMINI_BASE_URL}/{model}:generateContent"
    payload = {
        "system_instruction": {"parts": [{"text": system_prompt}]},
        "contents":           [{"parts": [{"text": user_prompt}]}],
        "generationConfig":   {"maxOutputTokens": max_tokens, "temperature": 0.7},
    }
    resp = requests.post(url, params={"key": GOOGLE_API_KEY}, json=payload, timeout=20)
    resp.raise_for_status()
    return resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()


def _call_groq(model: str, system_prompt: str, user_prompt: str, max_tokens=300) -> str:
    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY not set")
    resp = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt},
            ],
            "max_tokens": max_tokens,
            "temperature": 0.7,
        },
        timeout=20,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()


def _call_wikipedia_summary(company: str) -> str:
    """
    Zero-key fallback: fetch a plain-text Wikipedia summary and
    wrap it in an analyst-style blurb.
    """
    search_resp = requests.get(
        "https://en.wikipedia.org/w/api.php",
        params={"action": "query", "list": "search", "srsearch": company,
                "format": "json", "srlimit": 1},
        timeout=10,
    )
    results = search_resp.json().get("query", {}).get("search", [])
    if not results:
        raise RuntimeError("Wikipedia: no results found")

    title = results[0]["title"]
    summary_resp = requests.get(
        "https://en.wikipedia.org/api/rest_v1/page/summary/" + title.replace(" ", "_"),
        timeout=10,
    )
    summary_resp.raise_for_status()
    extract = summary_resp.json().get("extract", "")
    # Trim to ~3 sentences
    sentences = extract.split(". ")
    short = ". ".join(sentences[:3]).strip()
    if short and not short.endswith("."):
        short += "."
    return f"[Wikipedia] {short} Outlook depends on broader market conditions."


def _call_ai(system_prompt: str, user_prompt: str, company: str = "", max_tokens=300) -> str:
    """
    Provider chain (fastest/free first):
      1. Groq (free tier, very generous limits)
      2. Gemini models
      3. Wikipedia summary (zero-key, always works)
    """
    errors = []

    # 1. Groq — free, ~30 req/min on free tier
    for model in GROQ_MODELS:
        try:
            result = _call_groq(model, system_prompt, user_prompt, max_tokens)
            print(f"[_call_ai] success via Groq/{model}")
            return result
        except Exception as e:
            print(f"[_call_ai] Groq/{model} failed: {e}")
            errors.append(f"Groq/{model}: {e}")

    # 2. Gemini
    for model in GEMINI_MODELS:
        try:
            result = _call_gemini(model, system_prompt, user_prompt, max_tokens)
            print(f"[_call_ai] success via Gemini/{model}")
            return result
        except Exception as e:
            print(f"[_call_ai] Gemini/{model} failed: {e}")
            errors.append(f"Gemini/{model}: {e}")

    # 3. Wikipedia — zero keys, always available
    try:
        result = _call_wikipedia_summary(company or user_prompt)
        print("[_call_ai] success via Wikipedia fallback")
        return result
    except Exception as e:
        errors.append(f"Wikipedia: {e}")

    raise RuntimeError("All providers failed:\n" + "\n".join(errors))


# ====================== TICKER ======================

def get_global_ticker(query: str):
    q = str(query).strip().upper()
    brand_map = {
        "AIRTEL": "BHARTIARTL.NS", "RELIANCE": "RELIANCE.NS", "HDFC": "HDFCBANK.NS",
        "SBI": "SBIN.NS", "ICICI": "ICICIBANK.NS", "TCS": "TCS.NS", "INFOSYS": "INFY.NS",
        "NARAYANA": "NH.NS", "SAMSUNG": "005930.KS", "GOOGLE": "GOOG", "META": "META",
    }
    if q in brand_map:
        return brand_map[q]
    for name, ticker in brand_map.items():
        if name in q:
            return ticker
    try:
        results = yf.Search(query, max_results=1).quotes
        if results:
            return results[0]['symbol']
    except Exception:
        pass
    return q


def get_stock_data(query: str):
    ticker = get_global_ticker(query)
    currency = "₹" if ".NS" in ticker else "$"
    country  = "India" if ".NS" in ticker else "Global"

    df, stock = pd.DataFrame(), None
    try:
        stock = yf.Ticker(ticker)
        raw = stock.history(period="1y", auto_adjust=True)
        if not raw.empty:
            df = raw.reset_index()
            df.columns = [str(c).split(" ")[0].capitalize() for c in df.columns]
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None)
    except Exception as e:
        print(f"[get_stock_data] history error: {e}")

    current_price = float(df['Close'].iloc[-1]) if not df.empty and 'Close' in df.columns else 0.0

    forecast = None
    try:
        if len(df) > 60 and 'Close' in df.columns:
            df_t = df[['Date', 'Close']].rename(columns={'Date': 'ds', 'Close': 'y'})
            m = Prophet(daily_seasonality=False, yearly_seasonality=True, weekly_seasonality=True)
            m.fit(df_t)
            full = m.predict(m.make_future_dataframe(periods=30))
            last_date = df_t['ds'].max()
            forecast = full[full['ds'] > last_date][['ds', 'yhat', 'yhat_lower', 'yhat_upper']].copy()
            forecast['ds'] = pd.to_datetime(forecast['ds']).dt.date
    except Exception as e:
        print(f"[get_stock_data] forecast error: {e}")

    news = []
    try:
        if stock and hasattr(stock, 'news') and stock.news:
            for item in stock.news[:6]:
                content   = item.get('content', item)
                title     = content.get('title', item.get('title', ''))
                publisher = content.get('provider', {}).get('displayName', '') or item.get('publisher', 'Unknown')
                link      = content.get('canonicalUrl', {}).get('url', '') or item.get('link', '')
                news.append({'title': title, 'publisher': publisher, 'link': link})
    except Exception as e:
        print(f"[get_stock_data] news error: {e}")

    return current_price, df, forecast, currency, country, news


def get_technical_indicators(df: pd.DataFrame):
    if df.empty or 'Close' not in df.columns or len(df) < 20:
        return {"rsi": "N/A", "sma_50": "N/A", "sma_200": "N/A", "recommendation": "Neutral"}
    try:
        close = df['Close']
        delta = close.diff()
        gain  = delta.where(delta > 0, 0).rolling(14).mean()
        loss  = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rsi   = round(float((100 - (100 / (1 + gain / (loss + 1e-9)))).iloc[-1]), 2)
        sma_50  = round(float(close.rolling(50).mean().iloc[-1]),  2) if len(close) >= 50  else "N/A"
        sma_200 = round(float(close.rolling(200).mean().iloc[-1]), 2) if len(close) >= 200 else "N/A"
        rec = "Bullish" if rsi < 40 else "Bearish" if rsi > 70 else "Neutral"
        return {"rsi": rsi, "sma_50": sma_50, "sma_200": sma_200, "recommendation": rec}
    except Exception as e:
        print(f"[get_technical_indicators] error: {e}")
        return {"rsi": "N/A", "sma_50": "N/A", "sma_200": "N/A", "recommendation": "Neutral"}


def get_market_intelligence(ticker_or_name: str) -> dict:
    try:
        summary = _call_ai(
            system_prompt="You are a Senior VC Analyst. Be concise.",
            user_prompt=(
                f"Give a 3-sentence market outlook for {ticker_or_name}. "
                "End with exactly one word: Bullish, Bearish, or Neutral."
            ),
            company=ticker_or_name,
        )
        words = summary.strip().split()
        sentiment = "Neutral"
        for candidate in ["Bullish", "Bearish", "Neutral"]:
            if words and words[-1].strip(".,") == candidate:
                sentiment = candidate
                summary   = " ".join(words[:-1]).strip()
                break
        return {"summary": summary, "sentiment": sentiment}
    except Exception as e:
        print(f"[get_market_intelligence] error: {e}")
        return {"summary": f"Market intelligence unavailable. ({e})", "sentiment": "Neutral"}
