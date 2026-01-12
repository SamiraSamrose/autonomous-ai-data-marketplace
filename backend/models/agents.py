import time
import secrets
import pandas as pd
from typing import Dict, List, Optional, Tuple
from backend.utils.crypto import CryptoUtils

crypto = CryptoUtils()

class AgentWallet:
    """
    Non-custodial wallet for AI agents
    Manages MNEE holdings and transaction signing
    """
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.address = "0x" + secrets.token_hex(20)
        self.private_key, self.public_key = crypto.generate_keypair()
        self.nonce = 0
        self.pending_transactions = []
        self.transaction_history = []
    
    def get_balance(self, mnee_token) -> int:
        """Get MNEE balance"""
        return mnee_token.balance_of(self.address)
    
    def get_staked_balance(self, mnee_token) -> int:
        """Get staked MNEE balance"""
        return mnee_token.staked_amounts[self.address]
    
    def sign_transaction(self, tx_data: Dict) -> Dict:
        """Sign transaction with private key"""
        import json
        
        tx_data['nonce'] = self.nonce
        tx_data['from'] = self.address
        tx_data['timestamp'] = time.time()
        
        message = json.dumps(tx_data, sort_keys=True)
        signature = crypto.sign_message(self.private_key, message)
        
        self.nonce += 1
        
        return {
            'tx_data': tx_data,
            'signature': signature.hex(),
            'public_key': self.public_key
        }
    
    def send_mnee(self, mnee_token, to_address: str, amount: int) -> bool:
        """Send MNEE to another address"""
        if self.get_balance(mnee_token) < amount:
            return False
        
        tx_data = {
            'type': 'transfer',
            'to': to_address,
            'amount': amount
        }
        
        signed_tx = self.sign_transaction(tx_data)
        success = mnee_token.transfer(self.address, to_address, amount)
        
        if success:
            self.transaction_history.append(signed_tx)
        
        return success
    
    def stake_mnee(self, mnee_token, amount: int) -> bool:
        """Stake MNEE for reputation"""
        if self.get_balance(mnee_token) < amount:
            return False
        return mnee_token.stake(self.address, amount)

class DataProviderAgent:
    """
    Data provider agent that lists and sells datasets
    """
    
    def __init__(self, agent_id: str, agent_name: str, systems: Dict):
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.wallet = AgentWallet(agent_id)
        self.datasets = {}
        self.sales_history = []
        self.active_listings = {}
        self.systems = systems
        
        # Initialize in discovery service
        endpoint = f"https://provider-{agent_id}.marketplace.ai/api"
        systems['discovery_service'].register_provider(agent_id, endpoint, self.wallet)
        
        # Initialize reputation
        from backend.config import Config
        initial_stake = Config.MIN_STAKE_AMOUNT * 2
        systems['mnee_token'].mint(self.wallet.address, initial_stake)
        self.wallet.stake_mnee(systems['mnee_token'], initial_stake)
        systems['reputation_system'].initialize_reputation(self.wallet.address, initial_stake)
    
    def list_dataset(self, dataset_info: Dict, data: pd.DataFrame) -> str:
        """List dataset on marketplace"""
        quality_system = self.systems['quality_system']
        discovery = self.systems['discovery_service']
        
        # Assess quality
        quality_report = quality_system.assess_dataset(data)
        attestation = quality_system.generate_attestation(
            f"temp_{self.agent_id}",
            quality_report,
            'system_auditor'
        )
        
        # Enhanced registration
        registration_info = {
            'name': dataset_info['name'],
            'description': dataset_info['description'],
            'price': dataset_info.get('price'),
            'rows': len(data),
            'columns': len(data.columns),
            'size': len(data) * len(data.columns) * 8,
            'format': 'csv',
            'categories': dataset_info.get('categories', []),
            'tags': dataset_info.get('tags', []),
            'industry': dataset_info.get('industry', 'general'),
            'use_cases': dataset_info.get('use_cases', []),
            'quality_score': quality_report['quality_score'],
            'completeness': quality_report['completeness']['complete_ratio'],
            'schema': quality_report.get('schema_info', {}),
            'sample_available': True,
            'attestation_id': attestation['attestation_id']
        }
        
        dataset_id = discovery.register_dataset(self.agent_id, registration_info)
        
        if dataset_id:
            self.datasets[dataset_id] = {
                'data': data,
                'info': registration_info,
                'quality_report': quality_report,
                'attestation': attestation,
                'listed_at': time.time()
            }
            
            self.active_listings[dataset_id] = {
                'dataset_id': dataset_id,
                'price': registration_info['price'],
                'status': 'active',
                'views': 0,
                'inquiries': 0
            }
        
        return dataset_id
    
    def provide_sample(self, dataset_id: str, buyer: str) -> Dict:
        """Provide sample for evaluation"""
        if dataset_id not in self.datasets:
            return {'success': False, 'error': 'dataset_not_found'}
        
        dataset = self.datasets[dataset_id]
        full_data = dataset['data']
        
        sample_size = max(int(len(full_data) * 0.01), 10)
        sample = full_data.sample(n=sample_size, random_state=42)
        
        from backend.config import Config
        sample_price = int(0.01 * (10**Config.MNEE_DECIMALS))
        
        return {
            'success': True,
            'sample_data': sample.to_dict(),
            'sample_size': sample_size,
            'sample_price': sample_price,
            'full_dataset_price': dataset['info']['price'],
            'quality_score': dataset['quality_report']['quality_score']
        }
    
    def handle_purchase_request(self, buyer_agent: str, dataset_id: str,
                                offer_terms: Dict) -> Dict:
        """Handle purchase request with atomic swap"""
        if dataset_id not in self.datasets:
            return {'success': False, 'error': 'dataset_not_found'}
        
        listing = self.active_listings.get(dataset_id)
        if not listing or listing['status'] != 'active':
            return {'success': False, 'error': 'listing_not_available'}
        
        discovery = self.systems['discovery_service']
        pricing = self.systems['pricing_system']
        atomic_swap = self.systems['atomic_swap_engine']
        reputation = self.systems['reputation_system']
        
        dataset_info = discovery.get_dataset_info(dataset_id)
        current_price = pricing.get_optimized_price(dataset_id, dataset_info)
        offered_price = offer_terms.get('price', 0)
        
        if offered_price < current_price * 0.90:
            return {
                'success': False,
                'error': 'price_too_low',
                'counter_offer': current_price
            }
        
        # Initiate atomic swap
        swap_id = f"swap_{dataset_id}_{int(time.time())}"
        sla_terms = {
            'min_uptime': 0.99,
            'max_latency_ms': 100,
            'support_hours': 24
        }
        
        swap_result = atomic_swap.initiate_atomic_swap(
            swap_id,
            buyer_agent,
            self.wallet.address,
            offered_price,
            dataset_id,
            sla_terms
        )
        
        if not swap_result['success']:
            return swap_result
        
        # Record sale
        sale_record = {
            'dataset_id': dataset_id,
            'buyer': buyer_agent,
            'price': offered_price,
            'swap_id': swap_id,
            'timestamp': time.time()
        }
        
        self.sales_history.append(sale_record)
        listing['status'] = 'pending_completion'
        
        reputation.record_transaction(self.wallet.address, True, offered_price)
        
        return {
            'success': True,
            'swap_id': swap_id,
            'price': offered_price,
            'sla_terms': sla_terms
        }
    
    def get_performance_metrics(self) -> Dict:
        """Get provider performance metrics"""
        total_sales = len(self.sales_history)
        total_revenue = sum(s['price'] for s in self.sales_history)
        
        reputation = self.systems['reputation_system'].get_reputation(self.wallet.address)
        
        return {
            'agent_id': self.agent_id,
            'total_datasets': len(self.datasets),
            'active_listings': sum(1 for l in self.active_listings.values() if l['status'] == 'active'),
            'total_sales': total_sales,
            'total_revenue': total_revenue,
            'avg_sale_price': total_revenue / total_sales if total_sales > 0 else 0,
            'reputation_score': reputation['score'] if reputation else 0,
            'wallet_balance': self.wallet.get_balance(self.systems['mnee_token']),
            'staked_balance': self.wallet.get_staked_balance(self.systems['mnee_token'])
        }

class DataBuyerAgent:
    """
    Data buyer agent with autonomous procurement capabilities
    """
    
    def __init__(self, agent_id: str, agent_name: str, budget: int, systems: Dict):
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.wallet = AgentWallet(agent_id)
        self.budget = budget
        self.purchased_datasets = {}
        self.evaluated_samples = {}
        self.systems = systems
        
        systems['mnee_token'].mint(self.wallet.address, budget)
    
    def search_datasets(self, query: str, filters: Dict = None, 
                       relaxed: bool = False) -> List[Dict]:
        """Search for datasets with optional relaxed filters"""
        discovery = self.systems['discovery_service']
        pricing = self.systems['pricing_system']
        
        results = discovery.search_datasets(query, filters)
        
        if len(results) == 0 and relaxed and filters:
            if 'max_price' in filters:
                filters['max_price'] = int(filters['max_price'] * 1.5)
            if 'categories' in filters:
                del filters['categories']
            results = discovery.search_datasets(query, filters)
        
        evaluated = []
        for result in results:
            dataset_id = result['dataset_id']
            dataset_info = result['dataset_info']
            
            pricing.update_demand_metrics(dataset_id, 'view')
            
            quality_score = dataset_info.get('quality_score', 0.5)
            price = pricing.get_optimized_price(dataset_id, dataset_info)
            similarity = result['similarity_score']
            
            from backend.config import Config
            price_factor = price / Config.BASE_DATA_PRICE
            value_score = (quality_score * similarity) / max(price_factor, 0.5)
            
            match_score = (similarity * 0.4 + quality_score * 0.3 + 
                          min(1.0, self.budget / price) * 0.3)
            
            evaluated.append({
                'dataset_id': dataset_id,
                'info': dataset_info,
                'similarity_score': similarity,
                'quality_score': quality_score,
                'value_score': value_score,
                'match_score': match_score,
                'current_price': price
            })
        
        evaluated.sort(key=lambda x: x['match_score'], reverse=True)
        return evaluated
    
    def evaluate_sample(self, dataset_id: str, provider: DataProviderAgent) -> Dict:
        """Evaluate dataset sample"""
        sample_response = provider.provide_sample(dataset_id, self.wallet.address)
        
        if not sample_response['success']:
            return {'success': False, 'error': sample_response.get('error')}
        
        sample_price = sample_response['sample_price']
        payment_success = self.wallet.send_mnee(
            self.systems['mnee_token'],
            provider.wallet.address,
            sample_price
        )
        
        if not payment_success:
            return {'success': False, 'error': 'sample_payment_failed'}
        
        sample_df = pd.DataFrame(sample_response['sample_data'])
        sample_assessment = self.systems['quality_system'].assess_dataset(sample_df)
        
        evaluation = {
            'dataset_id': dataset_id,
            'sample_quality': sample_assessment['quality_score'],
            'full_quality': sample_response['quality_score'],
            'quality_match': abs(sample_assessment['quality_score'] - sample_response['quality_score']) < 0.1,
            'null_percentage': sample_assessment['completeness']['missing_ratio'],
            'recommendation': 'proceed' if sample_assessment['quality_score'] > 0.7 else 'reject'
        }
        
        self.evaluated_samples[dataset_id] = evaluation
        return {'success': True, 'evaluation': evaluation}
    
    def execute_purchase(self, dataset_id: str, provider: DataProviderAgent,
                        agreed_price: int, terms: Dict) -> Dict:
        """Execute dataset purchase"""
        if self.wallet.get_balance(self.systems['mnee_token']) < agreed_price:
            return {'success': False, 'error': 'insufficient_funds'}
        
        purchase_response = provider.handle_purchase_request(
            self.wallet.address, dataset_id, {'price': agreed_price, **terms}
        )
        
        if not purchase_response['success']:
            return purchase_response
        
        swap_id = purchase_response['swap_id']
        verification_result = self.systems['atomic_swap_engine'].verify_and_complete(swap_id)
        
        if not verification_result['success']:
            return verification_result
        
        self.purchased_datasets[dataset_id] = {
            'dataset_id': dataset_id,
            'provider': provider.agent_id,
            'price_paid': agreed_price,
            'swap_id': swap_id,
            'purchased_at': time.time()
        }
        
        self.systems['pricing_system'].update_demand_metrics(dataset_id, 'purchase')
        
        self.systems['reputation_system'].submit_review(
            self.wallet.address,
            provider.wallet.address,
            0.9,
            "Quality dataset, atomic swap successful",
            swap_id
        )
        
        return {
            'success': True,
            'dataset_id': dataset_id,
            'purchase_details': purchase_response
        }
    
    def autonomous_procurement(self, requirements: Dict) -> List[Dict]:
        """Autonomous dataset procurement"""
        query = requirements['query']
        max_price_per_dataset = requirements.get('max_price', self.budget // 2)
        min_quality = requirements.get('min_quality', 0.65)
        
        results = self.search_datasets(
            query,
            requirements.get('filters'),
            relaxed=True
        )
        
        recommendations = []
        for result in results[:5]:
            dataset_id = result['dataset_id']
            
            if result['current_price'] > max_price_per_dataset:
                continue
            
            if result['quality_score'] < min_quality:
                continue
            
            if result['match_score'] < 0.5:
                continue
            
            recommendations.append({
                'dataset_id': dataset_id,
                'provider_id': result['info']['provider'],
                'recommended_price': result['current_price'],
                'quality_score': result['quality_score'],
                'value_score': result['value_score'],
                'match_score': result['match_score']
            })
        
        return recommendations
    
    def get_purchase_summary(self) -> Dict:
        """Get purchase summary"""
        total_spent = sum(p['price_paid'] for p in self.purchased_datasets.values())
        
        return {
            'agent_id': self.agent_id,
            'total_datasets_purchased': len(self.purchased_datasets),
            'total_spent': total_spent,
            'remaining_budget': self.wallet.get_balance(self.systems['mnee_token']),
            'avg_dataset_price': total_spent / len(self.purchased_datasets) if self.purchased_datasets else 0,
            'purchases': list(self.purchased_datasets.values())
        }