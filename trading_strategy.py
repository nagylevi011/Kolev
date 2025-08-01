import os
import pandas as pd
import numpy as np
import pandas_ta as ta
from databento import DBNStore
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import warnings
warnings.filterwarnings('ignore')

# DATA CLEANING
def load_and_clean_data():
    """Load and clean the financial data"""
    base = r"C:\Users\Nagy Róbert\Documents"
    dbn_path = os.path.join(base, "xnas-itch-20180501-20250728.ohlcv-1m.dbn")
    
    store = DBNStore.from_file(path=dbn_path)
    df = store.to_df()
    
    # Convert index to datetime
    df.index = pd.to_datetime(df.index, unit='s')
    df.index.name = 'Gmt time'
    
    # Drop unnecessary columns
    df = df.drop(columns=['rtype', 'publisher_id', 'instrument_id', 'symbol'])
    
    # Remove timezone if present
    if df.index.tz is not None:
        df.index = df.index.tz_convert(None)
    
    # Filter trading hours (13:30 - 20:00)
    df = df.between_time('13:30', '20:00')
    
    # Rename columns to standard format
    df = df.rename(columns={
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'volume': 'Volume'
    })
    
    return df

def calculate_indicators(df, vwap_length=20, rsi_length=20):
    """Calculate VWAP and RSI indicators"""
    # Calculate VWAP
    df['VWAP'] = ta.vwap(
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        volume=df['Volume'],
        length=vwap_length
    )
    
    # Calculate RSI
    df['RSI'] = ta.rsi(
        close=df['Close'],
        length=rsi_length
    )
    
    return df

def generate_vwap_signals(df, backcandles=10):
    """Generate VWAP signals based on price action relative to VWAP"""
    vwap_signal = np.zeros(len(df), dtype=int)
    
    for row in range(backcandles, len(df)):
        upt = True  # Price consistently above VWAP
        dnt = True  # Price consistently below VWAP
        
        for i in range(row-backcandles, row+1):
            if df['High'].iat[i] >= df['VWAP'].iat[i]:
                dnt = False
            if df['Low'].iat[i] <= df['VWAP'].iat[i]:
                upt = False
        
        if upt and dnt:
            vwap_signal[row] = 3  # Neutral/Consolidation
        elif upt:
            vwap_signal[row] = 2  # Strong bullish
        elif dnt:
            vwap_signal[row] = 1  # Strong bearish
        else:
            vwap_signal[row] = 0  # Mixed signals
    
    df['VWAPSignal'] = vwap_signal
    return df

def generate_rsi_signals(df, oversold=30, overbought=70):
    """Generate RSI signals based on overbought/oversold conditions"""
    rsi_signal = np.zeros(len(df), dtype=int)
    
    for i in range(1, len(df)):
        current_rsi = df['RSI'].iat[i]
        prev_rsi = df['RSI'].iat[i-1]
        
        # RSI signals
        if current_rsi < oversold and prev_rsi >= oversold:
            rsi_signal[i] = 2  # Buy signal (oversold bounce)
        elif current_rsi > overbought and prev_rsi <= overbought:
            rsi_signal[i] = -2  # Sell signal (overbought reversal)
        elif current_rsi > 50 and prev_rsi <= 50:
            rsi_signal[i] = 1  # Weak buy signal (momentum shift)
        elif current_rsi < 50 and prev_rsi >= 50:
            rsi_signal[i] = -1  # Weak sell signal (momentum shift)
        else:
            rsi_signal[i] = 0  # No signal
    
    df['RSISignal'] = rsi_signal
    return df

def generate_combined_signals(df):
    """Combine VWAP and RSI signals for trading decisions"""
    combined_signal = np.zeros(len(df), dtype=int)
    
    for i in range(len(df)):
        vwap_sig = df['VWAPSignal'].iat[i]
        rsi_sig = df['RSISignal'].iat[i]
        
        # Strong buy conditions
        if (vwap_sig == 2 and rsi_sig >= 1) or (vwap_sig >= 1 and rsi_sig == 2):
            combined_signal[i] = 2  # Strong buy
        # Weak buy conditions
        elif (vwap_sig == 2 and rsi_sig == 0) or (vwap_sig == 1 and rsi_sig == 1):
            combined_signal[i] = 1  # Weak buy
        # Strong sell conditions
        elif (vwap_sig == 1 and rsi_sig <= -1) or (vwap_sig <= 1 and rsi_sig == -2):
            combined_signal[i] = -2  # Strong sell
        # Weak sell conditions
        elif (vwap_sig == 1 and rsi_sig == 0) or (vwap_sig == 2 and rsi_sig == -1):
            combined_signal[i] = -1  # Weak sell
        else:
            combined_signal[i] = 0  # Hold
    
    df['CombinedSignal'] = combined_signal
    return df

class RSI_VWAP_Strategy(Strategy):
    """
    Combined RSI and VWAP Trading Strategy
    """
    
    # Strategy parameters
    rsi_length = 20
    vwap_length = 20
    rsi_oversold = 30
    rsi_overbought = 70
    backcandles = 10
    
    # Risk management parameters
    stop_loss_pct = 0.02  # 2% stop loss
    take_profit_pct = 0.04  # 4% take profit
    
    def init(self):
        """Initialize strategy indicators"""
        # Calculate indicators
        self.vwap = self.I(ta.vwap, 
                           self.data.High, self.data.Low, 
                           self.data.Close, self.data.Volume, 
                           length=self.vwap_length)
        
        self.rsi = self.I(ta.rsi, self.data.Close, length=self.rsi_length)
        
        # Generate signals
        self.vwap_signal = self.I(self._generate_vwap_signals)
        self.rsi_signal = self.I(self._generate_rsi_signals)
        self.combined_signal = self.I(self._generate_combined_signals)
    
    def _generate_vwap_signals(self):
        """Generate VWAP signals"""
        signals = np.zeros(len(self.data))
        
        for i in range(self.backcandles, len(self.data)):
            upt = True
            dnt = True
            
            for j in range(i-self.backcandles, i+1):
                if self.data.High[j] >= self.vwap[j]:
                    dnt = False
                if self.data.Low[j] <= self.vwap[j]:
                    upt = False
            
            if upt and dnt:
                signals[i] = 3
            elif upt:
                signals[i] = 2
            elif dnt:
                signals[i] = 1
            else:
                signals[i] = 0
        
        return signals
    
    def _generate_rsi_signals(self):
        """Generate RSI signals"""
        signals = np.zeros(len(self.data))
        
        for i in range(1, len(self.data)):
            current_rsi = self.rsi[i]
            prev_rsi = self.rsi[i-1]
            
            if current_rsi < self.rsi_oversold and prev_rsi >= self.rsi_oversold:
                signals[i] = 2
            elif current_rsi > self.rsi_overbought and prev_rsi <= self.rsi_overbought:
                signals[i] = -2
            elif current_rsi > 50 and prev_rsi <= 50:
                signals[i] = 1
            elif current_rsi < 50 and prev_rsi >= 50:
                signals[i] = -1
            else:
                signals[i] = 0
        
        return signals
    
    def _generate_combined_signals(self):
        """Generate combined signals"""
        signals = np.zeros(len(self.data))
        
        for i in range(len(self.data)):
            vwap_sig = self.vwap_signal[i]
            rsi_sig = self.rsi_signal[i]
            
            # Strong buy conditions
            if (vwap_sig == 2 and rsi_sig >= 1) or (vwap_sig >= 1 and rsi_sig == 2):
                signals[i] = 2
            # Weak buy conditions
            elif (vwap_sig == 2 and rsi_sig == 0) or (vwap_sig == 1 and rsi_sig == 1):
                signals[i] = 1
            # Strong sell conditions
            elif (vwap_sig == 1 and rsi_sig <= -1) or (vwap_sig <= 1 and rsi_sig == -2):
                signals[i] = -2
            # Weak sell conditions
            elif (vwap_sig == 1 and rsi_sig == 0) or (vwap_sig == 2 and rsi_sig == -1):
                signals[i] = -1
            else:
                signals[i] = 0
        
        return signals
    
    def next(self):
        """Execute strategy logic on each bar"""
        current_signal = self.combined_signal[-1]
        current_price = self.data.Close[-1]
        
        # Entry conditions
        if not self.position:
            # Long entry
            if current_signal >= 1:  # Buy signal (weak or strong)
                self.buy(size=1.0)
            # Short entry
            elif current_signal <= -1:  # Sell signal (weak or strong)
                self.sell(size=1.0)
        
        # Exit conditions
        else:
            if self.position.is_long:
                # Exit long position
                if current_signal <= -1:  # Sell signal
                    self.position.close()
                # Stop loss and take profit
                elif (current_price <= self.position.entry_price * (1 - self.stop_loss_pct) or
                      current_price >= self.position.entry_price * (1 + self.take_profit_pct)):
                    self.position.close()
            
            elif self.position.is_short:
                # Exit short position
                if current_signal >= 1:  # Buy signal
                    self.position.close()
                # Stop loss and take profit
                elif (current_price >= self.position.entry_price * (1 + self.stop_loss_pct) or
                      current_price <= self.position.entry_price * (1 - self.take_profit_pct)):
                    self.position.close()

def run_strategy_analysis():
    """Run the complete strategy analysis"""
    print("Loading and cleaning data...")
    df = load_and_clean_data()
    print(f"Data loaded: {len(df)} rows")
    print(df.head())
    
    print("\nCalculating indicators...")
    df = calculate_indicators(df)
    df = generate_vwap_signals(df)
    df = generate_rsi_signals(df)
    df = generate_combined_signals(df)
    
    print("\nIndicator sample:")
    print(df[['Close', 'VWAP', 'RSI', 'VWAPSignal', 'RSISignal', 'CombinedSignal']].tail(10))
    
    print("\nRunning backtest...")
    
    # Prepare data for backtesting (ensure proper column names)
    bt_data = df[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
    
    # Initialize and run backtest
    bt = Backtest(bt_data, RSI_VWAP_Strategy, cash=100000, commission=0.002)
    
    # Run the backtest
    results = bt.run()
    
    print("\n" + "="*50)
    print("BACKTEST RESULTS")
    print("="*50)
    print(results)
    
    # Plot results
    try:
        bt.plot(filename='strategy_results.html')
        print("\nStrategy plot saved as 'strategy_results.html'")
    except Exception as e:
        print(f"Could not generate plot: {e}")
    
    return results, bt

def optimize_strategy():
    """Optimize strategy parameters"""
    print("\nOptimizing strategy parameters...")
    
    df = load_and_clean_data()
    df = calculate_indicators(df)
    bt_data = df[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
    
    bt = Backtest(bt_data, RSI_VWAP_Strategy, cash=100000, commission=0.002)
    
    # Parameter optimization
    optimization_results = bt.optimize(
        rsi_length=range(14, 25, 2),
        vwap_length=range(15, 25, 2),
        rsi_oversold=range(25, 35, 2),
        rsi_overbought=range(65, 75, 2),
        stop_loss_pct=[0.015, 0.02, 0.025],
        take_profit_pct=[0.03, 0.04, 0.05],
        maximize='Sharpe Ratio',
        max_tries=100
    )
    
    print("\n" + "="*50)
    print("OPTIMIZATION RESULTS")
    print("="*50)
    print(optimization_results)
    
    return optimization_results

if __name__ == "__main__":
    # Run the strategy analysis
    results, backtest_obj = run_strategy_analysis()
    
    # Uncomment the line below to run optimization (takes longer)
    # optimization_results = optimize_strategy()
    
    print("\nStrategy analysis complete!")