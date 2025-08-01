import os
import pandas as pd
import numpy as np
import pandas_ta as ta
from databento import DBNStore
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import matplotlib.pyplot as plt

# DATA CLEANING
base = r"C:\Users\Nagy Róbert\Documents"
dbn_path = os.path.join(base, "xnas-itch-20180501-20250728.ohlcv-1m.dbn")
store = DBNStore.from_file(path=dbn_path)
df = store.to_df()
df.index = pd.to_datetime(df.index, unit='s')
df.index.name = 'Gmt time'
df = df.drop(columns=['rtype', 'publisher_id', 'instrument_id', 'symbol'])
if df.index.tz is not None:
    df.index = df.index.tz_convert(None)
df = df.between_time('13:30', '20:00')
df = df.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
})
print("Data shape:", df.shape)
print(df.head())

# TECHNICAL INDICATORS IMPLEMENTATION
# VWAP for period of 20
df['vwap'] = ta.vwap(
    high=df['High'],
    low=df['Low'],
    close=df['Close'],
    volume=df['Volume'],
    length=20
)

# RSI for period of 20
df['rsi'] = ta.rsi(
    close=df['Close'],
    length=20
)

print(df[['vwap', 'rsi']].tail())

# VWAP SIGNAL GENERATION
vwap_signal = np.zeros(len(df), dtype=int)
backcandles = 10
for row in range(backcandles, len(df)):
    upt = True
    dnt = True
    for i in range(row-backcandles, row+1):
        if df['High'].iat[i] >= df['vwap'].iat[i]:
            dnt = False
        if df['Low'].iat[i] <= df['vwap'].iat[i]:
            upt = False
    if upt and dnt:
        vwap_signal[row] = 3
    elif upt:
        vwap_signal[row] = 2
    elif dnt:
        vwap_signal[row] = 1

df['VWAPSignal'] = vwap_signal

# RSI SIGNAL GENERATION
def generate_rsi_signals(rsi_series, oversold=30, overbought=70):
    """
    Generate RSI signals:
    1 = Oversold (buy signal)
    2 = Neutral
    3 = Overbought (sell signal)
    """
    rsi_signal = np.zeros(len(rsi_series), dtype=int)
    
    for i in range(len(rsi_series)):
        if pd.isna(rsi_series.iloc[i]):
            rsi_signal[i] = 2  # Neutral for NaN values
        elif rsi_series.iloc[i] <= oversold:
            rsi_signal[i] = 1  # Oversold - buy signal
        elif rsi_series.iloc[i] >= overbought:
            rsi_signal[i] = 3  # Overbought - sell signal
        else:
            rsi_signal[i] = 2  # Neutral
    
    return rsi_signal

df['RSISignal'] = generate_rsi_signals(df['rsi'])

# COMBINED STRATEGY SIGNALS
def generate_combined_signals(vwap_signal, rsi_signal):
    """
    Combined strategy logic:
    - Buy: RSI oversold (1) AND price above VWAP (2) 
    - Sell: RSI overbought (3) AND price below VWAP (1)
    - Hold: All other combinations
    
    Returns:
    1 = Buy
    0 = Hold
    -1 = Sell
    """
    combined_signal = np.zeros(len(vwap_signal), dtype=int)
    
    for i in range(len(vwap_signal)):
        # Strong buy: RSI oversold and price consistently above VWAP
        if rsi_signal[i] == 1 and vwap_signal[i] == 2:
            combined_signal[i] = 1
        # Strong sell: RSI overbought and price consistently below VWAP
        elif rsi_signal[i] == 3 and vwap_signal[i] == 1:
            combined_signal[i] = -1
        # Additional buy condition: RSI oversold and price touching VWAP (potential reversal)
        elif rsi_signal[i] == 1 and vwap_signal[i] == 3:
            combined_signal[i] = 1
        else:
            combined_signal[i] = 0
    
    return combined_signal

df['CombinedSignal'] = generate_combined_signals(df['VWAPSignal'], df['RSISignal'])

# BACKTESTING STRATEGY CLASS
class RSI_VWAP_Strategy(Strategy):
    # Strategy parameters
    rsi_oversold = 30
    rsi_overbought = 70
    stop_loss_pct = 0.02  # 2% stop loss
    take_profit_pct = 0.04  # 4% take profit
    
    def init(self):
        # Calculate indicators
        self.vwap = self.I(ta.vwap, 
                          self.data.High, 
                          self.data.Low, 
                          self.data.Close, 
                          self.data.Volume, 
                          length=20)
        
        self.rsi = self.I(ta.rsi, self.data.Close, length=20)
        
        # Generate signals
        self.vwap_signal = self.I(self.calculate_vwap_signal)
        self.rsi_signal = self.I(self.calculate_rsi_signal)
        self.combined_signal = self.I(self.calculate_combined_signal)
    
    def calculate_vwap_signal(self):
        vwap_signal = np.zeros(len(self.data), dtype=int)
        backcandles = 10
        
        for row in range(backcandles, len(self.data)):
            upt = True
            dnt = True
            for i in range(row-backcandles, row+1):
                if self.data.High[i] >= self.vwap[i]:
                    dnt = False
                if self.data.Low[i] <= self.vwap[i]:
                    upt = False
            if upt and dnt:
                vwap_signal[row] = 3
            elif upt:
                vwap_signal[row] = 2
            elif dnt:
                vwap_signal[row] = 1
        
        return vwap_signal
    
    def calculate_rsi_signal(self):
        rsi_signal = np.zeros(len(self.data), dtype=int)
        
        for i in range(len(self.data)):
            if pd.isna(self.rsi[i]):
                rsi_signal[i] = 2
            elif self.rsi[i] <= self.rsi_oversold:
                rsi_signal[i] = 1
            elif self.rsi[i] >= self.rsi_overbought:
                rsi_signal[i] = 3
            else:
                rsi_signal[i] = 2
        
        return rsi_signal
    
    def calculate_combined_signal(self):
        combined_signal = np.zeros(len(self.data), dtype=int)
        
        for i in range(len(self.data)):
            if self.rsi_signal[i] == 1 and self.vwap_signal[i] == 2:
                combined_signal[i] = 1
            elif self.rsi_signal[i] == 3 and self.vwap_signal[i] == 1:
                combined_signal[i] = -1
            elif self.rsi_signal[i] == 1 and self.vwap_signal[i] == 3:
                combined_signal[i] = 1
            else:
                combined_signal[i] = 0
        
        return combined_signal
    
    def next(self):
        # Get current signal
        current_signal = self.combined_signal[-1]
        
        # Entry logic
        if current_signal == 1 and not self.position:
            # Buy signal
            self.buy(size=0.95)  # Use 95% of available cash
            
        elif current_signal == -1 and not self.position:
            # Sell signal (short)
            self.sell(size=0.95)
        
        # Exit logic with stop loss and take profit
        if self.position:
            entry_price = self.position.entry_price
            current_price = self.data.Close[-1]
            
            if self.position.is_long:
                # Long position exits
                stop_loss_price = entry_price * (1 - self.stop_loss_pct)
                take_profit_price = entry_price * (1 + self.take_profit_pct)
                
                if current_price <= stop_loss_price or current_price >= take_profit_price:
                    self.position.close()
                elif current_signal == -1:  # Opposite signal
                    self.position.close()
                    
            elif self.position.is_short:
                # Short position exits
                stop_loss_price = entry_price * (1 + self.stop_loss_pct)
                take_profit_price = entry_price * (1 - self.take_profit_pct)
                
                if current_price >= stop_loss_price or current_price <= take_profit_price:
                    self.position.close()
                elif current_signal == 1:  # Opposite signal
                    self.position.close()

# PREPARE DATA FOR BACKTESTING
# Remove NaN values and ensure we have all required columns
df_clean = df.dropna().copy()

# Ensure proper column names for backtesting library
backtest_df = df_clean[['Open', 'High', 'Low', 'Close', 'Volume']].copy()

print(f"\nBacktesting data shape: {backtest_df.shape}")
print(f"Date range: {backtest_df.index.min()} to {backtest_df.index.max()}")

# RUN BACKTEST
bt = Backtest(backtest_df, RSI_VWAP_Strategy, cash=100000, commission=0.001)
stats = bt.run()

# DISPLAY RESULTS
print("\n" + "="*50)
print("BACKTEST RESULTS")
print("="*50)
print(stats)

# ANALYZE SIGNAL DISTRIBUTION
print("\n" + "="*50)
print("SIGNAL ANALYSIS")
print("="*50)

signal_counts = pd.Series(df_clean['CombinedSignal']).value_counts().sort_index()
print("Combined Signal Distribution:")
print(f"Sell signals (-1): {signal_counts.get(-1, 0)}")
print(f"Hold signals (0): {signal_counts.get(0, 0)}")
print(f"Buy signals (1): {signal_counts.get(1, 0)}")

vwap_counts = pd.Series(df_clean['VWAPSignal']).value_counts().sort_index()
print(f"\nVWAP Signal Distribution:")
print(f"Below VWAP (1): {vwap_counts.get(1, 0)}")
print(f"Above VWAP (2): {vwap_counts.get(2, 0)}")
print(f"Touching VWAP (3): {vwap_counts.get(3, 0)}")

rsi_counts = pd.Series(df_clean['RSISignal']).value_counts().sort_index()
print(f"\nRSI Signal Distribution:")
print(f"Oversold (1): {rsi_counts.get(1, 0)}")
print(f"Neutral (2): {rsi_counts.get(2, 0)}")
print(f"Overbought (3): {rsi_counts.get(3, 0)}")

# PLOT RESULTS
bt.plot(filename='backtest_results.html')
print(f"\nBacktest plot saved as 'backtest_results.html'")

# STRATEGY PERFORMANCE METRICS
print("\n" + "="*50)
print("KEY PERFORMANCE METRICS")
print("="*50)
print(f"Total Return: {stats['Return [%]']:.2f}%")
print(f"Buy & Hold Return: {stats['Buy & Hold Return [%]']:.2f}%")
print(f"Max Drawdown: {stats['Max. Drawdown [%]']:.2f}%")
print(f"Sharpe Ratio: {stats['Sharpe Ratio']:.2f}")
print(f"Number of Trades: {stats['# Trades']}")
print(f"Win Rate: {stats['Win Rate [%]']:.2f}%")
print(f"Profit Factor: {stats['Profit Factor']:.2f}")