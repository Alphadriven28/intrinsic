"""
Moat Engine — Quantitative competitive moat scoring (0–100).
Uses measurable financial proxies to estimate moat width.
"""
import statistics
from models.models import Financial, Ratio, SectorData, Company
from config import Config


class MoatEngine:
    """Produces a 0–100 moat score from financial fundamentals."""

    def run(self, ticker, wacc=None):
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
        company = Company.query.filter_by(ticker=ticker).first()
        sector = SectorData.query.filter_by(sector=company.sector).first() if company else None

        if len(financials) < 3:
            return {'score': 0, 'classification': 'No Moat', 'components': {}, 'error': 'Insufficient data'}

        if wacc is None:
            beta = company.beta if company and company.beta and company.beta > 0 else 1.0
            wacc = Config.RISK_FREE_RATE + beta * Config.EQUITY_RISK_PREMIUM

        components = {}

        # 1. Gross Margin Stability (20 pts)
        components['gross_margin_stability'] = self._gross_margin_stability(ratios)

        # 2. ROIC vs WACC Spread (20 pts)
        components['roic_spread'] = self._roic_spread(ratios, wacc)

        # 3. Revenue Growth vs Industry (15 pts)
        components['growth_vs_industry'] = self._growth_vs_industry(financials, sector)

        # 4. Intangible Intensity — R&D / Revenue (15 pts)
        components['intangible_intensity'] = self._intangible_intensity(financials)

        # 5. Brand Proxy — Gross margin above industry (15 pts)
        components['brand_proxy'] = self._brand_proxy(ratios, sector)

        # 6. Operating Leverage Consistency (15 pts)
        components['operating_leverage'] = self._operating_leverage(financials)

        total = sum(c['score'] for c in components.values())
        total = max(0, min(100, round(total)))

        if total >= 80:
            classification = 'Wide Moat'
        elif total >= 60:
            classification = 'Narrow Moat'
        else:
            classification = 'No Moat'

        return {
            'score': total,
            'classification': classification,
            'components': {k: {'score': round(v['score'], 1), 'max': v['max'], 'detail': v.get('detail', '')}
                          for k, v in components.items()},
            'error': None,
        }

    def _gross_margin_stability(self, ratios):
        """Consistent high gross margins indicate pricing power (20 pts)."""
        gm_vals = [r.gross_margin for r in ratios if r.gross_margin is not None]
        if len(gm_vals) < 3:
            return {'score': 5, 'max': 20, 'detail': 'Insufficient data'}

        avg_gm = statistics.mean(gm_vals[-5:])
        std_gm = statistics.stdev(gm_vals[-5:]) if len(gm_vals[-5:]) > 1 else 0

        # Level score (0–12)
        if avg_gm >= 0.60:
            level = 12
        elif avg_gm >= 0.45:
            level = 9
        elif avg_gm >= 0.30:
            level = 6
        else:
            level = 3

        # Stability score (0–8)
        cv = std_gm / avg_gm if avg_gm > 0 else 1
        if cv < 0.05:
            stability = 8
        elif cv < 0.10:
            stability = 6
        elif cv < 0.20:
            stability = 4
        else:
            stability = 2

        return {'score': min(level + stability, 20), 'max': 20, 'detail': f'Avg GM: {avg_gm:.0%}'}

    def _roic_spread(self, ratios, wacc):
        """ROIC consistently above WACC indicates competitive advantage (20 pts)."""
        roic_vals = [r.roic for r in ratios if r.roic is not None]
        if not roic_vals:
            return {'score': 5, 'max': 20, 'detail': 'No ROIC data'}

        avg_roic = statistics.mean(roic_vals[-5:])
        spread = avg_roic - wacc

        # How many years ROIC > WACC
        above_count = sum(1 for r in roic_vals[-5:] if r > wacc)
        consistency = above_count / len(roic_vals[-5:])

        # Spread magnitude (0–12)
        if spread >= 0.15:
            magnitude = 12
        elif spread >= 0.08:
            magnitude = 9
        elif spread >= 0.03:
            magnitude = 6
        elif spread >= 0:
            magnitude = 3
        else:
            magnitude = 0

        # Consistency (0–8)
        consistency_score = consistency * 8

        return {'score': min(magnitude + consistency_score, 20), 'max': 20,
                'detail': f'Spread: {spread:.1%}'}

    def _growth_vs_industry(self, financials, sector):
        """Revenue growth outperforming sector average (15 pts)."""
        revenues = [f.revenue for f in financials if f.revenue and f.revenue > 0]
        if len(revenues) < 2:
            return {'score': 5, 'max': 15, 'detail': 'Insufficient data'}

        n = min(5, len(revenues) - 1)
        company_cagr = (revenues[-1] / revenues[-(n+1)]) ** (1/n) - 1

        sector_growth = sector.avg_revenue_growth if sector and sector.avg_revenue_growth else 0.08
        outperformance = company_cagr - sector_growth

        if outperformance >= 0.10:
            score = 15
        elif outperformance >= 0.05:
            score = 12
        elif outperformance >= 0.02:
            score = 9
        elif outperformance >= 0:
            score = 6
        elif outperformance >= -0.03:
            score = 3
        else:
            score = 0

        return {'score': score, 'max': 15, 'detail': f'vs sector: {outperformance:+.1%}'}

    def _intangible_intensity(self, financials):
        """R&D / Revenue ratio as proxy for innovation moat (15 pts)."""
        rd_ratios = []
        for f in financials[-5:]:
            if f.revenue and f.revenue > 0 and f.rd_expense and f.rd_expense > 0:
                rd_ratios.append(f.rd_expense / f.revenue)

        if not rd_ratios:
            # If no R&D, score based on intangible assets
            latest = financials[-1]
            if latest.total_assets and latest.total_assets > 0:
                intangibles = (latest.intangible_assets or 0) + (latest.goodwill or 0)
                ratio = intangibles / latest.total_assets
                if ratio >= 0.30:
                    return {'score': 10, 'max': 15, 'detail': 'High intangible assets'}
                elif ratio >= 0.15:
                    return {'score': 7, 'max': 15, 'detail': 'Moderate intangible assets'}
            return {'score': 3, 'max': 15, 'detail': 'No R&D data'}

        avg_rd = statistics.mean(rd_ratios)
        if avg_rd >= 0.15:
            score = 15
        elif avg_rd >= 0.10:
            score = 12
        elif avg_rd >= 0.05:
            score = 8
        elif avg_rd >= 0.02:
            score = 5
        else:
            score = 2

        return {'score': score, 'max': 15, 'detail': f'R&D intensity: {avg_rd:.1%}'}

    def _brand_proxy(self, ratios, sector):
        """Gross margin premium over sector average (15 pts)."""
        gm_vals = [r.gross_margin for r in ratios if r.gross_margin is not None]
        if not gm_vals or not sector or not sector.avg_gross_margin:
            return {'score': 5, 'max': 15, 'detail': 'No sector comparison'}

        company_gm = statistics.mean(gm_vals[-3:])
        sector_gm = sector.avg_gross_margin
        premium = company_gm - sector_gm

        if premium >= 0.20:
            score = 15
        elif premium >= 0.10:
            score = 12
        elif premium >= 0.05:
            score = 9
        elif premium >= 0:
            score = 6
        else:
            score = 2

        return {'score': score, 'max': 15, 'detail': f'GM premium: {premium:+.1%}'}

    def _operating_leverage(self, financials):
        """Consistency of operating margin expansion (15 pts)."""
        op_margins = []
        for f in financials[-5:]:
            if f.revenue and f.revenue > 0 and f.operating_income is not None:
                op_margins.append(f.operating_income / f.revenue)

        if len(op_margins) < 3:
            return {'score': 5, 'max': 15, 'detail': 'Insufficient data'}

        # Check for expansion trend
        expanding = sum(1 for i in range(1, len(op_margins)) if op_margins[i] >= op_margins[i-1])
        expansion_ratio = expanding / (len(op_margins) - 1)

        # Average margin level
        avg_margin = statistics.mean(op_margins)

        level_score = 0
        if avg_margin >= 0.25:
            level_score = 8
        elif avg_margin >= 0.15:
            level_score = 6
        elif avg_margin >= 0.08:
            level_score = 4
        else:
            level_score = 2

        trend_score = expansion_ratio * 7

        return {'score': min(level_score + trend_score, 15), 'max': 15,
                'detail': f'Op margin: {avg_margin:.0%}'}
