# Strategy Development Guide

This guide covers how to develop, test, and optimize trading strategies for the Freqtrade trading bot.

## Understanding the MomentumStrategy

The initial `MomentumStrategy` is a momentum-based trading strategy that uses:

- **MACD (Moving Average Convergence Divergence)**: Primary trend detection
- **Volume Analysis**: Confirms trading signals
- **RSI (Relative Strength Index)**: Prevents overbought/oversold entries
- **Bollinger Bands**: Identifies price extremes
- **Multiple Momentum Indicators**: Stochastic, Williams %R, CCI

### Strategy Logic

**Entry Conditions:**
1. MACD bullish crossover (MACD line crosses above signal line)
2. Volume above average (confirms market interest)
3. Positive price momentum (recent price increase)
4. RSI not overbought
5. Price above EMA 20 (trend confirmation)
6. ADX shows trend strength
7. Multiple momentum indicators aligned

**Exit Conditions:**
1. MACD bearish crossover
2. RSI overbought
3. Price at upper Bollinger Band
4. Stochastic overbought
5. Negative price momentum

## Creating a New Strategy

### 1. Strategy Template

Create a new file in `strategies/` directory:

```python
# strategies/YourStrategy.py
from freqtrade.strategy import IStrategy, IntParameter, DecimalParameter
import talib.abstract as ta
import pandas as pd
import numpy as np

class YourStrategy(IStrategy):
    """
    Your strategy description here
    """
    
    # Strategy interface version
    INTERFACE_VERSION = 3
    
    # Optimal timeframe
    timeframe = '15m'
    
    # Can this strategy go short?
    can_short: bool = False
    
    # Minimal ROI
    minimal_roi = {
        "60": 0.01,
        "30": 0.02,
        "0": 0.04
    }
    
    # Optimal stoploss
    stoploss = -0.10
    
    # Trailing stoploss
    trailing_stop = True
    trailing_stop_positive = 0.01
    trailing_stop_positive_offset = 0.02
    
    # Strategy parameters (optimizable)
    your_parameter = IntParameter(10, 50, default=20, space="buy")
    
    def populate_indicators(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        """
        Add technical indicators to the dataframe
        """
        # Add your indicators here
        dataframe['sma_20'] = ta.SMA(dataframe, timeperiod=20)
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        
        return dataframe
    
    def populate_entry_trend(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        """
        Define entry conditions
        """
        dataframe.loc[
            (
                # Your entry conditions here
                (dataframe['rsi'] < 30) &
                (dataframe['close'] > dataframe['sma_20'])
            ),
            'enter_long'] = 1
        
        return dataframe
    
    def populate_exit_trend(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        """
        Define exit conditions
        """
        dataframe.loc[
            (
                # Your exit conditions here
                (dataframe['rsi'] > 70)
            ),
            'exit_long'] = 1
        
        return dataframe
```

### 2. Strategy Components

#### Required Methods

- **`populate_indicators()`**: Calculate technical indicators
- **`populate_entry_trend()`**: Define entry conditions
- **`populate_exit_trend()`**: Define exit conditions

#### Optional Methods

- **`custom_stoploss()`**: Custom stoploss logic
- **`custom_exit()`**: Custom exit logic
- **`informative_pairs()`**: Additional data pairs
- **`leverage()`**: Leverage calculation (for margin trading)

### 3. Technical Indicators

Common indicators available through TA-Lib:

```python
# Moving Averages
dataframe['sma_20'] = ta.SMA(dataframe, timeperiod=20)
dataframe['ema_20'] = ta.EMA(dataframe, timeperiod=20)

# Oscillators
dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
dataframe['stoch_k'] = ta.STOCH(dataframe)['slowk']
dataframe['williams_r'] = ta.WILLR(dataframe, timeperiod=14)

# Trend Indicators
dataframe['adx'] = ta.ADX(dataframe, timeperiod=14)
dataframe['macd'] = ta.MACD(dataframe)['macd']

# Volume Indicators
dataframe['obv'] = ta.OBV(dataframe)
dataframe['ad'] = ta.AD(dataframe)

# Volatility Indicators
bollinger = ta.BBANDS(dataframe, timeperiod=20)
dataframe['bb_upper'] = bollinger['upperband']
dataframe['bb_lower'] = bollinger['lowerband']
```

## Testing Your Strategy

### 1. Unit Testing

Create tests in `tests/test_strategies.py`:

```python
def test_your_strategy(self, strategy, sample_dataframe):
    """Test your strategy logic"""
    df = strategy.populate_indicators(sample_dataframe, {})
    df = strategy.populate_entry_trend(df, {})
    
    # Test that entry signals are generated
    assert 'enter_long' in df.columns
    assert df['enter_long'].isin([0, 1]).all()
```

Run tests:
```bash
pytest tests/test_strategies.py -v
```

### 2. Backtesting

```bash
# Basic backtest
freqtrade backtesting --config config/config.json --strategy YourStrategy

# Backtest with specific parameters
freqtrade backtesting --config config/config.json --strategy YourStrategy --timerange 20231201-20231231

# Backtest with specific pairs
freqtrade backtesting --config config/config.json --strategy YourStrategy --pairs BTC/USDT ETH/USDT
```

### 3. Strategy Analysis

```bash
# Plot strategy signals
freqtrade plot-dataframe --config config/config.json --strategy YourStrategy --pairs BTC/USDT

# Plot profit/loss
freqtrade plot-profit --config config/config.json --strategy YourStrategy

# Show trade analysis
freqtrade show-trades --config config/config.json --strategy YourStrategy
```

## Strategy Optimization

### 1. Hyperparameter Optimization

```bash
# Run hyperopt
freqtrade hyperopt --config config/config.json --strategy YourStrategy --hyperopt-loss SharpeHyperOptLoss --epochs 100

# Use specific parameter ranges
freqtrade hyperopt --config config/config.json --strategy YourStrategy --spaces buy --epochs 50

# List hyperopt results
freqtrade hyperopt-list --config config/config.json
```

### 2. Loss Functions

Available loss functions:
- `SharpeHyperOptLoss`: Maximizes Sharpe ratio
- `CalmarHyperOptLoss`: Maximizes Calmar ratio
- `SortinoHyperOptLoss`: Maximizes Sortino ratio
- `OnlyProfitHyperOptLoss`: Maximizes profit only

### 3. Optimization Spaces

```bash
# Optimize buy parameters only
freqtrade hyperopt --spaces buy

# Optimize sell parameters only
freqtrade hyperopt --spaces sell

# Optimize all parameters
freqtrade hyperopt --spaces buy sell
```

## Strategy Best Practices

### 1. Risk Management

```python
# Always set stoploss
stoploss = -0.10

# Use trailing stop
trailing_stop = True
trailing_stop_positive = 0.01

# Limit position size
max_open_trades = 3
```

### 2. Signal Quality

```python
# Use multiple confirmations
dataframe.loc[
    (
        (condition1) &
        (condition2) &
        (condition3)
    ),
    'enter_long'] = 1
```

### 3. Performance Optimization

```python
# Use vectorized operations
dataframe['signal'] = np.where(condition, 1, 0)

# Avoid loops in indicators
# Good: dataframe['sma'] = ta.SMA(dataframe, 20)
# Bad: for i in range(len(dataframe)): ...
```

### 4. Parameter Ranges

```python
# Use reasonable parameter ranges
rsi_period = IntParameter(10, 20, default=14, space="buy")
volume_factor = DecimalParameter(1.0, 3.0, default=1.5, space="buy")
```

## Advanced Features

### 1. Multi-Timeframe Analysis

```python
def informative_pairs(self):
    pairs = self.dp.current_whitelist()
    informative_pairs = [(pair, '1h') for pair in pairs]
    return informative_pairs

def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
    if self.dp:
        inf_tf = self.dp.get_pair_dataframe(pair=metadata['pair'], timeframe='1h')
        inf_tf = self.populate_indicators_1h(inf_tf, metadata)
        dataframe = merge_informative_pair(dataframe, inf_tf, self.timeframe, '1h', ffill=True)
    
    return dataframe
```

### 2. Custom Exit Logic

```python
def custom_exit(self, pair: str, trade: 'Trade', current_time: datetime,
                current_rate: float, current_profit: float, **kwargs) -> Optional[Union[str, bool]]:
    """
    Custom exit logic
    """
    if current_profit > 0.05:  # 5% profit
        return "profit_target"
    
    return None
```

### 3. Dynamic Position Sizing

```python
def custom_stake_amount(self, pair: str, current_time: datetime, current_rate: float,
                      proposed_stake: float, min_stake: Optional[float], max_stake: float,
                      leverage: float, entry_tag: Optional[str], side: str,
                      **kwargs) -> float:
    """
    Custom position sizing based on volatility
    """
    # Calculate volatility-based position size
    volatility = self.calculate_volatility(pair)
    if volatility > 0.05:  # High volatility
        return proposed_stake * 0.5
    return proposed_stake
```

## Strategy Examples

### 1. Mean Reversion Strategy

```python
class MeanReversionStrategy(IStrategy):
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe['bb_upper'] = ta.BBANDS(dataframe)['upperband']
        dataframe['bb_lower'] = ta.BBANDS(dataframe)['lowerband']
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        return dataframe
    
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe['close'] < dataframe['bb_lower']) &
                (dataframe['rsi'] < 30)
            ),
            'enter_long'] = 1
        return dataframe
```

### 2. Trend Following Strategy

```python
class TrendFollowingStrategy(IStrategy):
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe['ema_20'] = ta.EMA(dataframe, timeperiod=20)
        dataframe['ema_50'] = ta.EMA(dataframe, timeperiod=50)
        dataframe['adx'] = ta.ADX(dataframe, timeperiod=14)
        return dataframe
    
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe['ema_20'] > dataframe['ema_50']) &
                (dataframe['adx'] > 25)
            ),
            'enter_long'] = 1
        return dataframe
```

## Troubleshooting

### Common Issues

1. **Strategy not loading**: Check syntax errors and imports
2. **No signals generated**: Verify indicator calculations and conditions
3. **Poor performance**: Review entry/exit logic and risk management
4. **Optimization fails**: Check parameter ranges and data quality

### Debugging Tips

```python
# Add logging to your strategy
import logging
logger = logging.getLogger(__name__)

def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
    logger.info(f"Processing {metadata['pair']} with {len(dataframe)} candles")
    # Your indicator logic here
    return dataframe
```

### Performance Monitoring

```bash
# Monitor strategy performance
freqtrade status --config config/config.json

# Check trade history
freqtrade show-trades --config config/config.json

# Analyze profit/loss
freqtrade plot-profit --config config/config.json
```

## Next Steps

1. **Test your strategy thoroughly** with backtesting
2. **Optimize parameters** using hyperopt
3. **Paper trade** before going live
4. **Monitor performance** and adjust as needed
5. **Document your strategy** for future reference

For more advanced topics, see the Freqtrade documentation: https://www.freqtrade.io/
