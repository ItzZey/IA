from sqlalchemy import Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base


class Dividend(Base):
    __tablename__ = "dividends"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    stock_id: Mapped[int] = mapped_column(ForeignKey("stocks.id"), nullable=False)
    ex_dividend_date = mapped_column(Date)
    payment_date = mapped_column(Date)
    amount: Mapped[float | None] = mapped_column(Float)
    currency: Mapped[str | None] = mapped_column(String)
    frequency: Mapped[str | None] = mapped_column(String)
    dividend_yield: Mapped[float | None] = mapped_column(Float)
    payout_ratio: Mapped[float | None] = mapped_column(Float)
    dividend_growth_1y: Mapped[float | None] = mapped_column(Float)
    dividend_growth_3y: Mapped[float | None] = mapped_column(Float)
    dividend_growth_5y: Mapped[float | None] = mapped_column(Float)
    consecutive_growth_years: Mapped[int | None] = mapped_column(Integer)
