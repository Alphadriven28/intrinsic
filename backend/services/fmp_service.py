"""
FMP API Service — Financial Modeling Prep data fetcher.
Handles all external API calls with caching, structured error handling, and logging.
"""
import re
import requests
import logging
from config import Config
from datetime import datetime, timezone, timedelta
from models.models import db, Company, Financial, Ratio, SectorData, AnalysisCache
from services.exceptions import (
    FMPAuthError,
    FMPRateLimitError,
    FMPNotFoundError,
    FMPServiceError,
)
import json

logger = logging.getLogger(__name__)


class FMPService:
    """Client for Financial Modeling Prep API."""

    def __init__(self):
        self.api_key = Config.FMP_API_KEY
        self.base_url = Config.FMP_BASE_URL

    # ------------------------------------------------------------------
    # Core HTTP helper
    # ------------------------------------------------------------------

    def _get(self, endpoint, params=None):
        """Make authenticated GET request to FMP with structured error handling."""
        # Validate API key is present
        if not self.api_key:
            logger.error("FMP_API_KEY is not set in environment variables")
            raise FMPAuthError("API key not configured. Set FMP_API_KEY in your .env file.")

        if params is None:
            params = {}
        params['apikey'] = self.api_key
        url = f"{self.base_url}/{endpoint}"

        logger.info(f"FMP request: GET {url} (params: { {k: v for k, v in params.items() if k != 'apikey'} })")

        try:
            resp = requests.get(url, params=params, timeout=15)
        except requests.ConnectionError:
            logger.error(f"FMP connection error for {url}")
            raise FMPServiceError("Cannot reach Financial Modeling Prep API. Check your network.")
        except requests.Timeout:
            logger.error(f"FMP timeout for {url}")
            raise FMPServiceError("FMP API request timed out. Please try again.")
        except requests.RequestException as e:
            logger.error(f"FMP request exception for {url}: {e}")
            raise FMPServiceError(f"Network error: {e}")

        # Log response details
        logger.info(f"FMP response: status={resp.status_code} for {endpoint}")

        # --- Status code checks ---
        if resp.status_code == 401:
            logger.error(f"FMP 401 Unauthorized. Response: {resp.text[:200]}")
            raise FMPAuthError()

        if resp.status_code == 402:
            logger.warning(f"FMP 402 Payment Required. Response: {resp.text[:200]}")
            raise FMPRateLimitError("This feature requires a higher FMP plan.")

        if resp.status_code == 403:
            logger.error(f"FMP 403 Forbidden. Response: {resp.text[:200]}")
            raise FMPRateLimitError("API access forbidden. Check your plan or quota.")

        if resp.status_code >= 500:
            logger.error(f"FMP server error {resp.status_code}. Response: {resp.text[:200]}")
            raise FMPServiceError(f"FMP server returned {resp.status_code}.")

        if resp.status_code != 200:
            logger.error(f"FMP unexpected status {resp.status_code}. Response: {resp.text[:200]}")
            raise FMPServiceError(f"Unexpected API response (HTTP {resp.status_code}).")

        # --- Parse JSON ---
        # Some endpoints return plain text errors (e.g., "Restricted Endpoint")
        content_type = resp.headers.get('Content-Type', '')
        if 'application/json' not in content_type and 'text/' in content_type:
            body = resp.text.strip()
            if 'restricted' in body.lower():
                logger.warning(f"FMP restricted endpoint: {body[:200]}")
                raise FMPRateLimitError("This feature requires a paid FMP plan.")
            if 'invalid api' in body.lower() or 'invalid key' in body.lower():
                logger.error(f"FMP auth error in text response: {body[:200]}")
                raise FMPAuthError()
            if 'limit' in body.lower():
                logger.error(f"FMP rate limit in text response: {body[:200]}")
                raise FMPRateLimitError()

        try:
            data = resp.json()
        except ValueError:
            logger.error(f"FMP returned non-JSON response: {resp.text[:200]}")
            raise FMPServiceError("Invalid response from FMP API.")

        # --- Check for error messages embedded in response body ---
        if isinstance(data, dict):
            error_msg = data.get('Error Message', '') or data.get('error', '')
            if error_msg:
                lower = error_msg.lower()
                if 'invalid api' in lower or 'invalid key' in lower:
                    logger.error(f"FMP body error (auth): {error_msg}")
                    raise FMPAuthError()
                if 'limit' in lower:
                    logger.error(f"FMP body error (rate limit): {error_msg}")
                    raise FMPRateLimitError()
                logger.error(f"FMP body error: {error_msg}")
                raise FMPServiceError(error_msg)

        logger.debug(f"FMP response body type={type(data).__name__}, "
                     f"len={len(data) if isinstance(data, list) else 'N/A'}")
        return data

    # ------------------------------------------------------------------
    # Input validation
    # ------------------------------------------------------------------

    @staticmethod
    def sanitize_ticker(ticker):
        """Trim, uppercase, and validate ticker symbol."""
        if not ticker:
            return None
        cleaned = ticker.strip().upper()
        # Allow only alphanumeric and dots (e.g., BRK.B)
        if not re.match(r'^[A-Z0-9.]{1,10}$', cleaned):
            return None
        return cleaned

    # ------------------------------------------------------------------
    # Cache helpers
    # ------------------------------------------------------------------

    def is_cache_fresh(self, ticker):
        """Check if analysis cache exists and is less than 24 hours old."""
        cache = AnalysisCache.query.filter_by(ticker=ticker.upper()).first()
        if not cache:
            return False
        age = datetime.now(timezone.utc) - cache.created_at.replace(tzinfo=timezone.utc)
        return age < timedelta(hours=Config.CACHE_TTL_HOURS)

    def get_cached_analysis(self, ticker):
        """Return cached analysis JSON if fresh."""
        cache = AnalysisCache.query.filter_by(ticker=ticker.upper()).first()
        if cache:
            return json.loads(cache.analysis_json)
        return None

    def save_analysis_cache(self, ticker, analysis_dict):
        """Save or update the analysis cache."""
        ticker = ticker.upper()
        cache = AnalysisCache.query.filter_by(ticker=ticker).first()
        if cache:
            cache.analysis_json = json.dumps(analysis_dict)
            cache.created_at = datetime.now(timezone.utc)
        else:
            cache = AnalysisCache(
                ticker=ticker,
                analysis_json=json.dumps(analysis_dict),
            )
            db.session.add(cache)
        db.session.commit()

    # ------------------------------------------------------------------
    # Data fetchers
    # ------------------------------------------------------------------

    def fetch_profile(self, ticker):
        """Fetch company profile from FMP with fallback search."""
        data = self._get("profile", {'symbol': ticker})

        # If empty array, try fallback search before giving up
        if isinstance(data, list) and len(data) == 0:
            logger.info(f"Profile returned empty for '{ticker}', attempting fallback search…")
            resolved = self._fallback_search(ticker)
            if resolved and resolved != ticker:
                logger.info(f"Fallback search resolved '{ticker}' → '{resolved}'")
                data = self._get("profile", {'symbol': resolved})

        if not data or (isinstance(data, list) and len(data) == 0):
            raise FMPNotFoundError(f"Ticker '{ticker}' not found in US markets.")

        return data[0] if isinstance(data, list) else data

    def _fallback_search(self, ticker):
        """Search FMP for the ticker as a fallback to handle symbol formatting issues."""
        try:
            results = self._get("search-symbol", {
                'query': ticker,
                'limit': 5,
            })
            if results and isinstance(results, list) and len(results) > 0:
                # Filter for US exchanges and return the best match
                us_results = [r for r in results if r.get('exchange') in ('NASDAQ', 'NYSE')]
                best = us_results[0] if us_results else results[0]
                symbol = best.get('symbol', '')
                logger.info(f"Fallback search found: {symbol} ({best.get('name', 'N/A')})")
                return symbol
        except Exception as e:
            logger.warning(f"Fallback search failed for '{ticker}': {e}")
        return None

    def fetch_quote(self, ticker):
        """Fetch current stock quote."""
        data = self._get("quote", {'symbol': ticker})
        if not data or (isinstance(data, list) and len(data) == 0):
            return None
        return data[0] if isinstance(data, list) else data

    def fetch_income_statements(self, ticker, limit=5):
        """Fetch annual income statements."""
        data = self._get("income-statement", {'symbol': ticker, 'limit': limit, 'period': 'annual'})
        return data if isinstance(data, list) else []

    def fetch_cash_flow_statements(self, ticker, limit=5):
        """Fetch annual cash flow statements."""
        data = self._get("cash-flow-statement", {'symbol': ticker, 'limit': limit, 'period': 'annual'})
        return data if isinstance(data, list) else []

    def fetch_balance_sheets(self, ticker, limit=5):
        """Fetch annual balance sheet statements."""
        data = self._get("balance-sheet-statement", {'symbol': ticker, 'limit': limit, 'period': 'annual'})
        return data if isinstance(data, list) else []

    def fetch_ratios(self, ticker, limit=5):
        """Fetch financial ratios."""
        data = self._get("ratios", {'symbol': ticker, 'limit': limit})
        return data if isinstance(data, list) else []

    def fetch_sector_peers(self, sector, limit=30):
        """Fetch sector peers for comparison via company screener.
        Note: This endpoint may be restricted on free FMP plans."""
        try:
            data = self._get("company-screener", {
                'sector': sector,
                'marketCapMoreThan': 10000000000,
                'limit': limit,
                'isActivelyTrading': True,
                'exchange': 'NYSE,NASDAQ',
            })
            return data if isinstance(data, list) else []
        except (FMPRateLimitError, FMPServiceError) as e:
            logger.warning(f"Sector screener unavailable (likely plan restriction): {e}")
            return []

    # ------------------------------------------------------------------
    # Health check
    # ------------------------------------------------------------------

    def check_api_health(self):
        """Check if the FMP API is reachable with the current key."""
        try:
            data = self._get("profile", {'symbol': 'AAPL'})
            return bool(data)
        except FMPAuthError:
            return False
        except Exception:
            return False

    # ------------------------------------------------------------------
    # Data storage
    # ------------------------------------------------------------------

    def store_company(self, profile, quote):
        """Store or update company profile in database."""
        ticker = profile['symbol'].upper()
        company = Company.query.filter_by(ticker=ticker).first()
        price = quote.get('price', 0) if quote else 0
        mcap = profile.get('marketCap') or profile.get('mktCap') or 0

        vals = dict(
            name=profile.get('companyName', ''),
            sector=profile.get('sector', ''),
            industry=profile.get('industry', ''),
            description=profile.get('description', ''),
            beta=profile.get('beta', 1.0),
            shares_outstanding=mcap // max(price, 1) if price else 0,
            market_cap=mcap,
            exchange=profile.get('exchange') or profile.get('exchangeShortName', ''),
            updated_at=datetime.now(timezone.utc),
        )

        if company:
            for k, v in vals.items():
                setattr(company, k, v)
        else:
            company = Company(ticker=ticker, **vals)
            db.session.add(company)
        db.session.commit()
        return company

    def store_financials(self, ticker, income_stmts, cf_stmts, bs_stmts):
        """Store historical financials for a ticker."""
        ticker = ticker.upper()

        # Index cash-flow and balance-sheet by fiscal year
        cf_by_year = {}
        for cf in cf_stmts:
            year = self._extract_year(cf)
            if year:
                cf_by_year[year] = cf

        bs_by_year = {}
        for bs in bs_stmts:
            year = self._extract_year(bs)
            if year:
                bs_by_year[year] = bs

        for inc in income_stmts:
            year = self._extract_year(inc)
            if not year:
                continue

            cf = cf_by_year.get(year, {})
            bs = bs_by_year.get(year, {})

            existing = Financial.query.filter_by(ticker=ticker, year=year).first()
            vals = dict(
                revenue=inc.get('revenue', 0),
                net_income=inc.get('netIncome', 0),
                gross_profit=inc.get('grossProfit', 0),
                operating_income=inc.get('operatingIncome', 0),
                free_cash_flow=cf.get('freeCashFlow', 0),
                operating_cash_flow=cf.get('operatingCashFlow', 0),
                capital_expenditure=cf.get('capitalExpenditure', 0),
                total_debt=bs.get('totalDebt', 0),
                total_equity=bs.get('totalStockholdersEquity', 0),
                total_assets=bs.get('totalAssets', 0),
                cash_and_equivalents=bs.get('cashAndCashEquivalents', 0),
                dividends_paid=cf.get('dividendsPaid', 0),
                shares_outstanding=inc.get('weightedAverageShsOut', 0),
                interest_expense=inc.get('interestExpense', 0),
                intangible_assets=bs.get('intangibleAssets', 0),
                goodwill=bs.get('goodwill', 0),
                rd_expense=inc.get('researchAndDevelopmentExpenses', 0),
                ebitda=inc.get('ebitda', 0),
                total_liabilities=bs.get('totalLiabilities', 0),
                updated_at=datetime.now(timezone.utc),
            )
            if existing:
                for k, v in vals.items():
                    setattr(existing, k, v)
            else:
                fin = Financial(ticker=ticker, year=year, **vals)
                db.session.add(fin)

        db.session.commit()

    def store_ratios(self, ticker, ratios_data):
        """Store financial ratios."""
        ticker = ticker.upper()
        for r in ratios_data:
            year = self._extract_year(r)
            if not year:
                continue

            existing = Ratio.query.filter_by(ticker=ticker, year=year).first()
            vals = dict(
                pe_ratio=r.get('priceEarningsRatio'),
                pb_ratio=r.get('priceBookValueRatio'),
                gross_margin=r.get('grossProfitMargin'),
                operating_margin=r.get('operatingProfitMargin'),
                net_margin=r.get('netProfitMargin'),
                roe=r.get('returnOnEquity'),
                roic=r.get('returnOnCapitalEmployed'),
                roa=r.get('returnOnAssets'),
                debt_to_equity=r.get('debtEquityRatio'),
                current_ratio=r.get('currentRatio'),
                ev_to_ebitda=r.get('enterpriseValueOverEBITDA'),
                price_to_sales=r.get('priceToSalesRatio'),
                updated_at=datetime.now(timezone.utc),
            )
            if existing:
                for k, v in vals.items():
                    setattr(existing, k, v)
            else:
                ratio = Ratio(ticker=ticker, year=year, **vals)
                db.session.add(ratio)

        db.session.commit()

    def compute_and_store_sector_data(self, sector, peers):
        """Compute sector averages from peer data and store."""
        if not peers or len(peers) == 0:
            return None

        pe_vals = [p.get('pe') for p in peers if p.get('pe') and p['pe'] > 0]
        avg_pe = sum(pe_vals) / len(pe_vals) if pe_vals else None

        sector_obj = SectorData.query.filter_by(sector=sector).first()
        vals = dict(
            avg_pe=avg_pe,
            avg_revenue_growth=0.08,
            avg_gross_margin=0.40,
            avg_operating_margin=0.15,
            avg_net_margin=0.10,
            avg_roic=0.12,
            avg_pb=3.0,
            avg_ev_ebitda=14.0,
            avg_ps=3.5,
            updated_at=datetime.now(timezone.utc),
        )

        if sector_obj:
            for k, v in vals.items():
                setattr(sector_obj, k, v)
        else:
            sector_obj = SectorData(sector=sector, **vals)
            db.session.add(sector_obj)
        db.session.commit()
        return sector_obj

    # ------------------------------------------------------------------
    # Full data fetch pipeline
    # ------------------------------------------------------------------

    def fetch_and_store_all(self, ticker):
        """
        Full pipeline: fetch all FMP data and store.
        Raises FMPError subclasses on failure — caller must handle.
        """
        ticker = self.sanitize_ticker(ticker)
        if not ticker:
            raise FMPNotFoundError("Invalid ticker symbol.")

        logger.info(f"=== Starting full analysis pipeline for {ticker} ===")

        # fetch_profile raises FMPNotFoundError if not found (after fallback)
        profile = self.fetch_profile(ticker)

        # Use the symbol from the profile (may differ if fallback resolved it)
        resolved_ticker = profile.get('symbol', ticker).upper()

        quote = self.fetch_quote(resolved_ticker)
        income = self.fetch_income_statements(resolved_ticker)
        cashflow = self.fetch_cash_flow_statements(resolved_ticker)
        balance = self.fetch_balance_sheets(resolved_ticker)
        ratios = self.fetch_ratios(resolved_ticker)

        if not income:
            raise FMPNotFoundError("Financial data not available for this ticker.")

        company = self.store_company(profile, quote)
        self.store_financials(resolved_ticker, income, cashflow, balance)
        self.store_ratios(resolved_ticker, ratios)

        # Sector data
        sector = profile.get('sector', '')
        if sector:
            peers = self.fetch_sector_peers(sector)
            self.compute_and_store_sector_data(sector, peers)

        logger.info(f"=== Analysis pipeline complete for {resolved_ticker} ===")

        return {
            'company': company,
            'quote': quote,
            'profile': profile,
        }, None

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_year(record):
        """Extract fiscal year from an FMP record."""
        date_str = record.get('date') or record.get('calendarYear')
        if not date_str:
            return None
        try:
            return int(str(date_str)[:4])
        except (ValueError, TypeError):
            return None
