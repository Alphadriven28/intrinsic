export default function CompanyHeader({ company, valuation, weighting }) {
    if (!company) return null;

    const formatPrice = (val) => {
        if (val == null) return '—';
        return `$${Number(val).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    };

    const formatMarketCap = (val) => {
        if (!val) return '—';
        if (val >= 1e12) return `$${(val / 1e12).toFixed(2)}T`;
        if (val >= 1e9) return `$${(val / 1e9).toFixed(1)}B`;
        if (val >= 1e6) return `$${(val / 1e6).toFixed(0)}M`;
        return `$${val.toLocaleString()}`;
    };

    // Use weighted IV if available
    const weightedIV = weighting?.weighted_intrinsic_value;
    const displayIV = weightedIV && weightedIV > 0 ? weightedIV : valuation?.intrinsic_value;
    const mos = displayIV && displayIV > 0 ? ((displayIV - company.price) / displayIV * 100) : null;

    const mosClass = mos > 0 ? 'metric-item__value--green'
        : mos < -20 ? 'metric-item__value--red'
            : 'metric-item__value--amber';

    return (
        <div className="company-header">
            <div className="company-header__top">
                <h1 className="company-header__name">{company.name}</h1>
                <span className="company-header__ticker">{company.ticker}</span>
                {company.exchange && (
                    <span className="company-header__exchange">{company.exchange}</span>
                )}
            </div>

            <div className="company-header__metrics">
                <div className="metric-item">
                    <span className="metric-item__label">Current Price</span>
                    <span className="metric-item__value">{formatPrice(company.price)}</span>
                </div>

                <div className="metric-item">
                    <span className="metric-item__label">Weighted Intrinsic Value</span>
                    <span className={`metric-item__value ${mosClass}`}>
                        {valuation?.error ? '—' : formatPrice(displayIV)}
                    </span>
                </div>

                <div className="metric-item">
                    <span className="metric-item__label">Margin of Safety</span>
                    <span className={`metric-item__value ${mosClass}`}>
                        {mos != null ? `${mos > 0 ? '+' : ''}${mos.toFixed(1)}%` : '—'}
                    </span>
                </div>

                <div className="metric-item">
                    <span className="metric-item__label">Market Cap</span>
                    <span className="metric-item__value">{formatMarketCap(company.market_cap)}</span>
                </div>

                <div className="metric-item">
                    <span className="metric-item__label">Sector</span>
                    <span className="metric-item__value" style={{ fontSize: 'var(--font-size-base)' }}>
                        {company.sector || '—'}
                    </span>
                </div>

                <div className="metric-item">
                    <span className="metric-item__label">Beta</span>
                    <span className="metric-item__value">{company.beta?.toFixed(2) || '—'}</span>
                </div>
            </div>
        </div>
    );
}
