#!/bin/bash
# Installation and functionality verification script

echo "============================================================"
echo "Nifty Alpha Screen - Installation Verification"
echo "============================================================"
echo ""

# Check Python version
echo "1. Checking Python version..."
python_version=$(python3 --version 2>&1)
echo "   $python_version"

if python3 -c 'import sys; exit(0 if sys.version_info >= (3, 7) else 1)' 2>/dev/null; then
    echo "   ✓ Python version OK"
else
    echo "   ✗ Python 3.7+ required"
    exit 1
fi
echo ""

# Check if requirements are installed
echo "2. Checking required packages..."
packages="pandas numpy yfinance matplotlib requests beautifulsoup4"
all_installed=true

for package in $packages; do
    if python3 -c "import $package" 2>/dev/null; then
        echo "   ✓ $package installed"
    else
        echo "   ✗ $package not installed"
        all_installed=false
    fi
done

if [ "$all_installed" = false ]; then
    echo ""
    echo "   Installing missing packages..."
    pip install -q -r requirements.txt
    echo "   ✓ Packages installed"
fi
echo ""

# Verify syntax
echo "3. Verifying Python syntax..."
if python3 -m py_compile nifty_alpha_screen.py 2>/dev/null; then
    echo "   ✓ nifty_alpha_screen.py syntax OK"
else
    echo "   ✗ Syntax error in nifty_alpha_screen.py"
    exit 1
fi

if python3 -m py_compile demo.py 2>/dev/null; then
    echo "   ✓ demo.py syntax OK"
else
    echo "   ✗ Syntax error in demo.py"
    exit 1
fi
echo ""

# Run tests
echo "4. Running unit tests..."
if python3 test_nifty_alpha_screen.py > /tmp/test_output.txt 2>&1; then
    test_count=$(grep -c "^ok$\|^OK$" /tmp/test_output.txt || echo "0")
    echo "   ✓ All tests passed"
else
    echo "   ✗ Some tests failed"
    cat /tmp/test_output.txt
    exit 1
fi
echo ""

# Run demo
echo "5. Running demo script (this may take 10-20 seconds)..."
if timeout 30 python3 demo.py > /tmp/demo_output.txt 2>&1; then
    if grep -q "DEMO COMPLETE" /tmp/demo_output.txt; then
        echo "   ✓ Demo completed successfully"
        
        if [ -f "demo_results.png" ]; then
            echo "   ✓ Chart generated: demo_results.png"
        fi
    else
        echo "   ✗ Demo did not complete"
        tail -20 /tmp/demo_output.txt
        exit 1
    fi
else
    echo "   ✗ Demo timed out or failed"
    exit 1
fi
echo ""

echo "============================================================"
echo "✓ Installation Verification Complete"
echo "============================================================"
echo ""
echo "Next steps:"
echo "  1. Run: python3 demo.py (for offline demo)"
echo "  2. Run: python3 nifty_alpha_screen.py (for real analysis)"
echo "  3. Read: USAGE.md for detailed instructions"
echo ""
