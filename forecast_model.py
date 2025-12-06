import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

class DemandForecaster:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.is_fitted = False
    
    def create_features(self, df):
        """Extract time-series features"""
        df = df.copy()
        df['week'] = df['date'].dt.isocalendar().week
        df['month'] = df['date'].dt.month
        df['quarter'] = df['date'].dt.quarter
        df['lag_1'] = df['demand'].shift(1)
        df['lag_4'] = df['demand'].shift(4)
        df['rolling_mean_4'] = df['demand'].rolling(4).mean()
        return df.dropna()
    
    def fit(self, df):
        """Train the forecasting model"""
        df_features = self.create_features(df)
        features = ['week', 'month', 'quarter', 'lag_1', 'lag_4', 'rolling_mean_4']
        
        X = df_features[features]
        y = df_features['demand']
        
        self.model.fit(X, y)
        self.feature_names = features
        self.is_fitted = True
        
        predictions = self.model.predict(X)
        mae = mean_absolute_error(y, predictions)
        print(f"Model MAE: {mae:.2f}")
        
    def predict(self, df, periods=4):
        """Forecast future demand"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted first")
            
        df_pred = df.copy()
        predictions = []
        
        for i in range(periods):
            df_features = self.create_features(df_pred)
            if len(df_features) == 0:
                break
                
            X_pred = df_features[self.feature_names].iloc[-1:].fillna(0)
            pred = self.model.predict(X_pred)[0]
            predictions.append(pred)
            
            next_date = df_pred['date'].max() + timedelta(weeks=1)
            new_row = pd.DataFrame({
                'date': [next_date],
                'demand': [pred]
            })
            df_pred = pd.concat([df_pred, new_row], ignore_index=True)
            
        return predictions
    
    def plot_forecast(self, df, predictions):
        """Visualize historical data and forecasts"""
        plt.figure(figsize=(12, 6))
        
        plt.plot(df['date'], df['demand'], label='Historical', marker='o')
        
        future_dates = [df['date'].max() + timedelta(weeks=i+1) for i in range(len(predictions))]
        plt.plot(future_dates, predictions, label='Forecast', marker='s', color='red')
        
        plt.title('Weekly Demand Forecast')
        plt.xlabel('Date')
        plt.ylabel('Demand')
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

def generate_sample_data():
    """Generate sample retail demand data"""
    dates = pd.date_range('2023-01-01', periods=52, freq='W')
    
    trend = np.linspace(100, 120, 52)
    seasonal = 20 * np.sin(2 * np.pi * np.arange(52) / 52)
    noise = np.random.normal(0, 10, 52)
    demand = trend + seasonal + noise
    
    return pd.DataFrame({
        'date': dates,
        'demand': np.maximum(demand, 0)
    })

if __name__ == "__main__":
    data = generate_sample_data()
    
    forecaster = DemandForecaster()
    forecaster.fit(data)
    
    predictions = forecaster.predict(data, periods=4)
    print(f"Next 4 weeks forecast: {[f'{p:.1f}' for p in predictions]}")
    
    forecaster.plot_forecast(data, predictions)