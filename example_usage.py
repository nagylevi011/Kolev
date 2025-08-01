#!/usr/bin/env python3
"""
Example usage of the RSI-VWAP Trading Strategy

This script demonstrates how to use the trading strategy with your data.
Make sure to update the file path to your actual .dbn file location.
"""

from trading_strategy import (
    load_and_clean_data,
    calculate_indicators,
    generate_vwap_signals,
    generate_rsi_signals,
    generate_combined_signals,
    RSI_VWAP_Strategy,
    run_strategy_analysis
)
import pandas as pd
import numpy as np

def create_sample_data():
    """Create sample OHLCV data for testing (if you don't have the .dbn file)"""
    # Generate 1000 minutes of sample data
    np.random.seed(42)
    dates = pd.date_range('2024-01-01 13:30', periods=1000, freq='1min')
    
    # Create realistic price movements
    base_price = 100.0
    returns = np.random.normal(0, 0.001, 1000)
    prices = [base_price]
    
    for ret in returns[1:]:
        prices.append(prices[-1] * (1 + ret))
    
    # Create OHLCV data
    data = []
    for i, price in enumerate(prices):
        high = price * (1 + abs(np.random.normal(0, 0.005)))
        low = price * (1 - abs(np.random.normal(0, 0.005)))
        open_price = prices[i-1] if i > 0 else price
        close_price = price
        volume = np.random.randint(1000, 10000)
        
        data.append({
            'Open': open_price,
            'High': max(open_price, high, close_price),
            'Low': min(open_price, low, close_price),
            'Close': close_price,
            'Volume': volume
        })
    
    df = pd.DataFrame(data, index=dates)
    return df

def analyze_sample_strategy():
    """Analyze the strategy with sample data"""
    print("Creating sample data for demonstration...")
    df = create_sample_data()
    
    print("Calculating indicators...")
    df = calculate_indicators(df)
    df = generate_vwap_signals(df)
    df = generate_rsi_signals(df)
    df = generate_combined_signals(df)
    
    print("\nSample data with indicators:")
    print(df[['Close', 'VWAP', 'RSI', 'VWAPSignal', 'RSISignal', 'CombinedSignal']].tail())
    
    # Show signal distribution
    print(f"\nVWAP Signal Distribution:")
    print(df['VWAPSignal'].value_counts().sort_index())
    
    print(f"\nRSI Signal Distribution:")
    print(df['RSISignal'].value_counts().sort_index())
    
    print(f"\nCombined Signal Distribution:")
    print(df['CombinedSignal'].value_counts().sort_index())
    
    return df

def main():
    """Main execution function"""
    print("RSI-VWAP Trading Strategy Example")
    print("=" * 40)
    
    try:
        # Try to run with real data
        print("Attempting to load real data...")
        results, bt = run_strategy_analysis()
        
    except FileNotFoundError:
        print("Real data file not found. Using sample data for demonstration...")
        df = analyze_sample_strategy()
        
        print("\nTo use with your actual data:")
        print("1. Update the file path in load_and_clean_data() function")
        print("2. Ensure you have the databento package installed")
        print("3. Run: python trading_strategy.py")
        
    except Exception as e:
        print(f"Error running with real data: {e}")
        print("Using sample data for demonstration...")
        df = analyze_sample_strategy()

if __name__ == "__main__":
    main()