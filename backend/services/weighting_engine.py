"""
Weighting Engine — Dynamic model weight allocation.
Assigns weights to each valuation model based on company type
and data reliability, then computes weighted intrinsic value.
"""
import statistics
from models.models import Financial, Ratio, Company


# Default weight profiles per company type
WEIGHT_PROFILES = {
    'high_growth': {
        'dcf': 0.30, 'relative': 0.20, 'ddm': 0.00, 'residual_income': 0.15,
        'asset_based': 0.00, 'epv': 0.10, 'graham': 0.05, 'sotp': 0.10, 'eva': 0.10,
    },
    'stable': {
        'dcf': 0.30, 'relative': 0.20, 'ddm': 0.15, 'residual_income': 0.10,
        'asset_based': 0.00, 'epv': 0.10, 'graham': 0.05, 'sotp': 0.05, 'eva': 0.05,
    },
    'mature_dividend': {
        'dcf': 0.20, 'relative': 0.15, 'ddm': 0.30, 'residual_income': 0.05,
        'asset_based': 0.10, 'epv': 0.10, 'graham': 0.05, 'sotp': 0.00, 'eva': 0.05,
    },
    'asset_heavy': {
        'dcf': 0.15, 'relative': 0.15, 'ddm': 0.05, 'residual_income': 0.10,
        'asset_based': 0.25, 'epv': 0.10, 'graham': 0.05, 'sotp': 0.10, 'eva': 0.05,
    },
    'loss_making': {
        'dcf': 0.10, 'relative': 0.25, 'ddm': 0.00, 'residual_income': 0.00,
        'asset_based': 0.35, 'epv': 0.00, 'graham': 0.00, 'sotp': 0.20, 'eva': 0.10,
    },
    'default': {
        'dcf': 0.25, 'relative': 0.20, 'ddm': 0.10, 'residual_income': 0.10,
        'asset_based': 0.05, 'epv': 0.10, 'graham': 0.05, 'sotp': 0.10, 'eva': 0.05,
    },
}

MODEL_NAMES = {
    'dcf': 'DCF',
    'relative': 'Relative',
    'ddm': 'DDM',
    'residual_income': 'Residual Income',
    'asset_based': 'Asset-Based',
    'epv': 'EPV',
    'graham': 'Graham',
    'sotp': 'SOTP',
    'eva': 'EVA',
}


class WeightingEngine:
    """Dynamically weights valuation models based on company characteristics."""

    def run(self, ticker, valuation_result):
        """
        Args:
            ticker: company ticker
            valuation_result: full output from ValuationEngine.run()
        Returns:
            dict with company_type, weights, weighted_iv, contributions
        """
        ticker = ticker.upper()
        models = valuation_result.get('models', {})

        if not models:
            return {'error': 'No model results to weight'}

        # Step 1: Detect company type
        company_type = self._detect_type(ticker)

        # Step 2: Get base weights
        base_weights = dict(WEIGHT_PROFILES.get(company_type, WEIGHT_PROFILES['default']))

        # Step 3: Reliability adjustments — zero out models that failed
        adjusted = {}
        for model_key, weight in base_weights.items():
            model = models.get(model_key, {})
            if not model.get('value') or model.get('error') or model['value'] <= 0:
                adjusted[model_key] = 0.0
            else:
                adjusted[model_key] = weight

        # Step 3b: Additional reliability penalties
        adjusted = self._apply_reliability_penalties(ticker, adjusted, models)

        # Step 4: Normalize weights to 100%
        total = sum(adjusted.values())
        if total <= 0:
            return {
                'company_type': company_type,
                'weights': {},
                'weighted_intrinsic_value': 0,
                'contributions': {},
                'error': 'All models failed or had zero weight',
            }

        normalized = {k: round(v / total, 4) for k, v in adjusted.items()}

        # Step 5: Compute weighted intrinsic value
        weighted_iv = 0
        contributions = {}
        for model_key, weight in normalized.items():
            if weight > 0:
                value = models[model_key]['value']
                contribution = value * weight
                weighted_iv += contribution
                contributions[model_key] = {
                    'name': MODEL_NAMES.get(model_key, model_key),
                    'value': round(value, 2),
                    'weight': round(weight * 100, 1),
                    'contribution': round(contribution, 2),
                }

        return {
            'company_type': company_type,
            'company_type_label': company_type.replace('_', ' ').title(),
            'weights': {k: round(v * 100, 1) for k, v in normalized.items() if v > 0},
            'weighted_intrinsic_value': round(weighted_iv, 2),
            'contributions': contributions,
            'error': None,
        }

    def _detect_type(self, ticker):
        """Classify company into a type based on financial characteristics."""
        financials = (
            Financial.query
            .filter_by(ticker=ticker)
            .order_by(Financial.year.asc())
            .all()
        )
        if len(financials) < 2:
            return 'default'

        latest = financials[-1]

        # Check loss-making
        if latest.net_income is not None and latest.net_income < 0:
            return 'loss_making'

        # Revenue CAGR
        revenues = [f.revenue for f in financials if f.revenue and f.revenue > 0]
        rev_cagr = None
        if len(revenues) >= 2:
            n = min(5, len(revenues) - 1)
            start = revenues[-(n + 1)]
            end = revenues[-1]
            if start > 0 and end > 0:
                rev_cagr = (end / start) ** (1 / n) - 1

        # Check dividend focused
        divs = [abs(f.dividends_paid) for f in financials[-3:]
                if f.dividends_paid and f.dividends_paid != 0]
        ni_vals = [f.net_income for f in financials[-3:]
                   if f.net_income and f.net_income > 0]
        if divs and ni_vals:
            avg_payout = statistics.mean(divs) / statistics.mean(ni_vals)
            if avg_payout > 0.40:
                return 'mature_dividend'

        # Check asset heavy
        if latest.total_assets and latest.revenue:
            asset_turnover = latest.revenue / latest.total_assets
            if asset_turnover < 0.3:
                return 'asset_heavy'

        # Growth classification
        if rev_cagr is not None:
            if rev_cagr > 0.15:
                return 'high_growth'
            elif rev_cagr >= 0.05:
                return 'stable'

        return 'stable'

    def _apply_reliability_penalties(self, ticker, weights, models):
        """Reduce weights for unreliable models based on data quality."""
        financials = (
            Financial.query
            .filter_by(ticker=ticker)
            .order_by(Financial.year.asc())
            .all()
        )

        # Negative FCF → reduce DCF weight
        if financials:
            recent_fcfs = [f.free_cash_flow for f in financials[-3:]
                         if f.free_cash_flow is not None]
            neg_count = sum(1 for f in recent_fcfs if f < 0)
            if neg_count >= 2:
                weights['dcf'] *= 0.3
            elif neg_count >= 1:
                weights['dcf'] *= 0.6

        # Unstable dividends → reduce DDM weight
        divs = [abs(f.dividends_paid) for f in financials
                if f.dividends_paid and f.dividends_paid != 0]
        if len(divs) < 3 or any(d <= 0 for d in divs[-3:]):
            weights['ddm'] *= 0.2

        # Volatile margins → reduce EPV weight
        if len(financials) >= 3:
            margins = []
            for f in financials[-5:]:
                if f.revenue and f.revenue > 0 and f.operating_income is not None:
                    margins.append(f.operating_income / f.revenue)
            if len(margins) >= 3:
                cv = statistics.stdev(margins) / abs(statistics.mean(margins)) if statistics.mean(margins) != 0 else 1
                if cv > 0.5:
                    weights['epv'] *= 0.4

        # Negative book value → reduce residual income and asset-based
        if financials and financials[-1].total_equity is not None:
            if financials[-1].total_equity <= 0:
                weights['residual_income'] *= 0.1
                weights['asset_based'] *= 0.1

        return weights
