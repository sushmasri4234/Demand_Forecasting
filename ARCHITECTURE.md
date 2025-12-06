# 🏗️ System Architecture

## Overview

The Demand Forecasting application follows a classic MVC (Model-View-Controller) architecture with Flask as the backend framework.

---

## 📐 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        USER BROWSER                          │
│                     (HTML + Bootstrap 5)                     │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP Requests
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      FLASK APPLICATION                       │
│                         (app.py)                             │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              ROUTING LAYER                           │  │
│  │  / → home()                                          │  │
│  │  /upload → upload()                                  │  │
│  │  /train_select → train_select()                      │  │
│  │  /train → train()                                    │  │
│  │  /models → models()                                  │  │
│  │  /predict → predict()                                │  │
│  │  /dashboard → dashboard()                            │  │
│  └──────────────────────────────────────────────────────┘  │
│                         │                                    │
│                         ▼                                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           BUSINESS LOGIC LAYER                       │  │
│  │  • convert_to_weekly()                               │  │
│  │  • create_features()                                 │  │
│  │  • train_model()                                     │  │
│  │  • predict_future()                                  │  │
│  └──────────────────────────────────────────────────────┘  │
│                         │                                    │
│                         ▼                                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              ML PIPELINE                             │  │
│  │  • Feature Engineering (pandas)                      │  │
│  │  • Model Training (scikit-learn)                     │  │
│  │  • Prediction (RandomForest)                         │  │
│  │  • Serialization (joblib)                            │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    DATA STORAGE LAYER                        │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   uploads/   │  │   models/    │  │  templates/  │     │
│  │              │  │              │  │              │     │
│  │ • raw_data   │  │ • model_101  │  │ • base.html  │     │
│  │   .csv       │  │   .pkl       │  │ • home.html  │     │
│  │ • weekly_    │  │ • model_102  │  │ • upload.    │     │
│  │   data.csv   │  │   .pkl       │  │   html       │     │
│  │              │  │ • ...        │  │ • ...        │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Data Flow

### 1. Upload Flow
```
User uploads CSV
    ↓
Flask receives file
    ↓
Validate columns (date, product_id, demand)
    ↓
Save as raw_data.csv
    ↓
Convert daily → weekly (convert_to_weekly)
    ↓
Save as weekly_data.csv
    ↓
Redirect to train_select
```

### 2. Training Flow
```
User selects product
    ↓
Load weekly_data.csv
    ↓
Filter by product_id
    ↓
Create features (create_features)
    ├─ Lag features (1-12)
    ├─ Rolling mean (4 weeks)
    └─ Week of year
    ↓
Split train/test (80/20)
    ↓
Train RandomForest
    ↓
Evaluate (MAE)
    ↓
Save model + metadata (joblib)
    ↓
Display success message
```

### 3. Prediction Flow
```
User selects product + n_weeks
    ↓
Load model_{product_id}.pkl
    ↓
Extract last 12 weeks demand
    ↓
For each future week:
    ├─ Calculate features
    ├─ Predict demand
    ├─ Update lag values
    └─ Store prediction
    ↓
Create results DataFrame
    ↓
Display table
```

### 4. Dashboard Flow
```
Load weekly_data.csv
    ↓
Filter by product
    ↓
Create Plotly figure
    ├─ Add historical trace (blue)
    └─ Add forecast trace (red, if model exists)
    ↓
Serialize to JSON
    ↓
Render template with graph
    ↓
JavaScript displays interactive chart
```

---

## 🧩 Component Breakdown

### Frontend Components

```
templates/
├── base.html           # Master template
│   ├── Navigation bar
│   ├── Flash messages
│   └── Content block
│
├── home.html          # Landing page
│   └── Feature cards (4)
│
├── upload.html        # File upload
│   ├── File input form
│   └── Format example
│
├── train_select.html  # Product selection
│   ├── Dropdown menu
│   └── Training info
│
├── models.html        # Model list
│   └── Table with MAE
│
├── predict.html       # Prediction form
│   ├── Product dropdown
│   └── Weeks input
│
├── predict_result.html # Results display
│   └── Predictions table
│
└── dashboard.html     # Visualization
    └── Plotly chart div
```

### Backend Components

```python
# app.py structure

# Configuration
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MODEL_FOLDER'] = 'models'

# Utility Functions
def convert_to_weekly(df)      # Daily → Weekly
def create_features(df, pid)   # Feature engineering
def train_model(product_id)    # ML training
def predict_future(pid, n)     # Forecasting

# Routes
@app.route('/')                # Homepage
@app.route('/upload')          # Upload handler
@app.route('/train_select')    # Product selector
@app.route('/train')           # Training handler
@app.route('/models')          # Model list
@app.route('/predict')         # Prediction handler
@app.route('/dashboard')       # Visualization
```

---

## 🔧 Technology Stack

### Backend
- **Framework**: Flask 2.3.2
- **Language**: Python 3.10+
- **WSGI**: Werkzeug 2.3.6

### Machine Learning
- **Library**: scikit-learn 1.3.0
- **Algorithm**: RandomForestRegressor
- **Serialization**: joblib 1.3.1

### Data Processing
- **Library**: pandas 2.0.3
- **Numerical**: numpy 1.24.3

### Visualization
- **Library**: Plotly 5.15.0
- **Type**: Interactive JavaScript charts

### Frontend
- **Framework**: Bootstrap 5.1.3
- **Template Engine**: Jinja2 (Flask default)

---

## 📊 Database Schema (File-based)

### uploads/raw_data.csv
```
date        | product_id | demand
------------|------------|--------
2023-01-01  | 101        | 150
2023-01-02  | 101        | 145
...
```

### uploads/weekly_data.csv
```
date        | product_id | demand
------------|------------|--------
2023-01-01  | 101        | 1050
2023-01-08  | 101        | 1120
...
```

### models/model_{product_id}.pkl
```python
{
    'model': RandomForestRegressor(...),
    'max_lag': 12,
    'last_12_weeks': [150, 160, ...],
    'last_date': '2023-05-24',
    'mae': 25.5,
    'product_id': 101
}
```

---

## 🔐 Security Architecture

### Input Validation
```
File Upload
    ├─ File type check (.csv only)
    ├─ File size limit (16MB)
    ├─ Secure filename (Werkzeug)
    └─ Column validation

Form Inputs
    ├─ Product ID (integer)
    ├─ Weeks (1-52 range)
    └─ CSRF protection (Flask)
```

### Session Management
```
Flask Sessions
    ├─ Secret key encryption
    ├─ Flash messages
    └─ User feedback
```

---

## 🚀 Deployment Architecture

### Local Development
```
Developer Machine
    ├─ Python 3.10+
    ├─ Virtual Environment
    ├─ Flask Dev Server
    └─ Port 5000
```

### Docker Container
```
Docker Image
    ├─ Python 3.10 slim
    ├─ App files
    ├─ Dependencies
    └─ Exposed port 5000
```

### Cloud Deployment
```
Cloud Platform (Render/Heroku/AWS)
    ├─ Git repository
    ├─ Build process
    ├─ WSGI server (Gunicorn)
    ├─ Environment variables
    └─ Public URL
```

---

## 📈 Scalability Considerations

### Current Architecture
- Single-threaded Flask dev server
- File-based storage
- In-memory processing
- Suitable for: Development, small teams

### Production Enhancements
```
Load Balancer (Nginx)
    ├─ Worker 1 (Gunicorn)
    ├─ Worker 2 (Gunicorn)
    └─ Worker N (Gunicorn)
        ↓
Database (PostgreSQL)
    ├─ Historical data
    ├─ Model metadata
    └─ User sessions
        ↓
Object Storage (S3)
    ├─ Uploaded files
    └─ Trained models
        ↓
Cache Layer (Redis)
    ├─ Predictions
    └─ Dashboard data
```

---

## 🔄 Request/Response Cycle

### Example: Training a Model

```
1. User clicks "Train Model" button
   ↓
2. Browser sends POST /train
   ↓
3. Flask receives request
   ↓
4. Extract product_id from form
   ↓
5. Call train_model(product_id)
   ↓
6. Load weekly_data.csv
   ↓
7. Create features (pandas)
   ↓
8. Train RandomForest (sklearn)
   ↓
9. Calculate MAE
   ↓
10. Save model (joblib)
    ↓
11. Flash success message
    ↓
12. Redirect to /models
    ↓
13. Render models.html
    ↓
14. Browser displays updated page
```

---

## 🧪 Testing Architecture

### Unit Tests (Future)
```python
test_convert_to_weekly()
test_create_features()
test_train_model()
test_predict_future()
```

### Integration Tests (Future)
```python
test_upload_flow()
test_training_flow()
test_prediction_flow()
test_dashboard_flow()
```

### Manual Testing (Current)
```
1. Upload sample_data.csv
2. Train Product 101
3. Predict 12 weeks
4. View dashboard
5. Verify MAE < 50
```

---

## 📝 API Endpoints Summary

| Method | Endpoint | Purpose | Returns |
|--------|----------|---------|---------|
| GET | / | Homepage | HTML |
| GET | /upload | Upload form | HTML |
| POST | /upload | Process CSV | Redirect |
| GET | /train_select | Product list | HTML |
| POST | /train | Train model | Redirect |
| GET | /models | Model list | HTML |
| GET | /predict | Prediction form | HTML |
| POST | /predict | Generate forecast | HTML |
| GET | /dashboard | Visualization | HTML |

---

## 🎯 Design Patterns Used

1. **MVC Pattern**: Separation of concerns
2. **Template Pattern**: Jinja2 inheritance
3. **Factory Pattern**: Model creation
4. **Strategy Pattern**: Feature engineering
5. **Repository Pattern**: File-based storage

---

## 🔮 Future Architecture Enhancements

1. **Microservices**: Separate ML service
2. **API Gateway**: RESTful API endpoints
3. **Message Queue**: Async training (Celery)
4. **Monitoring**: Prometheus + Grafana
5. **CI/CD**: Automated testing & deployment
6. **Authentication**: User management
7. **Multi-tenancy**: Organization support
8. **Real-time**: WebSocket updates

---

**This architecture provides a solid foundation for a production-ready demand forecasting application.**
