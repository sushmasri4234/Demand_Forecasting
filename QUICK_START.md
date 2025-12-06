# ⚡ Quick Start Guide

Get the Demand Forecasting app running in under 5 minutes!

## 🚀 Fastest Way to Start

### Windows Users
```bash
# Just double-click this file:
run.bat
```

### Mac/Linux Users
```bash
# Run this command:
chmod +x run.sh && ./run.sh
```

That's it! The app will open at **http://localhost:5000**

---

## 📝 Manual Installation (If Scripts Don't Work)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run the App
```bash
python app.py
```

### Step 3: Open Browser
```
http://localhost:5000
```

---

## 🧪 Test with Sample Data

1. **Upload Data**
   - Go to "Upload Data" page
   - Select `sample_data.csv`
   - Click "Upload and Process"

2. **Train Model**
   - Go to "Train Model" page
   - Select "Product 101"
   - Click "Train Model"
   - Wait ~10 seconds

3. **Make Predictions**
   - Go to "Predict" page
   - Select "Product 101"
   - Enter "12" weeks
   - Click "Generate Forecast"

4. **View Dashboard**
   - Go to "Dashboard" page
   - See interactive chart with historical data and forecast

---

## 🐳 Docker Quick Start

```bash
# Build
docker build -t demand-forecasting .

# Run
docker run -p 5000:5000 demand-forecasting

# Access
http://localhost:5000
```

---

## 🆘 Common Issues

### "Python not found"
**Solution:** Install Python 3.10+ from python.org

### "pip not found"
**Solution:** Run `python -m ensurepip --upgrade`

### "Port 5000 in use"
**Solution:** Edit app.py, change port to 5001:
```python
app.run(debug=True, port=5001)
```

### "Module not found"
**Solution:** Activate virtual environment:
```bash
# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

---

## 📚 Next Steps

- Read [README.md](README.md) for full documentation
- Check [INSTALLATION.md](INSTALLATION.md) for detailed setup
- See [DEPLOYMENT.md](DEPLOYMENT.md) for cloud deployment
- Review [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) for overview

---

## 🎯 Application Flow

```
1. Upload CSV → 2. Train Model → 3. Predict → 4. Dashboard
     ↓              ↓                ↓           ↓
  Daily data    RandomForest    12-week      Interactive
  → Weekly      per product     forecast      Plotly chart
```

---

## 📊 What You Get

✅ Automatic daily → weekly conversion  
✅ 12 lag features + rolling averages  
✅ RandomForest ML models  
✅ Autoregressive forecasting  
✅ Interactive Plotly dashboards  
✅ Model persistence & management  

---

## 🔗 Quick Links

- **Homepage**: http://localhost:5000
- **Upload**: http://localhost:5000/upload
- **Train**: http://localhost:5000/train_select
- **Predict**: http://localhost:5000/predict
- **Dashboard**: http://localhost:5000/dashboard
- **Models**: http://localhost:5000/models

---

## 💡 Pro Tips

1. **Use sample_data.csv** for quick testing
2. **Train takes ~10 seconds** per product
3. **Dashboard updates** automatically with new models
4. **MAE < 50** indicates good model performance
5. **Forecast 12-52 weeks** for best results

---

**Need help? Check the troubleshooting section above or read the full documentation!**

🎉 **Happy Forecasting!**
