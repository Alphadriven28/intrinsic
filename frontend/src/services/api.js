const API_BASE = '/api';

/**
 * Error code to user-friendly message mapping.
 */
const ERROR_MESSAGES = {
    auth_failed: 'API authentication failed. Please check your API key.',
    rate_limited: 'API limit reached. Please try again later.',
    not_found: 'Ticker not listed in US markets or invalid symbol.',
    server_error: 'Temporary server issue. Please try again.',
    invalid_input: 'Invalid ticker symbol. Use only letters and numbers.',
};

/**
 * Sanitize ticker input: trim, uppercase, strip non-alphanumeric.
 */
function sanitizeTicker(ticker) {
    return ticker.trim().toUpperCase().replace(/[^A-Z0-9.]/g, '');
}

/**
 * Analyze a stock ticker via the backend API.
 * Throws an Error with a structured message and error_code property.
 */
export async function analyzeStock(rawTicker) {
    const ticker = sanitizeTicker(rawTicker);
    if (!ticker) {
        const err = new Error('Please enter a valid ticker symbol.');
        err.errorCode = 'invalid_input';
        throw err;
    }

    let response;
    try {
        response = await fetch(`${API_BASE}/analyze/${ticker}`);
    } catch (networkError) {
        const err = new Error('Network error. Please check your connection and try again.');
        err.errorCode = 'network_error';
        throw err;
    }

    let data;
    try {
        data = await response.json();
    } catch (parseError) {
        const err = new Error('Received an invalid response from the server.');
        err.errorCode = 'server_error';
        throw err;
    }

    if (!response.ok || data.error) {
        const errorCode = data.error_code || 'server_error';
        const message = ERROR_MESSAGES[errorCode] || data.error || 'Analysis failed.';
        const err = new Error(message);
        err.errorCode = errorCode;
        throw err;
    }

    return data;
}

/**
 * Fetch backend health status.
 */
export async function fetchHealth() {
    const response = await fetch(`${API_BASE}/health`);
    return response.json();
}
