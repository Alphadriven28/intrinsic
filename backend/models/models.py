from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class Company(db.Model):
    __tablename__ = 'companies'
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(10), unique=True, nullable=False, index=True)
    name = db.Column(db.String(255))
    sector = db.Column(db.String(128))
    industry = db.Column(db.String(128))
    description = db.Column(db.Text)
    beta = db.Column(db.Float)
    shares_outstanding = db.Column(db.BigInteger)
    market_cap = db.Column(db.BigInteger)
    exchange = db.Column(db.String(32))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class Financial(db.Model):
    __tablename__ = 'financials'
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(10), db.ForeignKey('companies.ticker'), nullable=False, index=True)
    year = db.Column(db.Integer, nullable=False)
    revenue = db.Column(db.BigInteger)
    net_income = db.Column(db.BigInteger)
    gross_profit = db.Column(db.BigInteger)
    operating_income = db.Column(db.BigInteger)
    free_cash_flow = db.Column(db.BigInteger)
    operating_cash_flow = db.Column(db.BigInteger)
    capital_expenditure = db.Column(db.BigInteger)
    total_debt = db.Column(db.BigInteger)
    total_equity = db.Column(db.BigInteger)
    total_assets = db.Column(db.BigInteger)
    cash_and_equivalents = db.Column(db.BigInteger)
    dividends_paid = db.Column(db.BigInteger)
    shares_outstanding = db.Column(db.BigInteger)
    # New fields for expanded valuation models
    interest_expense = db.Column(db.BigInteger)
    intangible_assets = db.Column(db.BigInteger)
    goodwill = db.Column(db.BigInteger)
    rd_expense = db.Column(db.BigInteger)
    ebitda = db.Column(db.BigInteger)
    total_liabilities = db.Column(db.BigInteger)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (db.UniqueConstraint('ticker', 'year', name='uq_ticker_year'),)


class Ratio(db.Model):
    __tablename__ = 'ratios'
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(10), db.ForeignKey('companies.ticker'), nullable=False, index=True)
    year = db.Column(db.Integer, nullable=False)
    pe_ratio = db.Column(db.Float)
    pb_ratio = db.Column(db.Float)
    gross_margin = db.Column(db.Float)
    operating_margin = db.Column(db.Float)
    net_margin = db.Column(db.Float)
    roe = db.Column(db.Float)
    roic = db.Column(db.Float)
    roa = db.Column(db.Float)
    debt_to_equity = db.Column(db.Float)
    current_ratio = db.Column(db.Float)
    # New fields for relative valuation
    ev_to_ebitda = db.Column(db.Float)
    price_to_sales = db.Column(db.Float)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (db.UniqueConstraint('ticker', 'year', name='uq_ratio_ticker_year'),)


class SectorData(db.Model):
    __tablename__ = 'sector_data'
    id = db.Column(db.Integer, primary_key=True)
    sector = db.Column(db.String(128), unique=True, nullable=False)
    avg_pe = db.Column(db.Float)
    avg_revenue_growth = db.Column(db.Float)
    avg_gross_margin = db.Column(db.Float)
    avg_operating_margin = db.Column(db.Float)
    avg_net_margin = db.Column(db.Float)
    avg_roic = db.Column(db.Float)
    # New fields for relative valuation
    avg_pb = db.Column(db.Float)
    avg_ev_ebitda = db.Column(db.Float)
    avg_ps = db.Column(db.Float)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class AnalysisCache(db.Model):
    __tablename__ = 'analysis_cache'
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(10), unique=True, nullable=False, index=True)
    analysis_json = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
