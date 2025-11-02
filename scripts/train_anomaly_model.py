"""
Train Anomaly Detection Model using sample ACORD data.

Creates a simple Isolation Forest model trained on the
sample submissions to detect statistical outliers.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
from pathlib import Path


def train_anomaly_model():
    """Train Isolation Forest on sample data"""
    
    # Sample training data based on our ACORD files
    # In production, this would load from historical submissions
    training_data = pd.DataFrame({
        'annual_revenue': [
            5000000, 2500000, 7500000, 1200000, 3400000,
            15000000, 8900000, 4200000, 6100000, 2800000,
            # Add anomalous examples
            100000,  # Too low for business size
            500000000,  # Too high
        ],
        'employee_count': [
            50, 25, 75, 12, 34,
            150, 89, 42, 61, 28,
            # Add anomalous examples
            2,  # Too few
            5000,  # Too many
        ],
        'years_in_business': [
            10, 5, 15, 3, 8,
            20, 12, 7, 11, 6,
            # Add anomalous examples
            0,  # Brand new
            100,  # Too old
        ]
    })
    
    # Extract features
    features = training_data[['annual_revenue', 'employee_count', 'years_in_business']].values
    
    # Scale features
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)
    
    # Train Isolation Forest
    model = IsolationForest(
        contamination=0.1,  # Expect 10% anomalies
        random_state=42,
        n_estimators=100
    )
    model.fit(features_scaled)
    
    # Save model and scaler
    model_dir = Path(__file__).parent.parent / 'models' / 'anomaly_detection'
    model_dir.mkdir(parents=True, exist_ok=True)
    
    joblib.dump(model, model_dir / 'isolation_forest.joblib')
    joblib.dump(scaler, model_dir / 'scaler.joblib')
    
    print("✓ Anomaly detection model trained and saved")
    print(f"  Model: {model_dir / 'isolation_forest.joblib'}")
    print(f"  Scaler: {model_dir / 'scaler.joblib'}")
    
    # Test predictions
    predictions = model.predict(features_scaled)
    anomalies = np.sum(predictions == -1)
    print(f"\n  Detected {anomalies} anomalies in training data")


if __name__ == "__main__":
    train_anomaly_model()
