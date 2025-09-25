#!/bin/bash

# NAMASTE-ICD11 Terminology Service Startup Script
# This script sets up and runs the FastAPI backend with authentic terminology data

echo "🏥 Starting NAMASTE-ICD11 Terminology Service"
echo "=============================================="

# Change to backend directory
cd /workspaces/spark-template/backend

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Check if database exists and is populated
if [ ! -f "namaste_terminology.db" ]; then
    echo "🗄️  Database not found. It will be created automatically on first run."
else
    echo "✅ Database found: namaste_terminology.db"
fi

echo ""
echo "🚀 Starting NAMASTE Terminology Service..."
echo "   - Service URL: http://localhost:8000"
echo "   - API Documentation: http://localhost:8000/docs"
echo "   - ReDoc Documentation: http://localhost:8000/redoc"
echo ""
echo "📋 Features Available:"
echo "   - ✅ Authentic NAMASTE terminology search"
echo "   - ✅ ICD-11 mapping visualization" 
echo "   - ✅ FHIR R4 compliant endpoints"
echo "   - ✅ Dual-coding demonstration"
echo "   - ✅ Comprehensive statistics"
echo ""
echo "💡 The frontend will automatically connect to this backend"
echo "   Frontend URL: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop the service"
echo "=============================================="

# Start the FastAPI server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload