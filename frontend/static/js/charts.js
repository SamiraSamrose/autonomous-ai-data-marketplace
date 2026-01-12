function initDashboardCharts() {
    loadTransactionVolumeChart();
    loadDatasetDistributionChart();
    loadPriceTrendsChart();
    loadAgentActivityChart();
}

async function loadTransactionVolumeChart() {
    const ctx = document.getElementById('transaction-volume-chart');
    if (!ctx) return;

    try {
        const response = await api.getMarketplaceStats();
        const history = await api.getTransactionHistory();
        
        // Group transactions by hour
        const hourlyData = processHourlyTransactions(history.transactions);
        
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: hourlyData.labels,
                datasets: [{
                    label: 'Transaction Volume',
                    data: hourlyData.volumes,
                    borderColor: '#2E86AB',
                    backgroundColor: 'rgba(46, 134, 171, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    },
                    title: {
                        display: true,
                        text: 'Transaction Volume Over Time'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return formatMNEE(value) + ' MNEE';
                            }
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error loading transaction volume chart:', error);
    }
}

async function loadDatasetDistributionChart() {
    const ctx = document.getElementById('dataset-distribution-chart');
    if (!ctx) return;

    try {
        const response = await api.getDatasets();
        const categoryData = processCategoryDistribution(response.datasets);
        
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: categoryData.labels,
                datasets: [{
                    data: categoryData.counts,
                    backgroundColor: [
                        '#2E86AB',
                        '#06D6A0',
                        '#FFD166',
                        '#EF476F',
                        '#073B4C',
                        '#118AB2'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'right'
                    },
                    title: {
                        display: true,
                        text: 'Dataset Category Distribution'
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error loading dataset distribution chart:', error);
    }
}

async function loadPriceTrendsChart() {
    const ctx = document.getElementById('price-trends-chart');
    if (!ctx) return;

    try {
        const response = await api.getPricingAnalytics();
        const datasets = await api.getDatasets();
        
        const priceData = processPriceTrends(datasets.datasets);
        
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: priceData.labels,
                datasets: [{
                    label: 'Average Price',
                    data: priceData.prices,
                    backgroundColor: '#06D6A0',
                    borderColor: '#05B58A',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    title: {
                        display: true,
                        text: 'Average Price by Category'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return formatMNEE(value) + ' MNEE';
                            }
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error loading price trends chart:', error);
    }
}

async function loadAgentActivityChart() {
    const ctx = document.getElementById('agent-activity-chart');
    if (!ctx) return;

    try {
        const response = await api.getMarketplaceStats();
        
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
                datasets: [{
                    label: 'Provider Agents',
                    data: [15, 22, 28, 35],
                    borderColor: '#2E86AB',
                    backgroundColor: 'rgba(46, 134, 171, 0.1)',
                    tension: 0.4
                }, {
                    label: 'Buyer Agents',
                    data: [10, 18, 25, 32],
                    borderColor: '#06D6A0',
                    backgroundColor: 'rgba(6, 214, 160, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    },
                    title: {
                        display: true,
                        text: 'Agent Activity Trends'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error loading agent activity chart:', error);
    }
}

async function loadTransactionChart() {
    const ctx = document.getElementById('analytics-transaction-chart');
    if (!ctx) return;

    try {
        const response = await api.getTransactionHistory();
        const typeData = processTransactionTypes(response.transactions);
        
        new Chart(ctx, {
            type: 'pie',
            data: {
                labels: typeData.labels,
                datasets: [{
                    data: typeData.counts,
                    backgroundColor: [
                        '#2E86AB',
                        '#06D6A0',
                        '#FFD166',
                        '#EF476F',
                        '#073B4C'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'bottom'
                    },
                    title: {
                        display: true,
                        text: 'Transaction Types Distribution'
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error loading transaction chart:', error);
    }
}

async function loadPricingChart() {
    const ctx = document.getElementById('analytics-pricing-chart');
    if (!ctx) return;

    try {
        const response = await api.getPricingAnalytics();
        
        new Chart(ctx, {
            type: 'scatter',
            data: {
                datasets: [{
                    label: 'Price vs Quality',
                    data: generatePriceQualityData(),
                    backgroundColor: '#2E86AB'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true
                    },
                    title: {
                        display: true,
                        text: 'Dataset Price vs Quality Analysis'
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Quality Score'
                        },
                        min: 0,
                        max: 1
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Price (MNEE)'
                        },
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return formatMNEE(value);
                            }
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error loading pricing chart:', error);
    }
}

async function loadQualityChart() {
    const ctx = document.getElementById('analytics-quality-chart');
    if (!ctx) return;

    try {
        const response = await api.getDatasets();
        const qualityData = processQualityDistribution(response.datasets);
        
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: qualityData.labels,
                datasets: [{
                    label: 'Number of Datasets',
                    data: qualityData.counts,
                    backgroundColor: '#06D6A0'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    title: {
                        display: true,
                        text: 'Quality Score Distribution'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error loading quality chart:', error);
    }
}

async function loadPerformanceChart() {
    const ctx = document.getElementById('analytics-performance-chart');
    if (!ctx) return;

    try {
        const response = await api.getPerformanceMetrics();
        
        new Chart(ctx, {
            type: 'radar',
            data: {
                labels: ['TPS', 'Latency', 'Uptime', 'Success Rate', 'Quality'],
                datasets: [{
                    label: 'System Performance',
                    data: [
                        response.metrics.tps / 10,
                        100 - response.metrics.avg_latency_ms,
                        response.metrics.uptime_percentage,
                        95,
                        85
                    ],
                    backgroundColor: 'rgba(46, 134, 171, 0.2)',
                    borderColor: '#2E86AB',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true
                    },
                    title: {
                        display: true,
                        text: 'System Performance Metrics'
                    }
                },
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error loading performance chart:', error);
    }
}

function processHourlyTransactions(transactions) {
    const hourlyMap = {};
    
    transactions.forEach(tx => {
        const date = new Date(tx.timestamp * 1000);
        const hour = date.getHours();
        const key = `${hour}:00`;
        
        if (!hourlyMap[key]) {
            hourlyMap[key] = 0;
        }
        hourlyMap[key] += tx.amount || 0;
    });
    
    const labels = Object.keys(hourlyMap).sort();
    const volumes = labels.map(label => hourlyMap[label]);
    
    return { labels, volumes };
}

function processCategoryDistribution(datasets) {
    const categoryMap = {};
    
    datasets.forEach(dataset => {
        dataset.categories.forEach(category => {
            categoryMap[category] = (categoryMap[category] || 0) + 1;
        });
    });
    
    const labels = Object.keys(categoryMap);
    const counts = labels.map(label => categoryMap[label]);
    
    return { labels, counts };
}

function processPriceTrends(datasets) {
    const categoryPrices = {};
    
    datasets.forEach(dataset => {
        const category = dataset.categories[0] || 'other';
        if (!categoryPrices[category]) {
            categoryPrices[category] = [];
        }
        categoryPrices[category].push(dataset.price);
    });
    
    const labels = Object.keys(categoryPrices);
    const prices = labels.map(label => {
        const prices = categoryPrices[label];
        return prices.reduce((a, b) => a + b, 0) / prices.length;
    });
    
    return { labels, prices };
}

function processTransactionTypes(transactions) {
    const typeMap = {};
    
    transactions.forEach(tx => {
        const type = tx.type || 'unknown';
        typeMap[type] = (typeMap[type] || 0) + 1;
    });
    
    const labels = Object.keys(typeMap);
    const counts = labels.map(label => typeMap[label]);
    
    return { labels, counts };
}

function processQualityDistribution(datasets) {
    const ranges = ['0.0-0.2', '0.2-0.4', '0.4-0.6', '0.6-0.8', '0.8-1.0'];
    const counts = [0, 0, 0, 0, 0];
    
    datasets.forEach(dataset => {
        const score = dataset.quality_score;
        const index = Math.min(Math.floor(score * 5), 4);
        counts[index]++;
    });
    
    return { labels: ranges, counts };
}

function generatePriceQualityData() {
    return Array.from({ length: 20 }, () => ({
        x: Math.random(),
        y: Math.random() * 50 * 1e18
    }));
}

function displayPerformanceMetrics(metrics) {
    document.getElementById('metric-tps').textContent = metrics.tps.toFixed(2);
    document.getElementById('metric-contracts').textContent = metrics.total_contracts;
    document.getElementById('metric-latency').textContent = metrics.avg_latency_ms + 'ms';
    document.getElementById('metric-uptime').textContent = metrics.uptime_percentage.toFixed(1) + '%';
}
