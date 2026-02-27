export default function LoadingState() {
    return (
        <div className="loading-container">
            <div className="loading-spinner" />
            <div className="loading-text">Running analysis…</div>
            <div className="loading-subtext">Fetching financial data and computing valuation</div>
        </div>
    );
}

export function SkeletonDashboard() {
    return (
        <>
            <div className="skeleton skeleton--header" />
            <div className="cards-grid">
                <div className="skeleton skeleton--card" />
                <div className="skeleton skeleton--card" />
                <div className="skeleton skeleton--card" />
            </div>
            <div className="skeleton skeleton--section" />
            <div className="skeleton skeleton--section" />
        </>
    );
}
