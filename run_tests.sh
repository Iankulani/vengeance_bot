#!/bin/bash

# Vengeance Bot Test Runner
# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║           🧪 VENGEANCE BOT - Test Suite                       ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Create test directories
mkdir -p test_reports test_logs

# Run unit tests
echo -e "${YELLOW}[1/4] Running Unit Tests...${NC}"
pytest test_unit.py -v --cov=. --cov-report=html --cov-report=xml --junitxml=test_reports/unit_test_report.xml
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Unit tests passed${NC}"
else
    echo -e "${RED}❌ Unit tests failed${NC}"
fi

# Run integration tests
echo -e "\n${YELLOW}[2/4] Running Integration Tests...${NC}"
pytest test_integration.py -v --timeout=300 --junitxml=test_reports/integration_test_report.xml
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Integration tests passed${NC}"
else
    echo -e "${RED}❌ Integration tests failed${NC}"
fi

# Run command tests
echo -e "\n${YELLOW}[3/4] Running Command Tests...${NC}"
pytest test_commands.py -v --junitxml=test_reports/command_test_report.xml
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Command tests passed${NC}"
else
    echo -e "${RED}❌ Command tests failed${NC}"
fi

# Run security scan
echo -e "\n${YELLOW}[4/4] Running Security Scan...${NC}"
python security_scan.py
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Security scan passed${NC}"
else
    echo -e "${RED}⚠️ Security scan found issues${NC}"
fi

# Generate test report
echo -e "\n${BLUE}📊 Generating Test Report...${NC}"
cat > test_reports/test_summary.html << EOF
<!DOCTYPE html>
<html>
<head>
    <title>Vengeance Bot Test Report</title>
    <style>
        body { font-family: Arial; margin: 40px; }
        h1 { color: #FF6B00; }
        .pass { color: green; }
        .fail { color: red; }
        .summary { background: #f0f0f0; padding: 20px; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>🦅 Vengeance Bot Test Report</h1>
    <div class="summary">
        <h2>Test Summary</h2>
        <p>Generated: $(date)</p>
        <p>Environment: $(python --version 2>&1)</p>
    </div>
    <h2>Test Results</h2>
    <ul>
        <li>Unit Tests: Check test_reports/unit_test_report.xml</li>
        <li>Integration Tests: Check test_reports/integration_test_report.xml</li>
        <li>Command Tests: Check test_reports/command_test_report.xml</li>
    </ul>
    <h2>Coverage Reports</h2>
    <ul>
        <li><a href="htmlcov/index.html">Code Coverage Report</a></li>
    </ul>
</body>
</html>
EOF

echo -e "${GREEN}✅ Test report generated at test_reports/test_summary.html${NC}"
echo -e "\n${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                    ✅ ALL TESTS COMPLETE!                      ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"