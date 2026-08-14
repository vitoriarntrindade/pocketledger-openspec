#!/bin/bash

# Python Code Quality Check Script
# Runs ruff, flake8, and mypy on Python code
# Usage: ./check-quality.sh [path]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default path
CHECK_PATH="${1:-.}"

# Track results
FAILED=0
WARNINGS=0

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         Python Code Quality Check                              ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if tools are installed
check_tool() {
    if ! command -v "$1" &> /dev/null; then
        echo -e "${RED}✗ $1 not found${NC}"
        echo "  Install with: pip install $2"
        return 1
    fi
    echo -e "${GREEN}✓ $1 found${NC}"
    return 0
}

echo -e "${BLUE}Checking required tools...${NC}"
check_tool "ruff" "ruff" || FAILED=1
check_tool "flake8" "flake8" || FAILED=1
check_tool "mypy" "mypy" || FAILED=1

if [ "$FAILED" -eq 1 ]; then
    echo ""
    echo -e "${RED}Missing required tools. Install with:${NC}"
    echo "  pip install ruff flake8 mypy"
    exit 1
fi

echo ""
echo -e "${BLUE}Running checks on: ${CHECK_PATH}${NC}"
echo ""

# 1. Ruff Check
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}1. Ruff (Fast comprehensive linter)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if ruff check "$CHECK_PATH"; then
    echo -e "${GREEN}✓ Ruff: No issues${NC}"
else
    echo -e "${YELLOW}⚠ Ruff: Issues found${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

echo ""

# 2. Flake8 Check
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}2. Flake8 (PEP 8 compliance)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if flake8 "$CHECK_PATH" --max-line-length=78; then
    echo -e "${GREEN}✓ Flake8: No issues${NC}"
else
    echo -e "${YELLOW}⚠ Flake8: Issues found${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

echo ""

# 3. MyPy Check
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}3. MyPy (Type checking)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if mypy "$CHECK_PATH" --ignore-missing-imports; then
    echo -e "${GREEN}✓ MyPy: No type errors${NC}"
else
    echo -e "${YELLOW}⚠ MyPy: Type errors found${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

echo ""

# Summary
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"

if [ "$WARNINGS" -eq 0 ]; then
    echo -e "${GREEN}║ ✓ All checks passed!                                          ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
    exit 0
else
    echo -e "${YELLOW}║ ⚠ Issues found (see above for details)                        ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
    exit 1
fi
