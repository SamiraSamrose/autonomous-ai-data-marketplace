import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.models.agents import DataBuyerAgent
from backend.config import Config
from scripts.init_db import initialize_system
from scripts.load_datasets import load_datasets_to_marketplace, generate_sample_datasets

def run_simulation(systems):
    """Run marketplace simulation"""
    print("\n" + "="*60)
    print("MARKETPLACE SIMULATION")
    print("="*60)
    
    # Create buyer agents
    print("\nCreating buyer agents...")
    buyer1 = DataBuyerAgent(
        "buyer_001",
        "AI Research Lab",
        100000 * (10**Config.MNEE_DECIMALS),
        systems
    )
    buyer2 = DataBuyerAgent(
        "buyer_002",
        "Tech Startup",
        50000 * (10**Config.MNEE_DECIMALS),
        systems
    )
    
    buyers = [buyer1, buyer2]
    print(f"  Created {len(buyers)} buyer agents")
    
    # Buyer 1 autonomous procurement
    print("\n### Buyer 1: Autonomous Procurement ###")
    requirements = {
        'query': 'machine learning classification datasets',
        'max_price': 15000 * (10**Config.MNEE_DECIMALS),
        'min_quality': 0.65,
        'filters': {'categories': ['machine-learning']}
    }
    
    recommendations = buyer1.autonomous_procurement(requirements)
    print(f"  Found {len(recommendations)} recommended datasets")
    
    for rec in recommendations:
        print(f"\n  Dataset: {rec['dataset_id']}")
        print(f"    Recommended Price: {rec['recommended_price'] / (10**Config.MNEE_DECIMALS)} MNEE")
        print(f"    Quality Score: {rec['quality_score']:.2f}")
        print(f"    Match Score: {rec['match_score']:.2f}")
    
    # Buyer 2 search and purchase
    print("\n### Buyer 2: Search and Purchase ###")
    results = buyer2.search_datasets('financial trading data', relaxed=True)
    print(f"  Found {len(results)} datasets")
    
    if results:
        top_result = results[0]
        print(f"\n  Top Result: {top_result['dataset_id']}")
        print(f"  Match Score: {top_result['match_score']:.2f}")
    
    # Display final statistics
    print("\n" + "="*60)
    print("SIMULATION SUMMARY")
    print("="*60)
    
    mnee = systems['mnee_token']
    discovery = systems['discovery_service']
    contracts = systems['contract_engine']
    
    print(f"\nMarketplace Statistics:")
    print(f"  Total Datasets: {len(discovery.dataset_registry)}")
    print(f"  Total Transactions: {mnee.transaction_count}")
    print(f"  Total Volume: {sum(tx.get('amount', 0) for tx in mnee.transactions) / (10**Config.MNEE_DECIMALS):,.0f} MNEE")
    print(f"  Smart Contracts: {len(contracts.contracts)}")
    
    print(f"\nAgent Statistics:")
    print(f"  Provider Agents: {len(discovery.registered_agents)}")
    print(f"  Buyer Agents: {len(buyers)}")
    
    for buyer in buyers:
        summary = buyer.get_purchase_summary()
        print(f"\n  {buyer.agent_name}:")
        print(f"    Purchases: {summary['total_datasets_purchased']}")
        print(f"    Spent: {summary['total_spent'] / (10**Config.MNEE_DECIMALS):,.0f} MNEE")
        print(f"    Remaining: {summary['remaining_budget'] / (10**Config.MNEE_DECIMALS):,.0f} MNEE")
    
    print("\n" + "="*60)

if __name__ == '__main__':
    try:
        print("Initializing system...")
        systems = initialize_system()
        
        print("\nLoading datasets...")
        load_datasets_to_marketplace(systems)
        
        print("\nRunning simulation...")
        run_simulation(systems)
        
        print("\nSimulation complete!")
    except Exception as e:
        print(f"\nError during simulation: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
