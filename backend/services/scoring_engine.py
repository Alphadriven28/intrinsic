"""
Scoring Engine — Growth & Quality scoring model.
Weighted scoring based on fundamental metrics.
Now includes expanded Quality Score (0–100) with 7 components.
"""
import statistics
from models.models import Financial, Ratio


class ScoringEngine:
    """Computes Growth Score (0–10) and Quality Score (0–10 + 0–100)."""

    def run(self, ticker):
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
            return {'growth_score': None, 'quality_score': None,
                    'quality_score_100': None, 'error': 'Insufficient data'}

        # Component scores (0–10)
        rev_cagr_score = self._score_revenue_cagr(financials)
        roic_score = self._score_roic(ratios)
        fcf_score = self._score_fcf_consistency(financials)
        debt_score = self._score_debt_to_equity(ratios)
        margin_score = self._score_gross_margin(ratios)

        # ---- Growth Score (weighted, 0–10) ----
        growth = (
            rev_cagr_score * 0.25 +
            roic_score * 0.20 +
            fcf_score * 0.20 +
            debt_score * 0.15 +
            margin_score * 0.20
        )

        # ---- Quality Score (stability emphasis, 0–10) ----
        quality = (
            rev_cagr_score * 0.15 +
            roic_score * 0.25 +
            fcf_score * 0.25 +
            debt_score * 0.20 +
            margin_score * 0.15
        )

        # ---- Quality Score 100 (expanded, 0–100) ----
        q100_components = {}
        q100_components['roe_consistency'] = self._q100_roe_consistency(ratios)
        q100_components['fcf_consistency'] = self._q100_fcf_consistency(financials)
        q100_components['debt_levels'] = self._q100_debt_levels(ratios)
        q100_components['margin_expansion'] = self._q100_margin_expansion(financials)
        q100_components['earnings_predictability'] = self._q100_earnings_predictability(financials)
        q100_components['capex_discipline'] = self._q100_capex_discipline(financials)
        q100_components['share_dilution'] = self._q100_share_dilution(financials)

        quality_100 = sum(c['score'] for c in q100_components.values())
        quality_100 = max(0, min(100, round(quality_100)))

        return {
            'growth_score': round(growth, 1),
            'quality_score': round(quality, 1),
            'quality_score_100': quality_100,
            'quality_components': {k: {'score': round(v['score'], 1), 'max': v['max']}
                                   for k, v in q100_components.items()},
            'components': {
                'revenue_cagr': round(rev_cagr_score, 1),
                'roic': round(roic_score, 1),
                'fcf_consistency': round(fcf_score, 1),
                'debt_safety': round(debt_score, 1),
                'gross_margin': round(margin_score, 1),
            },
            'error': None,
        }

    # ------------------------------------------------------------------
    # Component scorers  (each returns 0–10)
    # ------------------------------------------------------------------

    def _score_revenue_cagr(self, financials):
        revenues = [f.revenue for f in financials if f.revenue and f.revenue > 0]
        if len(revenues) < 2:
            return 5.0
        n = min(5, len(revenues) - 1)
        cagr = (revenues[-1] / revenues[-(n + 1)]) ** (1 / n) - 1

        if cagr >= 0.20: return 10.0
        elif cagr >= 0.15: return 8.5
        elif cagr >= 0.10: return 7.0
        elif cagr >= 0.05: return 5.5
        elif cagr >= 0.0: return 3.5
        else: return 1.5

    def _score_roic(self, ratios):
        roic_vals = [r.roic for r in ratios if r.roic is not None]
        if not roic_vals:
            return 5.0
        avg = sum(roic_vals) / len(roic_vals)

        if avg >= 0.25: return 10.0
        elif avg >= 0.20: return 8.5
        elif avg >= 0.15: return 7.0
        elif avg >= 0.10: return 5.5
        elif avg >= 0.05: return 3.5
        else: return 2.0

    def _score_fcf_consistency(self, financials):
        fcfs = [f.free_cash_flow for f in financials if f.free_cash_flow is not None]
        if not fcfs:
            return 5.0
        positive = sum(1 for f in fcfs if f > 0)
        ratio = positive / len(fcfs)
        return round(ratio * 10, 1)

    def _score_debt_to_equity(self, ratios):
        de_vals = [r.debt_to_equity for r in ratios if r.debt_to_equity is not None]
        if not de_vals:
            return 5.0
        avg = sum(de_vals) / len(de_vals)

        if avg <= 0.3: return 10.0
        elif avg <= 0.5: return 8.5
        elif avg <= 1.0: return 7.0
        elif avg <= 1.5: return 5.0
        elif avg <= 2.5: return 3.0
        else: return 1.0

    def _score_gross_margin(self, ratios):
        gm_vals = [r.gross_margin for r in ratios if r.gross_margin is not None]
        if not gm_vals:
            return 5.0
        avg = sum(gm_vals) / len(gm_vals)

        if avg >= 0.60: return 10.0
        elif avg >= 0.50: return 8.5
        elif avg >= 0.40: return 7.0
        elif avg >= 0.30: return 5.5
        elif avg >= 0.20: return 3.5
        else: return 2.0

    # ------------------------------------------------------------------
    # Quality Score 100 — 7 components
    # ------------------------------------------------------------------

    def _q100_roe_consistency(self, ratios):
        """ROE consistency over time (15 pts max)."""
        roe_vals = [r.roe for r in ratios if r.roe is not None]
        if len(roe_vals) < 3:
            return {'score': 5, 'max': 15}

        avg_roe = statistics.mean(roe_vals[-5:])
        all_pos = all(r > 0 for r in roe_vals[-5:])

        score = 0
        if avg_roe >= 0.20 and all_pos:
            score = 15
        elif avg_roe >= 0.15 and all_pos:
            score = 12
        elif avg_roe >= 0.10:
            score = 9
        elif avg_roe >= 0.05:
            score = 6
        else:
            score = 3

        return {'score': score, 'max': 15}

    def _q100_fcf_consistency(self, financials):
        """FCF consistently positive (15 pts max)."""
        fcfs = [f.free_cash_flow for f in financials if f.free_cash_flow is not None]
        if not fcfs:
            return {'score': 5, 'max': 15}

        pos_ratio = sum(1 for f in fcfs if f > 0) / len(fcfs)
        return {'score': round(pos_ratio * 15, 1), 'max': 15}

    def _q100_debt_levels(self, ratios):
        """Low and stable debt (15 pts max)."""
        de_vals = [r.debt_to_equity for r in ratios if r.debt_to_equity is not None]
        if not de_vals:
            return {'score': 7, 'max': 15}

        avg = statistics.mean(de_vals[-3:])
        if avg <= 0.3: return {'score': 15, 'max': 15}
        elif avg <= 0.7: return {'score': 12, 'max': 15}
        elif avg <= 1.0: return {'score': 9, 'max': 15}
        elif avg <= 2.0: return {'score': 5, 'max': 15}
        else: return {'score': 2, 'max': 15}

    def _q100_margin_expansion(self, financials):
        """Margin expansion trend (15 pts max)."""
        margins = []
        for f in financials[-5:]:
            if f.revenue and f.revenue > 0 and f.net_income is not None:
                margins.append(f.net_income / f.revenue)

        if len(margins) < 3:
            return {'score': 5, 'max': 15}

        expanding = sum(1 for i in range(1, len(margins)) if margins[i] >= margins[i-1])
        ratio = expanding / (len(margins) - 1)

        return {'score': round(ratio * 15, 1), 'max': 15}

    def _q100_earnings_predictability(self, financials):
        """Low variance in earnings growth (15 pts max)."""
        nis = [f.net_income for f in financials if f.net_income is not None and f.net_income > 0]
        if len(nis) < 3:
            return {'score': 5, 'max': 15}

        yoy = [(nis[i] / nis[i-1]) - 1 for i in range(1, len(nis)) if nis[i-1] > 0]
        if not yoy:
            return {'score': 5, 'max': 15}

        cv = statistics.stdev(yoy) / abs(statistics.mean(yoy)) if statistics.mean(yoy) != 0 else 2

        if cv < 0.2: return {'score': 15, 'max': 15}
        elif cv < 0.4: return {'score': 11, 'max': 15}
        elif cv < 0.7: return {'score': 7, 'max': 15}
        else: return {'score': 3, 'max': 15}

    def _q100_capex_discipline(self, financials):
        """CapEx/Revenue ratio — efficient capital allocation (10 pts max)."""
        capex_ratios = []
        for f in financials[-5:]:
            if f.revenue and f.revenue > 0 and f.capital_expenditure is not None:
                capex_ratios.append(abs(f.capital_expenditure) / f.revenue)

        if not capex_ratios:
            return {'score': 5, 'max': 10}

        avg = statistics.mean(capex_ratios)
        if avg <= 0.05: return {'score': 10, 'max': 10}
        elif avg <= 0.10: return {'score': 8, 'max': 10}
        elif avg <= 0.15: return {'score': 6, 'max': 10}
        elif avg <= 0.25: return {'score': 4, 'max': 10}
        else: return {'score': 2, 'max': 10}

    def _q100_share_dilution(self, financials):
        """Share count stability (15 pts max). Buybacks = bonus."""
        shares = [f.shares_outstanding for f in financials
                  if f.shares_outstanding and f.shares_outstanding > 0]
        if len(shares) < 2:
            return {'score': 7, 'max': 15}

        change = (shares[-1] / shares[0]) - 1  # total change

        if change <= -0.05:  # buybacks
            return {'score': 15, 'max': 15}
        elif change <= 0.0:
            return {'score': 13, 'max': 15}
        elif change <= 0.05:
            return {'score': 10, 'max': 15}
        elif change <= 0.15:
            return {'score': 6, 'max': 15}
        else:
            return {'score': 2, 'max': 15}
