# API Documentation

Complete API reference for the Autonomous AI Data Marketplace.

## Base URL

```
http://localhost:5000/api
```

## Authentication

Currently, the API does not require authentication. For production deployment, implement JWT-based authentication.

## Endpoints

### Datasets

#### List All Datasets

```
GET /api/datasets
```

Response:
```json
{
  "success": true,
  "count": 5,
  "datasets": [
    {
      "id": "ds_0_1234567890",
      "name": "Dataset Name",
      "description": "Description",
      "provider": "provider_001",
      "price": 10000000000000000000,
      "quality_score": 0.85,
      "categories": ["category1", "category2"],
      "format": "csv",
      "row_count": 1000
    }
  ]
}
```

#### Get Dataset Details

```
GET /api/datasets/<dataset_id>
```

#### Search Datasets

```
POST /api/datasets/search
Content-Type: application/json

{
  "query": "machine learning classification",
  "filters": {
    "max_price": 50000000000000000000,
    "categories": ["machine-learning"]
  }
}
```

#### Get Dataset Sample

```
GET /api/datasets/<dataset_id>/sample
```

### Transactions

#### Purchase Dataset

```
POST /api/transactions/purchase
Content-Type: application/json

{
  "buyer_id": "buyer_001",
  "dataset_id": "ds_0_1234567890",
  "price": 10000000000000000000
}
```

#### Get Transaction Status

```
GET /api/transactions/<transaction_id>
```

#### Get Transaction History

```
GET /api/transactions/history?address=0x123...
```

### Analytics

#### Get Marketplace Statistics

```
GET /api/analytics/marketplace
```

Response:
```json
{
  "success": true,
  "statistics": {
    "total_datasets": 10,
    "total_transactions": 50,
    "total_volume": 500000000000000000000,
    "active_agents": 8
  }
}
```

#### Get Performance Metrics

```
GET /api/analytics/performance
```

#### Get Pricing Analytics

```
GET /api/analytics/pricing
```

### Agents

#### Register Provider Agent

```
POST /api/agents/provider
Content-Type: application/json

{
  "agent_id": "provider_001",
  "name": "DataCorp Solutions",
  "endpoint": "https://provider.example.com/api"
}
```

## Error Responses

All endpoints return error responses in the following format:

```json
{
  "error": "Error message description"
}
```

Common HTTP status codes:
- 200: Success
- 400: Bad Request
- 401: Unauthorized
- 404: Not Found
- 500: Internal Server Error
```

---

**File: docs/ARCHITECTURE.md**
```markdown
# System Architecture

## Overview

The Autonomous AI Data Marketplace is built with a modular architecture enabling autonomous agent-to-agent data commerce.

## Components

### 1. MNEE Token System
- ERC-20 compatible programmable money
- Staking and slashing mechanisms
- Transaction history tracking
- Treasury management

### 2. Smart Contract Engine
- Escrow contracts for secure transactions
- NFT-based access licenses
- Event emission and logging
- Automated execution

### 3. Discovery Service
- JSON-LD metadata schema
- Vector embedding based semantic search
- RFQ (Request for Quote) broadcasting
- Provider registration

### 4. Quality Assessment
- Statistical quality metrics
- Third-party attestation
- Certification system
- Outlier detection

### 5. Dynamic Pricing
- Bonding curve algorithms
- Demand-based adjustments
- Freshness multipliers
- Quality-based pricing

### 6. Reputation System
- Stake-based trust scores
- Transaction success tracking
- Review submissions
- Slashing for misbehavior

### 7. Atomic Swap Engine
- Escrow-based swaps
- Receipt oracle verification
- SLA enforcement
- Automated refunds

### 8. Federated Learning
- Gradient compression
- Privacy-preserving training
- Multi-provider aggregation
- Version control

## Data Flow

```
1. Provider lists dataset → Discovery Service
2. Buyer searches datasets → Vector Embedding Search
3. Buyer evaluates sample → Quality Assessment
4. Buyer initiates purchase → Atomic Swap
5. Escrow locks MNEE → Smart Contract
6. Receipt oracle verifies → Data Access Granted
7. Payment released → Seller Receives MNEE
8. Review submitted → Reputation Updated
```

## Technology Stack

- Backend: Python 3.10, Flask
- Frontend: HTML5, CSS3, JavaScript, Chart.js
- Data Processing: Pandas, NumPy, Scikit-learn
- Cryptography: RSA-2048, SHA-256
- Visualization: Chart.js, Matplotlib

## Scalability

- Asynchronous processing support
- Batch transaction handling
- Caching layer with Redis
- Load balancing ready
- Microservices compatible
