import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    
    # Application
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Server
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    WORKERS = int(os.getenv('WORKERS', 4))
    
    # MNEE Token
    MNEE_DECIMALS = int(os.getenv('MNEE_DECIMALS', 18))
    MNEE_INITIAL_SUPPLY = int(os.getenv('MNEE_INITIAL_SUPPLY', 1000000000)) * (10 ** MNEE_DECIMALS)
    MNEE_PER_ETH = int(os.getenv('MNEE_PER_ETH', 1000))
    
    # Marketplace
    BASE_DATA_PRICE = int(float(os.getenv('BASE_DATA_PRICE', 10)) * (10 ** MNEE_DECIMALS))
    STREAMING_RATE = int(float(os.getenv('STREAMING_RATE', 0.001)) * (10 ** MNEE_DECIMALS))
    MIN_STAKE_AMOUNT = int(float(os.getenv('MIN_STAKE_AMOUNT', 100)) * (10 ** MNEE_DECIMALS))
    
    # Discovery
    VECTOR_EMBEDDING_DIM = int(os.getenv('VECTOR_EMBEDDING_DIM', 384))
    MAX_SEARCH_RESULTS = int(os.getenv('MAX_SEARCH_RESULTS', 20))
    SEMANTIC_SIMILARITY_THRESHOLD = float(os.getenv('SEMANTIC_SIMILARITY_THRESHOLD', 0.60))
    
    # Quality
    QUALITY_SCORE_THRESHOLD = float(os.getenv('QUALITY_SCORE_THRESHOLD', 0.80))
    TRY_BEFORE_BUY_SAMPLES = int(os.getenv('TRY_BEFORE_BUY_SAMPLES', 100))
    
    # Smart Contracts
    ESCROW_TIMEOUT = int(os.getenv('ESCROW_TIMEOUT', 3600))
    SLASHING_PENALTY = float(os.getenv('SLASHING_PENALTY', 0.10))
    
    # Reputation
    REPUTATION_THRESHOLD = float(os.getenv('REPUTATION_THRESHOLD', 0.70))
    
    # Cross-Chain
    SUPPORTED_CHAINS = os.getenv('SUPPORTED_CHAINS', 'ethereum,solana,polygon,arbitrum').split(',')
    BRIDGE_FEE_PERCENTAGE = float(os.getenv('BRIDGE_FEE_PERCENTAGE', 0.003))
    
    # Federated Learning
    FL_EPOCHS = int(os.getenv('FL_EPOCHS', 3))
    FL_LEARNING_RATE = float(os.getenv('FL_LEARNING_RATE', 0.01))
    GRADIENT_COMPRESSION_RATIO = float(os.getenv('GRADIENT_COMPRESSION_RATIO', 0.3))
    
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///marketplace.db')
    REDIS_URL = os.getenv('REDIS_URL', None)
    
    # API Keys
    ETHEREUM_RPC_URL = os.getenv('ETHEREUM_RPC_URL', '')
    INFURA_API_KEY = os.getenv('INFURA_API_KEY', '')
    ALCHEMY_API_KEY = os.getenv('ALCHEMY_API_KEY', '')
    
    # Monitoring
    ENABLE_METRICS = os.getenv('ENABLE_METRICS', 'True').lower() == 'true'
    METRICS_PORT = int(os.getenv('METRICS_PORT', 9090))
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/marketplace.log')
    
    # Performance
    TARGET_TPS = int(os.getenv('TARGET_TPS', 1000))
    MAX_LATENCY_MS = int(os.getenv('MAX_LATENCY_MS', 100))
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        required = ['SECRET_KEY']
        for key in required:
            if not getattr(cls, key) or getattr(cls, key) == 'dev-secret-key-change-in-production':
                if cls.FLASK_ENV == 'production':
                    raise ValueError(f"{key} must be set in production")
        
        return True