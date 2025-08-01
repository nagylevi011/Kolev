import pandas as pd
import numpy as np
import pandas_ta as ta
from backtesting import Backtest, Strategy
import matplotlib.pyplot as plt

# SAMPLE DATA GENERATION (for testing without the actual DBN file)
def generate_sample_data():
    """Generate sample OHLCV data for testing"""
    np.random.seed(42)
    dates = pd.date_range('2023-01-01 13:30:00', '2023-12-31 20:00:00', freq='1min')
    dates = dates[dates.time >= pd.Timestamp('13:30:00').time()]
    dates = dates[dates.time <= pd.Timestamp('20:00:00').time()]
    
    n = len(dates)
    
    # Generate realistic price data
    returns = np.random.normal(0.0001, 0.02, n)
    prices = 100 * np.exp(np.cumsum(returns))
    
    # Create OHLCV data
    df = pd.DataFrame(index=dates)
    df['Close'] = prices
    df['Open'] = df['Close'].shift(1)
    df['High'] = np.maximum(df['Open'], df['Close']) * (1 + np.abs(np.random.normal(0, 0.005, n)))
    df['Low'] = np.minimum(df['Open'], df['Close']) * (1 - np.abs(np.random.normal(0, 0.005, n)))
    df['Volume'] = np.random.lognormal(10, 1, n)
    
    return df.dropna()

# TECHNICAL INDICATORS AND SIGNALS
def add_indicators(df):
    """Add VWAP, RSI and generate signals"""
    # VWAP calculation
    df['vwap'] = ta.vwap(
        high=df['High'],
        low=df['Low'], 
        close=df['Close'],
        volume=df['Volume'],
        length=20
    )
    
    # RSI calculation
    df['rsi'] = ta.rsi(close=df['Close'], length=20)
    
    # VWAP Signal Generation
    vwap_signal = np.zeros(len(df), dtype=int)
    backcandles = 10
    
    for row in range(backcandles, len(df)):
        upt = True  # Price consistently above VWAP
        dnt = True  # Price consistently below VWAP
        
        for i in range(row-backcandles, row+1):
            if df['High'].iloc[i] >= df['vwap'].iloc[i]:
                dnt = False
            if df['Low'].iloc[i] <= df['vwap'].iloc[i]:
                upt = False
        
        if upt and dnt:
            vwap_signal[row] = 3  # Price touching VWAP
        elif upt:
            vwap_signal[row] = 2  # Price above VWAP
        elif dnt:
            vwap_signal[row] = 1  # Price below VWAP
    
    df['VWAPSignal'] = vwap_signal
    
    # RSI Signal Generation
    rsi_signal = np.zeros(len(df), dtype=int)
    for i in range(len(df)):
        if pd.isna(df['rsi'].iloc[i]):
            rsi_signal[i] = 2  # Neutral
        elif df['rsi'].iloc[i] <= 30:
            rsi_signal[i] = 1  # Oversold
        elif df['rsi'].iloc[i] >= 70:
            rsi_signal[i] = 3  # Overbought
        else:
            rsi_signal[i] = 2  # Neutral
    
    df['RSISignal'] = rsi_signal
    
    # Combined Signal Generation
    combined_signal = np.zeros(len(df), dtype=int)
    for i in range(len(df)):
        # Buy conditions
        if (df['RSISignal'].iloc[i] == 1 and df['VWAPSignal'].iloc[i] == 2) or \
           (df['RSISignal'].iloc[i] == 1 and df['VWAPSignal'].iloc[i] == 3):
            combined_signal[i] = 1
        # Sell conditions  
        elif df['RSISignal'].iloc[i] == 3 and df['VWAPSignal'].iloc[i] == 1:
            combined_signal[i] = -1
        else:
            combined_signal[i] = 0
    
    df['CombinedSignal'] = combined_signal
    
    return df

# STRATEGY CLASS
class RSI_VWAP_Strategy(Strategy):
    # Parameters
    rsi_oversold = 30
    rsi_overbought = 70
    stop_loss_pct = 0.02
    take_profit_pct = 0.04
    
    def init(self):
        # Calculate indicators
        self.vwap = self.I(ta.vwap, 
                          self.data.High, 
                          self.data.Low, 
                          self.data.Close, 
                          self.data.Volume, 
                          length=20)
        
        self.rsi = self.I(ta.rsi, self.data.Close, length=20)
        
        # Calculate signals
        self.vwap_signal = self.I(self.calc_vwap_signal)
        self.rsi_signal = self.I(self.calc_rsi_signal)
        self.combined_signal = self.I(self.calc_combined_signal)
    
    def calc_vwap_signal(self):
        signal = np.zeros(len(self.data))
        backcandles = 10
        
        for i in range(backcandles, len(self.data)):
            above_count = sum(1 for j in range(i-backcandles, i+1) 
                            if self.data.Low[j] > self.vwap[j])
            below_count = sum(1 for j in range(i-backcandles, i+1) 
                            if self.data.High[j] < self.vwap[j])
            
            if above_count == backcandles + 1:
                signal[i] = 2  # Above VWAP
            elif below_count == backcandles + 1:
                signal[i] = 1  # Below VWAP
            else:
                signal[i] = 3  # Around VWAP
        
        return signal
    
    def calc_rsi_signal(self):
        signal = np.zeros(len(self.data))
        for i in range(len(self.data)):
            if self.rsi[i] <= self.rsi_oversold:
                signal[i] = 1
            elif self.rsi[i] >= self.rsi_overbought:
                signal[i] = 3
            else:
                signal[i] = 2
        return signal
    
    def calc_combined_signal(self):
        signal = np.zeros(len(self.data))
        for i in range(len(self.data)):
            if (self.rsi_signal[i] == 1 and self.vwap_signal[i] == 2) or \
               (self.rsi_signal[i] == 1 and self.vwap_signal[i] == 3):
                signal[i] = 1  # Buy
            elif self.rsi_signal[i] == 3 and self.vwap_signal[i] == 1:
                signal[i] = -1  # Sell
            else:
                signal[i] = 0  # Hold
        return signal
    
    def next(self):
        current_signal = self.combined_signal[-1]
        
        # Entry logic
        if current_signal == 1 and not self.position:
            self.buy(size=0.9)
        elif current_signal == -1 and not self.position:
            self.sell(size=0.9)
        
        # Exit logic
        if self.position:
            entry_price = self.position.entry_price
            current_price = self.data.Close[-1]
            
            if self.position.is_long:
                stop_loss = entry_price * (1 - self.stop_loss_pct)
                take_profit = entry_price * (1 + self.take_profit_pct)
                
                if current_price <= stop_loss or current_price >= take_profit:
                    self.position.close()
                elif current_signal == -1:
                    self.position.close()
                    
            else:  # Short position
                stop_loss = entry_price * (1 + self.stop_loss_pct)
                take_profit = entry_price * (1 - self.take_profit_pct)
                
                if current_price >= stop_loss or current_price <= take_profit:
                    self.position.close()
                elif current_signal == 1:
                    self.position.close()

# MAIN EXECUTION
if __name__ == "__main__":
    print("RSI-VWAP Trading Strategy Backtest")
    print("=" * 40)
    
    # Generate or load data
    print("Generating sample data...")
    df = generate_sample_data()
    
    # Add indicators and signals
    print("Calculating indicators and signals...")
    df = add_indicators(df)
    
    # Prepare data for backtesting
    backtest_df = df[['Open', 'High', 'Low', 'Close', 'Volume']].dropna()
    
    print(f"Data period: {backtest_df.index[0]} to {backtest_df.index[-1]}")
    print(f"Total bars: {len(backtest_df)}")
    
    # Run backtest
    print("\nRunning backtest...")
    bt = Backtest(backtest_df, RSI_VWAP_Strategy, cash=100000, commission=0.001)
    stats = bt.run()
    
    # Display results
    print("\nBacktest Results:")
    print("-" * 20)
    print(f"Total Return: {stats['Return [%]']:.2f}%")
    print(f"Buy & Hold Return: {stats['Buy & Hold Return [%]']:.2f}%")
    print(f"Max Drawdown: {stats['Max. Drawdown [%]']:.2f}%")
    print(f"Sharpe Ratio: {stats['Sharpe Ratio']:.2f}")
    print(f"Number of Trades: {stats['# Trades']}")
    print(f"Win Rate: {stats['Win Rate [%]']:.2f}%")
    
    # Signal analysis
    signal_counts = df['CombinedSignal'].value_counts().sort_index()
    print(f"\nSignal Distribution:")
    print(f"Sell signals: {signal_counts.get(-1, 0)}")
    print(f"Hold signals: {signal_counts.get(0, 0)}")
    print(f"Buy signals: {signal_counts.get(1, 0)}")
    
    # Generate plot
    try:
        bt.plot(filename='strategy_backtest.html')
        print("\nBacktest chart saved as 'strategy_backtest.html'")
    except Exception as e:
        print(f"Could not generate plot: {e}")
    
    print("\nFull statistics:")
    print(stats)