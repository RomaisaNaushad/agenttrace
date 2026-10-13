from sqlalchemy import Column, Integer, String, Date, Numeric, BigInteger, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True)
    ticker = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    sector = Column(String)

    prices = relationship("StockPrice", back_populates="company")


class StockPrice(Base):
    __tablename__ = "stock_prices"
    __table_args__ = (UniqueConstraint("company_id", "date", name="uq_company_date"),)

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    date = Column(Date, nullable=False)
    close_price = Column(Numeric(12, 4), nullable=False)
    volume = Column(BigInteger)

    company = relationship("Company", back_populates="prices")