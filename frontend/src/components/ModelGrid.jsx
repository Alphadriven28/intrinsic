const MODEL_META = {
    dcf: { name: 'DCF', desc: 'Discounted Cash Flow' },
    relative: { name: 'Relative', desc: 'P/E, P/B, EV/EBITDA' },
    ddm: { name: 'DDM', desc: 'Dividend Discount' },
    residual_income: { name: 'Residual Income', desc: 'Excess Return' },
    asset_based: { name: 'Asset-Based', desc: 'Net Asset Value' },
    epv: { name: 'EPV', desc: 'Earnings Power' },
    graham: { name: 'Graham', desc: 'Graham Formula' },
    sotp: { name: 'SOTP', desc: 'Sum of Parts' },
    eva: { name: 'EVA', desc: 'Economic Value Added' },
};

export default function ModelGrid({ models, weighting, currentPrice }) {
    if (!models) return null;

    const weights = weighting?.weights || {};
    const formatPrice = (val) => {
        if (val == null) return '—';
        return `$${Number(val).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    };

    // Filter to valid models
    const entries = Object.entries(models)
        .filter(([, m]) => m.value && m.value > 0 && !m.error)
        .sort((a, b) => (weights[b[0]] || 0) - (weights[a[0]] || 0));

    const errorModels = Object.entries(models)
        .filter(([, m]) => m.error || !m.value || m.value <= 0);

    return (
        <div className="model-grid-section">
            <h3 className="section-title">9-Model Valuation Grid</h3>
            <div className="model-grid">
                {entries.map(([key, model]) => {
                    const meta = MODEL_META[key] || { name: key, desc: '' };
                    const weight = weights[key];
                    const upside = currentPrice > 0 ? ((model.value - currentPrice) / currentPrice * 100) : 0;
                    const isUnder = upside >= 0;

                    return (
                        <div className={`model-tile ${isUnder ? 'model-tile--under' : 'model-tile--over'}`} key={key}>
                            <div className="model-tile__header">
                                <span className="model-tile__name">{meta.name}</span>
                                {weight != null && (
                                    <span className="model-tile__weight">{weight}%</span>
                                )}
                            </div>
                            <div className="model-tile__desc">{meta.desc}</div>
                            <div className="model-tile__value">{formatPrice(model.value)}</div>
                            <div className={`model-tile__upside ${isUnder ? 'text-green' : 'text-red'}`}>
                                {isUnder ? '+' : ''}{upside.toFixed(1)}%
                            </div>
                        </div>
                    );
                })}
            </div>
            {errorModels.length > 0 && (
                <div className="model-grid__excluded">
                    <span className="model-grid__excluded-label">Excluded models: </span>
                    {errorModels.map(([key, m]) => (
                        <span className="model-grid__excluded-item" key={key}>
                            {MODEL_META[key]?.name || key}
                            <span className="model-grid__excluded-reason"> ({m.error || 'N/A'})</span>
                        </span>
                    ))}
                </div>
            )}
        </div>
    );
}
