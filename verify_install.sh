#!/bin/bash
# Installation and verification script

echo "========================================"
echo "NSE Stock Analysis System"
echo "Installation Verification"
echo "========================================"
echo ""

# Check Python version
echo "1. Checking Python version..."
python3 --version
if [ $? -eq 0 ]; then
    echo "   ✓ Python installed"
else
    echo "   ✗ Python not found"
    exit 1
fi
echo ""

# Check pip
echo "2. Checking pip..."
pip --version
if [ $? -eq 0 ]; then
    echo "   ✓ pip installed"
else
    echo "   ✗ pip not found"
    exit 1
fi
echo ""

# Install dependencies
echo "3. Installing dependencies..."
pip install -r requirements.txt --quiet
if [ $? -eq 0 ]; then
    echo "   ✓ Dependencies installed"
else
    echo "   ✗ Failed to install dependencies"
    exit 1
fi
echo ""

# Run tests
echo "4. Running unit tests..."
python test_system.py
if [ $? -eq 0 ]; then
    echo "   ✓ All tests passed"
else
    echo "   ✗ Tests failed"
    exit 1
fi
echo ""

# Check modules can be imported
echo "5. Verifying modules..."
python -c "import nse_data_fetcher; import data_pipeline; import pandas; import streamlit" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "   ✓ All modules can be imported"
else
    echo "   ✗ Module import failed"
    exit 1
fi
echo ""

echo "========================================"
echo "✓ Installation Verified Successfully!"
echo "========================================"
echo ""
echo "Next steps:"
echo "  1. Run dashboard: streamlit run dashboard.py"
echo "  2. Run CLI: python cli.py --symbol RELIANCE"
echo "  3. Read docs: cat README.md"
echo ""

