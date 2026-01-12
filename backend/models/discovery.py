import time
from collections
import defaultdict
from typing import Dict, List, Optional

class DiscoveryService:
    """
    Discovery service for agent registration and dataset search
    """
    
    def __init__(self, embedding_system):
        self.embedding_system = embedding_system
        self.registered_agents = {}
        self.dataset_registry = {}
        self.agent_endpoints = {}
        self.schema_versions = defaultdict(int)
        self.rfq_broadcasts = []
    
    def register_provider(self, agent_id: str, endpoint: str, agent_wallet) -> bool:
        """Register data provider agent"""
        agent_info = {
            'agent_id': agent_id,
            'endpoint': endpoint,
            'wallet_address': agent_wallet.address,
            'registered_at': time.time(),
            'reputation_score': 1.0,
            'total_sales': 0,
            'datasets': []
        }
        
        self.registered_agents[agent_id] = agent_info
        self.agent_endpoints[endpoint] = agent_id
        
        return True
    
    def register_dataset(self, agent_id: str, dataset_info: Dict) -> str:
        """Register dataset with standardized metadata"""
        if agent_id not in self.registered_agents:
            return None
        
        dataset_id = f"ds_{len(self.dataset_registry)}_{int(time.time())}"
        
        schema = {
            '@context': 'https://schema.org/',
            '@type': 'Dataset',
            'identifier': dataset_id,
            'name': dataset_info['name'],
            'description': dataset_info['description'],
            'provider': agent_id,
            'price_mnee': dataset_info['price'],
            'currency': 'MNEE',
            'size_bytes': dataset_info.get('size', 0),
            'row_count': dataset_info.get('rows', 0),
            'column_count': dataset_info.get('columns', 0),
            'format': dataset_info.get('format', 'csv'),
            'categories': dataset_info.get('categories', []),
            'tags': dataset_info.get('tags', []),
            'industry': dataset_info.get('industry', 'general'),
            'use_cases': dataset_info.get('use_cases', []),
            'quality_score': dataset_info.get('quality_score', 0.5),
            'completeness': dataset_info.get('completeness', 1.0),
            'temporal_coverage': dataset_info.get('temporal_coverage', {}),
            'spatial_coverage': dataset_info.get('spatial_coverage', {}),
            'update_frequency': dataset_info.get('update_frequency', 'static'),
            'last_updated': time.time(),
            'license': dataset_info.get('license', 'proprietary'),
            'access_type': dataset_info.get('access_type', 'full'),
            'sample_available': dataset_info.get('sample_available', True),
            'sample_price': int(dataset_info['price'] * 0.01),
            'schema': dataset_info.get('schema', {}),
            'data_types': dataset_info.get('data_types', []),
            'created_at': time.time()
        }
        
        self.dataset_registry[dataset_id] = schema
        self.registered_agents[agent_id]['datasets'].append(dataset_id)
        
        embedding_text = f"{schema['name']} {schema['description']} {schema['industry']}"
        self.embedding_system.add_dataset(dataset_id, embedding_text, schema)
        
        self.schema_versions[dataset_id] = 1
        
        return dataset_id
    
    def broadcast_rfq(self, buyer_id: str, data_intent: Dict) -> str:
        """Broadcast Request for Quote"""
        rfq_id = f"rfq_{len(self.rfq_broadcasts)}_{int(time.time())}"
        
        rfq = {
            'rfq_id': rfq_id,
            'buyer': buyer_id,
            'data_intent': data_intent,
            'timestamp': time.time(),
            'responses': []
        }
        
        self.rfq_broadcasts.append(rfq)
        return rfq_id
    
    def search_datasets(self, query: str, filters: Dict = None) -> List[Dict]:
        """Search datasets with semantic matching"""
        results = self.embedding_system.search(query, filters=filters)
        
        filtered_results = []
        for dataset_id, similarity, match_details in results:
            if dataset_id not in self.dataset_registry:
                continue
            
            dataset = self.dataset_registry[dataset_id]
            
            filtered_results.append({
                'dataset_id': dataset_id,
                'similarity_score': similarity,
                'dataset_info': dataset,
                'match_details': match_details
            })
        
        return filtered_results
    
    def get_dataset_info(self, dataset_id: str) -> Optional[Dict]:
        """Get dataset information"""
        return self.dataset_registry.get(dataset_id)
    
    def get_provider_info(self, agent_id: str) -> Optional[Dict]:
        """Get provider information"""
        return self.registered_agents.get(agent_id)
    
    def get_dataset_sample(self, dataset_id: str, sample_size: int = 100) -> Optional[Dict]:
        """Get dataset sample info"""
        if dataset_id not in self.dataset_registry:
            return None
        
        dataset = self.dataset_registry[dataset_id]
        
        return {
            'dataset_id': dataset_id,
            'sample_size': sample_size,
            'sample_price': dataset['sample_price'],
            'schema': dataset.get('schema', {}),
            'preview_available': dataset['sample_available']
        }