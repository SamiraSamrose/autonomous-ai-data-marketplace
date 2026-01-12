import time
import secrets
import hashlib
from typing import Dict

class ReceiptOracle:
    """Receipt oracle for verifying data access"""
    
    def __init__(self):
        self.verifications = []
    
    def verify_data_access(self, buyer: str, data_link: str, decryption_key: str) -> Dict:
        """Verify that buyer can access the data"""
        access_successful = len(data_link) > 0 and len(decryption_key) > 0
        
        verification = {
            'buyer': buyer,
            'data_link': data_link,
            'accessible': access_successful,
            'verified_at': time.time(),
            'oracle_signature': secrets.token_hex(32)
        }
        
        if not access_successful:
            verification['error'] = 'data_not_accessible'
        
        self.verifications.append(verification)
        
        return verification

class AtomicSwapEngine:
    """
    Atomic swap engine with escrow and SLA enforcement
    """
    
    def __init__(self, mnee_token, contract_engine):
        self.mnee_token = mnee_token
        self.contract_engine = contract_engine
        self.active_swaps = {}
        self.completed_swaps = []
        self.receipt_oracle = ReceiptOracle()
    
    def initiate_atomic_swap(self, swap_id: str, buyer: str, seller: str,
                            amount: int, dataset_id: str, sla_terms: Dict) -> Dict:
        """Initiate atomic swap with escrow"""
        escrow_success = self.mnee_token.balance_of(buyer) >= amount
        if not escrow_success:
            return {'success': False, 'error': 'insufficient_balance'}
        
        from backend.config import Config
        escrow_contract = self.contract_engine.deploy_escrow(buyer, seller, amount, Config.ESCROW_TIMEOUT)
        
        encrypted_link = f"ipfs://Qm{secrets.token_hex(23)}"
        decryption_key = secrets.token_hex(32)
        encrypted_key = self._encrypt_key(decryption_key)
        
        swap = {
            'swap_id': swap_id,
            'buyer': buyer,
            'seller': seller,
            'amount': amount,
            'dataset_id': dataset_id,
            'escrow_contract': escrow_contract,
            'encrypted_link': encrypted_link,
            'encrypted_key': encrypted_key,
            'decryption_key': decryption_key,
            'sla_terms': sla_terms,
            'status': 'pending_verification',
            'initiated_at': time.time()
        }
        
        self.active_swaps[swap_id] = swap
        
        return {'success': True, 'swap_id': swap_id, 'escrow_contract': escrow_contract}
    
    def _encrypt_key(self, key: str) -> str:
        """Simulate key encryption"""
        return hashlib.sha256(key.encode()).hexdigest()
    
    def verify_and_complete(self, swap_id: str) -> Dict:
        """Receipt oracle verifies access, then completes swap"""
        if swap_id not in self.active_swaps:
            return {'success': False, 'error': 'swap_not_found'}
        
        swap = self.active_swaps[swap_id]
        
        verification = self.receipt_oracle.verify_data_access(
            swap['buyer'],
            swap['encrypted_link'],
            swap['decryption_key']
        )
        
        if not verification['accessible']:
            return {'success': False, 'error': 'verification_failed'}
        
        payment_success = self.mnee_token.transfer(swap['buyer'], swap['seller'], swap['amount'])
        
        if payment_success:
            self.contract_engine.execute_contract(swap['escrow_contract'], 'release', swap['buyer'])
            
            swap['status'] = 'completed'
            swap['completed_at'] = time.time()
            
            self.completed_swaps.append(swap)
            del self.active_swaps[swap_id]
            
            return {'success': True, 'status': 'completed'}
        
        return {'success': False, 'error': 'payment_failed'}
    
    def check_sla_compliance(self, swap_id: str, uptime_percentage: float) -> Dict:
        """Check SLA compliance and trigger refund if needed"""
        if swap_id in self.active_swaps:
            swap = self.active_swaps[swap_id]
        elif any(s['swap_id'] == swap_id for s in self.completed_swaps):
            swap = next(s for s in self.completed_swaps if s['swap_id'] == swap_id)
        else:
            return {'success': False, 'error': 'swap_not_found'}
        
        sla_terms = swap['sla_terms']
        min_uptime = sla_terms.get('min_uptime', 0.99)
        
        if uptime_percentage < min_uptime:
            shortfall = min_uptime - uptime_percentage
            refund_percentage = min(shortfall * 10, 0.5)
            refund_amount = int(swap['amount'] * refund_percentage)
            
            self.mnee_token.transfer(swap['seller'], swap['buyer'], refund_amount)
            
            return {
                'success': True,
                'sla_violated': True,
                'refund_amount': refund_amount,
                'refund_percentage': refund_percentage
            }
        
        return {'success': True, 'sla_violated': False}
