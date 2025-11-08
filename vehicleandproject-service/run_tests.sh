#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "========================================"
echo "Vehicle & Project Service - Test Suite"
echo "========================================"
echo ""
echo "Running tests with coverage..."
echo ""

# Run pytest with coverage
python3 -m pytest tests/ -v --cov=vehicles --cov=projects --cov-report=term --cov-report=html

# Capture the exit code
EXIT_CODE=$?

echo ""
echo "========================================"
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
else
    echo -e "${RED}✗ Some tests failed${NC}"
fi
echo "========================================"
echo ""
echo "Coverage report generated in htmlcov/index.html"
echo ""

exit $EXIT_CODE
