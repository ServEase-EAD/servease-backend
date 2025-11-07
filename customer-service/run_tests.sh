#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}================================${NC}"
echo -e "${YELLOW}Customer Service - Running Tests${NC}"
echo -e "${YELLOW}================================${NC}"
echo ""

# Run pytest with coverage
pytest --cov=customers --cov-report=html --cov-report=term-missing

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}==================================${NC}"
    echo -e "${GREEN}✓ All tests passed successfully!${NC}"
    echo -e "${GREEN}==================================${NC}"
else
    echo ""
    echo -e "${RED}==================================${NC}"
    echo -e "${RED}✗ Tests failed!${NC}"
    echo -e "${RED}Please review the errors above.${NC}"
    echo -e "${RED}==================================${NC}"
    exit 1
fi
