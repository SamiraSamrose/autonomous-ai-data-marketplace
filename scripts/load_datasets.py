import sys
import os
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.models.agents import DataProviderAgent
from backend.config import Config
from scripts.init_db import initialize_system

def generate_sample_datasets():
    """Generate sample datasets for the marketplace"""
    datasets = {}
    
    # Dataset 1: Iris Classification
    print("\nGenerating Dataset 1: Iris Classification...")
    from sklearn.datasets import load_iris
    iris = load_iris()
    iris_df = pd.DataFrame(
        data=np.c_[iris['data'], iris['target']],
        columns=iris['feature_names'] + ['target']
    )
    datasets['iris'] = {
        'data': iris_df,
        'info': {
            'name': 'Iris Flower Classification Dataset',
            'description': 'Classic dataset for flower species classification with measurements',
            'categories': ['machine-learning', 'classification', 'biology'],
            'industry': 'research',
            'tags': ['classification', 'supervised-learning', 'flowers'],
            'use_cases': ['education', 'research', 'benchmarking'],
            'price': Config.BASE_DATA_PRICE
        }
    }
    
    # Dataset 2: Financial Time Series
    print("Generating Dataset 2: Financial Time Series...")
    dates = pd.date_range('2023-01-01', periods=500, freq='D')
    price = 100 + np.cumsum(np.random.randn(500) * 2)
    volume = np.random.lognormal(10, 1, 500)
    financial_df = pd.DataFrame({
        'date': dates,
        'price': price,
        'volume': volume,
        'returns': np.diff(price, prepend=price[0]) / price,
        'moving_avg_7': pd.Series(price).rolling(7).mean(),
        'volatility': pd.Series(np.diff(price, prepend=price[0])).rolling(20).std()
    })
    datasets['financial'] = {
        'data': financial_df,
        'info': {
            'name': 'Financial Market Time Series',
            'description': 'Stock market price and volume data with technical indicators',
            'categories': ['finance', 'timeseries', 'trading'],
            'industry': 'finance',
            'tags': ['stock-market', 'trading', 'technical-analysis'],
            'use_cases': ['algorithmic-trading', 'risk-management', 'forecasting'],
            'price': Config.BASE_DATA_PRICE * 2
        }
    }
    
    # Dataset 3: Customer Behavior
    print("Generating Dataset 3: Customer Behavior...")
    n_customers = 800
    customer_df = pd.DataFrame({
        'customer_id': range(n_customers),
        'age': np.random.randint(18, 80, n_customers),
        'income': np.random.lognormal(10, 0.5, n_customers),
        'purchase_frequency': np.random.poisson(5, n_customers),
        'avg_purchase_value': np.random.lognormal(4, 0.8, n_customers),
        'customer_lifetime_value': np.random.lognormal(6, 1, n_customers),
        'churn_risk': np.random.beta(2, 5, n_customers)
    })
    datasets['customer'] = {
        'data': customer_df,
        'info': {
            'name': 'Customer Behavior Analytics Dataset',
            'description': 'Customer purchase patterns and lifetime value predictions',
            'categories': ['retail', 'marketing', 'analytics'],
            'industry': 'retail',
            'tags': ['customer-analytics', 'churn-prediction', 'segmentation'],
            'use_cases': ['customer-segmentation', 'churn-prediction', 'marketing-optimization'],
            'price': int(Config.BASE_DATA_PRICE * 1.5)
        }
    }
    
    # Dataset 4: Urban Traffic
    print("Generating Dataset 4: Urban Traffic...")
    n_samples = 1000
    traffic_df = pd.DataFrame({
        'hour': np.random.randint(0, 24, n_samples),
        'day_of_week': np.random.randint(0, 7, n_samples),
        'weather': np.random.choice(['sunny', 'rainy', 'cloudy'], n_samples),
        'temperature': np.random.normal(20, 10, n_samples),
        'traffic_volume': np.random.poisson(100, n_samples),
        'average_speed': np.random.normal(45, 15, n_samples)
    })
    datasets['traffic'] = {
        'data': traffic_df,
        'info': {
            'name': 'Urban Traffic Patterns Dataset',
            'description': 'High-resolution urban traffic data with weather conditions',
            'categories': ['transportation', 'urban-planning', 'timeseries'],
            'industry': 'transportation',
            'tags': ['traffic-analysis', 'urban-mobility', 'smart-cities'],
            'use_cases': ['traffic-prediction', 'urban-planning', 'route-optimization'],
            'price': Config.BASE_DATA_PRICE * 2
        }
    }
    
    # Dataset 5: Healthcare Records
    print("Generating Dataset 5: Healthcare Records...")
    n_patients = 600
    healthcare_df = pd.DataFrame({
        'patient_id': range(n_patients),
        'age': np.random.randint(0, 100, n_patients),
        'bmi': np.random.normal(25, 5, n_patients),
        'blood_pressure': np.random.normal(120, 20, n_patients),
        'cholesterol': np.random.normal(200, 40, n_patients),
        'glucose': np.random.normal(100, 20, n_patients),
        'diagnosis': np.random.choice(['healthy', 'at-risk', 'condition'], n_patients)
    })
    datasets['healthcare'] = {
        'data': healthcare_df,
        'info': {
            'name': 'Healthcare Patient Records Dataset',
            'description': 'Medical patient data with health indicators and diagnoses',
            'categories': ['healthcare', 'medical', 'classification'],
            'industry': 'healthcare',
            'tags': ['medical-records', 'diagnosis', 'health-analytics'],
            'use_cases': ['disease-prediction', 'health-monitoring', 'treatment-optimization'],
            'price': Config.BASE_DATA_PRICE * 3
        }
    }
    
    print(f"\nGenerated {len(datasets)} sample datasets")
    return datasets

def load_datasets_to_marketplace(systems):
    """Load datasets into marketplace"""
    print("\n" + "="*60)
    print("LOADING DATASETS TO MARKETPLACE")
    print("="*60)
    
    # Generate sample datasets
    datasets = generate_sample_datasets()
    
    # Create provider agents
    print("\nCreating provider agents...")
    providers = []
    for i in range(3):
        provider = DataProviderAgent(
            f"provider_{i+1:03d}",
            f"DataProvider {i+1}",
            systems
        )
        providers.append(provider)
        print(f"  Created: {provider.agent_name}")
    
    # Distribute datasets among providers
    print("\nListing datasets...")
    dataset_items = list(datasets.items())
    
    for i, (key, dataset) in enumerate(dataset_items):
        provider = providers[i % len(providers)]
        dataset_id = provider.list_dataset(dataset['info'], dataset['data'])
        if dataset_id:
            print(f"  Listed: {dataset['info']['name']} (ID: {dataset_id})")
    
    print("\n" + "="*60)
    print("Dataset loading complete!")
    print(f"Total datasets in marketplace: {len(systems['discovery_service'].dataset_registry)}")
    print("="*60)

if __name__ == '__main__':
    try:
        systems = initialize_system()
        load_datasets_to_marketplace(systems)
        print("\nDatasets loaded successfully!")
    except Exception as e:
        print(f"\nError loading datasets: {str(e)}")
        sys.exit(1)
