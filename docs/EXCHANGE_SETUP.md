# Exchange Setup Guide

This guide covers how to set up and connect to cryptocurrency exchanges for paper trading and live trading.

## Supported Exchanges

The project is configured to work with MEXC exchange by default, but supports many other exchanges through Freqtrade's CCXT integration.

### Primary Exchange: MEXC

MEXC is configured as the default exchange for:
- Paper trading (sandbox mode)
- Live trading
- Data downloading

### Alternative Exchanges

Freqtrade supports 100+ exchanges through CCXT. Popular alternatives:
- Binance
- Coinbase Pro
- Kraken
- KuCoin
- Bybit

## MEXC Exchange Setup

### 1. Create MEXC Account

1. Visit [MEXC Global](https://www.mexc.com/)
2. Sign up for an account
3. Complete KYC verification (required for trading)

### 2. Generate API Keys

1. **Log in to MEXC**
2. **Navigate to API Management**
   - Go to Account → API Management
   - Or visit: https://www.mexc.com/user/api

3. **Create New API Key**
   - Click "Create API Key"
   - Set a descriptive name (e.g., "Freqtrade Bot")
   - Choose permissions (see below)

4. **Set API Permissions**
   - ✅ **Read**: Required for data access
   - ✅ **Trade**: Required for paper trading and live trading
   - ✅ **Futures Trading**: Required for futures contracts
   - ❌ **Withdraw**: Not needed for trading (leave disabled for security)

5. **Configure IP Restrictions** (Recommended)
   - Add your server's IP address
   - Or leave blank for development (less secure)

6. **Save API Credentials**
   - Copy the API Key
   - Copy the Secret Key
   - **Important**: Save these securely - you won't see them again

### 3. Configure Environment

Update your `.env` file with MEXC credentials:

```bash
# MEXC Exchange Configuration
MEXC_API_KEY=your_api_key_here
MEXC_SECRET_KEY=your_secret_key_here
MEXC_PASSPHRASE=your_passphrase_here  # If required
```

### 4. Test Connection

```bash
# Activate virtual environment
source venv/bin/activate

# Test MEXC connection
freqtrade list-markets --exchange mexc

# Test futures markets specifically
freqtrade list-markets --exchange mexc --trading-mode futures

# Test with specific pair
freqtrade list-markets --exchange mexc --quote USDT
```

## Paper Trading Setup

### 1. MEXC Sandbox Mode

MEXC provides a sandbox environment for testing:

```json
{
    "exchange": {
        "name": "mexc",
        "ccxt_config": {
            "sandbox": true,
            "apiKey": "your_sandbox_api_key",
            "secret": "your_sandbox_secret"
        }
    }
}
```

### 2. Configure Paper Trading

Use the `config_dry_run.json` configuration:

```bash
# Start paper trading
freqtrade trade --config config/config_dry_run.json --strategy MomentumStrategy

# Check paper trading status
freqtrade status --config config/config_dry_run.json
```

### 3. Paper Trading Features

- **Simulated Trading**: No real money at risk
- **Real Market Data**: Uses live market prices
- **Full Strategy Testing**: Complete trading simulation
- **Performance Tracking**: Monitor strategy performance

## Alternative Exchange Setup

### Binance Setup

1. **Create Binance Account**
   - Visit [Binance](https://www.binance.com/)
   - Complete registration and KYC

2. **Generate API Keys**
   - Go to Account → API Management
   - Create new API key
   - Enable "Enable Trading" permission
   - Disable "Enable Withdrawals" (security)

3. **Update Configuration**

```json
{
    "exchange": {
        "name": "binance",
        "key": "your_binance_api_key",
        "secret": "your_binance_secret_key"
    }
}
```

4. **Update Environment**

```bash
# In .env file
BINANCE_API_KEY=your_binance_api_key
BINANCE_SECRET_KEY=your_binance_secret_key
```

### Coinbase Pro Setup

1. **Create Coinbase Pro Account**
   - Visit [Coinbase Pro](https://pro.coinbase.com/)
   - Link to existing Coinbase account

2. **Generate API Keys**
   - Go to Settings → API
   - Create new API key
   - Set permissions: View, Trade
   - Generate passphrase

3. **Update Configuration**

```json
{
    "exchange": {
        "name": "coinbasepro",
        "key": "your_coinbase_api_key",
        "secret": "your_coinbase_secret",
        "password": "your_coinbase_passphrase"
    }
}
```

## Exchange Configuration

### 1. Main Configuration (`config/config.json`)

```json
{
    "exchange": {
        "name": "mexc",
        "key": "",
        "secret": "",
        "ccxt_config": {
            "sandbox": false,
            "apiKey": "",
            "secret": "",
            "options": {
                "defaultType": "spot"
            }
        },
        "pair_whitelist": [
            "BTC/USDT",
            "ETH/USDT",
            "BNB/USDT"
        ]
    }
}
```

### 2. Paper Trading Configuration (`config/config_dry_run.json`)

```json
{
    "exchange": {
        "name": "mexc",
        "ccxt_config": {
            "sandbox": true,
            "apiKey": "",
            "secret": "",
            "options": {
                "defaultType": "spot"
            }
        }
    }
}
```

## Security Best Practices

### 1. API Key Security

- **Never commit API keys** to version control
- **Use environment variables** for sensitive data
- **Rotate API keys** regularly
- **Use IP restrictions** when possible
- **Disable withdrawal permissions**

### 2. Account Security

- **Enable 2FA** on your exchange account
- **Use strong passwords**
- **Monitor account activity** regularly
- **Keep API keys secure** and private

### 3. Trading Security

- **Start with paper trading** to test strategies
- **Use small amounts** when going live
- **Monitor trades** closely
- **Set up alerts** for unusual activity

## Troubleshooting

### Common Issues

1. **API Key Invalid**
   ```
   Error: Invalid API key
   ```
   - Check API key and secret in `.env` file
   - Verify API key is active on exchange
   - Check API key permissions

2. **Insufficient Permissions**
   ```
   Error: Insufficient permissions
   ```
   - Enable "Trade" permission on API key
   - Check IP restrictions
   - Verify account verification status

3. **Sandbox Mode Issues**
   ```
   Error: Sandbox not available
   ```
   - Some exchanges don't have sandbox
   - Use paper trading mode instead
   - Check exchange-specific sandbox setup

4. **Rate Limiting**
   ```
   Error: Rate limit exceeded
   ```
   - Reduce trading frequency
   - Increase delays between requests
   - Check exchange rate limits

### Debugging Connection

```bash
# Test exchange connection
freqtrade list-markets --exchange mexc --verbose

# Check specific pair
freqtrade list-markets --exchange mexc --pairs BTC/USDT

# Test with sandbox
freqtrade list-markets --exchange mexc --config config/config_dry_run.json
```

### Exchange-Specific Issues

#### MEXC Issues

- **Passphrase Required**: Some MEXC accounts require a passphrase
- **IP Restrictions**: Check if IP is whitelisted
- **Account Verification**: Ensure account is fully verified

#### Binance Issues

- **API Restrictions**: Check if API key has trading permissions
- **IP Restrictions**: Verify IP whitelist settings
- **Account Status**: Ensure account is not restricted

## Testing Your Setup

### 1. Connection Test

```bash
# Test basic connection
freqtrade list-markets --exchange mexc

# Test with specific configuration
freqtrade list-markets --config config/config_dry_run.json
```

### 2. Paper Trading Test

```bash
# Start paper trading
freqtrade trade --config config/config_dry_run.json --strategy MomentumStrategy

# Check status
freqtrade status --config config/config_dry_run.json

# View trades
freqtrade show-trades --config config/config_dry_run.json
```

### 3. Data Download Test

```bash
# Download test data
freqtrade download-data --exchange mexc --pairs BTC/USDT --timeframes 15m --days 1

# Verify data
freqtrade list-data --exchange mexc
```

## Going Live

### 1. Pre-Live Checklist

- [ ] Strategy thoroughly backtested
- [ ] Paper trading successful
- [ ] Risk management configured
- [ ] Monitoring systems in place
- [ ] Emergency stop procedures ready

### 2. Live Trading Configuration

```bash
# Update .env with live API keys
MEXC_API_KEY=your_live_api_key
MEXC_SECRET_KEY=your_live_secret_key

# Start live trading
freqtrade trade --config config/config.json --strategy MomentumStrategy
```

### 3. Monitoring

- **Check trades regularly**
- **Monitor performance metrics**
- **Set up alerts for errors**
- **Keep logs for analysis**

## Support and Resources

### Exchange Support

- **MEXC Support**: https://support.mexc.com/
- **Binance Support**: https://www.binance.com/en/support
- **Coinbase Support**: https://help.coinbase.com/

### Freqtrade Documentation

- **Exchange Configuration**: https://www.freqtrade.io/en/stable/configuration/#exchange-configuration
- **CCXT Exchanges**: https://github.com/ccxt/ccxt/wiki/Exchange-Markets
- **Troubleshooting**: https://www.freqtrade.io/en/stable/troubleshooting/

### Community Support

- **Freqtrade Discord**: https://discord.gg/freqtrade
- **Reddit**: r/freqtrade
- **GitHub Issues**: https://github.com/freqtrade/freqtrade/issues
