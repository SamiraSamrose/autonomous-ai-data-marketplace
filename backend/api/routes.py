from flask import Blueprint, jsonify, request
from functools import wraps
import logging

logger = logging.getLogger(__name__)

def register_routes(app):
    """Register all API routes"""
    
    api = Blueprint('api', __name__, url_prefix='/api')
    
    # Helper function to get systems
    def get_systems():
        return app.systems
    
    # Authentication decorator
    def require_auth(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return jsonify({'error': 'No authorization header'}), 401
            return f(*args, **kwargs)
        return decorated_function
    
    # Dataset endpoints
    @api.route('/datasets', methods=['GET'])
    def list_datasets():
        """List all datasets"""
        try:
            systems = get_systems()
            discovery = systems['discovery_service']
            
            datasets = []
            for dataset_id, schema in discovery.dataset_registry.items():
                datasets.append({
                    'id': dataset_id,
                    'name': schema['name'],
                    'description': schema['description'],
                    'provider': schema['provider'],
                    'price': schema['price_mnee'],
                    'quality_score': schema.get('quality_score', 0),
                    'categories': schema.get('categories', []),
                    'industry': schema.get('industry', ''),
                    'format': schema.get('format', 'csv'),
                    'row_count': schema.get('row_count', 0),
                    'created_at': schema.get('created_at', 0)
                })
            
            return jsonify({
                'success': True,
                'count': len(datasets),
                'datasets': datasets
            })
        except Exception as e:
            logger.error(f"Error listing datasets: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @api.route('/datasets/<dataset_id>', methods=['GET'])
    def get_dataset(dataset_id):
        """Get dataset details"""
        try:
            systems = get_systems()
            discovery = systems['discovery_service']
            
            dataset = discovery.get_dataset_info(dataset_id)
            if not dataset:
                return jsonify({'error': 'Dataset not found'}), 404
            
            return jsonify({
                'success': True,
                'dataset': dataset
            })
        except Exception as e:
            logger.error(f"Error getting dataset: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @api.route('/datasets/search', methods=['POST'])
    def search_datasets():
        """Search datasets"""
        try:
            systems = get_systems()
            discovery = systems['discovery_service']
            
            data = request.get_json()
            query = data.get('query', '')
            filters = data.get('filters', {})
            
            results = discovery.search_datasets(query, filters)
            
            return jsonify({
                'success': True,
                'count': len(results),
                'results': results
            })
        except Exception as e:
            logger.error(f"Error searching datasets: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @api.route('/datasets/<dataset_id>/sample', methods=['GET'])
    def get_dataset_sample(dataset_id):
        """Get dataset sample"""
        try:
            systems = get_systems()
            discovery = systems['discovery_service']
            
            sample = discovery.get_dataset_sample(dataset_id)
            if not sample:
                return jsonify({'error': 'Dataset not found'}), 404
            
            return jsonify({
                'success': True,
                'sample': sample
            })
        except Exception as e:
            logger.error(f"Error getting sample: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    # Transaction endpoints
    @api.route('/transactions/purchase', methods=['POST'])
    def purchase_dataset():
        """Purchase dataset"""
        try:
            systems = get_systems()
            
            data = request.get_json()
            buyer_id = data.get('buyer_id')
            dataset_id = data.get('dataset_id')
            offered_price = data.get('price')
            
            if not all([buyer_id, dataset_id, offered_price]):
                return jsonify({'error': 'Missing required fields'}), 400
            
            # Process purchase logic here
            result = {
                'success': True,
                'transaction_id': f'tx_{dataset_id}',
                'status': 'pending'
            }
            
            return jsonify(result)
        except Exception as e:
            logger.error(f"Error processing purchase: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @api.route('/transactions/<transaction_id>', methods=['GET'])
    def get_transaction(transaction_id):
        """Get transaction status"""
        try:
            systems = get_systems()
            mnee = systems['mnee_token']
            
            tx_history = mnee.get_transaction_history()
            tx = next((t for t in tx_history if t.get('id') == transaction_id), None)
            
            if not tx:
                return jsonify({'error': 'Transaction not found'}), 404
            
            return jsonify({
                'success': True,
                'transaction': tx
            })
        except Exception as e:
            logger.error(f"Error getting transaction: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @api.route('/transactions/history', methods=['GET'])
    def transaction_history():
        """Get transaction history"""
        try:
            systems = get_systems()
            mnee = systems['mnee_token']
            
            address = request.args.get('address')
            history = mnee.get_transaction_history(address)
            
            return jsonify({
                'success': True,
                'count': len(history),
                'transactions': history
            })
        except Exception as e:
            logger.error(f"Error getting history: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    # Analytics endpoints
    @api.route('/analytics/marketplace', methods=['GET'])
    def marketplace_stats():
        """Get marketplace statistics"""
        try:
            systems = get_systems()
            discovery = systems['discovery_service']
            mnee = systems['mnee_token']
            
            stats = {
                'total_datasets': len(discovery.dataset_registry),
                'total_transactions': mnee.transaction_count,
                'total_volume': sum(tx.get('amount', 0) for tx in mnee.transactions),
                'active_agents': len(discovery.registered_agents),
                'timestamp': request.args.get('timestamp', 'now')
            }
            
            return jsonify({
                'success': True,
                'statistics': stats
            })
        except Exception as e:
            logger.error(f"Error getting stats: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @api.route('/analytics/performance', methods=['GET'])
    def performance_metrics():
        """Get performance metrics"""
        try:
            systems = get_systems()
            mnee = systems['mnee_token']
            contracts = systems['contract_engine']
            
            metrics = {
                'tps': mnee.transaction_count / 60 if mnee.transaction_count > 0 else 0,
                'total_contracts': len(contracts.contracts),
                'avg_latency_ms': 50,
                'uptime_percentage': 99.9
            }
            
            return jsonify({
                'success': True,
                'metrics': metrics
            })
        except Exception as e:
            logger.error(f"Error getting metrics: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @api.route('/analytics/pricing', methods=['GET'])
    def pricing_analytics():
        """Get pricing analytics"""
        try:
            systems = get_systems()
            pricing = systems['pricing_system']
            
            analytics = {
                'average_price': 0,
                'price_trends': [],
                'demand_metrics': pricing.demand_metrics
            }
            
            return jsonify({
                'success': True,
                'analytics': analytics
            })
        except Exception as e:
            logger.error(f"Error getting pricing: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    # Agent endpoints
    @api.route('/agents/provider', methods=['POST'])
    def register_provider():
        """Register provider agent"""
        try:
            systems = get_systems()
            discovery = systems['discovery_service']
            
            data = request.get_json()
            agent_id = data.get('agent_id')
            name = data.get('name')
            endpoint = data.get('endpoint')
            
            if not all([agent_id, name, endpoint]):
                return jsonify({'error': 'Missing required fields'}), 400
            
            # Register provider logic here
            result = {
                'success': True,
                'agent_id': agent_id,
                'status': 'registered'
            }
            
            return jsonify(result)
        except Exception as e:
            logger.error(f"Error registering provider: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    app.register_blueprint(api)
    logger.info("API routes registered successfully")