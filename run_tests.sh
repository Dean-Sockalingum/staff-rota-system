#!/bin/bash

# Test Runner Script for Staff Rota System
# Executes Django tests with coverage reporting

set -e

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Staff Rota System - Test Runner${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    echo -e "${RED}Error: manage.py not found. Please run this script from the project root.${NC}"
    exit 1
fi

# Default options
COVERAGE=false
VERBOSE=false
SPECIFIC_TEST=""
PHASE6_ONLY=false
FAST=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --coverage|-c)
            COVERAGE=true
            shift
            ;;
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --phase6|-p6)
            PHASE6_ONLY=true
            shift
            ;;
        --fast|-f)
            FAST=true
            shift
            ;;
        --test|-t)
            SPECIFIC_TEST="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: ./run_tests.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  -c, --coverage       Generate coverage report"
            echo "  -v, --verbose        Show verbose test output"
            echo "  -p6, --phase6        Run only Phase 6 tests (Tasks 55-59)"
            echo "  -f, --fast           Fast mode (skip coverage, minimal output)"
            echo "  -t, --test <name>    Run specific test file or test case"
            echo "  -h, --help           Show this help message"
            echo ""
            echo "Examples:"
            echo "  ./run_tests.sh                           # Run all tests"
            echo "  ./run_tests.sh --coverage                # Run with coverage"
            echo "  ./run_tests.sh --phase6 --coverage       # Test Phase 6 with coverage"
            echo "  ./run_tests.sh --test test_task55        # Run specific test"
            echo "  ./run_tests.sh --fast                    # Quick test run"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Determine which tests to run
if [ "$PHASE6_ONLY" = true ]; then
    TEST_PATTERN="scheduling.tests.test_task55_activity_feed scheduling.tests.test_task56_compliance_widgets scheduling.tests.test_task57_form_autosave scheduling.tests.test_task59_leave_calendar"
    echo -e "${YELLOW}Running Phase 6 tests only...${NC}"
elif [ -n "$SPECIFIC_TEST" ]; then
    TEST_PATTERN="$SPECIFIC_TEST"
    echo -e "${YELLOW}Running specific test: $SPECIFIC_TEST${NC}"
else
    TEST_PATTERN=""
    echo -e "${YELLOW}Running all tests...${NC}"
fi

# Build test command
if [ "$COVERAGE" = true ] && [ "$FAST" = false ]; then
    echo -e "${BLUE}Enabling coverage reporting...${NC}"
    
    # Install coverage if not available
    if ! python -c "import coverage" 2>/dev/null; then
        echo -e "${YELLOW}Installing coverage package...${NC}"
        pip install coverage -q
    fi
    
    # Run tests with coverage
    TEST_CMD="coverage run --source='.' manage.py test"
    
    if [ "$VERBOSE" = true ]; then
        TEST_CMD="$TEST_CMD --verbosity=2"
    else
        TEST_CMD="$TEST_CMD --verbosity=1"
    fi
    
    TEST_CMD="$TEST_CMD $TEST_PATTERN"
    
    echo -e "${GREEN}Executing: $TEST_CMD${NC}"
    echo ""
    
    eval $TEST_CMD
    TEST_EXIT_CODE=$?
    
    if [ $TEST_EXIT_CODE -eq 0 ]; then
        echo ""
        echo -e "${BLUE}========================================${NC}"
        echo -e "${BLUE}Coverage Report${NC}"
        echo -e "${BLUE}========================================${NC}"
        
        # Generate coverage report
        coverage report -m
        
        # Generate HTML coverage report
        echo ""
        echo -e "${YELLOW}Generating HTML coverage report...${NC}"
        coverage html
        echo -e "${GREEN}HTML report saved to htmlcov/index.html${NC}"
        
        # Show coverage percentage
        COVERAGE_PCT=$(coverage report | tail -1 | awk '{print $NF}')
        echo ""
        echo -e "${GREEN}Total Coverage: $COVERAGE_PCT${NC}"
    fi
    
else
    # Run tests without coverage
    TEST_CMD="python manage.py test"
    
    if [ "$VERBOSE" = true ]; then
        TEST_CMD="$TEST_CMD --verbosity=2"
    elif [ "$FAST" = true ]; then
        TEST_CMD="$TEST_CMD --verbosity=0"
    else
        TEST_CMD="$TEST_CMD --verbosity=1"
    fi
    
    TEST_CMD="$TEST_CMD $TEST_PATTERN"
    
    echo -e "${GREEN}Executing: $TEST_CMD${NC}"
    echo ""
    
    eval $TEST_CMD
    TEST_EXIT_CODE=$?
fi

# Summary
echo ""
echo -e "${BLUE}========================================${NC}"
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
else
    echo -e "${RED}✗ Tests failed with exit code $TEST_EXIT_CODE${NC}"
fi
echo -e "${BLUE}========================================${NC}"

exit $TEST_EXIT_CODE
