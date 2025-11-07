#!/bin/bash

# Authentication Service Test Runner
# This script runs all tests with coverage reporting

echo "=================================="
echo "Authentication Service Test Suite"
echo "=================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Run tests with coverage
echo "${YELLOW}Running tests with coverage...${NC}"
echo ""

pytest --cov=accounts \
       --cov-report=term-missing \
       --cov-report=html \
       --cov-fail-under=80 \
       -v

# Capture the exit code
TEST_EXIT_CODE=$?

echo ""
echo "=================================="

# Check if tests passed
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "${GREEN}✓ All tests passed!${NC}"
    echo ""
    echo "${GREEN}Coverage report generated in htmlcov/index.html${NC}"
    echo "Open it with: open htmlcov/index.html"
else
    echo "${RED}✗ Tests failed!${NC}"
    echo "Please review the errors above."
fi

echo "=================================="
echo ""

# Exit with the same code as pytest
exit $TEST_EXIT_CODE
