export default function SectorCard({ sector }) {
    if (!sector || sector.error) {
        return (
            <div className="card">
                <h2 className="card__title">Sector Position</h2>
                <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-tertiary)' }}>
                    {sector?.error || 'Sector data unavailable'}
                </p>
            </div>
        );
    }

    const formatValue = (val) => {
        if (val == null) return '—';
        return typeof val === 'number'
            ? val % 1 === 0 ? val.toString() : val.toFixed(1)
            : val;
    };

    return (
        <div className="card">
            <h2 className="card__title">Sector Position — {sector.sector_name}</h2>

            <table className="sector-table">
                <thead>
                    <tr>
                        <th>Metric</th>
                        <th>Company</th>
                        <th>Sector Avg</th>
                    </tr>
                </thead>
                <tbody>
                    {sector.comparisons?.map((row, i) => (
                        <tr key={i}>
                            <td>{row.metric}</td>
                            <td style={{ fontWeight: 600 }}>
                                {formatValue(row.company)}{row.metric !== 'P/E Ratio' && row.company != null ? '%' : ''}
                            </td>
                            <td>
                                {formatValue(row.sector_avg)}{row.metric !== 'P/E Ratio' && row.sector_avg != null ? '%' : ''}
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}
