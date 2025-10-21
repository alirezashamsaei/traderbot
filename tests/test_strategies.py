"""
Test suite for trading strategies
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock

# Import the strategy to test
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'strategies'))

from MomentumStrategy import MomentumStrategy


class TestMomentumStrategy:
    """Test cases for MomentumStrategy"""
    
    @pytest.fixture
    def strategy(self):
        """Create a strategy instance for testing"""
        return MomentumStrategy()
    
    @pytest.fixture
    def sample_dataframe(self):
        """Create sample OHLCV data for testing"""
        # Generate 100 candles of sample data
        dates = pd.date_range(start='2023-01-01', periods=100, freq='15min')
        
        # Create realistic price data with some trend
        base_price = 100
        price_changes = np.random.normal(0, 0.02, 100)  # 2% volatility
        prices = [base_price]
        for change in price_changes:
            prices.append(prices[-1] * (1 + change))
        
        df = pd.DataFrame({
            'date': dates,
            'open': prices[:-1],
            'high': [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices[:-1]],
            'low': [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices[:-1]],
            'close': prices[1:],
            'volume': np.random.uniform(1000, 10000, 100)
        })
        
        # Ensure high >= low and high/low contain open/close
        df['high'] = df[['open', 'close', 'high']].max(axis=1)
        df['low'] = df[['open', 'close', 'low']].min(axis=1)
        
        return df
    
    def test_strategy_initialization(self, strategy):
        """Test that strategy initializes correctly"""
        assert strategy.timeframe == '15m'
        assert strategy.can_short is True  # Updated for futures trading
        assert strategy.minimal_roi is not None
        assert strategy.stoploss == -0.10
        assert strategy.trailing_stop is True
    
    def test_populate_indicators(self, strategy, sample_dataframe):
        """Test that indicators are calculated correctly"""
        df = strategy.populate_indicators(sample_dataframe, {})
        
        # Check that required indicators are present
        required_indicators = [
            'macd', 'macdsignal', 'macdhist',
            'rsi', 'bb_lowerband', 'bb_middleband', 'bb_upperband',
            'volume_mean', 'volume_ratio', 'price_change', 'price_momentum',
            'ema_20', 'ema_50', 'adx', 'stoch_k', 'stoch_d',
            'williams_r', 'cci', 'macd_cross', 'macd_cross_down'
        ]
        
        for indicator in required_indicators:
            assert indicator in df.columns, f"Missing indicator: {indicator}"
        
        # Check that indicators have reasonable values
        assert df['rsi'].dropna().between(0, 100).all(), "RSI should be between 0 and 100"
        assert df['macd'].dropna().notna().all(), "MACD should not contain NaN values"
        assert df['volume_ratio'].dropna().gt(0).all(), "Volume ratio should be positive"
    
    def test_entry_signals(self, strategy, sample_dataframe):
        """Test entry signal generation for both long and short"""
        df = strategy.populate_indicators(sample_dataframe, {})
        df = strategy.populate_entry_trend(df, {})
        
        # Check that both enter_long and enter_short columns exist
        assert 'enter_long' in df.columns, "Missing enter_long column"
        assert 'enter_short' in df.columns, "Missing enter_short column"
        
        # Check that signals are binary (0 or 1)
        if df['enter_long'].dropna().any():
            assert df['enter_long'].dropna().isin([0, 1]).all(), "Long entry signals should be binary"
        
        if df['enter_short'].dropna().any():
            assert df['enter_short'].dropna().isin([0, 1]).all(), "Short entry signals should be binary"
    
    def test_exit_signals(self, strategy, sample_dataframe):
        """Test exit signal generation for both long and short"""
        df = strategy.populate_indicators(sample_dataframe, {})
        df = strategy.populate_exit_trend(df, {})
        
        # Check that both exit_long and exit_short columns exist
        assert 'exit_long' in df.columns, "Missing exit_long column"
        assert 'exit_short' in df.columns, "Missing exit_short column"
        
        # Check that signals are binary (0 or 1)
        if df['exit_long'].dropna().any():
            assert df['exit_long'].dropna().isin([0, 1]).all(), "Long exit signals should be binary"
        
        if df['exit_short'].dropna().any():
            assert df['exit_short'].dropna().isin([0, 1]).all(), "Short exit signals should be binary"
    
    def test_strategy_parameters(self, strategy):
        """Test that strategy parameters are within valid ranges"""
        # Test MACD parameters
        assert 8 <= strategy.macd_fast.value <= 16
        assert 20 <= strategy.macd_slow.value <= 30
        assert 7 <= strategy.macd_signal.value <= 12
        
        # Test volume factor
        assert 1.0 <= strategy.volume_factor.value <= 3.0
        
        # Test RSI parameters
        assert 10 <= strategy.rsi_period.value <= 20
        assert 20 <= strategy.rsi_oversold.value <= 40
        assert 60 <= strategy.rsi_overbought.value <= 80
    
    def test_custom_stoploss(self, strategy):
        """Test custom stoploss logic for both long and short positions"""
        from freqtrade.persistence import Trade
        from datetime import datetime
        
        # Mock trade object for long position
        trade_long = Mock()
        trade_long.is_short = False
        trade_long.open_date_utc = datetime.now() - timedelta(minutes=15)  # After 10 minutes
        
        # Test long position stoploss
        current_time = datetime.now()
        current_rate = 100.0
        current_profit = 0.03  # 3% profit
        
        stoploss_long = strategy.custom_stoploss(
            pair="BTC/USDT",
            trade=trade_long,
            current_time=current_time,
            current_rate=current_rate,
            current_profit=current_profit
        )
        
        assert stoploss_long == -0.02, "Long position should use -2% trailing stop for 3% profit"
        
        # Mock trade object for short position
        trade_short = Mock()
        trade_short.is_short = True
        trade_short.open_date_utc = datetime.now() - timedelta(minutes=15)  # After 10 minutes
        
        # Test short position stoploss
        stoploss_short = strategy.custom_stoploss(
            pair="BTC/USDT",
            trade=trade_short,
            current_time=current_time,
            current_rate=current_rate,
            current_profit=current_profit
        )
        
        assert stoploss_short == 0.02, "Short position should use +2% trailing stop for 3% profit"
    
    def test_dataframe_consistency(self, strategy, sample_dataframe):
        """Test that the dataframe maintains consistency after processing"""
        original_length = len(sample_dataframe)
        
        df = strategy.populate_indicators(sample_dataframe, {})
        df = strategy.populate_entry_trend(df, {})
        df = strategy.populate_exit_trend(df, {})
        
        # Check that dataframe length is preserved
        assert len(df) == original_length, "Dataframe length should be preserved"
        
        # Check that original columns are preserved
        original_columns = set(sample_dataframe.columns)
        processed_columns = set(df.columns)
        
        assert original_columns.issubset(processed_columns), "Original columns should be preserved"
    
    def test_indicators_with_insufficient_data(self, strategy):
        """Test strategy behavior with insufficient data"""
        # Create dataframe with only 5 candles (less than startup_candle_count)
        dates = pd.date_range(start='2023-01-01', periods=5, freq='15min')
        df = pd.DataFrame({
            'date': dates,
            'open': [100, 101, 102, 103, 104],
            'high': [101, 102, 103, 104, 105],
            'low': [99, 100, 101, 102, 103],
            'close': [101, 102, 103, 104, 105],
            'volume': [1000, 1100, 1200, 1300, 1400]
        })
        
        # Should not raise an error, but indicators may have NaN values
        df_processed = strategy.populate_indicators(df, {})
        
        # Check that the dataframe is returned (even with NaN indicators)
        assert len(df_processed) == len(df)
        assert 'macd' in df_processed.columns
    
    def test_leverage_calculation(self, strategy, sample_dataframe):
        """Test dynamic leverage calculation"""
        # Mock the data provider
        strategy.dp = Mock()
        strategy.dp.get_analyzed_dataframe.return_value = (sample_dataframe, None)
        
        # Test leverage calculation with different volatility levels
        current_time = datetime.now()
        current_rate = 100.0
        
        # Test with normal volatility
        leverage = strategy.leverage(
            pair="BTC/USDT",
            current_time=current_time,
            current_rate=current_rate,
            proposed_leverage=10,
            max_leverage=20,
            entry_tag=None,
            side="long"
        )
        
        # Leverage should be within reasonable bounds
        assert 1 <= leverage <= strategy.max_leverage.value
        assert leverage <= 20  # Should not exceed max_leverage parameter
    
    def test_short_entry_conditions(self, strategy, sample_dataframe):
        """Test that short entry conditions are properly defined"""
        df = strategy.populate_indicators(sample_dataframe, {})
        df = strategy.populate_entry_trend(df, {})
        
        # Check that short entry conditions are inverse of long conditions
        # This is a basic test - in practice, you'd want more sophisticated validation
        if df['enter_short'].dropna().any():
            # Verify that short signals don't occur at the same time as long signals
            conflicting_signals = (df['enter_long'] == 1) & (df['enter_short'] == 1)
            assert not conflicting_signals.any(), "Long and short signals should not conflict"
    
    def test_short_exit_conditions(self, strategy, sample_dataframe):
        """Test that short exit conditions are properly defined"""
        df = strategy.populate_indicators(sample_dataframe, {})
        df = strategy.populate_exit_trend(df, {})
        
        # Check that short exit conditions are inverse of long exit conditions
        if df['exit_short'].dropna().any():
            # Verify that short exits don't occur at the same time as long exits
            conflicting_signals = (df['exit_long'] == 1) & (df['exit_short'] == 1)
            assert not conflicting_signals.any(), "Long and short exits should not conflict"


if __name__ == "__main__":
    # Run tests if script is executed directly
    pytest.main([__file__, "-v"])
