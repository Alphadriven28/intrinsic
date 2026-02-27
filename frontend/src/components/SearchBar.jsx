import { useState } from 'react';

export default function SearchBar({ onSearch, isLoading }) {
    const [ticker, setTicker] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();
        const cleaned = ticker.trim().toUpperCase();
        if (cleaned) {
            onSearch(cleaned);
        }
    };

    return (
        <div className="search-container">
            <form className="search-form" onSubmit={handleSubmit}>
                <input
                    className="search-input"
                    type="text"
                    value={ticker}
                    onChange={(e) => setTicker(e.target.value)}
                    placeholder='Enter Ticker (e.g., AAPL)'
                    disabled={isLoading}
                    maxLength={10}
                    autoFocus
                />
                <button
                    className="search-btn"
                    type="submit"
                    disabled={isLoading || !ticker.trim()}
                >
                    {isLoading ? 'Analyzing…' : 'Analyze'}
                </button>
            </form>
        </div>
    );
}
