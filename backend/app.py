import os
import sys
import logging
from datetime import datetime
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from backend.config import Config
from backend.api.routes import register_routes
from backend.models.mnee_token import MNEEToken
from backend.models.smart_contracts import SmartContractEngine
from backend.models.discovery import DiscoveryService
from backend.models.quality import QualityAssessment
from backend.models.pricing import DynamicPricing
from backend.models.reputation import ReputationSystem
from backend.utils.embeddings import VectorEmbedding
from backend.utils.atomic_swap import AtomicSwapEngine

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Config.LOG_FILE) if os.path.exists(os.path.dirname(Config.LOG_FILE) or '.') else logging.StreamHandler(),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, 
            static_folder='../frontend/static',
            template_folder='../frontend/templates')

app.config.from_object(Config)
CORS(app)

# Initialize core systems
logger.info("Initializing Autonomous AI Data Marketplace...")

try:
    # MNEE Token System
    mnee_token = MNEEToken()
    app.mnee_token = mnee_token
    logger.info("MNEE Token system initialized")
    
    # Smart Contract Engine
    contract_engine = SmartContractEngine()
    app.contract_engine = contract_engine
    logger.info("Smart Contract Engine initialized")
    
    # Vector Embedding System
    embedding_system = VectorEmbedding(Config.VECTOR_EMBEDDING_DIM)
    app.embedding_system = embedding_system
    logger.info("Vector Embedding System initialized")
    
    # Discovery Service
    discovery_service = DiscoveryService(embedding_system)
    app.discovery_service = discovery_service
    logger.info("Discovery Service initialized")
    
    # Quality Assessment
    quality_system = QualityAssessment()
    app.quality_system = quality_system
    logger.info("Quality Assessment System initialized")
    
    # Dynamic Pricing
    pricing_system = DynamicPricing()
    app.pricing_system = pricing_system
    logger.info("Dynamic Pricing System initialized")
    
    # Reputation System
    reputation_system = ReputationSystem(mnee_token)
    app.reputation_system = reputation_system
    logger.info("Reputation System initialized")
    
    # Atomic Swap Engine
    atomic_swap_engine = AtomicSwapEngine(mnee_token, contract_engine)
    app.atomic_swap_engine = atomic_swap_engine
    logger.info("Atomic Swap Engine initialized")
    
    # Store systems globally for API access
    app.systems = {
        'mnee_token': mnee_token,
        'contract_engine': contract_engine,
        'embedding_system': embedding_system,
        'discovery_service': discovery_service,
        'quality_system': quality_system,
        'pricing_system': pricing_system,
        'reputation_system': reputation_system,
        'atomic_swap_engine': atomic_swap_engine
    }
    
    logger.info("All systems initialized successfully")
    
except Exception as e:
    logger.error(f"Failed to initialize systems: {str(e)}")
    sys.exit(1)

# Register API routes
register_routes(app)
logger.info("API routes registered")

# Frontend routes
@app.route('/')
def index():
    """Dashboard homepage"""
    return render_template('index.html')

@app.route('/datasets')
def datasets_page():
    """Dataset marketplace page"""
    return render_template('datasets.html')

@app.route('/analytics')
def analytics_page():
    """Analytics dashboard page"""
    return render_template('analytics.html')

@app.route('/transactions')
def transactions_page():
    """Transaction history page"""
    return render_template('transactions.html')

# Health check endpoint
@app.route('/health')
def health_check():
    """System health check"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'systems': {
            'mnee_token': 'operational',
            'smart_contracts': 'operational',
            'discovery': 'operational',
            'quality': 'operational',
            'pricing': 'operational',
            'reputation': 'operational'
        }
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(Exception)
def handle_exception(error):
    """Handle all exceptions"""
    logger.error(f"Unhandled exception: {str(error)}")
    return jsonify({'error': str(error)}), 500

# Application startup
if __name__ == '__main__':
    try:
        Config.validate()
        logger.info(f"Starting server on {Config.HOST}:{Config.PORT}")
        logger.info(f"Environment: {Config.FLASK_ENV}")
        logger.info(f"Debug mode: {Config.DEBUG}")
        
        app.run(
            host=Config.HOST,
            port=Config.PORT,
            debug=Config.DEBUG
        )
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        sys.exit(1)