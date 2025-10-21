# Freqtrade Algorithmic Trading Bot

A professional algorithmic trading project built with Freqtrade for cryptocurrency trading. This project provides a foundation for developing, testing, and deploying multiple trading strategies with AI/ML capabilities and parameter optimization.

## 🚀 Features

- **Multi-Strategy Architecture**: Easy to add and manage multiple competing trading strategies
- **Futures Trading**: Full support for perpetual futures with both long and short positions
- **Dynamic Leverage**: 10x default leverage with automatic adjustment based on volatility
- **Momentum-Based Strategy**: MACD + Volume strategy for medium-term futures trading
- **Paper Trading**: Safe testing environment with MEXC futures sandbox integration
- **Docker Deployment**: Production-ready containerized deployment
- **AI/ML Ready**: Pre-configured for future machine learning features
- **Parameter Optimization**: Built-in hyperparameter tuning capabilities
- **Professional Documentation**: Comprehensive guides for all aspects

## 📋 Quick Start

### Prerequisites

- Python 3.11+
- Docker (optional, for deployment)
- MEXC account for paper trading

### 1. Setup

```bash
# Clone the repository
git clone <repository-url> traderbot
cd traderbot

# Run automated setup
./scripts/setup.sh

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

### 2. Download Data

```bash
# Download historical data for backtesting
./scripts/download_data.sh
```

### 3. Run Backtest

```bash
# Activate virtual environment
source venv/bin/activate

# Run backtest
freqtrade backtesting --config config/config.json --strategy MomentumStrategy
```

### 4. Start Paper Trading

```bash
# Start paper trading
freqtrade trade --config config/config_dry_run.json --strategy MomentumStrategy
```

## 🏗️ Project Structure

```
traderbot/
├── config/                 # Configuration files
│   ├── config.json         # Main trading configuration
│   ├── config_dry_run.json # Paper trading configuration
│   └── blacklist.json      # Coin blacklist
├── strategies/             # Trading strategies
│   └── MomentumStrategy.py # Initial momentum strategy
├── user_data/              # Freqtrade data directory
│   ├── data/               # Historical data
│   ├── logs/               # Log files
│   ├── backtest_results/   # Backtest results
│   └── plot/               # Plot files
├── scripts/                # Helper scripts
│   ├── setup.sh           # Automated setup
│   └── download_data.sh    # Data download
├── tests/                  # Test files
├── docs/                   # Documentation
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose setup
└── requirements.txt        # Python dependencies
```

## 📚 Documentation

- **[Setup Guide](docs/SETUP.md)**: Complete installation and configuration guide
- **[Strategy Development](docs/STRATEGY_DEVELOPMENT.md)**: How to create and test trading strategies
- **[Exchange Setup](docs/EXCHANGE_SETUP.md)**: Connect to MEXC and other exchanges
- **[Deployment Guide](docs/DEPLOYMENT.md)**: Production deployment with Docker

## 🤖 Trading Strategies

### MomentumStrategy

The initial strategy uses momentum-based signals for both long and short positions:

- **MACD**: Primary trend detection with bullish/bearish crossovers
- **Volume Analysis**: Confirms trading signals with volume spikes
- **RSI**: Prevents overbought/oversold entries
- **Bollinger Bands**: Identifies price extremes
- **Multiple Confirmations**: Stochastic, Williams %R, CCI for signal validation
- **Dynamic Leverage**: Automatically adjusts leverage based on market volatility

**Long Entry Signals:**
- MACD bullish crossover
- Volume above average
- Positive price momentum
- RSI not overbought
- Price above EMA 20
- ADX shows trend strength

**Short Entry Signals:**
- MACD bearish crossover
- Volume above average
- Negative price momentum
- RSI not oversold
- Price below EMA 20
- ADX shows trend strength

**Exit Signals:**
- Long exits: MACD bearish crossover, RSI overbought, price at upper Bollinger Band
- Short exits: MACD bullish crossover, RSI oversold, price at lower Bollinger Band

## 🔧 Configuration

### Environment Variables

```bash
# Exchange API Configuration
MEXC_API_KEY=your_mexc_api_key
MEXC_SECRET_KEY=your_mexc_secret_key

# Optional: Telegram notifications
TELEGRAM_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id

# Risk Management
MAX_OPEN_TRADES=3
STAKE_AMOUNT=100
STAKE_CURRENCY=USDT
```

### Trading Parameters

- **Trading Mode**: Futures (both long and short positions)
- **Leverage**: 10x default with dynamic adjustment (5x-20x range)
- **Margin Mode**: Isolated (risk per position)
- **Timeframe**: 15 minutes (optimized for medium-term trading)
- **Max Open Trades**: 5 concurrent positions
- **Stake Amount**: 100 USDT per trade
- **Stop Loss**: -10% with trailing stop for both directions
- **ROI**: 4% target with time-based scaling

## 🐳 Docker Deployment

### Development

```bash
# Build and run paper trading
docker-compose up freqtrade-dry-run

# Run in background
docker-compose up -d freqtrade-dry-run
```

### Production

```bash
# Build production image
docker-compose build

# Start live trading (after configuration)
docker-compose up freqtrade
```

## 🧪 Testing

### Run Tests

```bash
# Activate virtual environment
source venv/bin/activate

# Run strategy tests
pytest tests/test_strategies.py -v
```

### Backtesting

```bash
# Basic backtest
freqtrade backtesting --config config/config.json --strategy MomentumStrategy

# Backtest with specific date range
freqtrade backtesting --config config/config.json --strategy MomentumStrategy --timerange 20231201-20231231
```

### Strategy Optimization

```bash
# Hyperparameter optimization
freqtrade hyperopt --config config/config.json --strategy MomentumStrategy --hyperopt-loss SharpeHyperOptLoss --epochs 100

# View optimization results
freqtrade hyperopt-list --config config/config.json
```

## 📊 Monitoring

### Paper Trading

```bash
# Check trading status
freqtrade status --config config/config_dry_run.json

# View trade history
freqtrade show-trades --config config/config_dry_run.json

# Plot performance
freqtrade plot-profit --config config/config_dry_run.json
```

### Live Trading

```bash
# Monitor live trades
freqtrade status --config config/config.json

# View live performance
freqtrade plot-profit --config config/config.json
```

## 🔮 Future Features

- **AI/ML Integration**: Machine learning for strategy optimization
- **Parameter Tuning**: Automated hyperparameter optimization
- **Multi-Exchange Support**: Support for additional exchanges
- **Advanced Analytics**: Enhanced performance metrics and reporting
- **Strategy Competition**: Framework for comparing multiple strategies

## 🛡️ Security

- **API Key Protection**: Environment variables for sensitive data
- **Paper Trading First**: Always test strategies before live trading
- **Risk Management**: Built-in position sizing and stop losses
- **Monitoring**: Comprehensive logging and alerting

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Develop your strategy
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This software is for educational and research purposes only. **Futures trading with leverage involves substantial risk of loss and potential liquidation.** Never trade with money you cannot afford to lose. Always test strategies thoroughly with paper trading before using real funds. Leverage amplifies both gains and losses - use appropriate risk management.

## 🆘 Support

- **Documentation**: Check the `docs/` directory for detailed guides
- **Issues**: Report bugs and feature requests via GitHub issues
- **Community**: Join the Freqtrade Discord for support
- **Exchange Setup**: See `docs/EXCHANGE_SETUP.md` for exchange configuration

## 🚀 Getting Started

1. **Read the Setup Guide**: [docs/SETUP.md](docs/SETUP.md)
2. **Configure Exchange**: [docs/EXCHANGE_SETUP.md](docs/EXCHANGE_SETUP.md)
3. **Develop Strategies**: [docs/STRATEGY_DEVELOPMENT.md](docs/STRATEGY_DEVELOPMENT.md)
4. **Deploy to Production**: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)

---

**Happy Trading! 📈**
