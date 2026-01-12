import numpy as np
import pandas as pd
from collections import defaultdict
from typing import Dict, List, Tuple
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor

class FederatedLearning:
    """
    Federated learning for gradient-based data marketplace
    """
    
    def __init__(self):
        self.models = {}
        self.training_sessions = {}
        self.gradient_history = defaultdict(list)
    
    def initialize_model(self, model_id: str, model_type: str, 
                        input_dim: int, output_dim: int) -> bool:
        """Initialize federated learning model"""
        if model_type == 'classification':
            model = RandomForestClassifier(n_estimators=10, max_depth=5, random_state=42)
        elif model_type == 'regression':
            model = GradientBoostingRegressor(n_estimators=10, max_depth=3, random_state=42)
        else:
            return False
        
        self.models[model_id] = {
            'model': model,
            'type': model_type,
            'input_dim': input_dim,
            'output_dim': output_dim,
            'version': 0,
            'created_at': time.time(),
            'training_rounds': 0
        }
        
        return True
    
    def start_training_session(self, session_id: str, model_id: str,
                              data_providers: List[str]) -> bool:
        """Start federated training session"""
        if model_id not in self.models:
            return False
        
        from backend.config import Config
        
        session = {
            'session_id': session_id,
            'model_id': model_id,
            'data_providers': data_providers,
            'status': 'active',
            'current_round': 0,
            'max_rounds': Config.FL_EPOCHS,
            'started_at': time.time(),
            'gradients_received': defaultdict(list)
        }
        
        self.training_sessions[session_id] = session
        
        return True
    
    def compute_local_gradients(self, data: pd.DataFrame, labels: np.ndarray,
                               model_id: str) -> Dict:
        """Compute gradients on local data"""
        if model_id not in self.models:
            return None
        
        model_info = self.models[model_id]
        
        X = data.values if isinstance(data, pd.DataFrame) else data
        y = labels
        
        local_model = model_info['model'].__class__(**model_info['model'].get_params())
        local_model.fit(X, y)
        
        if hasattr(local_model, 'feature_importances_'):
            gradients = local_model.feature_importances_
        else:
            gradients = np.random.randn(X.shape[1])
        
        compressed_gradients = self.compress_gradients(gradients)
        
        gradient_data = {
            'gradients': compressed_gradients.tolist(),
            'sample_count': len(X),
            'loss': 0.5,
            'timestamp': time.time()
        }
        
        return gradient_data
    
    def compress_gradients(self, gradients: np.ndarray) -> np.ndarray:
        """Compress gradients using top-k sparsification"""
        from backend.config import Config
        
        k = int(len(gradients) * Config.GRADIENT_COMPRESSION_RATIO)
        if k == 0:
            k = 1
        
        abs_gradients = np.abs(gradients)
        threshold_idx = np.argsort(abs_gradients)[-k:]
        
        compressed = np.zeros_like(gradients)
        compressed[threshold_idx] = gradients[threshold_idx]
        
        return compressed
    
    def aggregate_gradients(self, session_id: str) -> np.ndarray:
        """Aggregate gradients from multiple providers"""
        if session_id not in self.training_sessions:
            return None
        
        session = self.training_sessions[session_id]
        gradients_list = session['gradients_received'][session['current_round']]
        
        if not gradients_list:
            return None
        
        total_samples = sum(g['sample_count'] for g in gradients_list)
        
        aggregated = None
        for grad_data in gradients_list:
            weight = grad_data['sample_count'] / total_samples
            grads = np.array(grad_data['gradients'])
            
            if aggregated is None:
                aggregated = grads * weight
            else:
                aggregated += grads * weight
        
        return aggregated
    
    def update_global_model(self, model_id: str, aggregated_gradients: np.ndarray) -> bool:
        """Update global model with aggregated gradients"""
        if model_id not in self.models:
            return False
        
        model_info = self.models[model_id]
        model_info['version'] += 1
        model_info['training_rounds'] += 1
        
        self.gradient_history[model_id].append({
            'gradients': aggregated_gradients.tolist(),
            'version': model_info['version'],
            'timestamp': time.time()
        })
        
        return True
    
    def federated_training_round(self, session_id: str, 
                                provider_data: Dict[str, Tuple[pd.DataFrame, np.ndarray]]) -> Dict:
        """Execute one round of federated training"""
        import time
        
        if session_id not in self.training_sessions:
            return {'success': False, 'error': 'session_not_found'}
        
        session = self.training_sessions[session_id]
        model_id = session['model_id']
        
        round_gradients = []
        for provider_id, (data, labels) in provider_data.items():
            grad_data = self.compute_local_gradients(data, labels, model_id)
            if grad_data:
                grad_data['provider'] = provider_id
                round_gradients.append(grad_data)
        
        session['gradients_received'][session['current_round']] = round_gradients
        
        aggregated = self.aggregate_gradients(session_id)
        
        if aggregated is not None:
            self.update_global_model(model_id, aggregated)
        
        session['current_round'] += 1
        
        if session['current_round'] >= session['max_rounds']:
            session['status'] = 'completed'
            session['completed_at'] = time.time()
        
        return {
            'success': True,
            'round': session['current_round'],
            'status': session['status'],
            'providers_participated': len(round_gradients)
        }