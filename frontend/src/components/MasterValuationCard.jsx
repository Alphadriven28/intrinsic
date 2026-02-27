export default function MasterValuationCard({ valuation, weighting, master }) {
    if (!valuation || valuation.error) {
        return (
            <div className="master-card">
                <h2 className="master-card__title">Valuation Intelligence</h2>
                <p className="master-card__empty">Valuation data unavailable</p>
            </div>
        );
    }

    const weightedIV = weighting?.weighted_intrinsic_value;
    const currentPrice = valuation.current_price;
    const displayIV = weightedIV && weightedIV > 0 ? weightedIV : valuation.intrinsic_value;
    const upside = currentPrice > 0 ? ((displayIV - currentPrice) / currentPrice * 100) : 0;
    const mos = displayIV > 0 ? ((displayIV - currentPrice) / displayIV * 100) : 0;

    const rating = master?.rating || 'Hold';
    const ratingClass = {
        'Strong Buy': 'rating--strong-buy',
        'Buy': 'rating--buy',
        'Hold': 'rating--hold',
        'Weak': 'rating--weak',
        'Avoid': 'rating--avoid',
    }[rating] || 'rating--hold';

    const companyType = weighting?.company_type_label || '';
    const modelCount = valuation.model_count || 0;

    const formatPrice = (val) => {
        if (val == null) return '—';
        return `$${Number(val).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    };

    return (
        <div className="master-card">
            <div className="master-card__header">
                <div>
                    <h2 className="master-card__title">Valuation Intelligence</h2>
                    <div className="master-card__meta">
                        {companyType && <span className="master-card__type-badge">{companyType}</span>}
                        <span className="master-card__model-count">{modelCount} models</span>
                    </div>
                </div>
                <div className={`master-card__rating ${ratingClass}`}>
                    <span className="master-card__rating-label">Rating</span>
                    <span className="master-card__rating-value">{rating}</span>
                    {master?.investment_score != null && (
                        <span className="master-card__rating-score">{master.investment_score}/100</span>
                    )}
                </div>
            </div>

            <div className="master-card__values">
                <div className="master-card__value-block">
                    <span className="master-card__value-label">Current Price</span>
                    <span className="master-card__value-price">{formatPrice(currentPrice)}</span>
                </div>
                <div className="master-card__arrow">
                    {upside >= 0 ? '→' : '→'}
                </div>
                <div className="master-card__value-block master-card__value-block--primary">
                    <span className="master-card__value-label">Weighted Intrinsic Value</span>
                    <span className={`master-card__value-price ${upside >= 0 ? 'text-green' : 'text-red'}`}>
                        {formatPrice(displayIV)}
                    </span>
                </div>
                <div className="master-card__value-block">
                    <span className="master-card__value-label">Upside / Downside</span>
                    <span className={`master-card__value-pct ${upside >= 0 ? 'text-green' : 'text-red'}`}>
                        {upside >= 0 ? '+' : ''}{upside.toFixed(1)}%
                    </span>
                </div>
                <div className="master-card__value-block">
                    <span className="master-card__value-label">Margin of Safety</span>
                    <span className={`master-card__value-pct ${mos >= 0 ? 'text-green' : 'text-red'}`}>
                        {mos >= 0 ? '+' : ''}{mos.toFixed(1)}%
                    </span>
                </div>
            </div>
        </div>
    );
}
