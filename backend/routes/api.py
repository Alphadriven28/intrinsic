"""
API Routes — Main REST endpoints for the Intrinsic platform.
"""
import re
import logging
from flask import Blueprint, jsonify, current_app
from services.fmp_service import FMPService
from services.exceptions import FMPError, FMPAuthError, FMPRateLimitError, FMPNotFoundError, FMPServiceError
from services.valuation_engine import ValuationEngine
from services.scoring_engine import ScoringEngine
from services.sector_service import SectorService
from services.risk_engine import RiskEngine
from services.summary_engine import SummaryEngine
from services.weighting_engine import WeightingEngine
from services.confidence_engine import ConfidenceEngine
from services.moat_engine import MoatEngine
from services.master_engine import MasterEngine
from config import Config
from models.models import db

logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__)


@api_bp.route('/analyze/<ticker>', methods=['GET'])
def analyze(ticker):
    """Full automated analysis for a given ticker."""
    # --- Input sanitization ---
    ticker = FMPService.sanitize_ticker(ticker)
    if not ticker:
        return jsonify({
            'error': 'Invalid ticker symbol. Use only letters and numbers.',
            'error_code': 'invalid_input',
        }), 400

    logger.info(f"Analysis requested for: {ticker}")

    fmp = FMPService()

    # Check cache first
    if fmp.is_cache_fresh(ticker):
        cached = fmp.get_cached_analysis(ticker)
        if cached:
            logger.info(f"Returning cached analysis for {ticker}")
            return jsonify(cached)

    # Fetch and store all data — exceptions are now structured
    try:
        result, error = fmp.fetch_and_store_all(ticker)
    except FMPAuthError as e:
        logger.error(f"Auth error for {ticker}: {e.message}")
        return jsonify({'error': e.message, 'error_code': e.error_code}), e.status_code
    except FMPRateLimitError as e:
        logger.error(f"Rate limit error for {ticker}: {e.message}")
        return jsonify({'error': e.message, 'error_code': e.error_code}), e.status_code
    except FMPNotFoundError as e:
        logger.warning(f"Not found for {ticker}: {e.message}")
        return jsonify({'error': e.message, 'error_code': e.error_code}), e.status_code
    except FMPServiceError as e:
        logger.error(f"Service error for {ticker}: {e.message}")
        return jsonify({'error': e.message, 'error_code': e.error_code}), e.status_code
    except FMPError as e:
        logger.error(f"FMP error for {ticker}: {e.message}")
        return jsonify({'error': e.message, 'error_code': e.error_code}), e.status_code
    except Exception as e:
        logger.exception(f"Unexpected error analyzing {ticker}")
        return jsonify({
            'error': 'An unexpected server error occurred.',
            'error_code': 'server_error',
        }), 500

    company = result['company']
    quote = result['quote']
    current_price = quote.get('price', 0) if quote else 0

    # --- Run valuation engine (9 models) ---
    valuation_engine = ValuationEngine()
    valuation = valuation_engine.run(ticker, current_price)

    # --- Run weighting engine ---
    weighting_engine = WeightingEngine()
    weighting = weighting_engine.run(ticker, valuation)

    # --- Run scoring engine (includes quality_score_100) ---
    scoring_engine = ScoringEngine()
    scores = scoring_engine.run(ticker)

    # --- Run confidence engine ---
    confidence_engine = ConfidenceEngine()
    confidence = confidence_engine.run(ticker, valuation)

    # --- Run moat engine ---
    moat_engine = MoatEngine()
    wacc_decimal = valuation.get('wacc', 10) / 100
    moat = moat_engine.run(ticker, wacc=wacc_decimal)

    # --- Run master engine (composite rating) ---
    master_engine = MasterEngine()
    quality_100 = scores.get('quality_score_100', 50)
    master = master_engine.run(weighting, quality_100, moat, confidence, current_price)

    # --- Run sector comparison ---
    sector_service = SectorService()
    sector = sector_service.run(ticker)

    # --- Run risk engine ---
    risk_engine = RiskEngine()
    risk = risk_engine.run(ticker, valuation)

    # --- Generate executive summary ---
    summary_engine = SummaryEngine()
    summary = summary_engine.run(
        company.name, ticker, valuation, scores, risk, sector,
        weighting=weighting, confidence=confidence, moat=moat, master=master
    )

    # Build response
    analysis = {
        'company': {
            'name': company.name,
            'ticker': company.ticker,
            'sector': company.sector,
            'industry': company.industry,
            'exchange': company.exchange,
            'price': current_price,
            'beta': company.beta,
            'market_cap': company.market_cap,
            'description': company.description,
        },
        'valuation': valuation,
        'weighting': weighting,
        'confidence': confidence,
        'moat': moat,
        'scores': scores,
        'master': master,
        'sector': sector,
        'risk': risk,
        'summary': summary,
    }

    # Cache the result
    fmp.save_analysis_cache(ticker, analysis)

    logger.info(f"Analysis complete for {ticker}")
    return jsonify(analysis)


@api_bp.route('/health', methods=['GET'])
def health():
    """Comprehensive health check endpoint."""
    # 1. API key loaded?
    api_key_loaded = bool(Config.FMP_API_KEY)

    # 2. FMP reachable?
    fmp_reachable = False
    if api_key_loaded:
        try:
            fmp = FMPService()
            fmp_reachable = fmp.check_api_health()
        except Exception:
            fmp_reachable = False

    # 3. Database connected?
    db_connected = False
    try:
        db.session.execute(db.text('SELECT 1'))
        db_connected = True
    except Exception:
        db_connected = False

    status = 'ok' if (api_key_loaded and fmp_reachable and db_connected) else 'degraded'

    return jsonify({
        'status': status,
        'service': 'intrinsic-api',
        'checks': {
            'api_key_loaded': api_key_loaded,
            'fmp_reachable': fmp_reachable,
            'database_connected': db_connected,
        }
    })
