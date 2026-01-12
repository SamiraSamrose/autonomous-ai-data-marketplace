**File: backend/utils/crypto.py**
import hashlib
import secrets
from typing import List
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend

class CryptoUtils:
    """Cryptographic utilities for secure marketplace operations"""
    
    @staticmethod
    def generate_keypair():
        """Generate RSA keypair for agent identity"""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        public_key = private_key.public_key()
        return private_key, public_key
    
    @staticmethod
    def hash_data(data: bytes) -> str:
        """Generate SHA-256 hash of data"""
        return hashlib.sha256(data).hexdigest()
    
    @staticmethod
    def sign_message(private_key, message: str) -> bytes:
        """Sign message with private key"""
        signature = private_key.sign(
            message.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return signature
    
    @staticmethod
    def verify_signature(public_key, message: str, signature: bytes) -> bool:
        """Verify message signature"""
        try:
            public_key.verify(
                signature,
                message.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except:
            return False
    
    @staticmethod
    def generate_merkle_root(data_hashes: List[str]) -> str:
        """Generate Merkle root for data integrity"""
        if not data_hashes:
            return ""
        
        while len(data_hashes) > 1:
            if len(data_hashes) % 2 != 0:
                data_hashes.append(data_hashes[-1])
            
            new_level = []
            for i in range(0, len(data_hashes), 2):
                combined = data_hashes[i] + data_hashes[i+1]
                new_level.append(hashlib.sha256(combined.encode()).hexdigest())
            data_hashes = new_level
        
        return data_hashes[0]
    
    @staticmethod
    def generate_zk_commitment(value: float, salt: str) -> str:
        """Generate zero-knowledge commitment"""
        commitment_input = f"{value}:{salt}"
        return hashlib.sha256(commitment_input.encode()).hexdigest()
