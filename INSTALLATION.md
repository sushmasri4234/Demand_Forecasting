# 📦 Installation & Setup Guide

## Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Git (optional, for version control)

## Step-by-Step Installation

### 1. Navigate to Project Directory

```bash
cd c:\Users\keert\OneDrive\Desktop\Projects\demand_forecasting
```

### 2. Create Virtual Environment

**Windows:**
```bash
python -m venv venv
```

**Mac/Linux:**
```bash
python3 -m venv venv
```

### 3. Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**Mac/Linux:**
```bash
source venv/bin/activate
```

You should see `(venv)` prefix in your terminal.

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- Flask 2.3.2
- pandas 2.0.3
- numpy 1.24.3
- scikit-learn 1.3.0
- plotly 5.15.0
- joblib 1.3.1
- Werkzeug 2.3.6

### 5. Verify Installation

```bash
python -c "import flask, pandas, sklearn, plotly; print('All packages installed successfully!')"
```

### 6. Run the Application

```bash
python app.py
```

You should see output like:
```
 * Running on http://0.0.0.0:5000
 * Running on http://127.0.0.1:5000
```

### 7. Access the Application

Open your web browser and navigate to:
```
http://localhost:5000
```

## Quick Test with Sample Data

1. Open the application at `http://localhost:5000`
2. Click "Upload Data"
3. Upload the `sample_data.csv` file
4. Click "Train Model" and select Product 101
5. Wait for training to complete
6. Click "Predict" and generate a 12-week forecast
7. View the "Dashboard" for visualizations

## Troubleshooting

### Issue: "python: command not found"
**Solution:** Use `python3` instead of `python`

### Issue: "pip: command not found"
**Solution:** Install pip:
```bash
python -m ensurepip --upgrade
```

### Issue: "Permission denied"
**Solution:** Run with administrator/sudo privileges or use:
```bash
pip install --user -r requirements.txt
```

### Issue: Port 5000 already in use
**Solution:** Edit `app.py` and change the port:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

### Issue: Module not found errors
**Solution:** Ensure virtual environment is activated and reinstall:
```bash
pip install --upgrade -r requirements.txt
```

## Deactivating Virtual Environment

When you're done, deactivate the virtual environment:
```bash
deactivate
```

## Updating Dependencies

To update all packages to latest versions:
```bash
pip install --upgrade -r requirements.txt
```

## Uninstallation

To remove the project:
1. Deactivate virtual environment: `deactivate`
2. Delete the project folder
3. Remove virtual environment: `rm -rf venv` (Mac/Linux) or `rmdir /s venv` (Windows)

## Next Steps

- Read the [README.md](README.md) for usage instructions
- Check deployment options for production use
- Customize the application for your specific needs

---

**Need help?** Open an issue on GitHub or contact support.
