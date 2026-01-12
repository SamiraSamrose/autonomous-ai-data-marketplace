import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.models.mnee_token import MNEEToken
from backend.models.smart_contracts import SmartContractEngine
from backend.models.discovery import DiscoveryService
from backend.models.quality import QualityAssessment
from backend.models.pricing import DynamicPricing
from backend.models.reputation import ReputationSystem
from backend.utils.embeddings import VectorEmbedding
from backend.utils.atomic_swap import AtomicSwapEngine
from backend.config import Config

def initialize_system():
    """Initialize all system components"""
    print("Initializing Autonomous AI Data Marketplace...")
    print("="*60)
    
    # Initialize MNEE Token
    print("\n1. Initializing MNEE Token System...")
    mnee_token = MNEEToken()
    print(f"   Total Supply: {mnee_token.total_supply / (10**Config.MNEE_DECIMALS):,.0f} MNEE")
    
    # Initialize Smart Contract Engine
    print("\n2. Initializing Smart Contract Engine...")
    contract_engine = SmartContractEngine()
    print("   Smart contracts ready")
    
    # Initialize Vector Embedding
    print("\n3. Initializing Vector Embedding System...")
    embedding_system = VectorEmbedding(Config.VECTOR_EMBEDDING_DIM)
    print(f"   Embedding dimension: {Config.VECTOR_EMBEDDING_DIM}")
    
    # Initialize Discovery Service
    print("\n4. Initializing Discovery Service...")
    discovery_service = DiscoveryService(embedding_system)
    print("   Discovery service ready")
    
    # Initialize Quality Assessment
    print("\n5. Initializing Quality Assessment...")
    quality_system = QualityAssessment()
    print("   Quality system ready")
    
    # Initialize Dynamic Pricing
    print("\n6. Initializing Dynamic Pricing...")
    pricing_system = DynamicPricing()
    print("   Pricing system ready")
    
    # Initialize Reputation System
    print("\n7. Initializing Reputation System...")
    reputation_system = ReputationSystem(mnee_token)
    print("   Reputation system ready")
    
    # Initialize Atomic Swap Engine
    print("\n8. Initializing Atomic Swap Engine...")
    atomic_swap_engine = AtomicSwapEngine(mnee_token, contract_engine)
    print("   Atomic swap engine ready")
    
    print("\n" + "="*60)
    print("System initialization complete!")
    print("="*60)
    
    return {
        'mnee_token': mnee_token,
        'contract_engine': contract_engine,
        'embedding_system': embedding_system,
        'discovery_service': discovery_service,
        'quality_system': quality_system,
        'pricing_system': pricing_system,
        'reputation_system': reputation_system,
        'atomic_swap_engine': atomic_swap_engine
    }

if __name__ == '__main__':
    try:
        systems = initialize_system()
        print("\nDatabase initialization successful!")
    except Exception as e:
        print(f"\nError during initialization: {str(e)}")
        sys.exit(1)
