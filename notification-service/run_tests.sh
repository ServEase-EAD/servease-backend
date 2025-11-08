#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Notification Service - Test Suite${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Run tests with coverage
echo -e "${YELLOW}Running tests with coverage...${NC}\n"
python3 -m pytest tests/ -v --cov=app_notifications --cov-report=term --cov-report=html

# Store the exit code
TEST_EXIT_CODE=$?

echo -e "\n${BLUE}========================================${NC}"

# Check if tests passed
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
else
    echo -e "${RED}✗ Some tests failed${NC}"
fi

echo -e "${BLUE}========================================${NC}\n"

# Display coverage summary
echo -e "${YELLOW}Coverage report generated in htmlcov/index.html${NC}\n"

exit $TEST_EXIT_CODE
