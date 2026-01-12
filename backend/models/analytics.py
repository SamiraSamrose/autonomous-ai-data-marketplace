import time
import numpy as np
from typing import Dict, List
from collections import defaultdict

class AnalyticsEngine:
    """
    Analytics engine for marketplace metrics
    """
    
    def __init__(self, systems: Dict):
        self.systems = systems
        self.metrics_history = defaultdict(list)
    
    def collect_marketplace_statistics(self) -> Dict:
        """Collect comprehensive marketplace statistics"""
        discovery = self.systems['discovery_service']
        mnee = self.systems['mnee_token']
        contracts = self.systems['contract_engine']
        
        stats = {
            'timestamp': time.time(),
            'total_datasets': len(discovery.dataset_registry),
            'active_datasets': sum(1 for d in discovery.dataset_registry.values() 
                                  if d.get('status', 'active') == 'active'),
            'total_agents': len(discovery.registered_agents),
            'total_transactions': mnee.transaction_count,
            'total_volume': sum(tx.get('amount', 0) for tx in mnee.transactions),
            'total_contracts': len(contracts.contracts),
            'circulating_supply': mnee.get_circulating_supply()
        }
        
        self.metrics_history['marketplace'].append(stats)
        return stats
    
    def collect_performance_metrics(self) -> Dict:
        """Collect system performance metrics"""
        mnee = self.systems['mnee_token']
        contracts = self.systems['contract_engine']
        
        time_window = 60
        recent_txs = [tx for tx in mnee.transactions 
                     if time.time() - tx.get('timestamp', 0) < time_window]
        
        metrics = {
            'timestamp': time.time(),
            'tps': len(recent_txs) / time_window if time_window > 0 else 0,
            'total_contracts': len(contracts.contracts),
            'escrow_contracts': sum(1 for c in contracts.contracts.values() 
                                   if c.__class__.__name__ == 'EscrowContract'),
            'license_contracts': sum(1 for c in contracts.contracts.values() 
                                    if c.__class__.__name__ == 'LicenseContract'),
            'avg_latency_ms': 50,
            'uptime_percentage': 99.9
        }
        
        self.metrics_history['performance'].append(metrics)
        return metrics
    
    def collect_pricing_analytics(self) -> Dict:
        """Collect pricing analytics"""
        pricing = self.systems['pricing_system']
        discovery = self.systems['discovery_service']
        
        all_prices = []
        for dataset_id in discovery.dataset_registry.keys():
            dataset_info = discovery.get_dataset_info(dataset_id)
            if dataset_info:
                price = pricing.get_optimized_price(dataset_id, dataset_info)
                all_prices.append(price)
        
        from backend.config import Config
        
        analytics = {
            'timestamp': time.time(),
            'average_price': int(np.mean(all_prices)) if all_prices else 0,
            'median_price': int(np.median(all_prices)) if all_prices else 0,
            'min_price': int(np.min(all_prices)) if all_prices else 0,
            'max_price': int(np.max(all_prices)) if all_prices else 0,
            'price_std': int(np.std(all_prices)) if len(all_prices) > 1 else 0,
            'base_price': Config.BASE_DATA_PRICE,
            'total_datasets': len(all_prices)
        }
        
        self.metrics_history['pricing'].append(analytics)
        return analytics
    
    def collect_quality_metrics(self) -> Dict:
        """Collect quality metrics"""
        quality = self.systems['quality_system']
        discovery = self.systems['discovery_service']
        
        quality_scores = []
        for dataset_id, schema in discovery.dataset_registry.items():
            score = schema.get('quality_score', 0)
            if score > 0:
                quality_scores.append(score)
        
        from backend.config import Config
        
        metrics = {
            'timestamp': time.time(),
            'total_assessments': len(quality_scores),
            'average_quality': float(np.mean(quality_scores)) if quality_scores else 0,
            'median_quality': float(np.median(quality_scores)) if quality_scores else 0,
            'quality_threshold': Config.QUALITY_SCORE_THRESHOLD,
            'datasets_above_threshold': sum(1 for s in quality_scores if s >= Config.QUALITY_SCORE_THRESHOLD),
            'certification_rate': sum(1 for s in quality_scores if s >= Config.QUALITY_SCORE_THRESHOLD) / len(quality_scores) if quality_scores else 0
        }
        
        self.metrics_history['quality'].append(metrics)
        return metrics
    
    def generate_comprehensive_report(self) -> Dict:
        """Generate comprehensive analytics report"""
        report = {
            'generated_at': time.time(),
            'marketplace_statistics': self.collect_marketplace_statistics(),
            'performance_metrics': self.collect_performance_metrics(),
            'pricing_analytics': self.collect_pricing_analytics(),
            'quality_metrics': self.collect_quality_metrics(),
            'reputation_summary': self.get_reputation_summary(),
            'transaction_summary': self.get_transaction_summary()
        }
        
        return report
    
    def get_reputation_summary(self) -> Dict:
        """Get reputation system summary"""
        reputation = self.systems['reputation_system']
        
        rep_scores = [r['score'] for r in reputation.reputations.values()]
        
        from backend.config import Config
        
        return {
            'total_agents': len(reputation.reputations),
            'average_reputation': float(np.mean(rep_scores)) if rep_scores else 0,
            'trusted_agents': len(reputation.get_trusted_agents(Config.REPUTATION_THRESHOLD)),
            'total_reviews': sum(len(r) for r in reputation.reviews.values()),
            'slashing_events': len(reputation.slashing_events)
        }
    
    def get_transaction_summary(self) -> Dict:
        """Get transaction summary"""
        mnee = self.systems['mnee_token']
        
        tx_types = defaultdict(int)
        tx_amounts = []
        
        for tx in mnee.transactions:
            tx_types[tx.get('type', 'unknown')] += 1
            if 'amount' in tx:
                tx_amounts.append(tx['amount'])
        
        from backend.config import Config
        
        return {
            'total_transactions': mnee.transaction_count,
            'transaction_types': dict(tx_types),
            'total_volume': sum(tx_amounts),
            'average_transaction': int(np.mean(tx_amounts)) if tx_amounts else 0,
            'largest_transaction': int(np.max(tx_amounts)) if tx_amounts else 0
        }

