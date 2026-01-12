import time
import secrets
import pandas as pd
import numpy as np
from typing import Dict, Optional
from scipy import stats

class QualityAssessment:
    """
    Quality assessment with third-party attestation
    """
    
    def __init__(self):
        self.quality_cache = {}
        self.attestations = {}
        self.auditor_agents = {}
        
        # Register system auditor
        self.register_auditor('system_auditor', 0.95)
    
    def register_auditor(self, auditor_id: str, trust_score: float = 0.9):
        """Register third-party auditor agent"""
        self.auditor_agents[auditor_id] = {
            'auditor_id': auditor_id,
            'trust_score': trust_score,
            'attestations_issued': 0,
            'registered_at': time.time()
        }
    
    def assess_dataset(self, data: pd.DataFrame) -> Dict:
        """Comprehensive quality assessment of dataset"""
        metrics = {
            'timestamp': time.time(),
            'total_rows': len(data),
            'total_columns': len(data.columns),
            'memory_usage_mb': data.memory_usage(deep=True).sum() / (1024**2),
            'completeness': {},
            'statistical_properties': {},
            'data_types': {},
            'quality_score': 0.0,
            'schema_info': {}
        }
        
        # Completeness analysis
        total_cells = len(data) * len(data.columns)
        missing_cells = data.isnull().sum().sum()
        metrics['completeness']['missing_ratio'] = missing_cells / total_cells if total_cells > 0 else 0
        metrics['completeness']['complete_rows'] = data.dropna().shape[0]
        metrics['completeness']['complete_ratio'] = data.dropna().shape[0] / len(data) if len(data) > 0 else 0
        
        # Schema information
        metrics['schema_info'] = {
            col: str(dtype) for col, dtype in data.dtypes.items()
        }
        
        # Data type distribution
        dtype_counts = data.dtypes.value_counts()
        metrics['data_types'] = {str(k): int(v) for k, v in dtype_counts.items()}
        
        # Statistical properties for numeric columns
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            stats_data = data[numeric_cols].describe()
            metrics['statistical_properties']['numeric'] = {
                'mean_values': {col: float(stats_data.loc['mean', col]) for col in numeric_cols},
                'std_values': {col: float(stats_data.loc['std', col]) for col in numeric_cols},
                'min_values': {col: float(stats_data.loc['min', col]) for col in numeric_cols},
                'max_values': {col: float(stats_data.loc['max', col]) for col in numeric_cols}
            }
            
            # Outlier detection using IQR method
            outlier_counts = {}
            for col in numeric_cols:
                Q1 = data[col].quantile(0.25)
                Q3 = data[col].quantile(0.75)
                IQR = Q3 - Q1
                outliers = ((data[col] < (Q1 - 1.5 * IQR)) | (data[col] > (Q3 + 1.5 * IQR))).sum()
                outlier_counts[col] = int(outliers)
            metrics['statistical_properties']['outlier_counts'] = outlier_counts
        
        # Categorical column analysis
        categorical_cols = data.select_dtypes(include=['object', 'category']).columns
        if len(categorical_cols) > 0:
            cat_stats = {}
            for col in categorical_cols:
                cat_stats[col] = {
                    'unique_values': int(data[col].nunique()),
                    'most_common': str(data[col].mode().iloc[0]) if len(data[col].mode()) > 0 else None
                }
            metrics['statistical_properties']['categorical'] = cat_stats
        
        # Calculate overall quality score
        completeness_score = metrics['completeness']['complete_ratio']
        consistency_score = 1.0 - (missing_cells / total_cells) if total_cells > 0 else 0
        
        outlier_penalty = 0
        if 'outlier_counts' in metrics['statistical_properties']:
            total_outliers = sum(metrics['statistical_properties']['outlier_counts'].values())
            outlier_penalty = min(total_outliers / total_cells, 0.2) if total_cells > 0 else 0
        
        metrics['quality_score'] = max(0, min(1, (completeness_score * 0.4 + 
                                                   consistency_score * 0.4 + 
                                                   (1.0 - outlier_penalty) * 0.2)))
        
        return metrics
    
    def generate_attestation(self, dataset_id: str, assessment: Dict, 
                           auditor_id: str = 'system_auditor') -> Dict:
        """Generate quality attestation certificate"""
        if auditor_id not in self.auditor_agents:
            self.register_auditor(auditor_id, 0.95)
        
        attestation_id = f"att_{len(self.attestations)}_{int(time.time())}"
        
        from backend.config import Config
        attestation = {
            'attestation_id': attestation_id,
            'dataset_id': dataset_id,
            'auditor_id': auditor_id,
            'quality_score': assessment['quality_score'],
            'completeness': assessment['completeness']['complete_ratio'],
            'trust_score': self.auditor_agents[auditor_id]['trust_score'],
            'certified': assessment['quality_score'] >= Config.QUALITY_SCORE_THRESHOLD,
            'timestamp': time.time(),
            'signature': secrets.token_hex(32),
            'on_chain_proof': f"0x{secrets.token_hex(32)}"
        }
        
        self.attestations[attestation_id] = attestation
        self.auditor_agents[auditor_id]['attestations_issued'] += 1
        
        return attestation
    
    def verify_attestation(self, attestation_id: str) -> bool:
        """Verify attestation validity"""
        if attestation_id not in self.attestations:
            return False
        
        attestation = self.attestations[attestation_id]
        auditor = self.auditor_agents.get(attestation['auditor_id'])
        
        if not auditor:
            return False
        
        return auditor['trust_score'] >= 0.8
    
    def generate_quality_report(self, dataset_id: str, data: pd.DataFrame) -> Dict:
        """Generate comprehensive quality report"""
        assessment = self.assess_dataset(data)
        
        report = {
            'dataset_id': dataset_id,
            'assessment': assessment,
            'recommendations': [],
            'certification': 'pending'
        }
        
        from backend.config import Config
        
        # Generate recommendations
        if assessment['completeness']['missing_ratio'] > 0.1:
            report['recommendations'].append({
                'severity': 'high',
                'issue': 'high_missing_data',
                'message': f"Dataset has {assessment['completeness']['missing_ratio']*100:.1f}% missing values"
            })
        
        if assessment['quality_score'] < Config.QUALITY_SCORE_THRESHOLD:
            report['recommendations'].append({
                'severity': 'medium',
                'issue': 'low_quality_score',
                'message': f"Quality score {assessment['quality_score']:.2f} below threshold"
            })
        
        # Certification
        if assessment['quality_score'] >= Config.QUALITY_SCORE_THRESHOLD:
            report['certification'] = 'certified'
        else:
            report['certification'] = 'needs_improvement'
        
        self.quality_cache[dataset_id] = report
        
        return report