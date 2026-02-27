function ScoreRing({ score, max, color, label, badge, badgeClass }) {
    const pct = Math.min(score / max * 100, 100);
    const deg = pct * 3.6;

    return (
        <div className="score-ring-card">
            <div className="score-ring" style={{
                background: `conic-gradient(${color} ${deg}deg, var(--color-border-light) ${deg}deg)`
            }}>
                <div className="score-ring__inner">
                    <span className="score-ring__value">{score}</span>
                    <span className="score-ring__max">/{max}</span>
                </div>
            </div>
            <div className="score-ring__label">{label}</div>
            {badge && <span className={`score-ring__badge ${badgeClass}`}>{badge}</span>}
        </div>
    );
}

function ComponentBreakdown({ components, title }) {
    if (!components) return null;

    const LABELS = {
        earnings_stability: 'Earnings Stability',
        cash_flow_quality: 'Cash Flow Quality',
        balance_sheet: 'Balance Sheet',
        return_metrics: 'Return Metrics',
        growth_visibility: 'Growth Visibility',
        model_agreement: 'Model Agreement',
        gross_margin_stability: 'Gross Margin',
        roic_spread: 'ROIC Spread',
        growth_vs_industry: 'Growth vs Industry',
        intangible_intensity: 'Intangible Intensity',
        brand_proxy: 'Brand Power',
        operating_leverage: 'Op. Leverage',
        roe_consistency: 'ROE Consistency',
        fcf_consistency: 'FCF Consistency',
        debt_levels: 'Debt Levels',
        margin_expansion: 'Margin Expansion',
        earnings_predictability: 'Earnings Predict.',
        capex_discipline: 'CapEx Discipline',
        share_dilution: 'Share Dilution',
    };

    return (
        <div className="component-breakdown">
            {Object.entries(components).map(([key, comp]) => {
                const pct = comp.max > 0 ? (comp.score / comp.max * 100) : 0;
                return (
                    <div className="component-row" key={key}>
                        <span className="component-row__name">{LABELS[key] || key}</span>
                        <div className="component-row__bar-wrap">
                            <div className="component-row__bar" style={{ width: `${pct}%` }} />
                        </div>
                        <span className="component-row__val">{comp.score}/{comp.max}</span>
                    </div>
                );
            })}
        </div>
    );
}

export default function IntelligenceScores({ confidence, moat, scores }) {
    const q100 = scores?.quality_score_100;
    const qualityComponents = scores?.quality_components;

    const confColor = confidence?.badge === 'High' ? 'var(--color-accent-green)'
        : confidence?.badge === 'Moderate' ? 'var(--color-accent-amber)' : 'var(--color-accent-red)';
    const confBadgeClass = confidence?.badge === 'High' ? 'badge--green'
        : confidence?.badge === 'Moderate' ? 'badge--amber' : 'badge--red';

    const moatColor = moat?.classification === 'Wide Moat' ? 'var(--color-accent-green)'
        : moat?.classification === 'Narrow Moat' ? 'var(--color-accent-amber)' : 'var(--color-accent-red)';
    const moatBadgeClass = moat?.classification === 'Wide Moat' ? 'badge--green'
        : moat?.classification === 'Narrow Moat' ? 'badge--amber' : 'badge--red';

    const qualColor = q100 >= 70 ? 'var(--color-accent-green)'
        : q100 >= 45 ? 'var(--color-accent-amber)' : 'var(--color-accent-red)';
    const qualBadgeClass = q100 >= 70 ? 'badge--green'
        : q100 >= 45 ? 'badge--amber' : 'badge--red';
    const qualBadge = q100 >= 70 ? 'High Quality' : q100 >= 45 ? 'Moderate' : 'Low Quality';

    return (
        <div className="intelligence-section">
            <h3 className="section-title">Intelligence Scores</h3>
            <div className="intelligence-grid">
                {/* Confidence Score */}
                <div className="intelligence-panel">
                    <ScoreRing
                        score={confidence?.score ?? 0}
                        max={100}
                        color={confColor}
                        label="Valuation Confidence"
                        badge={confidence?.badge}
                        badgeClass={confBadgeClass}
                    />
                    <ComponentBreakdown components={confidence?.components} title="Confidence" />
                </div>

                {/* Moat Score */}
                <div className="intelligence-panel">
                    <ScoreRing
                        score={moat?.score ?? 0}
                        max={100}
                        color={moatColor}
                        label="Competitive Moat"
                        badge={moat?.classification}
                        badgeClass={moatBadgeClass}
                    />
                    <ComponentBreakdown components={moat?.components} title="Moat" />
                </div>

                {/* Quality Score */}
                <div className="intelligence-panel">
                    <ScoreRing
                        score={q100 ?? 0}
                        max={100}
                        color={qualColor}
                        label="Business Quality"
                        badge={qualBadge}
                        badgeClass={qualBadgeClass}
                    />
                    <ComponentBreakdown components={qualityComponents} title="Quality" />
                </div>
            </div>
        </div>
    );
}
