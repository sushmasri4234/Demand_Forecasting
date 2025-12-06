#!/bin/bash

echo "========================================"
echo " Demand Forecasting Application"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo ""
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo ""

# Install/upgrade dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
echo ""

# Create necessary directories
mkdir -p uploads
mkdir -p models

# Run the application
echo "========================================"
echo " Starting Flask Application..."
echo " Access at: http://localhost:5000"
echo "========================================"
echo ""
python app.py
