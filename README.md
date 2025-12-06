# 🛒 Retail Demand Forecasting Web Application

A complete Flask-based web application for predicting weekly product demand using machine learning time-series forecasting.

## 🎯 Features

- **Automatic Data Processing**: Converts daily data to weekly aggregates
- **Advanced Feature Engineering**: 
  - 12 lag features (lag_1 to lag_12)
  - 4-week rolling averages
  - Week-of-year seasonality
- **Machine Learning**: RandomForest models trained per product
- **Autoregressive Forecasting**: Predicts future N weeks with feedback loop
- **Interactive Dashboard**: Plotly visualizations for historical data and forecasts
- **Model Management**: Save, load, and track trained models

## 📁 Project Structure

```
demand_forecasting/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── Dockerfile             # Docker configuration
├── .dockerignore          # Docker ignore file
├── .gitignore             # Git ignore file
├── sample_data.csv        # Sample dataset for testing
├── README.md              # This file
├── templates/             # HTML templates
│   ├── base.html          # Base template with navigation
│   ├── home.html          # Homepage
│   ├── upload.html        # CSV upload page
│   ├── train_select.html  # Model training selection
│   ├── models.html        # List trained models
│   ├── predict.html       # Prediction form
│   ├── predict_result.html # Prediction results
│   └── dashboard.html     # Interactive dashboard
├── uploads/               # Uploaded CSV files (auto-created)
└── models/                # Trained ML models (auto-created)
```

## 🚀 Quick Start

### Local Installation

1. **Clone or navigate to the project directory**
```bash
cd demand_forecasting
```

2. **Create a virtual environment**
```bash
python -m venv venv
```

3. **Activate virtual environment**
- Windows:
```bash
venv\Scripts\activate
```
- Mac/Linux:
```bash
source venv/bin/activate
```

4. **Install dependencies**
```bash
pip install -r requirements.txt
```

5. **Run the application**
```bash
python app.py
```

6. **Open your browser**
```
http://localhost:5000
```

## 📊 Usage Guide

### Step 1: Upload Data
1. Navigate to **Upload Data** page
2. Upload a CSV file with columns: `date`, `product_id`, `demand`
3. Daily data will be automatically converted to weekly aggregates

**CSV Format Example:**
```csv
date,product_id,demand
2023-01-01,101,150
2023-01-02,101,145
2023-01-03,102,200
```

### Step 2: Train Model
1. Go to **Train Model** page
2. Select a product from the dropdown
3. Click "Train Model"
4. Model will be trained with:
   - 12 lag features
   - Rolling averages
   - Seasonality features
   - 80/20 train/test split
   - RandomForest with 100 trees

### Step 3: View Models
- Navigate to **Models** page to see all trained models
- View MAE (Mean Absolute Error) for each model
- See last training date

### Step 4: Make Predictions
1. Go to **Predict** page
2. Select a trained product
3. Choose number of weeks to forecast (1-52)
4. View prediction results in table format

### Step 5: Dashboard
- Navigate to **Dashboard** for interactive visualizations
- Blue line: Historical weekly demand
- Red dashed line: 12-week forecast (if model exists)
- Interactive Plotly charts with zoom, pan, and hover

## 🐳 Docker Deployment

### Build Docker Image
```bash
docker build -t demand-forecasting .
```

### Run Docker Container
```bash
docker run -p 5000:5000 demand-forecasting
```

Access at: `http://localhost:5000`

## ☁️ Cloud Deployment

### Deploy to Render

1. **Create a new Web Service on Render**
2. **Connect your GitHub repository**
3. **Configure:**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python app.py`
   - Environment: Python 3
4. **Deploy**

### Deploy to Heroku

1. **Install Heroku CLI**
```bash
heroku login
```

2. **Create Heroku app**
```bash
heroku create your-app-name
```

3. **Create Procfile**
```bash
echo "web: python app.py" > Procfile
```

4. **Deploy**
```bash
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

5. **Open app**
```bash
heroku open
```

## 🔧 Technical Details

### Machine Learning Pipeline

1. **Data Preprocessing**
   - Convert daily to weekly aggregates
   - Sort by date
   - Handle missing values

2. **Feature Engineering**
   - Lag features: demand from previous 12 weeks
   - Rolling mean: 4-week moving average
   - Seasonality: week of year (1-52)

3. **Model Training**
   - Algorithm: RandomForestRegressor
   - Trees: 100
   - Train/Test Split: 80/20
   - Evaluation Metric: MAE

4. **Forecasting**
   - Autoregressive approach
   - Each prediction feeds into next
   - Ensures non-negative predictions

### API Routes

- `GET /` - Homepage
- `GET/POST /upload` - Upload CSV data
- `GET /train_select` - Select product for training
- `POST /train` - Train model for selected product
- `GET /models` - List all trained models
- `GET/POST /predict` - Generate predictions
- `GET /dashboard` - Interactive visualization dashboard

## 📦 Dependencies

- **Flask 2.3.2** - Web framework
- **pandas 2.0.3** - Data manipulation
- **numpy 1.24.3** - Numerical computing
- **scikit-learn 1.3.0** - Machine learning
- **plotly 5.15.0** - Interactive visualizations
- **joblib 1.3.1** - Model serialization

## 🧪 Testing with Sample Data

A `sample_data.csv` file is included with 144 days of data for 2 products (101 and 102).

1. Upload `sample_data.csv`
2. Train model for Product 101 or 102
3. Generate 12-week forecast
4. View dashboard

## 🛠️ Troubleshooting

**Issue: "No data uploaded"**
- Solution: Upload a CSV file first via Upload Data page

**Issue: "Not enough data for training"**
- Solution: Ensure at least 20 weeks of data per product

**Issue: "Model not found"**
- Solution: Train a model first via Train Model page

**Issue: Port 5000 already in use**
- Solution: Change port in app.py: `app.run(port=5001)`

## 📈 Performance Tips

- Use at least 6 months of historical data for better accuracy
- Retrain models periodically with new data
- Monitor MAE to assess model performance
- Consider ensemble methods for critical products

## 🔒 Security Notes

- Change `app.secret_key` in production
- Set `app.config['MAX_CONTENT_LENGTH']` for file size limits
- Use environment variables for sensitive configuration
- Enable HTTPS in production

## 📝 License

This project is open source and available for educational and commercial use.

## 🤝 Contributing

Contributions are welcome! Feel free to submit issues and pull requests.

## 📧 Support

For questions or issues, please open a GitHub issue or contact the development team.

---

**Built with ❤️ using Flask, scikit-learn, and Plotly**
