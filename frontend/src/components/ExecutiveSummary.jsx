export default function ExecutiveSummary({ summary }) {
    if (!summary) return null;

    const sections = [
        { key: 'valuation_verdict', heading: 'Valuation Verdict' },
        { key: 'growth_outlook', heading: 'Growth Outlook' },
        { key: 'financial_strength', heading: 'Financial Strength' },
        { key: 'risk_assessment', heading: 'Risk Assessment' },
        { key: 'investment_attractiveness', heading: 'Investment Attractiveness' },
    ];

    return (
        <div className="summary-section">
            <h2 className="summary-section__title">Executive Summary</h2>

            {sections.map(({ key, heading }) => (
                summary[key] ? (
                    <div className="summary-item" key={key}>
                        <h3 className="summary-item__heading">{heading}</h3>
                        <p className="summary-item__text">{summary[key]}</p>
                    </div>
                ) : null
            ))}
        </div>
    );
}
