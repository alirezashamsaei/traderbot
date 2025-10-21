#!/bin/bash

# Freqtrade Data Download Script
# This script downloads historical data for backtesting and analysis

set -e

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

# Default values
EXCHANGE="mexc"
TIMEFRAMES="15m 1h 4h 1d"
DAYS=30
PAIRS="BTC/USDT ETH/USDT BNB/USDT ADA/USDT SOL/USDT"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--exchange)
            EXCHANGE="$2"
            shift 2
            ;;
        -t|--timeframes)
            TIMEFRAMES="$2"
            shift 2
            ;;
        -d|--days)
            DAYS="$2"
            shift 2
            ;;
        -p|--pairs)
            PAIRS="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  -e, --exchange EXCHANGE    Exchange to download from (default: mexc)"
            echo "  -t, --timeframes TIMES    Timeframes to download (default: '15m 1h 4h 1d')"
            echo "  -d, --days DAYS          Number of days to download (default: 30)"
            echo "  -p, --pairs PAIRS        Pairs to download (default: 'BTC/USDT ETH/USDT BNB/USDT ADA/USDT SOL/USDT')"
            echo "  -h, --help               Show this help message"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Check if virtual environment exists
check_venv() {
    if [ ! -d "venv" ]; then
        print_error "Virtual environment not found. Please run ./scripts/setup.sh first"
        exit 1
    fi
}

# Activate virtual environment
activate_venv() {
    print_status "Activating virtual environment..."
    source venv/bin/activate
}

# Download data for each timeframe
download_data() {
    print_status "Starting data download..."
    print_status "Exchange: $EXCHANGE"
    print_status "Timeframes: $TIMEFRAMES"
    print_status "Days: $DAYS"
    print_status "Pairs: $PAIRS"
    
    for timeframe in $TIMEFRAMES; do
        print_status "Downloading data for timeframe: $timeframe"
        
        freqtrade download-data \
            --exchange $EXCHANGE \
            --timeframes $timeframe \
            --days $DAYS \
            --pairs $PAIRS \
            --data-format json \
            --user-data-dir user_data
        
        print_success "Downloaded data for $timeframe"
    done
}

# Validate downloaded data
validate_data() {
    print_status "Validating downloaded data..."
    
    # Check if data directory exists and has files
    if [ -d "user_data/data" ] && [ "$(ls -A user_data/data)" ]; then
        print_success "Data validation passed"
        
        # Show data summary
        echo ""
        print_status "Data summary:"
        find user_data/data -name "*.json" | head -10 | while read file; do
            echo "  - $(basename "$file")"
        done
        
        total_files=$(find user_data/data -name "*.json" | wc -l)
        print_status "Total files downloaded: $total_files"
    else
        print_error "No data found. Please check your exchange and pair settings"
        exit 1
    fi
}

# Main function
main() {
    print_status "Starting data download process..."
    
    check_venv
    activate_venv
    download_data
    validate_data
    
    print_success "Data download completed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Run backtest: freqtrade backtesting --config config/config.json --strategy MomentumStrategy"
    echo "2. Analyze results: freqtrade plot-dataframe --config config/config.json --strategy MomentumStrategy"
    echo "3. Start paper trading: freqtrade trade --config config/config_dry_run.json"
    echo ""
    echo "For more information, see docs/STRATEGY_DEVELOPMENT.md"
}

# Run main function
main "$@"
