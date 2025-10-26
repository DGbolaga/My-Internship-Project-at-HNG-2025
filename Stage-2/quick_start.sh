#!/bin/bash

echo "🚀 Country Currency API - Quick Start"
echo "===================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create cache directory
mkdir -p cache

echo ""
echo "✅ Setup complete!"
echo ""
echo "🎯 Next steps:"
echo "   1. Run the app: uvicorn main:app --reload"
echo "   2. Visit: http://localhost:8000/docs"
echo "   3. Test: pytest test_api.py -v"
echo ""
echo "📚 First time? Run this to load data:"
echo "   curl -X POST http://localhost:8000/countries/refresh"
echo ""