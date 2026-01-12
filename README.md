# Autonomous AI Data Marketplace

A decentralized, agent-to-agent data marketplace enabling autonomous data commerce with zero human negotiation. Built with MNEE programmable money, smart contracts and AI agents.

This autonomous AI data marketplace implements a decentralized agent-to-agent economy for dataset transactions using programmable money, eliminating human negotiation through smart contracts and cryptographic verification. The system deploys MNEE tokens as ERC-20 compatible currency for autonomous payments between AI agents representing data providers and buyers.

## Overview

This system enables:
- Data provider agents to list datasets with standardized metadata
- Buyer agents to evaluate quality, relevance and freshness
- Autonomous payments via MNEE token
- Instant access through smart contracts
- Federated learning without data movement
- Cross-chain settlement support

## Links
-**Source Code**: https://github.com/SamiraSamrose/autonomous-ai-data-marketplace
-**Video Demo**: https://youtu.be/tVZpVmZ01DU
-**Notebook**: https://github.com/SamiraSamrose/autonomous-ai-data-marketplace/blob/main/Autonomous_AI_Data_Marketplace_(Agent_to_Agent_Economy).ipynb

## Features

**MNEE Token System:** ERC-20 compatible programmable money with transfer, staking, slashing, minting and transaction history tracking, MNEE token for autonomous agent payments

**Smart Contract Engine:** Deploys and manages escrow contracts for secure fund holding, NFT-based license contracts for time-bound access, automated event emission and contract state management

**Agent Wallet System:** Non-custodial wallets with RSA key generation, transaction signing, balance management and MNEE operations

**Discovery Service:** JSON-LD metadata schema registration, vector embedding-based semantic search, RFQ broadcasting and agent endpoint management

**Vector Embedding Search:** 384-dimension semantic embeddings with domain-specific keyword vectors, cosine similarity matching and configurable threshold filtering

**Quality Assessment:** Statistical analysis of completeness, outlier detection using IQR, data type distribution, third-party attestation generation and certification based on threshold scoring, zero-knowledge proofs for data verification

**Zero-Knowledge Proofs:** Commitment generation for statistical properties, sample-based proof creation, range proofs and batch verification

**Dynamic Pricing:** Bonding curve algorithms (linear, exponential, sigmoid), demand-based adjustments, freshness multipliers, quality multipliers and price trend prediction

**Reputation System:** Stake-based trust scores, transaction success tracking, review submission and aggregation, slashing penalties for misbehavior and comprehensive trust calculation

**Atomic Swap Engine:** Escrow-based transaction locking, receipt oracle verification, SLA compliance checking, automated refunds and encrypted access key management

**Federated Learning:** Local gradient computation, top-k gradient compression, weighted gradient aggregation, global model updates and privacy-preserving training

**Streaming Payments:** Payment channel creation, micro-payment execution per API call, real-time balance tracking and automated channel closure

**Compliance System:** Automated tax receipt generation, proof of origin creation with blockchain timestamps, Merkle root verification and audit trail logging

**Cross-Chain Bridge:** Multi-blockchain support (Ethereum, Solana, Polygon, Arbitrum), transfer initiation with fee calculation, confirmation tracking and liquidity management

**Analytics Engine:** Real-time marketplace statistics, performance metrics collection, pricing analytics, quality distribution analysis and comprehensive reporting

**Data Provider Agents:** Dataset listing with metadata, sample provision, purchase request handling, sales tracking and performance metrics

**Data Buyer Agents:** Semantic search with filter relaxation, sample evaluation, autonomous procurement, purchase execution with atomic swaps and budget management


### Advanced Features
- NFT-based access licenses
- Streaming micro-payments
- SLA enforcement with automated refunds
- Compliance reporting with tax receipts
- Third-party quality attestation
- Sample data evaluation

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Provider Agent │────▶│ Discovery Layer │◀────│  Buyer Agent    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                      │                        │
         │              ┌───────▼───────┐                │
         │              │ Vector Search │                │
         │              └───────────────┘                │
         │                                               │
         ▼                                               ▼
┌─────────────────┐                           ┌─────────────────┐
│ MNEE Wallet     │                           │ Quality Oracle  │
└─────────────────┘                           └─────────────────┘
         │                                              │
         │              ┌───────────────┐               │
         └─────────────▶│ Smart Contract│◀──────────────┘
                        │    Engine     │
                        └───────┬───────┘
                                │
                        ┌───────▼───────┐
                        │ Atomic Swap   │
                        │    Engine     │
                        └───────────────┘
```

## Installation

### Prerequisites
- Python 3.8 or higher
- Node.js 14 or higher (for frontend build tools)
- PostgreSQL 12 or higher (optional, for persistent storage)
- Redis (optional, for caching)

### Quick Start

1. Clone the repository:
```bash
git clone https://github.com/samirasamrose/autonomous-ai-data-marketplace.git
cd autonomous-ai-data-marketplace
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Initialize the system:
```bash
python scripts/init_db.py
python scripts/load_datasets.py
```

6. Run the application:
```bash
python backend/app.py
```

7. Access the dashboard:
```
http://localhost:5000
```

## Configuration

Edit `.env` file:

```env
# Application
FLASK_ENV=production
SECRET_KEY=your-secret-key
DEBUG=False

# Server
HOST=0.0.0.0
PORT=5000

# MNEE Token
MNEE_INITIAL_SUPPLY=1000000000
MNEE_DECIMALS=18
BASE_DATA_PRICE=10

# System
MAX_SEARCH_RESULTS=20
QUALITY_THRESHOLD=0.8
REPUTATION_THRESHOLD=0.7
```

## API Documentation

### Endpoints

#### Datasets
- `GET /api/datasets` - List all datasets
- `GET /api/datasets/<id>` - Get dataset details
- `POST /api/datasets` - Register new dataset
- `GET /api/datasets/<id>/sample` - Get dataset sample

#### Transactions
- `POST /api/transactions/purchase` - Purchase dataset
- `GET /api/transactions/<id>` - Get transaction status
- `GET /api/transactions/history` - Transaction history

#### Agents
- `POST /api/agents/provider` - Register provider agent
- `POST /api/agents/buyer` - Register buyer agent
- `GET /api/agents/<id>` - Get agent information

#### Analytics
- `GET /api/analytics/marketplace` - Marketplace statistics
- `GET /api/analytics/performance` - Performance metrics
- `GET /api/analytics/pricing` - Pricing analytics

See `docs/API.md` for complete documentation.

## Usage Examples

### Register Provider Agent

```python
from backend.models.agents import DataProviderAgent
import pandas as pd

# Create provider agent
provider = DataProviderAgent("provider_001", "DataCorp Solutions")

# Load and list dataset
data = pd.read_csv("data/datasets/traffic_data.csv")
dataset_id = provider.list_dataset({
    'name': 'Urban Traffic Patterns',
    'description': 'High-resolution traffic data with weather conditions',
    'categories': ['transportation', 'urban-planning'],
    'industry': 'transportation',
    'price': 20 * (10**18)  # 20 MNEE
}, data)
```

### Purchase Dataset as Buyer

```python
from backend.models.agents import DataBuyerAgent

# Create buyer agent
buyer = DataBuyerAgent("buyer_001", "AI Research Lab", 100000 * (10**18))

# Search for datasets
results = buyer.search_datasets(
    "urban traffic patterns",
    filters={'max_price': 50 * (10**18)}
)

# Evaluate sample
evaluation = buyer.evaluate_sample(dataset_id, provider)

# Purchase dataset
purchase = buyer.execute_purchase(
    dataset_id, provider, agreed_price, terms
)
```

### Run Autonomous Procurement

```python
# Define requirements
requirements = {
    'query': 'machine learning classification datasets',
    'max_price': 30 * (10**18),
    'min_quality': 0.75,
    'filters': {'categories': ['machine-learning']}
}

# Execute autonomous procurement
recommendations = buyer.autonomous_procurement(requirements)
```

## Testing

Run test suite:
```bash
pytest tests/ -v
```

Run specific tests:
```bash
pytest tests/test_agents.py -v
pytest tests/test_contracts.py -v
```

## Deployment

### Docker Deployment

1. Build image:
```bash
docker-compose build
```

2. Start services:
```bash
docker-compose up -d
```

3. Check logs:
```bash
docker-compose logs -f
```

### Production Deployment

See `docs/DEPLOYMENT.md` for detailed instructions on deploying to:
- AWS
- Google Cloud Platform
- Azure
- Kubernetes

## Performance Benchmarks

- Transaction throughput: 1000+ TPS (target)
- Smart contract execution: Sub-second
- Dataset search: < 100ms
- Quality assessment: < 500ms per dataset
- Cross-chain settlement: 3-5 minutes

## Security

- Non-custodial agent wallets
- Cryptographic transaction signing
- Zero-knowledge proofs for data quality
- Escrow-based atomic swaps
- SLA enforcement with automated refunds
- Reputation system with slashing

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## Usages List

**MNEE Token Operations:** Transfer tokens between addresses, stake tokens for reputation building, slash staked tokens for misbehavior penalties, mint new tokens, track complete transaction history

**Smart Contracts:** Deploy escrow contracts locking funds until conditions met, create NFT licenses for time-bound access, execute automated contract actions, emit events for state changes, manage contract lifecycle

**Agent Management:** Register provider agents with endpoints, create buyer agents with budgets, generate cryptographic wallets, sign transactions with private keys, manage MNEE balances

**Dataset Discovery:** Register datasets with standardized metadata, search using semantic queries, filter by price and quality thresholds, rank results by similarity scores, broadcast RFQs

**Quality Verification:** Assess statistical properties of datasets, detect outliers using interquartile range, generate third-party attestations, verify certifications, provide quality scores

**Pricing Mechanisms:** Calculate bonding curve prices based on demand, apply freshness multipliers to recent data, adjust prices by quality scores, track price history, predict price trends

**Transaction Security:** Lock payments in escrow contracts, verify data access through receipt oracles, enforce SLA terms automatically, trigger refunds for violations, generate encrypted access keys

**Reputation Tracking:** Record transaction success rates, aggregate user reviews, calculate trust scores, slash stakes for bad actors, identify trusted agents

**Sample Evaluation:** Provide 1% data samples for evaluation, charge 0.01 MNEE sample fees, verify sample quality matches full dataset, enable try-before-buy decisions

**Federated Learning:** Train models on distributed private data, compute and compress local gradients, aggregate gradients from multiple sources, update global models without data sharing

**Streaming Payments:** Open payment channels with deposits, execute micro-payments per API call, track real-time balances, close channels with settlement

**Compliance Documentation:** Generate tax receipts automatically, create proof-of-origin certificates, maintain audit trails, verify Merkle roots, export compliance packages

**Cross-Chain Operations:** Initiate transfers between blockchains, track confirmations across chains, manage liquidity pools, calculate bridge fees

**Analytics Monitoring:** Track marketplace statistics, measure system performance metrics, analyze pricing trends, monitor quality distributions, generate comprehensive reports

**Autonomous Procurement:** Execute searches with relaxed filters, evaluate samples automatically, negotiate terms without human input, purchase datasets meeting criteria, manage procurement budgets

## License

This project is licensed under the MIT License - see LICENSE file for details.

