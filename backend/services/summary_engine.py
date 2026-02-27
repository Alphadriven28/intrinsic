"""
Executive Summary Generator — Professional structured summary.
Updated for multi-model valuation intelligence system.
"""


class SummaryEngine:
    """Generates institutional-tone executive summary from analysis results."""

    def run(self, company_name, ticker, valuation, scores, risk, sector,
            weighting=None, confidence=None, moat=None, master=None):
        """Generate structured executive summary."""
        sections = {}

        # 1. Valuation Verdict
        sections['valuation_verdict'] = self._valuation_verdict(
            company_name, valuation, weighting
        )

        # 2. Growth Outlook
        sections['growth_outlook'] = self._growth_outlook(
            company_name, scores, valuation
        )

        # 3. Financial Strength
        sections['financial_strength'] = self._financial_strength(
            company_name, scores, confidence
        )

        # 4. Risk Assessment
        sections['risk_assessment'] = self._risk_assessment(
            company_name, risk
        )

        # 5. Investment Attractiveness
        sections['investment_attractiveness'] = self._investment_attractiveness(
            company_name, valuation, scores, risk, master, moat
        )

        return sections

    def _valuation_verdict(self, name, valuation, weighting=None):
        if not valuation or valuation.get('error'):
            return f"Valuation data is currently unavailable for {name}."

        # Use weighted IV if available, else DCF
        if weighting and not weighting.get('error') and weighting.get('weighted_intrinsic_value', 0) > 0:
            iv = weighting['weighted_intrinsic_value']
            model_count = len(weighting.get('weights', {}))
            method = f"weighted consensus of {model_count} valuation models"
            company_type = weighting.get('company_type_label', 'standard')
        else:
            iv = valuation.get('intrinsic_value', 0)
            method = "discounted cash flow analysis"
            company_type = None

        price = valuation.get('current_price', 0)

        if price <= 0 or iv <= 0:
            return f"Valuation data for {name} is currently limited."

        mos = ((iv - price) / iv) * 100
        upside = ((iv - price) / price) * 100

        type_note = f" Classified as a {company_type} company." if company_type else ""

        if upside > 10:
            return (
                f"{name} appears undervalued based on our {method}. "
                f"The estimated intrinsic value of ${iv:,.2f} represents a "
                f"{mos:.1f}% margin of safety relative to the current price of ${price:,.2f}, "
                f"suggesting {upside:.0f}% potential upside.{type_note}"
            )
        elif upside < -10:
            return (
                f"{name} appears overvalued based on our {method}. "
                f"The current price of ${price:,.2f} exceeds our estimated intrinsic value of "
                f"${iv:,.2f}, implying the stock trades at a {abs(mos):.1f}% premium to fair value. "
                f"Investors should exercise caution at current levels.{type_note}"
            )
        else:
            return (
                f"{name} appears fairly valued. The current price of ${price:,.2f} is "
                f"broadly in line with our estimated intrinsic value of ${iv:,.2f} "
                f"based on our {method}.{type_note}"
            )

    def _growth_outlook(self, name, scores, valuation):
        if not scores or scores.get('error'):
            return f"Growth assessment for {name} is limited due to insufficient data."

        gs = scores.get('growth_score', 5)
        rev_cagr = valuation.get('revenue_cagr') if valuation else None
        fwd = valuation.get('forward_growth_rate') if valuation else None

        if gs >= 7.5:
            outlook = "strong"
            detail = "The company has demonstrated robust revenue growth and operational efficiency."
        elif gs >= 5.0:
            outlook = "moderate"
            detail = "The company exhibits steady growth characteristics with room for improvement."
        else:
            outlook = "limited"
            detail = "Growth has been constrained, warranting careful monitoring of strategic direction."

        text = f"{name} presents a {outlook} growth profile with a score of {gs}/10. {detail}"

        if rev_cagr is not None:
            text += f" Historical 5-year revenue CAGR stands at {rev_cagr}%."
        if fwd is not None:
            text += f" Our forward growth estimate is {fwd}%."

        return text

    def _financial_strength(self, name, scores, confidence=None):
        if not scores or scores.get('error'):
            return f"Financial strength data for {name} is currently limited."

        qs = scores.get('quality_score', 5)
        q100 = scores.get('quality_score_100', None)
        components = scores.get('components', {})

        if qs >= 7.5:
            strength = "robust"
        elif qs >= 5.0:
            strength = "adequate"
        else:
            strength = "a concern"

        text = f"{name} demonstrates {strength} financial fundamentals with a quality score of {qs}/10"

        if q100 is not None:
            text += f" ({q100}/100 on expanded metrics)"
        text += "."

        debt = components.get('debt_safety', 5)
        fcf = components.get('fcf_consistency', 5)

        if debt >= 7:
            text += " The balance sheet is conservatively managed with low leverage."
        elif debt < 4:
            text += " Elevated debt levels require monitoring."

        if fcf >= 8:
            text += " Free cash flow generation has been highly consistent."
        elif fcf < 5:
            text += " Free cash flow consistency has been intermittent."

        if confidence and not confidence.get('error'):
            conf_score = confidence.get('score', 0)
            text += f" Our valuation confidence score stands at {conf_score}/100 ({confidence.get('badge', 'N/A')})."

        return text

    def _risk_assessment(self, name, risk):
        if not risk or risk.get('error'):
            return f"Risk data for {name} is currently unavailable."

        level = risk.get('level', 'Moderate')
        flags = risk.get('flags', [])

        text = f"Overall risk for {name} is assessed as {level}."

        if flags:
            issues = [f['flag'] for f in flags]
            text += f" Key risk factors include: {', '.join(issues)}."
        else:
            text += " No material risk flags have been identified at this time."

        return text

    def _investment_attractiveness(self, name, valuation, scores, risk, master=None, moat=None):
        if master and not master.get('error'):
            score = master.get('investment_score', 0)
            rating = master.get('rating', 'Hold')
            upside = master.get('upside_pct', 0)

            moat_text = ""
            if moat and not moat.get('error'):
                moat_text = f" Competitive position classified as {moat.get('classification', 'N/A')} (moat score {moat.get('score', 0)}/100)."

            if rating in ('Strong Buy', 'Buy'):
                return (
                    f"{name} receives a composite investment score of {score}/100, "
                    f"earning a \"{rating}\" rating with {upside:+.1f}% implied upside.{moat_text} "
                    f"The combination of favorable valuation, business quality, and competitive positioning "
                    f"supports a constructive thesis."
                )
            elif rating == 'Hold':
                return (
                    f"{name} scores {score}/100 on our composite framework, translating to a "
                    f"\"{rating}\" rating.{moat_text} While the business shows solid fundamentals, "
                    f"current valuation limits near-term return potential."
                )
            else:
                return (
                    f"{name} scores {score}/100 on our composite framework, resulting in a "
                    f"\"{rating}\" rating.{moat_text} Investors should exercise caution given "
                    f"the current risk-reward profile."
                )

        # Fallback if master engine didn't run
        val_ok = (valuation and not valuation.get('error')
                  and valuation.get('margin_of_safety', 0) > 0)
        growth_ok = scores and scores.get('growth_score', 0) >= 6
        quality_ok = scores and scores.get('quality_score', 0) >= 6
        risk_ok = risk and risk.get('level') != 'High'

        positives = sum([val_ok, growth_ok, quality_ok, risk_ok])

        if positives >= 3:
            return (
                f"{name} presents an attractive long-term investment profile. "
                f"The combination of {'favorable valuation, ' if val_ok else ''}"
                f"{'solid growth prospects, ' if growth_ok else ''}"
                f"{'strong financial quality, ' if quality_ok else ''}"
                f"{'and manageable risk ' if risk_ok else ''}"
                f"supports a constructive thesis."
            )
        elif positives >= 2:
            return (
                f"{name} presents a mixed investment profile. While certain fundamentals "
                f"are encouraging, investors should weigh the identified weaknesses "
                f"before establishing a position."
            )
        else:
            return (
                f"{name} presents a challenging investment case at current levels. "
                f"Multiple fundamental concerns suggest caution is warranted. "
                f"Further improvement in key metrics would be needed to justify investment."
            )
