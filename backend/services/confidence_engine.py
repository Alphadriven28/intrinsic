"""
Confidence Engine — Valuation confidence scoring (0–100).
Assesses how reliable the valuation estimate is based on
business fundamentals and model agreement.
"""
import statistics
from models.models import Financial, Ratio, Company


class ConfidenceEngine:
    """Produces a 0–100 confidence score for the valuation."""

    def run(self, ticker, valuation_result):
        ticker = ticker.upper()

        financials = (
            Financial.query
            .filter_by(ticker=ticker)
            .order_by(Financial.year.asc())
            .all()
        )
        ratios = (
            Ratio.query
            .filter_by(ticker=ticker)
            .order_by(Ratio.year.asc())
            .all()
        )

        if len(financials) < 3:
            return {'score': 0, 'badge': 'Low', 'components': {}, 'error': 'Insufficient data'}

        components = {}

        # 1. Earnings Stability (20 pts)
        components['earnings_stability'] = self._earnings_stability(financials)

        # 2. Cash Flow Quality (20 pts)
        components['cash_flow_quality'] = self._cash_flow_quality(financials)

        # 3. Balance Sheet Strength (15 pts)
        components['balance_sheet'] = self._balance_sheet(ratios, financials)

        # 4. Return Metrics (15 pts)
        components['return_metrics'] = self._return_metrics(ratios)

        # 5. Growth Visibility (15 pts)
        components['growth_visibility'] = self._growth_visibility(financials)

        # 6. Model Agreement (15 pts)
        components['model_agreement'] = self._model_agreement(valuation_result)

        total = sum(c['score'] for c in components.values())
        total = max(0, min(100, round(total)))

        if total >= 80:
            badge = 'High'
        elif total >= 60:
            badge = 'Moderate'
        else:
            badge = 'Low'

        return {
            'score': total,
            'badge': badge,
            'components': {k: {'score': round(v['score'], 1), 'max': v['max'], 'detail': v.get('detail', '')}
                          for k, v in components.items()},
            'error': None,
        }

    def _earnings_stability(self, financials):
        """5Y revenue consistency + margin volatility (20 pts max)."""
        revenues = [f.revenue for f in financials if f.revenue and f.revenue > 0]
        score = 0

        # Revenue consistency: how many years of positive growth?
        if len(revenues) >= 3:
            growth_years = sum(1 for i in range(1, len(revenues)) if revenues[i] > revenues[i-1])
            consistency = growth_years / (len(revenues) - 1)
            score += consistency * 10  # up to 10 pts

        # Margin volatility
        margins = []
        for f in financials[-5:]:
            if f.revenue and f.revenue > 0 and f.net_income is not None:
                margins.append(f.net_income / f.revenue)

        if len(margins) >= 3:
            cv = statistics.stdev(margins) / abs(statistics.mean(margins)) if statistics.mean(margins) != 0 else 2
            if cv < 0.1:
                score += 10
            elif cv < 0.3:
                score += 7
            elif cv < 0.5:
                score += 4
            else:
                score += 1

        return {'score': min(score, 20), 'max': 20, 'detail': 'Revenue & margin consistency'}

    def _cash_flow_quality(self, financials):
        """FCF positive frequency + FCF/NI ratio (20 pts max)."""
        fcfs = [f.free_cash_flow for f in financials if f.free_cash_flow is not None]
        nis = [f.net_income for f in financials if f.net_income is not None]
        score = 0

        # FCF positive frequency
        if fcfs:
            pos_ratio = sum(1 for f in fcfs if f > 0) / len(fcfs)
            score += pos_ratio * 10

        # FCF / Net Income ratio (quality: FCF should track NI)
        if fcfs and nis and len(fcfs) >= 3:
            avg_fcf = statistics.mean(fcfs[-3:])
            avg_ni = statistics.mean(nis[-3:])
            if avg_ni > 0:
                ratio = avg_fcf / avg_ni
                if 0.7 <= ratio <= 1.5:
                    score += 10
                elif 0.4 <= ratio <= 2.0:
                    score += 6
                else:
                    score += 2

        return {'score': min(score, 20), 'max': 20, 'detail': 'FCF consistency & earnings quality'}

    def _balance_sheet(self, ratios, financials):
        """D/E + interest coverage (15 pts max)."""
        score = 0

        # Debt to equity
        de_vals = [r.debt_to_equity for r in ratios if r.debt_to_equity is not None]
        if de_vals:
            avg_de = statistics.mean(de_vals[-3:])
            if avg_de <= 0.3:
                score += 8
            elif avg_de <= 0.7:
                score += 6
            elif avg_de <= 1.5:
                score += 4
            elif avg_de <= 3.0:
                score += 2
            else:
                score += 0

        # Interest coverage proxy
        if financials:
            latest = financials[-1]
            if (latest.operating_income and latest.interest_expense
                    and latest.interest_expense > 0):
                coverage = latest.operating_income / latest.interest_expense
                if coverage > 10:
                    score += 7
                elif coverage > 5:
                    score += 5
                elif coverage > 2:
                    score += 3
                else:
                    score += 1

        return {'score': min(score, 15), 'max': 15, 'detail': 'Leverage & interest coverage'}

    def _return_metrics(self, ratios):
        """ROIC + ROE consistency (15 pts max)."""
        score = 0

        roic_vals = [r.roic for r in ratios if r.roic is not None]
        roe_vals = [r.roe for r in ratios if r.roe is not None]

        # ROIC level
        if roic_vals:
            avg_roic = statistics.mean(roic_vals[-3:])
            if avg_roic >= 0.20:
                score += 8
            elif avg_roic >= 0.12:
                score += 6
            elif avg_roic >= 0.08:
                score += 4
            else:
                score += 2

        # ROE consistency
        if len(roe_vals) >= 3:
            all_positive = all(r > 0 for r in roe_vals[-3:])
            if all_positive:
                cv = statistics.stdev(roe_vals[-3:]) / statistics.mean(roe_vals[-3:]) if statistics.mean(roe_vals[-3:]) != 0 else 1
                if cv < 0.2:
                    score += 7
                elif cv < 0.4:
                    score += 5
                else:
                    score += 3
            else:
                score += 1

        return {'score': min(score, 15), 'max': 15, 'detail': 'Return on capital quality'}

    def _growth_visibility(self, financials):
        """Revenue CAGR stability + sector alignment (15 pts max)."""
        revenues = [f.revenue for f in financials if f.revenue and f.revenue > 0]
        score = 0

        if len(revenues) >= 3:
            # Year-over-year growth rates
            yoy = [(revenues[i] / revenues[i-1]) - 1 for i in range(1, len(revenues))]

            # Positive growth trend
            pos_growth = sum(1 for g in yoy if g > 0) / len(yoy)
            score += pos_growth * 8

            # Stability of growth
            if len(yoy) >= 3:
                cv = statistics.stdev(yoy) / abs(statistics.mean(yoy)) if statistics.mean(yoy) != 0 else 2
                if cv < 0.3:
                    score += 7
                elif cv < 0.6:
                    score += 4
                else:
                    score += 1

        return {'score': min(score, 15), 'max': 15, 'detail': 'Growth stability & predictability'}

    def _model_agreement(self, valuation_result):
        """Std dev between valuation models (15 pts max). Lower = higher confidence."""
        models = valuation_result.get('models', {})
        values = [m['value'] for m in models.values()
                  if m.get('value') and m['value'] > 0 and not m.get('error')]

        if len(values) < 2:
            return {'score': 3, 'max': 15, 'detail': 'Too few models for comparison'}

        avg = statistics.mean(values)
        std = statistics.stdev(values)
        cv = std / avg if avg > 0 else 1

        if cv < 0.15:
            score = 15
        elif cv < 0.25:
            score = 12
        elif cv < 0.40:
            score = 8
        elif cv < 0.60:
            score = 5
        else:
            score = 2

        return {'score': score, 'max': 15, 'detail': f'Model dispersion CV: {cv:.1%}'}
