import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    FMP_API_KEY = os.getenv('FMP_API_KEY', '')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///intrinsic.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CACHE_TTL_HOURS = 24
    FMP_BASE_URL = 'https://financialmodelingprep.com/stable'

    # DCF Defaults
    RISK_FREE_RATE = 0.0425  # 10Y Treasury
    EQUITY_RISK_PREMIUM = 0.055
    TERMINAL_GROWTH_RATE = 0.025
    PROJECTION_YEARS = 5

    # Graham Formula Defaults
    GRAHAM_NO_GROWTH_PE = 8.5
    GRAHAM_GROWTH_MULTIPLE = 2.0
    GRAHAM_AAA_YIELD = 0.0420  # Current AAA bond yield

    # DDM Defaults
    DDM_TERMINAL_GROWTH = 0.03

    # Tax Rate (for EVA / NOPAT)
    CORPORATE_TAX_RATE = 0.21
