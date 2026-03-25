#!/bin/bash
# Medical AI Application Launcher (Linux/Mac)
# This script sets up and runs the Medical AI application

echo ""
echo "========================================"
echo "  Medical AI Pre-Diagnosis System"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "Virtual environment created."
    echo ""
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/Update dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt --quiet

# Create necessary directories
mkdir -p uploads/images
mkdir -p uploads/audio
mkdir -p data

echo ""
echo "========================================"
echo "  Starting Medical AI Server..."
echo "========================================"
echo ""
echo "Server will be available at:"
echo "http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo "========================================"
echo ""

# Run the application
python app.py
