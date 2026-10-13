from datetime import datetime
from  langchain_core.tools import tool
from app.db import SessionLocal
from app.models import Company, StockPrice

import os
from dotenv import load_dotenv
from exa_py import Exa

load_dotenv()

@tool
def list_companies() -> list:
    """List all companies available in the database.
    Returns each company's ticker, name and sector.
    Call this first to find out which tickers exist."""
    db = SessionLocal()
    try:
        companies = db.query(Company).all()
        return [
            {"ticker": c.ticker, "name": c.name, "sector": c.sector}
            for c in companies
        ]
    finally:
        db.close()

@tool
def get_stock_prices(ticker: str, start_date: str, end_date: str) -> dict:
    """ Get daily closing prices and volume for one company.
    ticker: stock symbol such as MDB, META, NVDA.
    start_date and end_date: dates in YYYY-MM-DD format, inclusive.
    Use list_companies first if you are unsure of the ticker."""
    #check dates before touching the database

    try:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        return {"error": "Dates must be in YYYY-MM-DD format."}

    db = SessionLocal()
    try:
        company=(
            db.query(Company)
            .filter(Company.ticker == ticker.upper())
            .first()
        )
        if company is None:
            return{"error": f"Ticker '{ticker}' not found. Use list_companies to see valid tickers."}
        rows = (
            db.query(StockPrice)
            .filter(
                StockPrice.company_id == company.id,
                StockPrice.date >= start,
                StockPrice.date <= end,
            )
            .order_by(StockPrice.date)
            .all()
        )
        if not rows:
            return {"error": f"No price date for {company.ticker} between {start_date} and {end_date}."}

        return {
            "ticker": company.ticker,
            "prices": [
                {
                    "date": r.date.isoformat(),
                    "close_price": float(r.close_price),
                    "volume": r.volume,
                }
                for r in rows
            ],
        }
    finally:
        db.close()

@tool
def calculator(operation: str, a: float, b: float) -> dict:
    """Do  basic math accurately. Always use this instead of calculating yourself.
    operation: one of add, subtract, multiply, divide, percent_change.
    For percent_change, a is the OLD value and b is the NEW value.
    The result is (b-a)/a*100, so a drop gives a negative number."""
    operation  = operation.lower().strip()

    if operation == "add":
        result = a+b
    elif operation == "subtract":
        result= a - b
    elif operation == "multiply":
        result = a * b
    elif operation == "divide":
        if b == 0:
            return {"error": "Cannot divide by zero."}
        result = a / b
    elif operation == "percent_change":
        if a == 0:
            return{"error":"Cannot calculate percent change from an old value of 0."}
        result = (b-a)/a*100
    else:
        return {"error": f"Unknown operation '{operation}'. Use add, subtract, multiply, divide or percent_change."}
    
    return {"operation": operation, "a":a, "b": b, "result": round(result,2)}


@tool
def web_search(query: str) -> dict:
    """ Search the web for recent news and explaations.
    Use this to find WHY something happened, such as why a stock moved,
    query: a specific search, ideally with the company name and month,
    for example 'MongoDB stock drop September 2026.' """

    api_key = os.getenv("EXA_API_KEY")
    if not api_key:
        return {"error": "EXA_API_KEY is missing from backend/.env"}

    try:
        exa = Exa(api_key=api_key)
        response = exa.search_and_contents(
            query,
            num_results=3,
            text={"max_charactrs": 600},
        )

    except Exception as e:
        return {"error": f"Web search failed: {e}"}

    results = []

    for r in response.results:
        results.append({
            "title": r.title,
            "url": r.url,
            "published": r.published_date,
            "snippet": (r.text or "")[:600],
        })

    if not results:
        return {"error": "No results found,Try a different query."}
    return {"query": query, "results": results}