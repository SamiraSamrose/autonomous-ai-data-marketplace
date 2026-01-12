import time
import secrets
from collections import defaultdict
from typing import Dict, List, Optional

class MNEEToken:
    """
    MNEE Token - Machine Native Economic Engine
    Handles token transfers, staking, and transaction history
    """
    
    def __init__(self, initial_supply: int = None, decimals: int = 18):
        from backend.config import Config
        
        self.name = "Machine Native Economic Engine"
        self.symbol = "MNEE"
        self.decimals = decimals
        self.total_supply = initial_supply or Config.MNEE_INITIAL_SUPPLY
        
        self.balances = defaultdict(int)
        self.allowances = defaultdict(lambda: defaultdict(int))
        self.staked_amounts = defaultdict(int)
        self.delegates = {}
        
        self.transactions = []
        self.transaction_count = 0
        
        # Mint initial supply to treasury
        self.treasury = "0x" + secrets.token_hex(20)
        self.balances[self.treasury] = self.total_supply
    
    def balance_of(self, address: str) -> int:
        """Get balance of address"""
        return self.balances[address]
    
    def transfer(self, from_addr: str, to_addr: str, amount: int) -> bool:
        """Transfer tokens between addresses"""
        if self.balances[from_addr] < amount:
            return False
        
        self.balances[from_addr] -= amount
        self.balances[to_addr] += amount
        
        tx = {
            'id': f"tx_{self.transaction_count}",
            'from': from_addr,
            'to': to_addr,
            'amount': amount,
            'timestamp': time.time(),
            'type': 'transfer'
        }
        self.transactions.append(tx)
        self.transaction_count += 1
        
        return True
    
    def approve(self, owner: str, spender: str, amount: int) -> bool:
        """Approve spender to use tokens"""
        self.allowances[owner][spender] = amount
        return True
    
    def transfer_from(self, spender: str, from_addr: str, to_addr: str, amount: int) -> bool:
        """Transfer tokens on behalf of owner"""
        if self.allowances[from_addr][spender] < amount:
            return False
        if self.balances[from_addr] < amount:
            return False
        
        self.allowances[from_addr][spender] -= amount
        self.balances[from_addr] -= amount
        self.balances[to_addr] += amount
        
        tx = {
            'id': f"tx_{self.transaction_count}",
            'from': from_addr,
            'to': to_addr,
            'amount': amount,
            'spender': spender,
            'timestamp': time.time(),
            'type': 'transfer_from'
        }
        self.transactions.append(tx)
        self.transaction_count += 1
        
        return True
    
    def stake(self, address: str, amount: int) -> bool:
        """Stake tokens for reputation"""
        if self.balances[address] < amount:
            return False
        
        self.balances[address] -= amount
        self.staked_amounts[address] += amount
        
        tx = {
            'id': f"tx_{self.transaction_count}",
            'address': address,
            'amount': amount,
            'timestamp': time.time(),
            'type': 'stake'
        }
        self.transactions.append(tx)
        self.transaction_count += 1
        
        return True
    
    def unstake(self, address: str, amount: int) -> bool:
        """Unstake tokens"""
        if self.staked_amounts[address] < amount:
            return False
        
        self.staked_amounts[address] -= amount
        self.balances[address] += amount
        
        tx = {
            'id': f"tx_{self.transaction_count}",
            'address': address,
            'amount': amount,
            'timestamp': time.time(),
            'type': 'unstake'
        }
        self.transactions.append(tx)
        self.transaction_count += 1
        
        return True
    
    def slash(self, address: str, penalty_rate: float) -> int:
        """Slash staked tokens for misbehavior"""
        staked = self.staked_amounts[address]
        penalty = int(staked * penalty_rate)
        
        self.staked_amounts[address] -= penalty
        self.balances[self.treasury] += penalty
        
        tx = {
            'id': f"tx_{self.transaction_count}",
            'address': address,
            'amount': penalty,
            'timestamp': time.time(),
            'type': 'slash'
        }
        self.transactions.append(tx)
        self.transaction_count += 1
        
        return penalty
    
    def mint(self, to_addr: str, amount: int) -> bool:
        """Mint new tokens"""
        self.balances[to_addr] += amount
        self.total_supply += amount
        
        tx = {
            'id': f"tx_{self.transaction_count}",
            'to': to_addr,
            'amount': amount,
            'timestamp': time.time(),
            'type': 'mint'
        }
        self.transactions.append(tx)
        self.transaction_count += 1
        
        return True
    
    def get_transaction_history(self, address: str = None) -> List[Dict]:
        """Get transaction history"""
        if address is None:
            return self.transactions
        
        return [tx for tx in self.transactions 
                if tx.get('from') == address or tx.get('to') == address or tx.get('address') == address]
    
    def get_total_supply(self) -> int:
        """Get total supply"""
        return self.total_supply
    
    def get_circulating_supply(self) -> int:
        """Get circulating supply (excluding treasury)"""
        return self.total_supply - self.balances[self.treasury]