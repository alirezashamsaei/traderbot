# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement
# flake8: noqa: F401
# isort: skip_file
# --- Do not remove these libs ---
import numpy as np
import pandas as pd
from pandas import DataFrame
from typing import Optional, Union
from datetime import datetime

from freqtrade.strategy import (BooleanParameter, CategoricalParameter, DecimalParameter,
                                IntParameter, IStrategy, merge_informative_pair)
from freqtrade.persistence import Trade

# --------------------------------
# Add your lib to import here
import talib.abstract as ta
from freqtrade.strategy import IStrategy, informative


class MomentumStrategy(IStrategy):
    """
    Momentum-based trading strategy using MACD with volume confirmation.
    
    This strategy identifies momentum shifts in the market using:
    - MACD (Moving Average Convergence Divergence) for trend detection
    - Volume analysis for confirmation
    - Price momentum indicators
    
    Entry signals:
    - MACD bullish crossover (MACD line crosses above signal line)
    - Volume above average (confirms interest)
    - Price momentum positive (recent price increase)
    
    Exit signals:
    - MACD bearish crossover
    - Trailing stop loss
    - Take profit levels
    """
    
    # Strategy interface version - allow new iterations of the strategy
    INTERFACE_VERSION = 3
    
    # Optimal timeframe for the strategy
    timeframe = '15m'
    
    # Can this strategy go short?
    can_short: bool = True
    
    # Minimal ROI designed for the strategy.
    minimal_roi = {
        "60": 0.01,
        "30": 0.02,
        "0": 0.04
    }
    
    # Optimal stoploss designed for the strategy
    stoploss = -0.10
    
    # Trailing stoploss
    trailing_stop = True
    trailing_stop_positive = 0.01
    trailing_stop_positive_offset = 0.02
    trailing_only_offset_is_reached = True
    
    # Run "populate_indicators" only for new candle
    process_only_new_candles = False
    
    # These values can be overridden in the config
    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = False
    
    # Number of candles the strategy requires before producing valid signals
    startup_candle_count: int = 30
    
    # Optional order type mapping
    order_types = {
        'entry': 'limit',
        'exit': 'limit',
        'stoploss': 'market',
        'stoploss_on_exchange': False
    }
    
    # Optional order time in force
    order_time_in_force = {
        'entry': 'gtc',
        'exit': 'gtc'
    }
    
    # Strategy parameters (optimizable)
    macd_fast = IntParameter(8, 16, default=12, space="buy")
    macd_slow = IntParameter(20, 30, default=26, space="buy")
    macd_signal = IntParameter(7, 12, default=9, space="buy")
    
    volume_factor = DecimalParameter(1.0, 3.0, default=1.5, space="buy")
    rsi_period = IntParameter(10, 20, default=14, space="buy")
    rsi_oversold = IntParameter(20, 40, default=30, space="buy")
    rsi_overbought = IntParameter(60, 80, default=70, space="buy")
    
    # Exit parameters
    exit_macd_threshold = DecimalParameter(-0.001, 0.001, default=0.0, space="sell")
    
    # Leverage parameters
    base_leverage = IntParameter(5, 20, default=10, space="buy")
    max_leverage = IntParameter(10, 50, default=20, space="buy")
    volatility_threshold = DecimalParameter(0.02, 0.10, default=0.05, space="buy")
    
    def informative_pairs(self):
        """
        Define additional, informative pair/interval combinations to be cached from the exchange.
        These pairs will automatically be available for use in the `populate_indicators` method.
        """
        pairs = self.dp.current_whitelist()
        informative_pairs = [(pair, '1h') for pair in pairs]
        return informative_pairs
    
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Adds several different TA indicators to the given DataFrame
        
        Performance Note: For the best performance be frugal on the number of indicators
        you are using. Let uncomment only the indicator you are using in your strategies
        or your hyperopt configuration, otherwise you will waste your memory and CPU usage.
        """
        
        # MACD
        macd = ta.MACD(dataframe, fastperiod=self.macd_fast.value, 
                      slowperiod=self.macd_slow.value, signalperiod=self.macd_signal.value)
        dataframe['macd'] = macd['macd']
        dataframe['macdsignal'] = macd['macdsignal']
        dataframe['macdhist'] = macd['macdhist']
        
        # RSI
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=self.rsi_period.value)
        
        # Bollinger Bands
        bollinger = ta.BBANDS(dataframe, timeperiod=20, nbdevup=2, nbdevdn=2)
        dataframe['bb_lowerband'] = bollinger['lowerband']
        dataframe['bb_middleband'] = bollinger['middleband']
        dataframe['bb_upperband'] = bollinger['upperband']
        dataframe['bb_percent'] = (dataframe['close'] - dataframe['bb_lowerband']) / (dataframe['bb_upperband'] - dataframe['bb_lowerband'])
        dataframe['bb_width'] = (dataframe['bb_upperband'] - dataframe['bb_lowerband']) / dataframe['bb_middleband']
        
        # Volume indicators
        dataframe['volume_mean'] = dataframe['volume'].rolling(window=20).mean()
        dataframe['volume_ratio'] = dataframe['volume'] / dataframe['volume_mean']
        
        # Price momentum
        dataframe['price_change'] = dataframe['close'].pct_change(periods=5)
        dataframe['price_momentum'] = dataframe['close'] / dataframe['close'].shift(5) - 1
        
        # EMA for trend confirmation
        dataframe['ema_20'] = ta.EMA(dataframe, timeperiod=20)
        dataframe['ema_50'] = ta.EMA(dataframe, timeperiod=50)
        
        # ADX for trend strength
        dataframe['adx'] = ta.ADX(dataframe, timeperiod=14)
        
        # Stochastic for momentum confirmation
        stoch = ta.STOCH(dataframe, fastk_period=14, slowk_period=3, slowd_period=3)
        dataframe['stoch_k'] = stoch['slowk']
        dataframe['stoch_d'] = stoch['slowd']
        
        # Williams %R
        dataframe['williams_r'] = ta.WILLR(dataframe, timeperiod=14)
        
        # CCI (Commodity Channel Index)
        dataframe['cci'] = ta.CCI(dataframe, timeperiod=20)
        
        # MACD crossover signals
        dataframe['macd_cross'] = np.where(
            (dataframe['macd'] > dataframe['macdsignal']) & 
            (dataframe['macd'].shift(1) <= dataframe['macdsignal'].shift(1)), 1, 0
        )
        dataframe['macd_cross_down'] = np.where(
            (dataframe['macd'] < dataframe['macdsignal']) & 
            (dataframe['macd'].shift(1) >= dataframe['macdsignal'].shift(1)), 1, 0
        )
        
        return dataframe
    
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the entry signal for the given dataframe
        :param dataframe: DataFrame populated with indicators
        :param metadata: Additional information, like the currently traded pair
        :return: DataFrame with entry columns populated
        """
        
        # Long entry conditions
        dataframe.loc[
            (
                # MACD bullish crossover
                (dataframe['macd_cross'] == 1) &
                
                # Volume confirmation
                (dataframe['volume_ratio'] > self.volume_factor.value) &
                
                # Price momentum positive
                (dataframe['price_momentum'] > 0.01) &
                
                # RSI not overbought
                (dataframe['rsi'] < self.rsi_overbought.value) &
                (dataframe['rsi'] > self.rsi_oversold.value) &
                
                # Trend confirmation (price above EMA)
                (dataframe['close'] > dataframe['ema_20']) &
                
                # ADX shows trend strength
                (dataframe['adx'] > 25) &
                
                # Stochastic not overbought
                (dataframe['stoch_k'] < 80) &
                (dataframe['stoch_d'] < 80) &
                
                # Williams %R not overbought
                (dataframe['williams_r'] > -20) &
                
                # CCI not overbought
                (dataframe['cci'] < 100) &
                
                # Price not at upper Bollinger Band
                (dataframe['bb_percent'] < 0.8)
            ),
            'enter_long'] = 1
        
        # Short entry conditions (inverse of long conditions)
        dataframe.loc[
            (
                # MACD bearish crossover
                (dataframe['macd_cross_down'] == 1) &
                
                # Volume confirmation
                (dataframe['volume_ratio'] > self.volume_factor.value) &
                
                # Price momentum negative
                (dataframe['price_momentum'] < -0.01) &
                
                # RSI not oversold
                (dataframe['rsi'] > self.rsi_oversold.value) &
                (dataframe['rsi'] < self.rsi_overbought.value) &
                
                # Trend confirmation (price below EMA)
                (dataframe['close'] < dataframe['ema_20']) &
                
                # ADX shows trend strength
                (dataframe['adx'] > 25) &
                
                # Stochastic not oversold
                (dataframe['stoch_k'] > 20) &
                (dataframe['stoch_d'] > 20) &
                
                # Williams %R not oversold
                (dataframe['williams_r'] < -80) &
                
                # CCI not oversold
                (dataframe['cci'] > -100) &
                
                # Price not at lower Bollinger Band
                (dataframe['bb_percent'] > 0.2)
            ),
            'enter_short'] = 1
        
        return dataframe
    
    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the exit signal for the given dataframe
        :param dataframe: DataFrame populated with indicators
        :param metadata: Additional information, like the currently traded pair
        :return: DataFrame with exit columns populated
        """
        
        # Long exit conditions
        dataframe.loc[
            (
                # MACD bearish crossover
                (dataframe['macd_cross_down'] == 1) |
                
                # RSI overbought
                (dataframe['rsi'] > self.rsi_overbought.value) |
                
                # Price at upper Bollinger Band
                (dataframe['bb_percent'] > 0.9) |
                
                # Stochastic overbought
                (dataframe['stoch_k'] > 80) |
                (dataframe['stoch_d'] > 80) |
                
                # Williams %R overbought
                (dataframe['williams_r'] < -20) |
                
                # CCI overbought
                (dataframe['cci'] > 100) |
                
                # Price momentum turning negative
                (dataframe['price_momentum'] < -0.02)
            ),
            'exit_long'] = 1
        
        # Short exit conditions (inverse of long exits)
        dataframe.loc[
            (
                # MACD bullish crossover
                (dataframe['macd_cross'] == 1) |
                
                # RSI oversold
                (dataframe['rsi'] < self.rsi_oversold.value) |
                
                # Price at lower Bollinger Band
                (dataframe['bb_percent'] < 0.1) |
                
                # Stochastic oversold
                (dataframe['stoch_k'] < 20) |
                (dataframe['stoch_d'] < 20) |
                
                # Williams %R oversold
                (dataframe['williams_r'] > -80) |
                
                # CCI oversold
                (dataframe['cci'] < -100) |
                
                # Price momentum turning positive
                (dataframe['price_momentum'] > 0.02)
            ),
            'exit_short'] = 1
        
        return dataframe
    
    def leverage(self, pair: str, current_time: datetime, current_rate: float,
                 proposed_leverage: float, max_leverage: float, entry_tag: Optional[str], 
                 side: str, **kwargs) -> float:
        """
        Calculate dynamic leverage based on market volatility and conditions.
        
        Args:
            pair: Trading pair
            current_time: Current time
            current_rate: Current price
            proposed_leverage: Proposed leverage from config
            max_leverage: Maximum allowed leverage
            entry_tag: Entry tag (if any)
            side: 'long' or 'short'
        
        Returns:
            Calculated leverage value
        """
        # Get recent price data for volatility calculation
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        
        if len(dataframe) < 20:
            return min(proposed_leverage, self.base_leverage.value)
        
        # Calculate recent volatility (standard deviation of returns)
        recent_returns = dataframe['close'].pct_change().dropna()
        volatility = recent_returns.std()
        
        # Calculate ATR for additional volatility measure
        atr = dataframe['high'].rolling(14).max() - dataframe['low'].rolling(14).min()
        atr_volatility = atr.iloc[-1] / dataframe['close'].iloc[-1] if len(atr) > 0 else 0.02
        
        # Combine volatility measures
        combined_volatility = max(volatility, atr_volatility)
        
        # Adjust leverage based on volatility
        if combined_volatility > self.volatility_threshold.value:
            # High volatility - reduce leverage
            leverage_multiplier = 0.5
        elif combined_volatility > self.volatility_threshold.value * 0.7:
            # Medium volatility - moderate leverage
            leverage_multiplier = 0.75
        else:
            # Low volatility - use full leverage
            leverage_multiplier = 1.0
        
        # Calculate final leverage
        calculated_leverage = self.base_leverage.value * leverage_multiplier
        
        # Ensure leverage is within bounds
        final_leverage = max(1, min(calculated_leverage, self.max_leverage.value, max_leverage))
        
        return final_leverage
    
    def custom_stoploss(self, pair: str, trade: 'Trade', current_time: datetime,
                        current_rate: float, current_profit: float, **kwargs) -> float:
        """
        Custom stoploss logic for both long and short positions.
        Returns the new distance relative to current_rate (as ratio).
        """
        
        # Let the default stoploss run for the first 10 minutes
        if (current_time - trade.open_date_utc).total_seconds() < 600:
            return self.stoploss
        
        # Different logic for long vs short positions
        if trade.is_short:
            # Short position logic
            if current_profit > 0.02:  # 2% profit on short
                return 0.02  # 2% trailing stop (positive for shorts)
            elif current_profit > 0.01:  # 1% profit on short
                return 0.015  # 1.5% trailing stop
            else:
                return self.stoploss  # Default stoploss for shorts
        else:
            # Long position logic
            if current_profit > 0.02:  # 2% profit on long
                return -0.02  # 2% trailing stop (negative for longs)
            elif current_profit > 0.01:  # 1% profit on long
                return -0.015  # 1.5% trailing stop
            else:
                return self.stoploss  # Default stoploss for longs
