import hashlib
import numpy as np
from typing import Dict, List, Tuple

class VectorEmbedding:
    """
    Semantic vector embedding with domain-specific knowledge
    """
    
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.embeddings = {}
        self.metadata = {}
        self.keyword_vectors = {}
        
        self._build_keyword_vectors()
    
    def _build_keyword_vectors(self):
        """Build semantic vectors for domain keywords"""
        domains = {
            'healthcare': ['medical', 'patient', 'diagnosis', 'treatment', 'clinical', 'health'],
            'finance': ['stock', 'price', 'trading', 'market', 'investment', 'portfolio'],
            'transportation': ['traffic', 'vehicle', 'route', 'transit', 'mobility'],
            'retail': ['customer', 'purchase', 'sales', 'product', 'transaction'],
            'technology': ['software', 'hardware', 'api', 'cloud', 'computing'],
            'classification': ['label', 'category', 'class', 'predict', 'classify'],
            'regression': ['continuous', 'predict', 'forecast', 'trend', 'value'],
            'timeseries': ['temporal', 'time', 'sequence', 'series', 'historical']
        }
        
        for domain, keywords in domains.items():
            hash_val = int(hashlib.sha256(domain.encode()).hexdigest(), 16)
            np.random.seed(hash_val % (2**32))
            base_vec = np.random.randn(self.dimension)
            
            for i, keyword in enumerate(keywords):
                kw_hash = int(hashlib.sha256(keyword.encode()).hexdigest(), 16)
                np.random.seed(kw_hash % (2**32))
                base_vec += np.random.randn(self.dimension) * 0.3
            
            self.keyword_vectors[domain] = base_vec / np.linalg.norm(base_vec)
    
    def generate_embedding(self, text: str, metadata: Dict = None) -> np.ndarray:
        """Generate semantic embedding with metadata enhancement"""
        text_lower = text.lower()
        
        hash_val = int(hashlib.sha256(text.encode()).hexdigest(), 16)
        np.random.seed(hash_val % (2**32))
        embedding = np.random.randn(self.dimension) * 0.5
        
        for domain, domain_vec in self.keyword_vectors.items():
            if any(kw in text_lower for kw in [domain]):
                weight = text_lower.count(domain)
                embedding += domain_vec * weight * 0.4
        
        if metadata:
            categories = metadata.get('categories', [])
            for cat in categories:
                if cat in self.keyword_vectors:
                    embedding += self.keyword_vectors[cat] * 0.5
            
            format_type = metadata.get('format', 'csv')
            format_hash = int(hashlib.sha256(format_type.encode()).hexdigest(), 16)
            np.random.seed(format_hash % (2**32))
            embedding += np.random.randn(self.dimension) * 0.2
            
            quality = metadata.get('quality_score', 0.5)
            embedding *= (0.8 + quality * 0.4)
        
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        
        return embedding
    
    def add_dataset(self, dataset_id: str, description: str, metadata: Dict):
        """Add dataset with enhanced metadata"""
        enhanced_text = f"{description} {' '.join(metadata.get('categories', []))}"
        if 'name' in metadata:
            enhanced_text = f"{metadata['name']} {enhanced_text}"
        
        embedding = self.generate_embedding(enhanced_text, metadata)
        self.embeddings[dataset_id] = embedding
        self.metadata[dataset_id] = {
            'description': description,
            'metadata': metadata,
            'timestamp': time.time()
        }
    
    def search(self, query: str, top_k: int = 20,
               filters: Dict = None) -> List[Tuple[str, float, Dict]]:
        """Semantic search with cosine similarity"""
        import time
        
        query_embedding = self.generate_embedding(query)
        
        results = []
        for dataset_id, embedding in self.embeddings.items():
            similarity = float(np.dot(query_embedding, embedding))
            
            metadata = self.metadata[dataset_id]['metadata']
            
            if filters:
                if 'max_price' in filters:
                    price = metadata.get('price_mnee', 0)
                    if price > filters['max_price']:
                        continue
                
                if 'categories' in filters:
                    dataset_cats = metadata.get('categories', [])
                    if not any(cat in dataset_cats for cat in filters['categories']):
                        continue
                
                if 'format' in filters:
                    if metadata.get('format') != filters['format']:
                        continue
            
            if similarity >= 0.45:
                match_details = {
                    'categories_match': any(cat in metadata.get('categories', []) 
                                          for cat in query.lower().split()),
                    'price': metadata.get('price_mnee', 0),
                    'quality': metadata.get('quality_score', 0.5)
                }
                results.append((dataset_id, similarity, match_details))
        
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
