export default function ValuationCard({ valuation }) {
    if (!valuation || valuation.error) {
        return (
            <div className="card">
                <h2 className="card__title">Valuation</h2>
                <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-tertiary)' }}>
                    {valuation?.error || 'Valuation data unavailable'}
                </p>
            </div>
        );
    }

    const statusClass = valuation.status === 'Undervalued'
        ? 'valuation-status--undervalued'
        : valuation.status === 'Overvalued'
            ? 'valuation-status--overvalued'
            : 'valuation-status--fair';

    const formatPct = (val) => val != null ? `${val > 0 ? '+' : ''}${val}%` : '—';

    return (
        <div className="card">
            <h2 className="card__title">Valuation</h2>

            <span className={`valuation-status ${statusClass}`}>
                {valuation.status}
            </span>

            <div className="valuation-detail">
                <span className="valuation-detail__label">Intrinsic Value</span>
                <span className="valuation-detail__value">${valuation.intrinsic_value?.toLocaleString()}</span>
            </div>

            <div className="valuation-detail">
                <span className="valuation-detail__label">Current Price</span>
                <span className="valuation-detail__value">${valuation.current_price?.toLocaleString()}</span>
            </div>

            <div className="valuation-detail">
                <span className="valuation-detail__label">Margin of Safety</span>
                <span className="valuation-detail__value">{formatPct(valuation.margin_of_safety)}</span>
            </div>

            <div className="valuation-detail">
                <span className="valuation-detail__label">Upside / Downside</span>
                <span className="valuation-detail__value">{formatPct(valuation.upside_downside)}</span>
            </div>

            <div className="valuation-detail">
                <span className="valuation-detail__label">WACC</span>
                <span className="valuation-detail__value">{valuation.wacc}%</span>
            </div>

            <div className="valuation-detail">
                <span className="valuation-detail__label">Forward Growth</span>
                <span className="valuation-detail__value">{valuation.forward_growth_rate}%</span>
            </div>

            <div className="valuation-detail">
                <span className="valuation-detail__label">Revenue CAGR (5Y)</span>
                <span className="valuation-detail__value">{valuation.revenue_cagr != null ? `${valuation.revenue_cagr}%` : '—'}</span>
            </div>
        </div>
    );
}
