#!/bin/bash
# Quick setup script for Patent Intelligence Dashboard

echo "🚀 Patent Intelligence Dashboard - Setup"
echo "=========================================="
echo ""

# Check Python version
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📥 Installing dependencies from requirements.txt..."
pip install -r requirements.txt

echo ""
echo "✓ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Run the pipeline: python patent_pipeline.py"
echo "2. Generate visualizations: python create_visualizations.py"
echo "3. Launch the dashboard: streamlit run app.py"
echo ""
echo "🌐 The dashboard will open at http://localhost:8501"
echo ""
