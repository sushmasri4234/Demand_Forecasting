import os
import pandas as pd
import numpy as np
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
import plotly.graph_objs as go
import plotly.utils
import json
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MODEL_FOLDER'] = 'models'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['MODEL_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_to_weekly(df):
    """Convert daily data to weekly aggregated data"""
    df['date'] = pd.to_datetime(df['date'])
    df['week'] = df['date'].dt.to_period('W').apply(lambda r: r.start_time)
    weekly_df = df.groupby(['week', 'product_id'])['demand'].sum().reset_index()
    weekly_df.columns = ['date', 'product_id', 'demand']
    return weekly_df

def create_features(df, product_id):
    """Create lag features, rolling averages, and seasonality features"""
    product_df = df[df['product_id'] == product_id].copy()
    product_df = product_df.sort_values('date').reset_index(drop=True)
    
    # Lag features (1 to 12 weeks)
    for i in range(1, 13):
        product_df[f'lag_{i}'] = product_df['demand'].shift(i)
    
    # Rolling mean (4 weeks)
    product_df['rolling_mean_4'] = product_df['demand'].shift(1).rolling(window=4).mean()
    
    # Week of year seasonality
    product_df['week_of_year'] = pd.to_datetime(product_df['date']).dt.isocalendar().week
    
    # Drop rows with NaN values (first 12 rows due to lag features)
    product_df = product_df.dropna()
    
    return product_df

def train_model(product_id):
    """Train RandomForest model for a specific product"""
    # Load weekly data
    weekly_file = os.path.join(app.config['UPLOAD_FOLDER'], 'weekly_data.csv')
    if not os.path.exists(weekly_file):
        return None, "No data uploaded"
    
    df = pd.read_csv(weekly_file)
    df['date'] = pd.to_datetime(df['date'])
    
    # Create features
    product_df = create_features(df, product_id)
    
    if len(product_df) < 20:
        return None, "Not enough data for training (need at least 20 weeks)"
    
    # Prepare features and target
    feature_cols = [f'lag_{i}' for i in range(1, 13)] + ['rolling_mean_4', 'week_of_year']
    X = product_df[feature_cols]
    y = product_df['demand']
    
    # Train/test split (80/20)
    split_idx = int(len(X) * 0.8)
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]
    
    # Train RandomForest
    model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    
    # Save model and metadata
    model_data = {
        'model': model,
        'max_lag': 12,
        'last_12_weeks': product_df['demand'].tail(12).values.tolist(),
        'last_date': product_df['date'].max(),
        'mae': mae,
        'product_id': product_id
    }
    
    model_path = os.path.join(app.config['MODEL_FOLDER'], f'model_{product_id}.pkl')
    joblib.dump(model_data, model_path)
    
    return mae, None

def predict_future(product_id, n_weeks):
    """Predict future N weeks using autoregressive approach"""
    model_path = os.path.join(app.config['MODEL_FOLDER'], f'model_{product_id}.pkl')
    if not os.path.exists(model_path):
        return None, "Model not found"
    
    model_data = joblib.load(model_path)
    model = model_data['model']
    last_12_weeks = model_data['last_12_weeks'].copy()
    last_date = pd.to_datetime(model_data['last_date'])
    
    predictions = []
    future_dates = []
    
    for i in range(n_weeks):
        # Calculate week of year for future date
        future_date = last_date + timedelta(weeks=i+1)
        week_of_year = future_date.isocalendar()[1]
        
        # Prepare features
        lags = last_12_weeks[-12:][::-1]  # Last 12 in reverse order
        rolling_mean = np.mean(lags[:4])
        
        features = lags + [rolling_mean, week_of_year]
        features = np.array(features).reshape(1, -1)
        
        # Predict
        pred = model.predict(features)[0]
        pred = max(0, pred)  # Ensure non-negative
        
        predictions.append(pred)
        future_dates.append(future_date)
        
        # Update last_12_weeks for next iteration
        last_12_weeks.append(pred)
    
    result_df = pd.DataFrame({
        'date': future_dates,
        'predicted_demand': predictions
    })
    
    return result_df, None

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'raw_data.csv')
            file.save(filepath)
            
            try:
                # Load and convert to weekly
                df = pd.read_csv(filepath)
                
                # Validate columns
                required_cols = ['date', 'product_id', 'demand']
                if not all(col in df.columns for col in required_cols):
                    flash(f'CSV must contain columns: {", ".join(required_cols)}', 'error')
                    return redirect(request.url)
                
                # Convert to weekly
                weekly_df = convert_to_weekly(df)
                weekly_path = os.path.join(app.config['UPLOAD_FOLDER'], 'weekly_data.csv')
                weekly_df.to_csv(weekly_path, index=False)
                
                flash(f'File uploaded successfully! Converted to weekly data with {len(weekly_df)} records.', 'success')
                return redirect(url_for('train_select'))
            
            except Exception as e:
                flash(f'Error processing file: {str(e)}', 'error')
                return redirect(request.url)
        else:
            flash('Only CSV files are allowed', 'error')
            return redirect(request.url)
    
    return render_template('upload.html')

@app.route('/train_select')
def train_select():
    weekly_file = os.path.join(app.config['UPLOAD_FOLDER'], 'weekly_data.csv')
    if not os.path.exists(weekly_file):
        flash('Please upload data first', 'error')
        return redirect(url_for('upload'))
    
    df = pd.read_csv(weekly_file)
    products = sorted(df['product_id'].unique())
    
    return render_template('train_select.html', products=products)

@app.route('/train', methods=['POST'])
def train():
    product_id = request.form.get('product_id')
    if not product_id:
        flash('Please select a product', 'error')
        return redirect(url_for('train_select'))
    
    try:
        product_id = int(product_id)
        mae, error = train_model(product_id)
        
        if error:
            flash(error, 'error')
            return redirect(url_for('train_select'))
        
        flash(f'Model trained successfully for Product {product_id}! MAE: {mae:.2f}', 'success')
        return redirect(url_for('models'))
    
    except Exception as e:
        flash(f'Error training model: {str(e)}', 'error')
        return redirect(url_for('train_select'))

@app.route('/models')
def models():
    model_files = [f for f in os.listdir(app.config['MODEL_FOLDER']) if f.endswith('.pkl')]
    
    models_info = []
    for model_file in model_files:
        model_path = os.path.join(app.config['MODEL_FOLDER'], model_file)
        model_data = joblib.load(model_path)
        models_info.append({
            'product_id': model_data['product_id'],
            'mae': model_data['mae'],
            'last_date': model_data['last_date']
        })
    
    return render_template('models.html', models=models_info)

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        product_id = int(request.form.get('product_id'))
        n_weeks = int(request.form.get('n_weeks', 12))
        
        result_df, error = predict_future(product_id, n_weeks)
        
        if error:
            flash(error, 'error')
            return redirect(request.url)
        
        # Convert to HTML table
        predictions_html = result_df.to_html(classes='table table-striped', index=False)
        
        return render_template('predict_result.html', 
                             product_id=product_id, 
                             predictions=predictions_html,
                             n_weeks=n_weeks)
    
    # GET request - show form
    model_files = [f for f in os.listdir(app.config['MODEL_FOLDER']) if f.endswith('.pkl')]
    products = [int(f.split('_')[1].split('.')[0]) for f in model_files]
    
    if not products:
        flash('No trained models available. Please train a model first.', 'error')
        return redirect(url_for('train_select'))
    
    return render_template('predict.html', products=products)

@app.route('/dashboard')
def dashboard():
    weekly_file = os.path.join(app.config['UPLOAD_FOLDER'], 'weekly_data.csv')
    if not os.path.exists(weekly_file):
        flash('Please upload data first', 'error')
        return redirect(url_for('upload'))
    
    df = pd.read_csv(weekly_file)
    df['date'] = pd.to_datetime(df['date'])
    
    # Get available products with models
    model_files = [f for f in os.listdir(app.config['MODEL_FOLDER']) if f.endswith('.pkl')]
    products_with_models = [int(f.split('_')[1].split('.')[0]) for f in model_files]
    
    # Select first product with model or first product
    if products_with_models:
        selected_product = products_with_models[0]
    else:
        selected_product = df['product_id'].iloc[0]
    
    # Get historical data
    product_df = df[df['product_id'] == selected_product].sort_values('date')
    
    # Create plot
    fig = go.Figure()
    
    # Historical data
    fig.add_trace(go.Scatter(
        x=product_df['date'],
        y=product_df['demand'],
        mode='lines+markers',
        name='Historical Demand',
        line=dict(color='blue', width=2)
    ))
    
    # Add forecast if model exists
    model_path = os.path.join(app.config['MODEL_FOLDER'], f'model_{selected_product}.pkl')
    if os.path.exists(model_path):
        forecast_df, _ = predict_future(selected_product, 12)
        if forecast_df is not None:
            fig.add_trace(go.Scatter(
                x=forecast_df['date'],
                y=forecast_df['predicted_demand'],
                mode='lines+markers',
                name='12-Week Forecast',
                line=dict(color='red', width=2, dash='dash')
            ))
    
    fig.update_layout(
        title=f'Demand Forecast Dashboard - Product {selected_product}',
        xaxis_title='Date',
        yaxis_title='Demand',
        hovermode='x unified',
        template='plotly_white'
    )
    
    graph_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    return render_template('dashboard.html', 
                         graph_json=graph_json, 
                         product_id=selected_product,
                         products=products_with_models)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
