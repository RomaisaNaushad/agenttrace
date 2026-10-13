import pandas as pd
import yfinance as yf

from app.db import SessionLocal
from app.models import Company, StockPrice

COMPANIES = [
    ("META", "Meta Platforms, Inc.", "Technology"),
    ("NVDA", "NVIDIA Corporation", "Semiconductors"),
    ("MDB","MongoDB, Inc.", "Software"),
]

def seed_companies(session):
    for ticker, name, sector in COMPANIES:
        exists = session.query(Company).filter_by(ticker=ticker).first()
        if not exists:
            session.add(Company(ticker=ticker, name=name, sector=sector))
        session.commit()

def seed_prices(session, period="6mo"):
    for company in session.query(Company).all():
        hist = yf.Ticker(company.ticker).history(period=period)
        if hist.empty:
            print(f"{company.ticker}: no data returened, skipping")
            continue

        added = 0
        for timestamp, row in hist.iterrows():
            if pd.isna(row["Close"]):
                continue
            day = timestamp.date()
            already =(
                session.query(StockPrice)
                .filter_by(company_id=company.id, date=day)
                .first()
            )
            
            if already:
                continue
            session.add(
                StockPrice(
                    company_id=company.id,
                    date=day,
                    close_price=round(float(row["Close"]), 4),
                    volume=int(row["Volume"]),
                )
            )
            added += 1

        session.commit()
        print(f"{company.ticker}: added {added} rows")




if __name__ == "__main__":
    session = SessionLocal()
    seed_companies(session)
    seed_prices(session)
    session.close()
    print("Done")      
