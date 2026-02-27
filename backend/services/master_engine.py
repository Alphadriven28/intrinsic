"""
Master Engine — Composite Investment Rating.
Combines valuation upside, quality, moat, and confidence
into a single institutional-grade investment score.
"""


class MasterEngine:
    """Produces the final composite investment rating."""

    # Weight allocation for final score
    UPSIDE_WEIGHT = 0.40
    QUALITY_WEIGHT = 0.20
    MOAT_WEIGHT = 0.20
    CONFIDENCE_WEIGHT = 0.20

    # Rating thresholds
    RATINGS = [
        (80, 'Strong Buy'),
        (65, 'Buy'),
        (50, 'Hold'),
        (35, 'Weak'),
        (0, 'Avoid'),
    ]

    def run(self, weighting_result, quality_score_100, moat_result, confidence_result, current_price):
        """
        Compute the composite investment score and rating.

        Args:
            weighting_result: output from WeightingEngine
            quality_score_100: 0–100 quality score
            moat_result: output from MoatEngine
            confidence_result: output from ConfidenceEngine
            current_price: current stock price

        Returns:
            dict with investment_score, rating, breakdown
        """
        # 1. Valuation Upside Score (0–100)
        weighted_iv = weighting_result.get('weighted_intrinsic_value', 0)
        upside_score = self._upside_to_score(weighted_iv, current_price)

        # 2. Quality Score (already 0–100)
        quality = quality_score_100 if quality_score_100 is not None else 50

        # 3. Moat Score (already 0–100)
        moat = moat_result.get('score', 50) if moat_result and not moat_result.get('error') else 50

        # 4. Confidence Score (already 0–100)
        confidence = confidence_result.get('score', 50) if confidence_result and not confidence_result.get('error') else 50

        # Composite score
        investment_score = (
            upside_score * self.UPSIDE_WEIGHT +
            quality * self.QUALITY_WEIGHT +
            moat * self.MOAT_WEIGHT +
            confidence * self.CONFIDENCE_WEIGHT
        )
        investment_score = max(0, min(100, round(investment_score)))

        # Rating
        rating = 'Hold'
        for threshold, label in self.RATINGS:
            if investment_score >= threshold:
                rating = label
                break

        # Upside percentage
        upside_pct = ((weighted_iv - current_price) / current_price * 100) if current_price > 0 else 0

        return {
            'investment_score': investment_score,
            'rating': rating,
            'upside_pct': round(upside_pct, 1),
            'breakdown': {
                'valuation_upside': {
                    'score': round(upside_score, 1),
                    'weight': round(self.UPSIDE_WEIGHT * 100),
                    'weighted': round(upside_score * self.UPSIDE_WEIGHT, 1),
                },
                'quality': {
                    'score': round(quality, 1),
                    'weight': round(self.QUALITY_WEIGHT * 100),
                    'weighted': round(quality * self.QUALITY_WEIGHT, 1),
                },
                'moat': {
                    'score': round(moat, 1),
                    'weight': round(self.MOAT_WEIGHT * 100),
                    'weighted': round(moat * self.MOAT_WEIGHT, 1),
                },
                'confidence': {
                    'score': round(confidence, 1),
                    'weight': round(self.CONFIDENCE_WEIGHT * 100),
                    'weighted': round(confidence * self.CONFIDENCE_WEIGHT, 1),
                },
            },
            'error': None,
        }

    @staticmethod
    def _upside_to_score(intrinsic_value, current_price):
        """Convert upside/downside % into a 0–100 score."""
        if current_price <= 0 or intrinsic_value <= 0:
            return 30

        upside = ((intrinsic_value - current_price) / current_price) * 100

        # Map upside to score:
        #   +50% upside → 100
        #   +25% → 80
        #   0%   → 50
        #  -25%  → 20
        #  -50%  → 0
        score = 50 + upside * 1.0  # 1:1 mapping offset by 50
        return max(0, min(100, score))
