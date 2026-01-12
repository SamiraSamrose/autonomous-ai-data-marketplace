import time
import numpy as np
from collections import defaultdict
from typing import Dict, List

class DynamicPricing:
    """
    Dynamic pricing with bonding curves and market-based adjustments
    """
    
    def __init__(self):
        self.price_history = defaultdict(list)
        self.demand_metrics = defaultdict(lambda: {'views': 0, 'purchases': 0})
    
    def calculate_bonding_curve_price(self, base_price: int, supply: int, 
                                     demand: int, curve_type: str = 'sigmoid') -> int:
        """Calculate price using bonding curve algorithm"""
        if curve_type == 'linear':
            if supply == 0:
                return base_price
            demand_ratio = demand / supply
            price = int(base_price * (1 + demand_ratio))
            
        elif curve_type == 'exponential':
            if supply == 0:
                return base_price
            demand_ratio = demand / supply
            price = int(base_price * np.exp(demand_ratio * 0.5))
            
        elif curve_type == 'sigmoid':
            if supply == 0:
                return base_price
            demand_ratio = demand / supply
            sigmoid = 1 / (1 + np.exp(-demand_ratio))
            price = int(base_price * (1 + sigmoid))
            
        else:
            price = base_price
        
        return price
    
    def update_demand_metrics(self, dataset_id: str, event_type: str):
        """Track demand metrics for pricing"""
        if event_type == 'view':
            self.demand_metrics[dataset_id]['views'] += 1
        elif event_type == 'purchase':
            self.demand_metrics[dataset_id]['purchases'] += 1
    
    def get_current_price(self, dataset_id: str, base_price: int,
                         current_supply: int = 1) -> int:
        """Get current dynamic price for dataset"""
        metrics = self.demand_metrics[dataset_id]
        
        # Calculate demand (weighted: purchase > view)
        demand = metrics['purchases'] * 10 + metrics['views']
        
        # Apply bonding curve
        current_price = self.calculate_bonding_curve_price(
            base_price, current_supply, demand, 'sigmoid'
        )
        
        # Record price history
        self.price_history[dataset_id].append({
            'price': current_price,
            'demand': demand,
            'timestamp': time.time()
        })
        
        return current_price
    
    def calculate_freshness_multiplier(self, last_updated: float) -> float:
        """Calculate price multiplier based on data freshness"""
        age_days = (time.time() - last_updated) / 86400
        
        if age_days < 1:
            return 1.5
        elif age_days < 7:
            return 1.2
        elif age_days < 30:
            return 1.0
        elif age_days < 90:
            return 0.8
        else:
            return 0.5
    
    def calculate_quality_multiplier(self, quality_score: float) -> float:
        """Calculate price multiplier based on quality"""
        if quality_score >= 0.9:
            return 1.5
        elif quality_score >= 0.8:
            return 1.2
        elif quality_score >= 0.7:
            return 1.0
        elif quality_score >= 0.5:
            return 0.8
        else:
            return 0.5
    
    def get_optimized_price(self, dataset_id: str, dataset_info: Dict) -> int:
        """Get optimized price considering all factors"""
        base_price = dataset_info.get('price_mnee', 0)
        if base_price == 0:
            from backend.config import Config
            base_price = Config.BASE_DATA_PRICE
        
        # Dynamic demand pricing
        dynamic_price = self.get_current_price(dataset_id, base_price)
        
        # Freshness multiplier
        last_updated = dataset_info.get('last_updated', time.time())
        freshness_mult = self.calculate_freshness_multiplier(last_updated)
        
        # Quality multiplier
        quality_score = dataset_info.get('quality_score', 0.7)
        quality_mult = self.calculate_quality_multiplier(quality_score)
        
        # Final optimized price
        optimized_price = int(dynamic_price * freshness_mult * quality_mult)
        
        return optimized_price
    
    def predict_price_trend(self, dataset_id: str, periods_ahead: int = 10) -> List[int]:
        """Predict future price trend"""
        history = self.price_history[dataset_id]
        
        if len(history) < 5:
            return []
        
        prices = [h['price'] for h in history[-20:]]
        
        window_size = min(5, len(prices))
        predicted = []
        
        for _ in range(periods_ahead):
            forecast = int(np.mean(prices[-window_size:]))
            predicted.append(forecast)
            prices.append(forecast)
        
        return predicted
    
    def get_price_statistics(self, dataset_id: str) -> Dict:
        """Get pricing statistics for dataset"""
        history = self.price_history[dataset_id]
        
        if not history:
            return {}
        
        prices = [h['price'] for h in history]
        
        return {
            'current_price': prices[-1],
            'min_price': min(prices),
            'max_price': max(prices),
            'avg_price': int(np.mean(prices)),
            'std_price': int(np.std(prices)),
            'price_changes': len(prices),
            'trend': 'increasing' if prices[-1] > prices[0] else 'decreasing'
        }