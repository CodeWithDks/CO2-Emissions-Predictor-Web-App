import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import os

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.linear_model import LinearRegression

def load_and_preprocess_data(file_path):
    """Load and preprocess the CO2 dataset"""
    print("Loading data...")
    df = pd.read_csv(file_path)
    
    print(f"Original dataset shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    
    # Check for missing values
    print(f"Missing values:\n{df.isnull().sum()}")
    
    # Check for duplicates
    duplicates = df.duplicated().sum()
    print(f"Duplicate rows: {duplicates}")
    
    if duplicates > 0:
        df = df.drop_duplicates()
        print(f"After removing duplicates: {df.shape}")
    
    # Drop Model column if it exists
    if 'Model' in df.columns:
        df = df.drop(columns=['Model'])
    
    # Rename columns for consistency
    df = df.rename(columns={
        'CO2 Emissions(g/km)': 'CO2',
        'Fuel Consumption Comb (L/100 km)': 'Fuel Consumption (L/100 km)',
        'Fuel Consumption Comb (mpg)': 'Fuel Efficiency (mpg)'
    })
    
    return df

def train_model(df):
    """Train the CO2 prediction model"""
    print("\nTraining model...")
    
    # Select features
    selected_features = [
        'Fuel Consumption (L/100 km)',
        'Fuel Efficiency (mpg)',
        'Fuel Type'
    ]
    
    # Check if all required features exist
    missing_features = [f for f in selected_features if f not in df.columns]
    if missing_features:
        raise ValueError(f"Missing required features: {missing_features}")
    
    X = df[selected_features]
    y = df['CO2']
    
    # Define transformers
    numerical_features = ['Fuel Consumption (L/100 km)', 'Fuel Efficiency (mpg)']
    categorical_features = ['Fuel Type']
    
    numerical_transformer = StandardScaler()
    categorical_transformer = OneHotEncoder(handle_unknown='ignore')
    
    # Create preprocessor
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numerical_transformer, numerical_features),
            ('cat', categorical_transformer, categorical_features)
        ]
    )
    
    # Create pipeline
    pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('model', LinearRegression())
    ])
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Train model
    pipeline.fit(X_train, y_train)
    
    # Make predictions
    y_pred = pipeline.predict(X_test)
    
    # Calculate metrics
    mse = mean_squared_error(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    print(f"\nModel Performance:")
    print(f"Mean Squared Error (MSE): {mse:.2f}")
    print(f"Mean Absolute Error (MAE): {mae:.2f}")
    print(f"R² Score: {r2:.4f}")
    
    return pipeline, X_test, y_test, y_pred

def save_model(pipeline, model_path):
    """Save the trained model"""
    print(f"\nSaving model to {model_path}...")
    
    # Create model directory if it doesn't exist
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    
    # Get feature names after preprocessing
    numerical_features = ['Fuel Consumption (L/100 km)', 'Fuel Efficiency (mpg)']
    categorical_features = ['Fuel Type']
    
    # Get categorical feature names after one-hot encoding
    try:
        cat_feature_names = pipeline.named_steps['preprocessor'].named_transformers_['cat'].get_feature_names_out(categorical_features)
    except:
        cat_feature_names = []
    
    # Save model with metadata
    model_data = {
        'model': pipeline,
        'feature_names': numerical_features + list(cat_feature_names),
        'numerical_features': numerical_features,
        'categorical_features': categorical_features
    }
    
    joblib.dump(model_data, model_path)
    print("Model saved successfully!")

def visualize_results(y_test, y_pred):
    """Create visualization of model performance"""
    plt.figure(figsize=(10, 6))
    
    # Actual vs Predicted scatter plot
    plt.subplot(1, 2, 1)
    plt.scatter(y_test, y_pred, alpha=0.5, color='blue')
    plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], '--r', lw=2)
    plt.xlabel('Actual CO2 Emissions (g/km)')
    plt.ylabel('Predicted CO2 Emissions (g/km)')
    plt.title('Actual vs Predicted CO2 Emissions')
    
    # Residuals plot
    plt.subplot(1, 2, 2)
    residuals = y_test - y_pred
    plt.scatter(y_pred, residuals, alpha=0.5, color='green')
    plt.axhline(y=0, color='red', linestyle='--', lw=2)
    plt.xlabel('Predicted CO2 Emissions (g/km)')
    plt.ylabel('Residuals')
    plt.title('Residuals Plot')
    
    plt.tight_layout()
    plt.show()

def main():
    """Main function to run the training pipeline"""
    # File paths
    data_path = 'Data/co2.csv'
    model_path = 'model/co2_emission_model.pkl'
    
    try:
        # Load and preprocess data
        df = load_and_preprocess_data(data_path)
        
        # Display basic statistics
        print(f"\nDataset Statistics:")
        print(df.describe())
        
        # Show fuel type distribution
        print(f"\nFuel Type Distribution:")
        print(df['Fuel Type'].value_counts())
        
        # Train model
        pipeline, X_test, y_test, y_pred = train_model(df)
        
        # Save model
        save_model(pipeline, model_path)
        
        # Visualize results
        visualize_results(y_test, y_pred)
        
        # Test model with sample data
        print("\nTesting model with sample data:")
        sample_data = pd.DataFrame({
            'Fuel Consumption (L/100 km)': [8.5],
            'Fuel Efficiency (mpg)': [33],
            'Fuel Type': ['Z']
        })
        
        prediction = pipeline.predict(sample_data)[0]
        print(f"Sample prediction: {prediction:.2f} g/km")
        
        print("\nTraining completed successfully!")
        
    except Exception as e:
        print(f"Error during training: {e}")
        raise

if __name__ == "__main__":
    main()