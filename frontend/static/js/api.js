**File: frontend/static/js/api.js**

class APIClient {
    constructor(baseURL = 'http://localhost:5000/api') {
        this.baseURL = baseURL;
        this.authToken = null;
    }

    /**
     * Set authentication token
     */
    setAuthToken(token) {
        this.authToken = token;
    }

    /**
     * Make HTTP request
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers};

        if (this.authToken) {
            headers['Authorization'] = `Bearer ${this.authToken}`;
        }

        try {
            const response = await fetch(url, {
                ...options,
                headers
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Request failed');
            }

            return await response.json();
        } catch (error) {
            console.error('API Request Error:', error);
            throw error;
        }
    }

    // Dataset endpoints
    async getDatasets() {
        return this.request('/datasets');
    }

    async getDataset(id) {
        return this.request(`/datasets/${id}`);
    }

    async searchDatasets(query, filters = {}) {
        return this.request('/datasets/search', {
            method: 'POST',
            body: JSON.stringify({ query, filters })
        });
    }

    async getDatasetSample(id) {
        return this.request(`/datasets/${id}/sample`);
    }

    // Transaction endpoints
    async purchaseDataset(buyerId, datasetId, price) {
        return this.request('/transactions/purchase', {
            method: 'POST',
            body: JSON.stringify({
                buyer_id: buyerId,
                dataset_id: datasetId,
                price
            })
        });
    }

    async getTransaction(id) {
        return this.request(`/transactions/${id}`);
    }

    async getTransactionHistory(address = null) {
        const query = address ? `?address=${address}` : '';
        return this.request(`/transactions/history${query}`);
    }

    // Analytics endpoints
    async getMarketplaceStats() {
        return this.request('/analytics/marketplace');
    }

    async getPerformanceMetrics() {
        return this.request('/analytics/performance');
    }

    async getPricingAnalytics() {
        return this.request('/analytics/pricing');
    }

    // Agent endpoints
    async registerProvider(agentId, name, endpoint) {
        return this.request('/agents/provider', {
            method: 'POST',
            body: JSON.stringify({
                agent_id: agentId,
                name,
                endpoint
            })
        });
    }
}

// Export for use in other scripts
const api = new APIClient();