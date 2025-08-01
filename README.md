# RSI-VWAP Trading Strategy

A comprehensive trading strategy that combines **RSI (Relative Strength Index)** and **VWAP (Volume Weighted Average Price)** indicators to generate trading signals for financial markets.

## 📊 Strategy Overview

This strategy uses two powerful technical indicators:

1. **VWAP (Volume Weighted Average Price)**: Measures the average price weighted by volume
2. **RSI (Relative Strength Index)**: Measures momentum and identifies overbought/oversold conditions

The strategy combines these signals to create more robust trading decisions with built-in risk management.

## 🔧 Features

- **Combined Signal Generation**: Merges VWAP and RSI signals for enhanced accuracy
- **Risk Management**: Built-in stop-loss (2%) and take-profit (4%) mechanisms
- **Backtesting Framework**: Complete backtesting using the `backtesting` library
- **Parameter Optimization**: Automated parameter optimization for best performance
- **Multiple Signal Strengths**: Weak and strong buy/sell signals for flexible trading
- **Trading Hours Filter**: Focuses on active market hours (13:30-20:00)

## 📈 Signal Logic

### VWAP Signals
- **Signal 2 (Strong Bullish)**: Price consistently above VWAP for the last 10 candles
- **Signal 1 (Strong Bearish)**: Price consistently below VWAP for the last 10 candles
- **Signal 3 (Neutral)**: Mixed price action around VWAP
- **Signal 0 (No Clear Trend)**: No consistent pattern

### RSI Signals
- **Signal 2 (Strong Buy)**: RSI crosses above oversold level (30)
- **Signal -2 (Strong Sell)**: RSI crosses below overbought level (70)
- **Signal 1 (Weak Buy)**: RSI crosses above 50 (momentum shift)
- **Signal -1 (Weak Sell)**: RSI crosses below 50 (momentum shift)

### Combined Signals
- **Strong Buy (2)**: VWAP bullish + RSI buy signals
- **Weak Buy (1)**: Moderate bullish conditions
- **Strong Sell (-2)**: VWAP bearish + RSI sell signals
- **Weak Sell (-1)**: Moderate bearish conditions
- **Hold (0)**: No clear trading signal

## 🚀 Installation

1. **Clone or download the files**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 📁 Files Structure

```
├── trading_strategy.py     # Main strategy implementation
├── example_usage.py        # Example usage with sample data
├── requirements.txt        # Python dependencies
└── README.md              # This documentation
```

## 💻 Usage

### With Your Data

1. **Update the file path** in `trading_strategy.py`:
   ```python
   base = r"YOUR_PATH_HERE"
   dbn_path = os.path.join(base, "your-data-file.dbn")
   ```

2. **Run the complete analysis**:
   ```bash
   python trading_strategy.py
   ```

### With Sample Data

Run the example to see how the strategy works:
```bash
python example_usage.py
```

## 📊 Strategy Parameters

### Default Parameters
- **RSI Length**: 20 periods
- **VWAP Length**: 20 periods
- **RSI Oversold**: 30
- **RSI Overbought**: 70
- **Backcandles**: 10 (for VWAP signal)
- **Stop Loss**: 2%
- **Take Profit**: 4%

### Customization
You can modify these parameters in the `RSI_VWAP_Strategy` class:

```python
class RSI_VWAP_Strategy(Strategy):
    # Modify these parameters
    rsi_length = 20
    vwap_length = 20
    rsi_oversold = 30
    rsi_overbought = 70
    stop_loss_pct = 0.02
    take_profit_pct = 0.04
```

## 🔍 Strategy Logic

### Entry Conditions
- **Long Entry**: Combined signal ≥ 1 (buy signal)
- **Short Entry**: Combined signal ≤ -1 (sell signal)

### Exit Conditions
- **Signal-based Exit**: Opposite signal triggers exit
- **Risk Management**: Stop-loss or take-profit levels reached

### Risk Management
- **Stop Loss**: 2% from entry price
- **Take Profit**: 4% from entry price
- **Position Sizing**: Fixed size (customizable)

## 📈 Backtesting Results

The strategy provides comprehensive backtesting metrics:

- **Total Return**: Overall strategy performance
- **Sharpe Ratio**: Risk-adjusted returns
- **Maximum Drawdown**: Largest peak-to-trough decline
- **Win Rate**: Percentage of profitable trades
- **Number of Trades**: Total trading activity
- **Average Trade Duration**: Time in market per trade

## 🎯 Optimization

Enable parameter optimization by uncommenting the optimization section:

```python
# Uncomment this line to run optimization
optimization_results = optimize_strategy()
```

The optimization will test different combinations of:
- RSI Length (14-24)
- VWAP Length (15-24)
- RSI Oversold/Overbought levels
- Stop-loss and take-profit percentages

## 📊 Visualization

The strategy generates an interactive HTML plot (`strategy_results.html`) showing:
- Price action and indicators
- Entry/exit points
- Portfolio equity curve
- Performance metrics

## ⚠️ Important Notes

1. **Data Requirements**: Strategy designed for 1-minute OHLCV data
2. **Trading Hours**: Filters for market hours (13:30-20:00)
3. **Commission**: Default 0.2% commission included in backtesting
4. **Risk Warning**: Past performance doesn't guarantee future results

## 🔧 Advanced Usage

### Custom Signal Generation
You can modify the signal generation functions:

```python
def generate_custom_signals(df):
    # Your custom logic here
    return df
```

### Different Assets
The strategy works with any OHLCV data. Update the data loading function for different sources:

```python
def load_custom_data():
    # Load your data here
    return df
```

## 📚 Dependencies

- `pandas`: Data manipulation
- `numpy`: Numerical computations
- `pandas-ta`: Technical analysis indicators
- `databento`: Market data access
- `backtesting`: Strategy backtesting framework
- `matplotlib/plotly/bokeh`: Visualization

## 🤝 Contributing

Feel free to modify and improve the strategy:
1. Test different indicator combinations
2. Add new risk management rules
3. Implement different signal weighting schemes
4. Add more sophisticated entry/exit logic

## 📄 License

This code is provided for educational and research purposes. Use at your own risk in live trading.

---

**Disclaimer**: This strategy is for educational purposes only. Always perform thorough testing and risk management before using any trading strategy with real money.
