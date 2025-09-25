#!/bin/bash

echo "Setting up NAMASTE-ICD11 Terminology Service Backend..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required but not installed."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Setup complete!"
echo ""
echo "To start the backend server:"
echo "1. cd backend"
echo "2. source venv/bin/activate"
echo "3. python main.py"
echo ""
echo "The API will be available at: http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"