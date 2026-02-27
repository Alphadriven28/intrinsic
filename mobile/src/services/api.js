const API_BASE_URL = 'https://intrinsic.onrender.com';
// For local development, use:
// const API_BASE_URL = 'http://localhost:5000';
// const API_BASE_URL = 'http://192.168.x.x:5000';
// const API_BASE_URL = 'https://your-deployed-backend.com';

export async function analyzeStock(ticker) {
    const cleanTicker = ticker.trim().toUpperCase();

    try {
        const response = await fetch(`${API_BASE_URL}/api/analyze/${cleanTicker}`, {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' },
        });

        const data = await response.json();

        if (!response.ok) {
            const error = new Error(data.error || 'Analysis failed');
            error.errorCode = data.error_code || 'server_error';
            throw error;
        }

        return data;
    } catch (error) {
        if (error.errorCode) throw error;

        const networkError = new Error('Network error. Check your connection and API address.');
        networkError.errorCode = 'network_error';
        throw networkError;
    }
}
