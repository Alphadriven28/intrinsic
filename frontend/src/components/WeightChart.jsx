export default function WeightChart({ weighting }) {
    if (!weighting || weighting.error || !weighting.contributions) return null;

    const contributions = Object.values(weighting.contributions)
        .sort((a, b) => b.weight - a.weight);

    if (contributions.length === 0) return null;

    const maxWeight = Math.max(...contributions.map(c => c.weight));

    const formatPrice = (val) => {
        if (val == null) return '—';
        return `$${Number(val).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    };

    return (
        <div className="weight-section">
            <h3 className="section-title">Model Weight Distribution</h3>
            <div className="weight-chart">
                {contributions.map((c) => (
                    <div className="weight-row" key={c.name}>
                        <div className="weight-row__label">
                            <span className="weight-row__name">{c.name}</span>
                            <span className="weight-row__pct">{c.weight}%</span>
                        </div>
                        <div className="weight-row__bar-wrap">
                            <div
                                className="weight-row__bar"
                                style={{ width: `${(c.weight / maxWeight) * 100}%` }}
                            />
                        </div>
                        <div className="weight-row__detail">
                            <span className="weight-row__iv">{formatPrice(c.value)}</span>
                            <span className="weight-row__contribution">
                                → {formatPrice(c.contribution)}
                            </span>
                        </div>
                    </div>
                ))}
            </div>
            <div className="weight-total">
                <span className="weight-total__label">Weighted Intrinsic Value</span>
                <span className="weight-total__value">
                    {formatPrice(weighting.weighted_intrinsic_value)}
                </span>
            </div>
        </div>
    );
}
