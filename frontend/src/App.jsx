import { useState } from 'react';
import SearchBar from './components/SearchBar';
import CompanyHeader from './components/CompanyHeader';
import MasterValuationCard from './components/MasterValuationCard';
import ModelGrid from './components/ModelGrid';
import IntelligenceScores from './components/IntelligenceScores';
import WeightChart from './components/WeightChart';
import GrowthQualityCard from './components/GrowthQualityCard';
import SectorCard from './components/SectorCard';
import RiskSection from './components/RiskSection';
import ExecutiveSummary from './components/ExecutiveSummary';
import LoadingState, { SkeletonDashboard } from './components/LoadingState';
import { analyzeStock } from './services/api';

const ERROR_DETAILS = {
    auth_failed: "The server API key is invalid or expired. Contact the administrator.",
    rate_limited: "The free API plan has a daily request limit. Analysis will resume tomorrow.",
    not_found: "Double-check the ticker symbol. Only US-listed equities are supported.",
    server_error: "The data provider may be experiencing downtime. Try again in a few minutes.",
    invalid_input: "Ticker symbols should contain only letters, numbers, or dots (e.g., AAPL, BRK.B).",
    network_error: "Could not reach the server. Verify your internet connection.",
};

const ERROR_ICONS = {
    auth_failed: '🔒',
    rate_limited: '⏱',
    not_found: '🔍',
    server_error: '⚠',
    invalid_input: '✏️',
    network_error: '📡',
};

export default function App() {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [errorCode, setErrorCode] = useState(null);

    const handleSearch = async (ticker) => {
        setLoading(true);
        setError(null);
        setErrorCode(null);
        setData(null);

        try {
            const result = await analyzeStock(ticker);
            setData(result);
        } catch (err) {
            setError(err.message || 'An unexpected error occurred');
            setErrorCode(err.errorCode || 'server_error');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="app">
            {/* Header */}
            <header className="app-header">
                <div className="app-header__brand">Intrinsic</div>
                <p className="app-header__tagline">
                    Institutional Equity Research & Valuation Intelligence
                </p>
            </header>

            {/* Search */}
            <SearchBar onSearch={handleSearch} isLoading={loading} />

            {/* Loading */}
            {loading && (
                <>
                    <LoadingState />
                    <SkeletonDashboard />
                </>
            )}

            {/* Error */}
            {error && (
                <div className="error-message">
                    <div className="error-message__icon">
                        {ERROR_ICONS[errorCode] || '⚠'}
                    </div>
                    <div className="error-message__text">{error}</div>
                    <div className="error-message__detail">
                        {ERROR_DETAILS[errorCode] || 'Please check the ticker and try again.'}
                    </div>
                </div>
            )}

            {/* Results Dashboard */}
            {data && !loading && (
                <div className="dashboard fade-in">
                    {/* Company Header */}
                    <CompanyHeader
                        company={data.company}
                        valuation={data.valuation}
                        weighting={data.weighting}
                    />

                    {/* Master Valuation Hero */}
                    <MasterValuationCard
                        valuation={data.valuation}
                        weighting={data.weighting}
                        master={data.master}
                    />

                    {/* 9-Model Grid */}
                    <ModelGrid
                        models={data.valuation?.models}
                        weighting={data.weighting}
                        currentPrice={data.company?.price}
                    />

                    {/* Intelligence Scores */}
                    <IntelligenceScores
                        confidence={data.confidence}
                        moat={data.moat}
                        scores={data.scores}
                    />

                    {/* Weight Distribution */}
                    <WeightChart weighting={data.weighting} />

                    {/* Existing sections */}
                    <div className="cards-grid">
                        <GrowthQualityCard scores={data.scores} />
                        <SectorCard sector={data.sector} />
                    </div>

                    <RiskSection risk={data.risk} />
                    <ExecutiveSummary summary={data.summary} />
                </div>
            )}

            {/* Footer */}
            <footer className="app-footer">
                <p className="app-footer__text">
                    Intrinsic — Quantitative equity research intelligence.
                    Data provided by Financial Modeling Prep.
                </p>
            </footer>
        </div>
    );
}
