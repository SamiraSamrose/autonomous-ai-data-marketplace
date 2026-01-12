document.addEventListener('DOMContentLoaded', function() {
    console.log('Autonomous AI Data Marketplace - Initialized');
    
    // Initialize components based on current page
    const path = window.location.pathname;
    
    if (path === '/' || path === '/index.html') {
        initDashboard();
    } else if (path === '/datasets' || path === '/datasets.html') {
        initDatasets();
    } else if (path === '/analytics' || path === '/analytics.html') {
        initAnalytics();
    } else if (path === '/transactions' || path === '/transactions.html') {
        initTransactions();
    }
});

async function initDashboard() {
    try {
        // Load marketplace statistics
        const stats = await api.getMarketplaceStats();
        updateStatsCards(stats.statistics);
        
        // Load performance metrics
        const performance = await api.getPerformanceMetrics();
        displayPerformanceMetrics(performance.metrics);
        
        // Initialize charts
        initDashboardCharts();
        
    } catch (error) {
        console.error('Dashboard initialization error:', error);
        showError('Failed to load dashboard data');
    }
}

function updateStatsCards(stats) {
    document.getElementById('total-datasets').textContent = stats.total_datasets || 0;
    document.getElementById('total-transactions').textContent = stats.total_transactions || 0;
    document.getElementById('total-volume').textContent = formatMNEE(stats.total_volume || 0);
    document.getElementById('active-agents').textContent = stats.active_agents || 0;
}

async function initDatasets() {
    try {
        const response = await api.getDatasets();
        displayDatasets(response.datasets);
        
        // Setup search
        document.getElementById('search-btn').addEventListener('click', handleSearch);
        document.getElementById('search-input').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                handleSearch();
            }
        });
        
    } catch (error) {
        console.error('Datasets initialization error:', error);
        showError('Failed to load datasets');
    }
}

function displayDatasets(datasets) {
    const grid = document.getElementById('dataset-grid');
    grid.innerHTML = '';
    
    datasets.forEach(dataset => {
        const card = createDatasetCard(dataset);
        grid.appendChild(card);
    });
}

function createDatasetCard(dataset) {
    const card = document.createElement('div');
    card.className = 'dataset-card';
    
    const qualityPercent = (dataset.quality_score * 100).toFixed(0);
    
    card.innerHTML = `
        <div class="dataset-header">
            <h3 class="dataset-title">${dataset.name}</h3>
            <span class="dataset-price">${formatMNEE(dataset.price)} MNEE</span>
        </div>
        <p class="dataset-description">${dataset.description}</p>
        <div class="dataset-meta">
            ${dataset.categories.map(cat => 
                `<span class="meta-tag">${cat}</span>`
            ).join('')}
            <span class="meta-tag">${dataset.format.toUpperCase()}</span>
            <span class="meta-tag">${dataset.row_count} rows</span>
        </div>
        <div class="quality-bar">
            <div class="quality-fill" style="width: ${qualityPercent}%"></div>
        </div>
        <div class="dataset-actions">
            <button class="btn btn-primary btn-small" onclick="viewDataset('${dataset.id}')">
                View Details
            </button>
            <button class="btn btn-outline btn-small" onclick="purchaseDataset('${dataset.id}')">
                Purchase
            </button>
        </div>
    `;
    
    return card;
}

async function handleSearch() {
    const query = document.getElementById('search-input').value;
    const category = document.getElementById('category-filter').value;
    const maxPrice = document.getElementById('price-filter').value;
    
    const filters = {};
    if (category) filters.categories = [category];
    if (maxPrice) filters.max_price = parseFloat(maxPrice) * 1e18;
    
    try {
        const response = await api.searchDatasets(query, filters);
        displayDatasets(response.results.map(r => r.dataset_info));
    } catch (error) {
        console.error('Search error:', error);
        showError('Search failed');
    }
}

async function viewDataset(id) {
    try {
        const response = await api.getDataset(id);
        showDatasetModal(response.dataset);
    } catch (error) {
        console.error('Error loading dataset:', error);
        showError('Failed to load dataset details');
    }
}

async function purchaseDataset(id) {
    if (!confirm('Proceed with dataset purchase?')) {
        return;
    }
    
    try {
        const buyerId = 'buyer_001'; // Would come from auth
        const dataset = await api.getDataset(id);
        const price = dataset.dataset.price_mnee;
        
        const response = await api.purchaseDataset(buyerId, id, price);
        
        if (response.success) {
            showSuccess('Purchase initiated successfully!');
        } else {
            showError('Purchase failed');
        }
    } catch (error) {
        console.error('Purchase error:', error);
        showError('Purchase failed');
    }
}

async function initAnalytics() {
    try {
        await Promise.all([
            loadTransactionChart(),
            loadPricingChart(),
            loadQualityChart(),
            loadPerformanceChart()
        ]);
    } catch (error) {
        console.error('Analytics initialization error:', error);
        showError('Failed to load analytics');
    }
}

async function initTransactions() {
    try {
        const response = await api.getTransactionHistory();
        displayTransactions(response.transactions);
    } catch (error) {
        console.error('Transactions initialization error:', error);
        showError('Failed to load transactions');
    }
}

function displayTransactions(transactions) {
    const tbody = document.getElementById('transactions-tbody');
    tbody.innerHTML = '';
    
    transactions.forEach(tx => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${tx.id}</td>
            <td>${tx.type}</td>
            <td>${formatMNEE(tx.amount || 0)} MNEE</td>
            <td>${tx.from ? tx.from.substring(0, 10) + '...' : 'N/A'}</td>
            <td>${tx.to ? tx.to.substring(0, 10) + '...' : 'N/A'}</td>
            <td>${new Date(tx.timestamp * 1000).toLocaleString()}</td>
            <td><span class="badge badge-success">Completed</span></td>
        `;
        tbody.appendChild(row);
    });
}

function formatMNEE(amount) {
    const mnee = amount / 1e18;
    return mnee.toLocaleString('en-US', {
        minimumFractionDigits: 0,
        maximumFractionDigits: 2
    });
}

function showSuccess(message) {
    alert(message); // Replace with proper notification system
}

function showError(message) {
    alert('Error: ' + message); // Replace with proper notification system
}

function showDatasetModal(dataset) {
    // Implementation would show a modal with full dataset details
    console.log('Show dataset modal:', dataset);
}
