export default function GrowthQualityCard({ scores }) {
    if (!scores || scores.error) {
        return (
            <div className="card">
                <h2 className="card__title">Growth & Quality</h2>
                <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-tertiary)' }}>
                    Scoring data unavailable
                </p>
            </div>
        );
    }

    const getBarClass = (score) => {
        if (score >= 7) return 'score-bar__fill--high';
        if (score >= 4) return 'score-bar__fill--mid';
        return 'score-bar__fill--low';
    };

    const componentLabels = {
        revenue_cagr: 'Revenue CAGR',
        roic: 'Return on Capital',
        fcf_consistency: 'FCF Consistency',
        debt_safety: 'Debt Safety',
        gross_margin: 'Gross Margin',
    };

    return (
        <div className="card">
            <h2 className="card__title">Growth & Quality</h2>

            <div className="score-block">
                <div className="score-block__header">
                    <span className="score-block__name">Growth Score</span>
                    <span className="score-block__value" style={{ color: scores.growth_score >= 7 ? 'var(--color-accent-green)' : scores.growth_score >= 4 ? 'var(--color-accent-amber)' : 'var(--color-accent-red)' }}>
                        {scores.growth_score}/10
                    </span>
                </div>
                <div className="score-bar">
                    <div
                        className={`score-bar__fill ${getBarClass(scores.growth_score)}`}
                        style={{ width: `${scores.growth_score * 10}%` }}
                    />
                </div>
            </div>

            <div className="score-block">
                <div className="score-block__header">
                    <span className="score-block__name">Quality Score</span>
                    <span className="score-block__value" style={{ color: scores.quality_score >= 7 ? 'var(--color-accent-green)' : scores.quality_score >= 4 ? 'var(--color-accent-amber)' : 'var(--color-accent-red)' }}>
                        {scores.quality_score}/10
                    </span>
                </div>
                <div className="score-bar">
                    <div
                        className={`score-bar__fill ${getBarClass(scores.quality_score)}`}
                        style={{ width: `${scores.quality_score * 10}%` }}
                    />
                </div>
            </div>

            {scores.components && (
                <div className="score-components">
                    {Object.entries(scores.components).map(([key, val]) => (
                        <div className="score-component" key={key}>
                            <span className="score-component__name">{componentLabels[key] || key}</span>
                            <span className="score-component__value">{val}/10</span>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
