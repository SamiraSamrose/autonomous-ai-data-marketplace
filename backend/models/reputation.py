import time
import numpy as np
from collections import defaultdict
from typing import Dict, List, Optional

class ReputationSystem:
    """
    Reputation system with stake-based trust and slashing
    """
    
    def __init__(self, mnee_token):
        self.mnee_token = mnee_token
        self.reputations = {}
        self.reviews = defaultdict(list)
        self.slashing_events = []
    
    def initialize_reputation(self, agent_id: str, initial_stake: int) -> bool:
        """Initialize reputation for new agent"""
        from backend.config import Config
        
        if self.mnee_token.staked_amounts[agent_id] < Config.MIN_STAKE_AMOUNT:
            return False
        
        self.reputations[agent_id] = {
            'agent_id': agent_id,
            'score': 1.0,
            'total_transactions': 0,
            'successful_transactions': 0,
            'failed_transactions': 0,
            'total_stake': initial_stake,
            'slashing_count': 0,
            'created_at': time.time(),
            'last_updated': time.time()
        }
        
        return True
    
    def record_transaction(self, agent_id: str, success: bool, 
                          transaction_value: int) -> bool:
        """Record transaction outcome for reputation"""
        if agent_id not in self.reputations:
            return False
        
        rep = self.reputations[agent_id]
        rep['total_transactions'] += 1
        
        if success:
            rep['successful_transactions'] += 1
        else:
            rep['failed_transactions'] += 1
        
        # Update score
        success_rate = rep['successful_transactions'] / rep['total_transactions']
        
        from backend.config import Config
        value_factor = min(transaction_value / Config.BASE_DATA_PRICE, 2.0)
        
        old_score = rep['score']
        if success:
            rep['score'] = min(1.0, old_score + (0.01 * value_factor))
        else:
            rep['score'] = max(0.0, old_score - (0.05 * value_factor))
        
        rep['last_updated'] = time.time()
        
        return True
    
    def submit_review(self, reviewer: str, reviewed_agent: str,
                     rating: float, comment: str, transaction_id: str) -> bool:
        """Submit review for agent"""
        if reviewed_agent not in self.reputations:
            return False
        
        if rating < 0 or rating > 1:
            return False
        
        review = {
            'reviewer': reviewer,
            'reviewed': reviewed_agent,
            'rating': rating,
            'comment': comment,
            'transaction_id': transaction_id,
            'timestamp': time.time()
        }
        
        self.reviews[reviewed_agent].append(review)
        
        # Update reputation score based on review
        rep = self.reputations[reviewed_agent]
        current_score = rep['score']
        
        review_count = len(self.reviews[reviewed_agent])
        weight = min(review_count / 100.0, 0.3)
        
        avg_review_score = np.mean([r['rating'] for r in self.reviews[reviewed_agent]])
        
        rep['score'] = (current_score * (1 - weight)) + (avg_review_score * weight)
        rep['last_updated'] = time.time()
        
        return True
    
    def slash_reputation(self, agent_id: str, reason: str, 
                        evidence: Dict) -> Dict:
        """Slash stake for misbehavior"""
        if agent_id not in self.reputations:
            return {'success': False, 'error': 'agent_not_found'}
        
        from backend.config import Config
        
        rep = self.reputations[agent_id]
        
        penalty_amount = self.mnee_token.slash(agent_id, Config.SLASHING_PENALTY)
        
        rep['slashing_count'] += 1
        rep['score'] = max(0.0, rep['score'] - 0.2)
        rep['total_stake'] -= penalty_amount
        rep['last_updated'] = time.time()
        
        slashing_event = {
            'agent_id': agent_id,
            'reason': reason,
            'penalty_amount': penalty_amount,
            'evidence': evidence,
            'timestamp': time.time(),
            'new_score': rep['score']
        }
        
        self.slashing_events.append(slashing_event)
        
        return {
            'success': True,
            'penalty_amount': penalty_amount,
            'new_score': rep['score'],
            'new_stake': rep['total_stake']
        }
    
    def get_reputation(self, agent_id: str) -> Optional[Dict]:
        """Get agent reputation"""
        return self.reputations.get(agent_id)
    
    def get_trusted_agents(self, min_score: float = 0.7) -> List[str]:
        """Get list of trusted agents above threshold"""
        trusted = []
        for agent_id, rep in self.reputations.items():
            if rep['score'] >= min_score:
                trusted.append(agent_id)
        
        return trusted
    
    def calculate_trust_score(self, agent_id: str) -> float:
        """Calculate comprehensive trust score"""
        if agent_id not in self.reputations:
            return 0.0
        
        rep = self.reputations[agent_id]
        
        base_score = rep['score']
        
        from backend.config import Config
        stake_factor = min(rep['total_stake'] / (Config.MIN_STAKE_AMOUNT * 10), 1.0)
        
        if rep['total_transactions'] > 0:
            success_rate = rep['successful_transactions'] / rep['total_transactions']
            history_factor = success_rate
        else:
            history_factor = 0.5
        
        if agent_id in self.reviews and len(self.reviews[agent_id]) > 0:
            avg_review = np.mean([r['rating'] for r in self.reviews[agent_id]])
            review_factor = avg_review
        else:
            review_factor = 0.5
        
        slashing_penalty = rep['slashing_count'] * 0.1
        
        trust_score = (base_score * 0.3 + 
                      stake_factor * 0.2 + 
                      history_factor * 0.3 + 
                      review_factor * 0.2 - 
                      slashing_penalty)
        
        return max(0.0, min(1.0, trust_score))