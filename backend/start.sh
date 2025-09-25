#!/bin/bash
# Development server startup script

echo "Starting NAMASTE-ICD11 Terminology Service Backend..."
echo "=========================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Start the server
echo "Starting FastAPI server on http://localhost:8000"
echo "API Documentation available at: http://localhost:8000/docs"
echo "=========================================="

uvicorn main:app --host 0.0.0.0 --port 8000 --reload --log-level info