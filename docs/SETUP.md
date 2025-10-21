# Setup Guide

This guide will help you set up the Freqtrade trading bot project for development and testing.

## Prerequisites

- Python 3.11 or higher
- Git
- Docker (optional, for deployment)
- Basic knowledge of cryptocurrency trading
- Understanding of futures trading and leverage risks

## Quick Start

### 1. Clone and Setup

```bash
# Navigate to your project directory
cd /path/to/your/projects

# Clone the repository (if using git)
git clone <repository-url> traderbot
cd traderbot

# Run the automated setup script
./scripts/setup.sh
```

### 2. Configure Environment

```bash
# Copy the environment template
cp .env.example .env

# Edit the environment file with your API keys
nano .env
```

**Important**: Update the following in your `.env` file:
- `MEXC_API_KEY`: Your MEXC API key
- `MEXC_SECRET_KEY`: Your MEXC secret key
- `MEXC_PASSPHRASE`: Your MEXC passphrase (if required)

### 3. Download Historical Data

```bash
# Activate virtual environment
source venv/bin/activate

# Download data for backtesting
./scripts/download_data.sh

# Or download specific data
./scripts/download_data.sh --exchange mexc --days 60 --pairs "BTC/USDT ETH/USDT"
```

### 4. Run Your First Backtest

```bash
# Run backtest with the momentum strategy
freqtrade backtesting --config config/config.json --strategy MomentumStrategy

# View backtest results
freqtrade plot-dataframe --config config/config.json --strategy MomentumStrategy --pairs BTC/USDT
```

### 5. Start Paper Trading

```bash
# Start paper trading (dry run)
freqtrade trade --config config/config_dry_run.json --strategy MomentumStrategy
```

## Manual Setup (Alternative)

If you prefer to set up manually:

### 1. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Create Directories

```bash
mkdir -p user_data/{data,logs,backtest_results,plot}
mkdir -p logs
```

### 4. Configure Environment

```bash
cp .env.example .env
# Edit .env with your API keys
```

## Project Structure

```
traderbot/
├── config/                 # Configuration files
│   ├── config.json         # Main configuration
│   ├── config_dry_run.json # Paper trading config
│   └── blacklist.json        # Coin blacklist
├── strategies/             # Trading strategies
│   └── MomentumStrategy.py  # Initial momentum strategy
├── user_data/              # Freqtrade data directory
│   ├── data/               # Historical data
│   ├── logs/               # Log files
│   ├── backtest_results/   # Backtest results
│   └── plot/               # Plot files
├── scripts/                # Helper scripts
│   ├── setup.sh           # Setup script
│   └── download_data.sh    # Data download script
├── tests/                  # Test files
├── docs/                   # Documentation
└── requirements.txt        # Python dependencies
```

## Configuration Files

### Main Configuration (`config/config.json`)

- **Exchange settings**: MEXC futures exchange configuration
- **Trading parameters**: Position sizing, risk management for futures
- **Leverage settings**: 10x default with dynamic adjustment
- **Margin mode**: Isolated margin for risk control
- **Pair lists**: Which cryptocurrencies to trade
- **Strategy settings**: Default strategy configuration

### Paper Trading Configuration (`config/config_dry_run.json`)

- **Dry run mode**: Simulates futures trading without real money
- **MEXC sandbox**: Uses MEXC testnet for paper trading
- **Futures mode**: Configured for perpetual futures contracts
- **Separate database**: Isolated from live trading data

## Common Commands

### Data Management

```bash
# Download data for specific timeframes
freqtrade download-data --exchange mexc --timeframes 15m 1h --days 30

# List available data
freqtrade list-data --exchange mexc

# Clean old data
freqtrade clean-data --exchange mexc --days 7
```

### Backtesting

```bash
# Run backtest
freqtrade backtesting --config config/config.json --strategy MomentumStrategy

# Backtest with specific date range
freqtrade backtesting --config config/config.json --strategy MomentumStrategy --timerange 20231201-20231231

# Backtest with specific pairs
freqtrade backtesting --config config/config.json --strategy MomentumStrategy --pairs BTC/USDT ETH/USDT
```

### Strategy Optimization

```bash
# Hyperopt for parameter optimization
freqtrade hyperopt --config config/config.json --strategy MomentumStrategy --hyperopt-loss SharpeHyperOptLoss --epochs 100

# List hyperopt results
freqtrade hyperopt-list --config config/config.json
```

### Paper Trading

```bash
# Start paper trading
freqtrade trade --config config/config_dry_run.json --strategy MomentumStrategy

# Check trading status
freqtrade status --config config/config_dry_run.json

# View trade history
freqtrade show-trades --config config/config_dry_run.json
```

## Troubleshooting

### Common Issues

1. **TA-Lib installation fails**
   ```bash
   # On Ubuntu/Debian
   sudo apt-get install build-essential
   wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
   tar -xzf ta-lib-0.4.0-src.tar.gz
   cd ta-lib
   ./configure --prefix=/usr
   make
   sudo make install
   ```

2. **Permission denied on scripts**
   ```bash
   chmod +x scripts/*.sh
   ```

3. **Virtual environment not found**
   ```bash
   # Recreate virtual environment
   rm -rf venv
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **API key errors**
   - Verify your API keys in `.env` file
   - Check API key permissions on MEXC
   - Ensure API keys are for the correct environment (sandbox vs live)

### Getting Help

- Check the logs in `user_data/logs/`
- Run with verbose output: `freqtrade trade --config config/config.json -v`
- Check Freqtrade documentation: https://www.freqtrade.io/
- Review strategy documentation in `docs/STRATEGY_DEVELOPMENT.md`

## Next Steps

1. **Read the strategy documentation**: `docs/STRATEGY_DEVELOPMENT.md`
2. **Set up exchange connection**: `docs/EXCHANGE_SETUP.md`
3. **Learn about deployment**: `docs/DEPLOYMENT.md`
4. **Develop your own strategies**: See examples in `strategies/` directory

## Security Notes

- Never commit your `.env` file with real API keys
- Use paper trading for testing strategies
- Start with small amounts when going live
- Regularly backup your configuration and data
- Keep your API keys secure and rotate them regularly
