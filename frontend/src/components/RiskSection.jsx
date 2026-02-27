export default function RiskSection({ risk }) {
    if (!risk || risk.error) return null;

    const badgeClass = risk.level === 'Low'
        ? 'risk-badge--low'
        : risk.level === 'High'
            ? 'risk-badge--high'
            : 'risk-badge--moderate';

    const severityIcon = (severity) => {
        if (severity === 'high') return '⬤';
        if (severity === 'moderate') return '◐';
        return '○';
    };

    const severityColor = (severity) => {
        if (severity === 'high') return 'var(--color-accent-red)';
        if (severity === 'moderate') return 'var(--color-accent-amber)';
        return 'var(--color-text-tertiary)';
    };

    return (
        <div className="risk-section">
            <div className="risk-section__header">
                <h2 className="risk-section__title">Risk Assessment</h2>
                <span className={`risk-badge ${badgeClass}`}>{risk.level} Risk</span>
            </div>

            {risk.flags && risk.flags.length > 0 ? (
                <div className="risk-flags">
                    {risk.flags.map((flag, i) => (
                        <div className="risk-flag" key={i}>
                            <span className="risk-flag__icon" style={{ color: severityColor(flag.severity) }}>
                                {severityIcon(flag.severity)}
                            </span>
                            <div>
                                <div className="risk-flag__text">{flag.flag}</div>
                                <div className="risk-flag__detail">{flag.detail}</div>
                            </div>
                        </div>
                    ))}
                </div>
            ) : (
                <p className="risk-none">No material risk flags identified.</p>
            )}
        </div>
    );
}
