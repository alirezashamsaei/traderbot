#!/bin/bash

# Freqtrade Trading Bot Setup Script
# This script sets up the development environment for the trading bot

set -e

echo "🚀 Setting up Freqtrade Trading Bot..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python 3.11+ is installed
check_python() {
    print_status "Checking Python version..."
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        if [[ $(echo "$PYTHON_VERSION >= 3.11" | bc -l) -eq 1 ]]; then
            print_success "Python $PYTHON_VERSION found"
        else
            print_error "Python 3.11+ is required. Found: $PYTHON_VERSION"
            exit 1
        fi
    else
        print_error "Python 3 is not installed"
        exit 1
    fi
}

# Check if virtual environment tools are available
check_venv() {
    print_status "Checking virtual environment tools..."
    if command -v python3 -m venv &> /dev/null; then
        print_success "Virtual environment support found"
    else
        print_error "python3-venv is not installed. Please install it first."
        exit 1
    fi
}

# Create virtual environment
create_venv() {
    print_status "Creating virtual environment..."
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_success "Virtual environment created"
    else
        print_warning "Virtual environment already exists"
    fi
}

# Activate virtual environment and install dependencies
install_dependencies() {
    print_status "Activating virtual environment and installing dependencies..."
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install requirements
    pip install -r requirements.txt
    
    print_success "Dependencies installed"
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    mkdir -p user_data/{data,logs,backtest_results,plot}
    mkdir -p logs
    print_success "Directories created"
}

# Copy environment file
setup_environment() {
    print_status "Setting up environment configuration..."
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_success "Environment file created from template"
            print_warning "Please edit .env file with your API keys and configuration"
        else
            print_error ".env.example file not found"
        fi
    else
        print_warning "Environment file already exists"
    fi
}

# Test Freqtrade installation
test_installation() {
    print_status "Testing Freqtrade installation..."
    source venv/bin/activate
    if freqtrade --version &> /dev/null; then
        print_success "Freqtrade is working correctly"
    else
        print_error "Freqtrade installation test failed"
        exit 1
    fi
}

# Main setup function
main() {
    print_status "Starting Freqtrade Trading Bot setup..."
    
    check_python
    check_venv
    create_venv
    install_dependencies
    create_directories
    setup_environment
    test_installation
    
    print_success "Setup completed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Edit .env file with your API keys"
    echo "2. Activate virtual environment: source venv/bin/activate"
    echo "3. Download data: ./scripts/download_data.sh"
    echo "4. Run backtest: freqtrade backtesting --config config/config.json --strategy MomentumStrategy"
    echo "5. Start paper trading: freqtrade trade --config config/config_dry_run.json"
    echo ""
    echo "For more information, see docs/SETUP.md"
}

# Run main function
main "$@"
