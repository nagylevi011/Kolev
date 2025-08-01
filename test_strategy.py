#!/usr/bin/env python3
"""
Test script for RSI-VWAP Trading Strategy

This script tests all components of the trading strategy to ensure
they work correctly before running with real data.
"""

import sys
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

def test_imports():
    """Test that all required packages can be imported"""
    print("Testing imports...")
    
    try:
        import pandas as pd
        print("✓ pandas imported successfully")
    except ImportError:
        print("✗ pandas import failed")
        return False
    
    try:
        import numpy as np
        print("✓ numpy imported successfully")
    except ImportError:
        print("✗ numpy import failed")
        return False
    
    try:
        import pandas_ta as ta
        print("✓ pandas_ta imported successfully")
    except ImportError:
        print("✗ pandas_ta import failed - install with: pip install pandas-ta")
        return False
    
    try:
        from backtesting import Backtest, Strategy
        print("✓ backtesting imported successfully")
    except ImportError:
        print("✗ backtesting import failed - install with: pip install backtesting")
        return False
    
    return True

def create_test_data():
    """Create synthetic test data"""
    print("\nCreating test data...")
    
    np.random.seed(42)
    n_periods = 500
    
    # Create date range
    dates = pd.date_range('2024-01-01 13:30', periods=n_periods, freq='1min')
    
    # Generate price series with some trend and volatility
    base_price = 100.0
    trend = 0.0001  # Small upward trend
    volatility = 0.01
    
    returns = np.random.normal(trend, volatility, n_periods)
    prices = [base_price]
    
    for ret in returns[1:]:
        new_price = prices[-1] * (1 + ret)
        prices.append(max(new_price, 0.01))  # Ensure positive prices
    
    # Create OHLCV data
    data = []
    for i, close_price in enumerate(prices):
        if i == 0:
            open_price = close_price
        else:
            open_price = prices[i-1]
        
        # Add some intrabar volatility
        high_noise = abs(np.random.normal(0, 0.005))
        low_noise = abs(np.random.normal(0, 0.005))
        
        high = max(open_price, close_price) * (1 + high_noise)
        low = min(open_price, close_price) * (1 - low_noise)
        volume = np.random.randint(1000, 50000)
        
        data.append({
            'Open': open_price,
            'High': high,
            'Low': low,
            'Close': close_price,
            'Volume': volume
        })
    
    df = pd.DataFrame(data, index=dates)
    print(f"✓ Created {len(df)} rows of test data")
    return df

def test_indicators():
    """Test indicator calculations"""
    print("\nTesting indicators...")
    
    # Import required functions
    try:
        from trading_strategy import calculate_indicators, generate_vwap_signals, generate_rsi_signals
    except ImportError:
        print("✗ Could not import strategy functions")
        return False
    
    # Create test data
    df = create_test_data()
    
    # Test indicator calculation
    try:
        df = calculate_indicators(df, vwap_length=20, rsi_length=20)
        
        # Check if indicators were added
        if 'VWAP' not in df.columns:
            print("✗ VWAP indicator not calculated")
            return False
        if 'RSI' not in df.columns:
            print("✗ RSI indicator not calculated")
            return False
        
        # Check for reasonable values
        if df['VWAP'].isna().all():
            print("✗ VWAP contains only NaN values")
            return False
        if df['RSI'].isna().all():
            print("✗ RSI contains only NaN values")
            return False
        
        # Check RSI bounds
        rsi_valid = ((df['RSI'] >= 0) & (df['RSI'] <= 100)).all()
        if not rsi_valid:
            print("✗ RSI values outside valid range [0, 100]")
            return False
        
        print("✓ Indicators calculated successfully")
        print(f"  - VWAP range: {df['VWAP'].min():.2f} - {df['VWAP'].max():.2f}")
        print(f"  - RSI range: {df['RSI'].min():.2f} - {df['RSI'].max():.2f}")
        
    except Exception as e:
        print(f"✗ Error calculating indicators: {e}")
        return False
    
    return True, df

def test_signals():
    """Test signal generation"""
    print("\nTesting signal generation...")
    
    try:
        from trading_strategy import generate_vwap_signals, generate_rsi_signals, generate_combined_signals
    except ImportError:
        print("✗ Could not import signal functions")
        return False
    
    # Get test data with indicators
    success, df = test_indicators()
    if not success:
        return False
    
    try:
        # Generate signals
        df = generate_vwap_signals(df, backcandles=10)
        df = generate_rsi_signals(df, oversold=30, overbought=70)
        df = generate_combined_signals(df)
        
        # Check if signals were added
        required_signals = ['VWAPSignal', 'RSISignal', 'CombinedSignal']
        for signal in required_signals:
            if signal not in df.columns:
                print(f"✗ {signal} not generated")
                return False
        
        # Check signal distributions
        print("✓ Signals generated successfully")
        print(f"  - VWAP signals: {df['VWAPSignal'].value_counts().to_dict()}")
        print(f"  - RSI signals: {df['RSISignal'].value_counts().to_dict()}")
        print(f"  - Combined signals: {df['CombinedSignal'].value_counts().to_dict()}")
        
    except Exception as e:
        print(f"✗ Error generating signals: {e}")
        return False
    
    return True, df

def test_strategy_class():
    """Test the strategy class"""
    print("\nTesting strategy class...")
    
    try:
        from trading_strategy import RSI_VWAP_Strategy
        from backtesting import Backtest
    except ImportError:
        print("✗ Could not import strategy class")
        return False
    
    # Get test data
    success, df = test_signals()
    if not success:
        return False
    
    try:
        # Prepare data for backtesting
        bt_data = df[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
        
        # Create backtest instance
        bt = Backtest(bt_data, RSI_VWAP_Strategy, cash=10000, commission=0.002)
        
        # Run a quick test
        results = bt.run()
        
        print("✓ Strategy backtest completed successfully")
        print(f"  - Final portfolio value: ${results['Equity Final [$]']:,.2f}")
        print(f"  - Total return: {results['Return [%]']:.2f}%")
        print(f"  - Number of trades: {results['# Trades']}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing strategy: {e}")
        return False

def test_full_pipeline():
    """Test the complete pipeline"""
    print("\nTesting complete pipeline...")
    
    try:
        from example_usage import analyze_sample_strategy
        
        # Run the sample analysis
        df = analyze_sample_strategy()
        
        print("✓ Complete pipeline test successful")
        return True
        
    except Exception as e:
        print(f"✗ Error in full pipeline test: {e}")
        return False

def main():
    """Run all tests"""
    print("RSI-VWAP Trading Strategy Test Suite")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Indicator Test", lambda: test_indicators()[0]),
        ("Signal Test", lambda: test_signals()[0]),
        ("Strategy Class Test", test_strategy_class),
        ("Full Pipeline Test", test_full_pipeline),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            if test_func():
                passed += 1
            else:
                print(f"✗ {test_name} failed")
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {e}")
    
    print(f"\n{'='*50}")
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The strategy is ready to use.")
        print("\nNext steps:")
        print("1. Update the data path in trading_strategy.py")
        print("2. Run: python trading_strategy.py")
    else:
        print("❌ Some tests failed. Please check the requirements and installation.")
        print("\nTo fix issues:")
        print("1. Install missing packages: pip install -r requirements.txt")
        print("2. Check Python version (3.7+ recommended)")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)