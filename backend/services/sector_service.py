"""
Sector Comparison Service — Compares company metrics vs sector averages.
"""
from models.models import Ratio, SectorData, Company


class SectorService:
    """Compare company fundamentals against sector peers."""

    def run(self, ticker):
        ticker = ticker.upper()
        company = Company.query.filter_by(ticker=ticker).first()
        if not company:
            return {'error': 'Company not found'}

        sector = SectorData.query.filter_by(sector=company.sector).first()
        if not sector:
            return {'error': 'Sector data not available'}

        # Get latest company ratios
        latest_ratio = (
            Ratio.query
            .filter_by(ticker=ticker)
            .order_by(Ratio.year.desc())
            .first()
        )

        company_pe = latest_ratio.pe_ratio if latest_ratio and latest_ratio.pe_ratio else None
        company_gross_margin = latest_ratio.gross_margin if latest_ratio else None
        company_operating_margin = latest_ratio.operating_margin if latest_ratio else None
        company_net_margin = latest_ratio.net_margin if latest_ratio else None

        # Revenue growth (use CAGR from financials)
        from models.models import Financial
        financials = (
            Financial.query
            .filter_by(ticker=ticker)
            .order_by(Financial.year.asc())
            .all()
        )
        company_growth = None
        if len(financials) >= 2:
            revs = [f.revenue for f in financials if f.revenue and f.revenue > 0]
            if len(revs) >= 2:
                n = min(5, len(revs) - 1)
                company_growth = (revs[-1] / revs[-(n + 1)]) ** (1 / n) - 1

        def _fmt(val, is_pct=False):
            if val is None:
                return None
            if is_pct:
                return round(val * 100, 1)
            return round(val, 1)

        return {
            'sector_name': company.sector,
            'comparisons': [
                {
                    'metric': 'P/E Ratio',
                    'company': _fmt(company_pe),
                    'sector_avg': _fmt(sector.avg_pe),
                    'verdict': self._pe_verdict(company_pe, sector.avg_pe),
                },
                {
                    'metric': 'Revenue Growth',
                    'company': _fmt(company_growth, is_pct=True),
                    'sector_avg': _fmt(sector.avg_revenue_growth, is_pct=True),
                    'verdict': self._growth_verdict(company_growth, sector.avg_revenue_growth),
                },
                {
                    'metric': 'Gross Margin',
                    'company': _fmt(company_gross_margin, is_pct=True),
                    'sector_avg': _fmt(sector.avg_gross_margin, is_pct=True),
                    'verdict': self._margin_verdict(company_gross_margin, sector.avg_gross_margin),
                },
                {
                    'metric': 'Operating Margin',
                    'company': _fmt(company_operating_margin, is_pct=True),
                    'sector_avg': _fmt(sector.avg_operating_margin, is_pct=True),
                    'verdict': self._margin_verdict(company_operating_margin, sector.avg_operating_margin),
                },
                {
                    'metric': 'Net Margin',
                    'company': _fmt(company_net_margin, is_pct=True),
                    'sector_avg': _fmt(sector.avg_net_margin, is_pct=True),
                    'verdict': self._margin_verdict(company_net_margin, sector.avg_net_margin),
                },
            ],
            'error': None,
        }

    @staticmethod
    def _pe_verdict(company, sector):
        if company is None or sector is None:
            return 'N/A'
        if company < sector * 0.8:
            return 'Attractively priced relative to sector'
        elif company > sector * 1.2:
            return 'Premium to sector'
        return 'In line with sector'

    @staticmethod
    def _growth_verdict(company, sector):
        if company is None or sector is None:
            return 'N/A'
        if company > sector * 1.2:
            return 'Outperforming sector growth'
        elif company < sector * 0.8:
            return 'Below sector growth'
        return 'In line with sector'

    @staticmethod
    def _margin_verdict(company, sector):
        if company is None or sector is None:
            return 'N/A'
        if company > sector * 1.2:
            return 'Superior margins'
        elif company < sector * 0.8:
            return 'Below sector average'
        return 'In line with sector'
