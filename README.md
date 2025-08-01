# RSI-VWAP Trading Strategy

A comprehensive trading strategy that combines RSI (Relative Strength Index) and VWAP (Volume Weighted Average Price) signals for algorithmic trading.

## Overview

This strategy uses two technical indicators to generate trading signals:

1. **RSI (20-period)**: Identifies overbought/oversold conditions
2. **VWAP (20-period)**: Identifies price position relative to volume-weighted average

## Strategy Logic

### Signal Generation

#### VWAP Signals:
- **1 (Below VWAP)**: Price consistently below VWAP for 10 periods
- **2 (Above VWAP)**: Price consistently above VWAP for 10 periods  
- **3 (Touching VWAP)**: Price oscillating around VWAP

#### RSI Signals:
- **1 (Oversold)**: RSI ≤ 30
- **2 (Neutral)**: 30 < RSI < 70
- **3 (Overbought)**: RSI ≥ 70

#### Combined Entry Signals:
- **Buy (1)**: RSI oversold AND (price above VWAP OR touching VWAP)
- **Sell (-1)**: RSI overbought AND price below VWAP
- **Hold (0)**: All other combinations

### Risk Management
- **Stop Loss**: 2% from entry price
- **Take Profit**: 4% from entry price
- **Position Sizing**: 95% of available capital
- **Commission**: 0.1% per trade

## Files

1. **`trading_strategy.py`**: Complete strategy with your actual DBN data
2. **`strategy_example.py`**: Simplified version with sample data for testing
3. **`requirements.txt`**: Required Python packages

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### With Your Data
```python
python trading_strategy.py
```

### With Sample Data (for testing)
```python
python strategy_example.py
```

## Key Features

- **Data Processing**: Handles 8-year, 1-minute timeframe data
- **Market Hours**: Filters data to 13:30-20:00 (trading hours)
- **Technical Indicators**: VWAP and RSI with 20-period lookback
- **Signal Combination**: Sophisticated logic combining both indicators
- **Backtesting**: Complete performance analysis using backtesting library
- **Visualization**: HTML charts showing strategy performance

## Expected Output

The strategy will generate:

1. **Performance Metrics**:
   - Total Return vs Buy & Hold
   - Maximum Drawdown
   - Sharpe Ratio
   - Win Rate
   - Number of Trades

2. **Signal Analysis**:
   - Distribution of buy/sell/hold signals
   - VWAP and RSI signal breakdowns

3. **Visual Charts**:
   - Interactive HTML chart showing trades and indicators
   - Price action with entry/exit points

## Strategy Parameters

You can modify these parameters in the strategy class:

```python
class RSI_VWAP_Strategy(Strategy):
    rsi_oversold = 30        # RSI oversold threshold
    rsi_overbought = 70      # RSI overbought threshold
    stop_loss_pct = 0.02     # Stop loss percentage
    take_profit_pct = 0.04   # Take profit percentage
```

## Data Requirements

- **Format**: DBN (Databento) file format
- **Timeframe**: 1-minute bars
- **Columns**: Open, High, Low, Close, Volume
- **Period**: 8 years of historical data
- **Market Hours**: 13:30-20:00

## Performance Considerations

- The strategy uses vectorized operations where possible
- Signal calculation includes lookback periods for stability
- Memory efficient processing of large datasets
- Optimized for intraday trading patterns

## Customization

### Adding New Indicators
```python
# In the init() method
self.new_indicator = self.I(ta.sma, self.data.Close, length=50)
```

### Modifying Entry Logic
```python
# In the next() method
if custom_condition and not self.position:
    self.buy(size=0.95)
```

### Risk Management Adjustments
```python
# Modify stop loss/take profit levels
stop_loss_pct = 0.015  # 1.5% stop loss
take_profit_pct = 0.06  # 6% take profit
```

## Troubleshooting

1. **Missing Dependencies**: Install all packages from requirements.txt
2. **Data Path Issues**: Update the file path in the script
3. **Memory Issues**: Consider processing data in chunks for very large datasets
4. **No Signals Generated**: Check indicator parameters and thresholds

## Disclaimer

This strategy is for educational and research purposes only. Past performance does not guarantee future results. Always test thoroughly before using with real money and consider transaction costs, slippage, and market conditions.
