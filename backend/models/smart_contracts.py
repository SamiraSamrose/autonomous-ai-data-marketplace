import time
import secrets
from typing import Dict, Optional

class SmartContract:
    """Base smart contract class"""
    
    def __init__(self, contract_id: str, creator: str):
        self.contract_id = contract_id
        self.creator = creator
        self.created_at = time.time()
        self.state = {}
        self.events = []
        self.executed = False
    
    def emit_event(self, event_name: str, data: Dict):
        """Emit contract event"""
        event = {
            'name': event_name,
            'data': data,
            'timestamp': time.time(),
            'contract_id': self.contract_id
        }
        self.events.append(event)
    
    def execute(self, *args, **kwargs):
        """Execute contract logic"""
        raise NotImplementedError

class EscrowContract(SmartContract):
    """
    Escrow contract for secure data transactions
    Holds MNEE until buyer confirms receipt
    """
    
    def __init__(self, contract_id: str, buyer: str, seller: str, amount: int, timeout: int):
        super().__init__(contract_id, buyer)
        self.buyer = buyer
        self.seller = seller
        self.amount = amount
        self.timeout = timeout
        self.deadline = time.time() + timeout
        self.state = {
            'status': 'pending',
            'amount_locked': amount,
            'buyer': buyer,
            'seller': seller,
            'deadline': self.deadline
        }
    
    def execute(self, action: str, actor: str) -> bool:
        """Execute escrow action"""
        current_time = time.time()
        
        if self.state['status'] != 'pending':
            return False
        
        if action == 'release' and actor == self.buyer:
            self.state['status'] = 'completed'
            self.emit_event('EscrowReleased', {
                'buyer': self.buyer,
                'seller': self.seller,
                'amount': self.amount
            })
            return True
                
        elif action == 'refund' and current_time > self.deadline:
            self.state['status'] = 'refunded'
            self.emit_event('EscrowRefunded', {
                'buyer': self.buyer,
                'amount': self.amount
            })
            return True
            
        elif action == 'dispute' and actor in [self.buyer, self.seller]:
            self.state['status'] = 'disputed'
            self.emit_event('DisputeInitiated', {
                'initiator': actor,
                'amount': self.amount
            })
            return True
            
        return False

class LicenseContract(SmartContract):
    """
    NFT-based access license for data
    Time-bound bearer token for API access
    """
    
    def __init__(self, contract_id: str, licensee: str, licensor: str, 
                 duration: int, access_terms: Dict):
        super().__init__(contract_id, licensor)
        self.licensee = licensee
        self.licensor = licensor
        self.duration = duration
        self.expiry = time.time() + duration
        self.access_terms = access_terms
        self.access_count = 0
        self.state = {
            'status': 'active',
            'licensee': licensee,
            'licensor': licensor,
            'expiry': self.expiry,
            'access_count': 0,
            'terms': access_terms
        }
    
    def execute(self, action: str, actor: str) -> bool:
        """Execute license action"""
        current_time = time.time()
        
        if action == 'access' and actor == self.licensee:
            if current_time > self.expiry:
                self.state['status'] = 'expired'
                return False
            
            if self.state['status'] == 'active':
                self.access_count += 1
                self.state['access_count'] = self.access_count
                self.emit_event('DataAccessed', {
                    'licensee': self.licensee,
                    'access_count': self.access_count
                })
                return True
                
        elif action == 'revoke' and actor == self.licensor:
            self.state['status'] = 'revoked'
            self.emit_event('LicenseRevoked', {
                'licensee': self.licensee,
                'reason': 'licensor_revocation'
            })
            return True
            
        return False
    
    def is_valid(self) -> bool:
        """Check if license is still valid"""
        return (self.state['status'] == 'active' and 
                time.time() <= self.expiry)

class SmartContractEngine:
    """
    Smart contract management engine
    Deploys and manages all marketplace contracts
    """
    
    def __init__(self):
        self.contracts = {}
        self.contract_count = 0
    
    def deploy_escrow(self, buyer: str, seller: str, amount: int, 
                     timeout: int = 3600) -> str:
        """Deploy new escrow contract"""
        contract_id = f"escrow_{self.contract_count}"
        contract = EscrowContract(contract_id, buyer, seller, amount, timeout)
        self.contracts[contract_id] = contract
        self.contract_count += 1
        return contract_id
    
    def deploy_license(self, licensee: str, licensor: str, duration: int,
                      access_terms: Dict) -> str:
        """Deploy new license contract"""
        contract_id = f"license_{self.contract_count}"
        contract = LicenseContract(contract_id, licensee, licensor, duration, access_terms)
        self.contracts[contract_id] = contract
        self.contract_count += 1
        return contract_id
    
    def execute_contract(self, contract_id: str, action: str, actor: str) -> bool:
        """Execute contract action"""
        if contract_id not in self.contracts:
            return False
        return self.contracts[contract_id].execute(action, actor)
    
    def get_contract(self, contract_id: str) -> Optional[SmartContract]:
        """Get contract by ID"""
        return self.contracts.get(contract_id)
    
    def get_all_events(self) -> list:
        """Get all contract events"""
        all_events = []
        for contract in self.contracts.values():
            all_events.extend(contract.events)
        return sorted(all_events, key=lambda x: x['timestamp'])