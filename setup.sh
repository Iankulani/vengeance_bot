#!/bin/bash

# Vengeance Bot Installation Script for Linux/Mac
# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     🦅 VENGEANCE BOT - Cybersecurity Command Center        ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check Python version
echo -e "${YELLOW}[1/8] Checking Python version...${NC}"
if command -v python3 &>/dev/null; then
    PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    if (( $(echo "$PYTHON_VERSION >= 3.9" | bc -l) )); then
        echo -e "${GREEN}✅ Python $PYTHON_VERSION found${NC}"
    else
        echo -e "${RED}❌ Python 3.9+ required (found $PYTHON_VERSION)${NC}"
        exit 1
    fi
else
    echo -e "${RED}❌ Python3 not found. Please install Python 3.9+${NC}"
    exit 1
fi

# Create virtual environment
echo -e "${YELLOW}[2/8] Creating virtual environment...${NC}"
python3 -m venv venv
source venv/bin/activate
echo -e "${GREEN}✅ Virtual environment created${NC}"

# Upgrade pip
echo -e "${YELLOW}[3/8] Upgrading pip...${NC}"
pip install --upgrade pip
echo -e "${GREEN}✅ pip upgraded${NC}"

# Install requirements
echo -e "${YELLOW}[4/8] Installing Python dependencies...${NC}"
pip install -r requirements.txt
echo -e "${GREEN}✅ Dependencies installed${NC}"

# Install development dependencies
echo -e "${YELLOW}[5/8] Installing development dependencies...${NC}"
pip install -r requirements-dev.txt
echo -e "${GREEN}✅ Development dependencies installed${NC}"

# Create directories
echo -e "${YELLOW}[6/8] Creating required directories...${NC}"
mkdir -p .vengeance reports logs data
mkdir -p .vengeance/phishing .vengeance/captured .vengeance/wordlists
mkdir -p .vengeance/ssh_keys .vengeance/traffic_logs .vengeance/nikto_results
echo -e "${GREEN}✅ Directories created${NC}"

# Install system dependencies (Linux only)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo -e "${YELLOW}[7/8] Installing system dependencies...${NC}"
    if command -v apt-get &>/dev/null; then
        sudo apt-get update
        sudo apt-get install -y nmap whois nikto crunch tcpdump net-tools
    elif command -v yum &>/dev/null; then
        sudo yum install -y nmap whois nikto crunch tcpdump net-tools
    elif command -v brew &>/dev/null; then
        brew install nmap whois nikto crunch tcpdump
    fi
        echo -e "${GREEN}✅ System dependencies installed${NC}"
fi

# Run security scan
echo -e "${YELLOW}[8/8] Running security scan...${NC}"
python security_scan.py
echo -e "${GREEN}✅ Security scan completed${NC}"

# Create .env file from example
if [ ! -f .env ]; then
    cp .env.example .env
    echo -e "${YELLOW}⚠️  Created .env file - please edit with your configuration${NC}"
fi

# Final message
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              ✅ INSTALLATION COMPLETE!                        ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}To start Vengeance Bot:${NC}"
echo -e "  ${BLUE}source venv/bin/activate${NC}"
echo -e "  ${BLUE}python vengeance.py${NC}"
echo ""
echo -e "${YELLOW}To run health check:${NC}"
echo -e "  ${BLUE}python healthcheck.py${NC}"
echo ""
echo -e "${YELLOW}To run security scan:${NC}"
echo -e "  ${BLUE}python security_scan.py${NC}"
echo ""
echo -e "${YELLOW}To run tests:${NC}"
echo -e "  ${BLUE}./run_tests.sh${NC}"
echo ""
echo -e "${YELLOW}Web Dashboard:${NC}"
echo -e "  ${BLUE}http://localhost:5000${NC}"
echo ""