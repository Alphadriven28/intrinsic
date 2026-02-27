"""
Valuation Engine — Multi-model intrinsic value calculator.
Implements 9 institutional-grade valuation methodologies.
All calculations are internal; FMP's built-in DCF is NOT used.
"""
import statistics
from config import Config
from models.models import db, Financial, Company, SectorData, Ratio


class ValuationEngine:
    """Performs multi-model valuation and returns individual + combined results."""

    def __init__(self):
        self.risk_free = Config.RISK_FREE_RATE
        self.erp = Config.EQUITY_RISK_PREMIUM
        self.terminal_growth = Config.TERMINAL_GROWTH_RATE
        self.projection_years = Config.PROJECTION_YEARS
        self.tax_rate = Config.CORPORATE_TAX_RATE

    def run(self, ticker, current_price):
        """Execute all valuation models. Returns dict with all results."""
        ticker = ticker.upper()

        financials = (
            Financial.query
            .filter_by(ticker=ticker)
            .order_by(Financial.year.asc())
            .all()
        )
        if len(financials) < 3:
            return self._error("Insufficient financial history")

        company = Company.query.filter_by(ticker=ticker).first()
        if not company:
            return self._error("Company not found")

        ratios = (
            Ratio.query
            .filter_by(ticker=ticker)
            .order_by(Ratio.year.asc())
            .all()
        )

        sector = SectorData.query.filter_by(sector=company.sector).first()

        beta = company.beta if company.beta and company.beta > 0 else 1.0
        cost_of_equity = self.risk_free + beta * self.erp
        cost_of_equity = max(0.06, min(cost_of_equity, 0.20))
        wacc = cost_of_equity  # Simplified WACC = cost of equity

        shares = company.shares_outstanding
        if not shares or shares <= 0:
            shares = financials[-1].shares_outstanding if financials[-1].shares_outstanding else 1

        # ------ Run all 9 models ------
        models = {}
        models['dcf'] = self._dcf(financials, company, sector, current_price, wacc, shares)
        models['relative'] = self._relative(ratios, sector, current_price, shares, financials)
        models['ddm'] = self._ddm(financials, cost_of_equity, shares)
        models['residual_income'] = self._residual_income(financials, cost_of_equity, shares)
        models['asset_based'] = self._asset_based(financials, shares)
        models['epv'] = self._epv(financials, wacc, shares)
        models['graham'] = self._graham(financials, shares)
        models['sotp'] = self._sotp(financials, ratios, sector, wacc, shares)
        models['eva'] = self._eva(financials, wacc, shares)

        # Collect valid model values
        valid_models = {k: v for k, v in models.items() if v.get('value') and v['value'] > 0 and not v.get('error')}
        valid_values = [v['value'] for v in valid_models.values()]

        if not valid_values:
            return {
                'models': models,
                'intrinsic_value': 0,
                'current_price': round(current_price, 2),
                'simple_average': 0,
                'margin_of_safety': -100,
                'upside_downside': 0,
                'status': 'N/A',
                'wacc': round(wacc * 100, 2),
                'beta': beta,
                'model_count': 0,
                'error': 'No valid model results',
            }

        simple_avg = statistics.mean(valid_values)
        model_std = statistics.stdev(valid_values) if len(valid_values) > 1 else 0

        # Legacy fields for backward compatibility
        dcf_iv = models['dcf'].get('value', simple_avg) or simple_avg

        if dcf_iv > 0:
            margin_of_safety = ((dcf_iv - current_price) / dcf_iv) * 100
        else:
            margin_of_safety = -100

        if dcf_iv > current_price:
            status = "Undervalued"
        elif dcf_iv < current_price * 0.95:
            status = "Overvalued"
        else:
            status = "Fairly Valued"

        upside = ((dcf_iv - current_price) / current_price * 100) if current_price > 0 else 0

        # Revenue CAGR for display
        revenue_cagr = self._cagr([f.revenue for f in financials], years=5)
        fcf_cagr = self._cagr([f.free_cash_flow for f in financials], years=5)

        return {
            'models': models,
            'intrinsic_value': round(dcf_iv, 2),
            'current_price': round(current_price, 2),
            'simple_average': round(simple_avg, 2),
            'model_std': round(model_std, 2),
            'margin_of_safety': round(margin_of_safety, 1),
            'upside_downside': round(upside, 1),
            'status': status,
            'wacc': round(wacc * 100, 2),
            'forward_growth_rate': models['dcf'].get('details', {}).get('forward_growth', 0),
            'terminal_growth_rate': round(self.terminal_growth * 100, 2),
            'revenue_cagr': round(revenue_cagr * 100, 2) if revenue_cagr else None,
            'fcf_cagr': round(fcf_cagr * 100, 2) if fcf_cagr else None,
            'enterprise_value': models['dcf'].get('details', {}).get('enterprise_value', 0),
            'beta': beta,
            'model_count': len(valid_models),
            'error': None,
        }

    # ==================================================================
    # MODEL 1: DCF (Discounted Cash Flow)
    # ==================================================================
    def _dcf(self, financials, company, sector, current_price, wacc, shares):
        try:
            revenue_cagr = self._cagr([f.revenue for f in financials], years=5)
            fcf_cagr = self._cagr([f.free_cash_flow for f in financials], years=5)

            sector_growth = sector.avg_revenue_growth if sector else 0.08

            if revenue_cagr is not None and revenue_cagr > 0:
                forward_growth = min(revenue_cagr, sector_growth)
            else:
                forward_growth = sector_growth * 0.5

            forward_growth = max(0.01, min(forward_growth, 0.30))

            latest_fcf = financials[-1].free_cash_flow
            if not latest_fcf or latest_fcf <= 0:
                recent = [f.free_cash_flow for f in financials[-3:] if f.free_cash_flow and f.free_cash_flow > 0]
                latest_fcf = sum(recent) / len(recent) if recent else 0

            if not latest_fcf or latest_fcf <= 0:
                return {'value': None, 'error': 'No positive FCF', 'details': {}}

            projected_fcfs = []
            for i in range(1, self.projection_years + 1):
                projected = latest_fcf * ((1 + forward_growth) ** i)
                projected_fcfs.append(projected)

            if wacc <= self.terminal_growth:
                return {'value': None, 'error': 'WACC <= terminal growth', 'details': {}}

            terminal_fcf = projected_fcfs[-1] * (1 + self.terminal_growth)
            terminal_value = terminal_fcf / (wacc - self.terminal_growth)

            pv_fcfs = [fcf / ((1 + wacc) ** i) for i, fcf in enumerate(projected_fcfs, 1)]
            pv_terminal = terminal_value / ((1 + wacc) ** self.projection_years)

            enterprise_value = sum(pv_fcfs) + pv_terminal
            intrinsic_value = enterprise_value / shares if shares > 0 else 0

            return {
                'value': round(intrinsic_value, 2),
                'error': None,
                'details': {
                    'forward_growth': round(forward_growth * 100, 2),
                    'enterprise_value': round(enterprise_value, 0),
                    'projected_fcfs': [round(f, 0) for f in projected_fcfs],
                }
            }
        except Exception as e:
            return {'value': None, 'error': str(e), 'details': {}}

    # ==================================================================
    # MODEL 2: Relative Valuation (P/E, P/B, EV/EBITDA multiples)
    # ==================================================================
    def _relative(self, ratios, sector, current_price, shares, financials):
        try:
            if not ratios or not sector:
                return {'value': None, 'error': 'Insufficient ratio/sector data', 'details': {}}

            latest = ratios[-1]
            estimates = []
            breakdown = {}

            # P/E based
            if latest.pe_ratio and latest.pe_ratio > 0 and sector.avg_pe and sector.avg_pe > 0:
                latest_fin = financials[-1] if financials else None
                if latest_fin and latest_fin.net_income and latest_fin.net_income > 0 and shares > 0:
                    eps = latest_fin.net_income / shares
                    pe_fair = sector.avg_pe * eps
                    estimates.append(pe_fair)
                    breakdown['pe_based'] = round(pe_fair, 2)

            # P/B based
            if latest.pb_ratio and latest.pb_ratio > 0 and sector.avg_pb and sector.avg_pb > 0:
                latest_fin = financials[-1] if financials else None
                if latest_fin and latest_fin.total_equity and latest_fin.total_equity > 0 and shares > 0:
                    bvps = latest_fin.total_equity / shares
                    pb_fair = sector.avg_pb * bvps
                    estimates.append(pb_fair)
                    breakdown['pb_based'] = round(pb_fair, 2)

            # EV/EBITDA based
            if sector.avg_ev_ebitda and sector.avg_ev_ebitda > 0:
                latest_fin = financials[-1] if financials else None
                if latest_fin and latest_fin.ebitda and latest_fin.ebitda > 0 and shares > 0:
                    fair_ev = sector.avg_ev_ebitda * latest_fin.ebitda
                    debt = latest_fin.total_debt or 0
                    cash = latest_fin.cash_and_equivalents or 0
                    fair_equity = fair_ev - debt + cash
                    ev_ebitda_fair = fair_equity / shares if fair_equity > 0 else 0
                    if ev_ebitda_fair > 0:
                        estimates.append(ev_ebitda_fair)
                        breakdown['ev_ebitda_based'] = round(ev_ebitda_fair, 2)

            if not estimates:
                return {'value': None, 'error': 'No relative estimates available', 'details': {}}

            avg_value = statistics.mean(estimates)
            return {
                'value': round(avg_value, 2),
                'error': None,
                'details': breakdown,
            }
        except Exception as e:
            return {'value': None, 'error': str(e), 'details': {}}

    # ==================================================================
    # MODEL 3: DDM (Dividend Discount Model)
    # ==================================================================
    def _ddm(self, financials, cost_of_equity, shares):
        try:
            divs = [abs(f.dividends_paid) for f in financials
                    if f.dividends_paid and f.dividends_paid != 0]

            if len(divs) < 2:
                return {'value': None, 'error': 'Insufficient dividend history', 'details': {}}

            # Dividends per share for last year
            latest_div_total = divs[-1]
            dps = latest_div_total / shares if shares > 0 else 0

            if dps <= 0:
                return {'value': None, 'error': 'No dividends paid', 'details': {}}

            # Dividend growth rate
            div_growth = self._cagr(divs, years=min(5, len(divs) - 1))
            if div_growth is None or div_growth < 0:
                div_growth = Config.DDM_TERMINAL_GROWTH

            div_growth = min(div_growth, cost_of_equity - 0.01)

            if cost_of_equity <= div_growth:
                return {'value': None, 'error': 'Cost of equity <= dividend growth', 'details': {}}

            # Gordon Growth Model
            next_dps = dps * (1 + div_growth)
            value = next_dps / (cost_of_equity - div_growth)

            return {
                'value': round(value, 2),
                'error': None,
                'details': {
                    'dps': round(dps, 2),
                    'dividend_growth': round(div_growth * 100, 2),
                }
            }
        except Exception as e:
            return {'value': None, 'error': str(e), 'details': {}}

    # ==================================================================
    # MODEL 4: Residual Income Model
    # ==================================================================
    def _residual_income(self, financials, cost_of_equity, shares):
        try:
            recent = financials[-3:]
            equities = [f.total_equity for f in recent if f.total_equity and f.total_equity > 0]
            net_incomes = [f.net_income for f in recent if f.net_income is not None]

            if len(equities) < 2 or len(net_incomes) < 2:
                return {'value': None, 'error': 'Insufficient equity/income data', 'details': {}}

            # Book value per share
            bvps = equities[-1] / shares if shares > 0 else 0

            # Project residual income for 5 years
            total_ri_pv = 0
            avg_ni = statistics.mean(net_incomes[-3:])
            avg_eq = statistics.mean(equities[-2:])

            roe = avg_ni / avg_eq if avg_eq > 0 else 0

            eq = equities[-1]
            for i in range(1, self.projection_years + 1):
                ni = eq * roe
                equity_charge = eq * cost_of_equity
                residual = ni - equity_charge
                pv = residual / ((1 + cost_of_equity) ** i)
                total_ri_pv += pv
                eq = eq + ni * 0.5  # assume 50% retention

            value = (equities[-1] + total_ri_pv) / shares if shares > 0 else 0

            return {
                'value': round(max(value, 0), 2),
                'error': None,
                'details': {
                    'roe': round(roe * 100, 2),
                    'book_value_per_share': round(bvps, 2),
                }
            }
        except Exception as e:
            return {'value': None, 'error': str(e), 'details': {}}

    # ==================================================================
    # MODEL 5: Asset-Based Valuation
    # ==================================================================
    def _asset_based(self, financials, shares):
        try:
            latest = financials[-1]
            total_assets = latest.total_assets or 0
            total_liabilities = latest.total_liabilities or 0
            intangibles = (latest.intangible_assets or 0) + (latest.goodwill or 0)

            if total_assets <= 0:
                return {'value': None, 'error': 'No asset data', 'details': {}}

            # Net Asset Value (tangible)
            tangible_nav = total_assets - total_liabilities - intangibles
            nav_per_share = tangible_nav / shares if shares > 0 else 0

            # Total book value (including intangibles)
            total_nav = total_assets - total_liabilities
            total_nav_per_share = total_nav / shares if shares > 0 else 0

            # Use blend: 70% tangible NAV + 30% total book value
            value = nav_per_share * 0.7 + total_nav_per_share * 0.3

            return {
                'value': round(max(value, 0), 2),
                'error': None,
                'details': {
                    'tangible_nav': round(nav_per_share, 2),
                    'total_book_value': round(total_nav_per_share, 2),
                    'intangibles': round(intangibles / shares if shares > 0 else 0, 2),
                }
            }
        except Exception as e:
            return {'value': None, 'error': str(e), 'details': {}}

    # ==================================================================
    # MODEL 6: EPV (Earnings Power Value)
    # ==================================================================
    def _epv(self, financials, wacc, shares):
        try:
            # Use normalized operating income (average of last 3 years)
            op_incomes = [f.operating_income for f in financials[-3:]
                         if f.operating_income is not None]

            if not op_incomes:
                return {'value': None, 'error': 'No operating income data', 'details': {}}

            normalized_oi = statistics.mean(op_incomes)
            if normalized_oi <= 0:
                return {'value': None, 'error': 'Negative normalized operating income', 'details': {}}

            # After-tax earnings power
            nopat = normalized_oi * (1 - self.tax_rate)

            if wacc <= 0:
                return {'value': None, 'error': 'Invalid WACC', 'details': {}}

            # EPV = NOPAT / WACC (no growth assumed)
            epv_enterprise = nopat / wacc

            # Adjust: subtract debt, add cash
            latest = financials[-1]
            debt = latest.total_debt or 0
            cash = latest.cash_and_equivalents or 0
            epv_equity = epv_enterprise - debt + cash

            value = epv_equity / shares if shares > 0 else 0

            return {
                'value': round(max(value, 0), 2),
                'error': None,
                'details': {
                    'normalized_nopat': round(nopat, 0),
                    'epv_enterprise': round(epv_enterprise, 0),
                }
            }
        except Exception as e:
            return {'value': None, 'error': str(e), 'details': {}}

    # ==================================================================
    # MODEL 7: Graham Formula
    # ==================================================================
    def _graham(self, financials, shares):
        try:
            latest = financials[-1]
            ni = latest.net_income
            if not ni or ni <= 0 or shares <= 0:
                return {'value': None, 'error': 'Negative or zero earnings', 'details': {}}

            eps = ni / shares

            # Estimate growth rate from revenue CAGR
            rev_cagr = self._cagr([f.revenue for f in financials], years=5)
            growth = rev_cagr if rev_cagr and rev_cagr > 0 else 0.05
            growth = min(growth, 0.20)  # Cap at 20%
            growth_pct = growth * 100

            # Graham Formula: V = EPS × (8.5 + 2g) × 4.4 / Y
            no_growth_pe = Config.GRAHAM_NO_GROWTH_PE
            growth_mult = Config.GRAHAM_GROWTH_MULTIPLE
            aaa_yield = Config.GRAHAM_AAA_YIELD

            base_yield = 0.044  # Graham's original 4.4% AAA yield
            value = eps * (no_growth_pe + growth_mult * growth_pct) * (base_yield / aaa_yield)

            return {
                'value': round(max(value, 0), 2),
                'error': None,
                'details': {
                    'eps': round(eps, 2),
                    'growth_rate': round(growth_pct, 1),
                }
            }
        except Exception as e:
            return {'value': None, 'error': str(e), 'details': {}}

    # ==================================================================
    # MODEL 8: SOTP (Sum of the Parts) — proxy approach
    # ==================================================================
    def _sotp(self, financials, ratios, sector, wacc, shares):
        try:
            latest = financials[-1]
            if not latest.revenue or latest.revenue <= 0:
                return {'value': None, 'error': 'No revenue data', 'details': {}}

            # Proxy SOTP: value operating business + cash + excess assets
            # Operating value: use normalized EBITDA × sector EV/EBITDA
            ebitda_vals = [f.ebitda for f in financials[-3:] if f.ebitda and f.ebitda > 0]
            if not ebitda_vals:
                return {'value': None, 'error': 'No EBITDA data', 'details': {}}

            norm_ebitda = statistics.mean(ebitda_vals)
            ev_multiple = sector.avg_ev_ebitda if sector and sector.avg_ev_ebitda else 12.0

            operating_value = norm_ebitda * ev_multiple

            # Add cash, subtract debt
            cash = latest.cash_and_equivalents or 0
            debt = latest.total_debt or 0
            equity_value = operating_value - debt + cash

            value = equity_value / shares if shares > 0 else 0

            return {
                'value': round(max(value, 0), 2),
                'error': None,
                'details': {
                    'normalized_ebitda': round(norm_ebitda, 0),
                    'ev_multiple': ev_multiple,
                    'operating_value': round(operating_value, 0),
                }
            }
        except Exception as e:
            return {'value': None, 'error': str(e), 'details': {}}

    # ==================================================================
    # MODEL 9: EVA (Economic Value Added)
    # ==================================================================
    def _eva(self, financials, wacc, shares):
        try:
            recent = financials[-3:]
            op_incomes = [f.operating_income for f in recent if f.operating_income is not None]
            equities = [f.total_equity for f in recent if f.total_equity and f.total_equity > 0]
            debts = [f.total_debt for f in recent if f.total_debt is not None]

            if not op_incomes or not equities:
                return {'value': None, 'error': 'Insufficient data', 'details': {}}

            # NOPAT
            avg_oi = statistics.mean(op_incomes)
            nopat = avg_oi * (1 - self.tax_rate)

            # Invested capital = equity + debt
            avg_equity = statistics.mean(equities)
            avg_debt = statistics.mean(debts) if debts else 0
            invested_capital = avg_equity + avg_debt

            if invested_capital <= 0:
                return {'value': None, 'error': 'No invested capital', 'details': {}}

            # EVA = NOPAT - (WACC × Invested Capital)
            eva = nopat - (wacc * invested_capital)

            # ROIC
            roic = nopat / invested_capital if invested_capital > 0 else 0

            # Value = Invested Capital + PV of future EVAs (assume constant for 10 years)
            if wacc > 0:
                pv_eva = eva * (1 - (1 + wacc) ** -10) / wacc
            else:
                pv_eva = eva * 10

            total_value = invested_capital + pv_eva

            # Subtract debt, add cash for equity value
            latest = financials[-1]
            debt = latest.total_debt or 0
            cash = latest.cash_and_equivalents or 0
            equity_value = total_value - debt + cash

            value = equity_value / shares if shares > 0 else 0

            return {
                'value': round(max(value, 0), 2),
                'error': None,
                'details': {
                    'nopat': round(nopat, 0),
                    'invested_capital': round(invested_capital, 0),
                    'eva_annual': round(eva, 0),
                    'roic': round(roic * 100, 2),
                }
            }
        except Exception as e:
            return {'value': None, 'error': str(e), 'details': {}}

    # ==================================================================
    # Helpers
    # ==================================================================

    @staticmethod
    def _cagr(values, years=5):
        """Calculate compound annual growth rate over N years."""
        if not values or len(values) < 2:
            return None

        n = min(years, len(values) - 1)
        start = values[-(n + 1)]
        end = values[-1]

        if not start or not end or start <= 0 or end <= 0:
            return None

        return (end / start) ** (1 / n) - 1

    @staticmethod
    def _error(msg):
        return {'error': msg}
