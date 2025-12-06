from forecast_model import DemandForecaster, generate_sample_data

# Generate sample data and run forecast
data = generate_sample_data()
print("Sample data shape:", data.shape)
print("\nFirst 5 rows:")
print(data.head())

# Train and predict
forecaster = DemandForecaster()
forecaster.fit(data)

predictions = forecaster.predict(data, periods=4)
print(f"\nNext 4 weeks forecast: {[f'{p:.1f}' for p in predictions]}")

# Show visualization
forecaster.plot_forecast(data, predictions)