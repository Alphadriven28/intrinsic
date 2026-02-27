"""
Risk Engine — Automated risk flagging and risk level assessment.
"""
from models.models import Financial, Company, Ratio


class RiskEngine:
    """Identifies risk flags and assigns overall risk level."""

    def run(self, ticker, valuation_result=None):
        ticker = ticker.upper()
        flags = []

        financials = (
            Financial.query
            .filter_by(ticker=ticker)
            .order_by(Financial.year.asc())
            .all()
        )
        company = Company.query.filter_by(ticker=ticker).first()
        latest_ratio = (
            Ratio.query
            .filter_by(ticker=ticker)
            .order_by(Ratio.year.desc())
            .first()
        )

        # 1. Negative FCF
        if financials:
            latest_fcf = financials[-1].free_cash_flow
            if latest_fcf is not None and latest_fcf < 0:
                flags.append({
                    'flag': 'Negative Free Cash Flow',
                    'detail': f'Latest FCF: ${latest_fcf:,.0f}',
                    'severity': 'high',
                })

        # 2. Revenue decline
        if len(financials) >= 2:
            revs = [f.revenue for f in financials if f.revenue]
            if len(revs) >= 2 and revs[-1] < revs[-2]:
                decline = ((revs[-2] - revs[-1]) / revs[-2]) * 100
                flags.append({
                    'flag': 'Revenue Decline',
                    'detail': f'YoY decline of {decline:.1f}%',
                    'severity': 'moderate',
                })

        # 3. High debt
        if latest_ratio and latest_ratio.debt_to_equity is not None:
            if latest_ratio.debt_to_equity > 2.0:
                flags.append({
                    'flag': 'High Debt',
                    'detail': f'Debt-to-Equity: {latest_ratio.debt_to_equity:.2f}',
                    'severity': 'high' if latest_ratio.debt_to_equity > 3.0 else 'moderate',
                })

        # 4. Overvaluation > 40%
        if valuation_result and not valuation_result.get('error'):
            mos = valuation_result.get('margin_of_safety', 0)
            if mos < -40:
                flags.append({
                    'flag': 'Significant Overvaluation',
                    'detail': f'Overvalued by {abs(mos):.1f}%',
                    'severity': 'high',
                })

        # 5. High beta
        if company and company.beta and company.beta > 1.5:
            flags.append({
                'flag': 'High Volatility',
                'detail': f'Beta: {company.beta:.2f}',
                'severity': 'moderate',
            })

        # 6. Declining margins
        if len(financials) >= 3:
            recent_margins = []
            for f in financials[-3:]:
                if f.revenue and f.revenue > 0 and f.gross_profit:
                    recent_margins.append(f.gross_profit / f.revenue)
            if len(recent_margins) >= 2 and recent_margins[-1] < recent_margins[0] * 0.9:
                flags.append({
                    'flag': 'Margin Compression',
                    'detail': 'Gross margins declining over recent years',
                    'severity': 'moderate',
                })

        # Determine overall risk level
        high_count = sum(1 for f in flags if f['severity'] == 'high')
        mod_count = sum(1 for f in flags if f['severity'] == 'moderate')

        if high_count >= 2 or (high_count >= 1 and mod_count >= 2):
            level = 'High'
        elif high_count >= 1 or mod_count >= 2:
            level = 'Moderate'
        else:
            level = 'Low'

        return {
            'level': level,
            'flags': flags,
            'flag_count': len(flags),
            'error': None,
        }
