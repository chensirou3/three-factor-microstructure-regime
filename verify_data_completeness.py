#!/usr/bin/env python3
"""
Verify Data Completeness for Three-Factor Regime Analysis

This script checks that all required data files exist for all symbols and timeframes.
"""

from pathlib import Path
import pandas as pd

# Configuration
SYMBOLS = ["BTCUSD", "ETHUSD", "EURUSD", "USDJPY", "XAGUSD", "XAUUSD"]
TIMEFRAMES = ["5min", "15min", "30min", "1h", "4h", "1d"]
ROOT = Path("/home/ubuntu/microstructure-three-factor-regime")

# Timeframe mapping for file names
TF_MAP = {
    "5min": "5min",
    "15min": "15min",
    "30min": "30min",
    "1h": "1H",
    "4h": "4H",
    "1d": "1D"
}

def check_raw_bars():
    """Check raw bars with OFI (Factor 2)."""
    print("=" * 80)
    print("Factor 2 - OFI (Raw Bars)")
    print("=" * 80)
    
    missing = []
    found = []
    
    for symbol in SYMBOLS:
        for tf in TIMEFRAMES:
            file_tf = TF_MAP[tf]
            file_path = ROOT / "data" / "raw_bars" / "bars_with_ofi" / f"{symbol}_{file_tf}_merged_bars_with_ofi.csv"
            
            if file_path.exists() or file_path.is_symlink():
                found.append(f"{symbol}_{tf}")
                # Get file size
                try:
                    size = file_path.stat().st_size
                    size_str = f"{size / 1024:.0f}K" if size < 1024*1024 else f"{size / (1024*1024):.1f}M"
                    print(f"  ✓ {symbol:8s} {tf:6s} - {size_str:>8s}")
                except:
                    print(f"  ✓ {symbol:8s} {tf:6s} - (symlink)")
            else:
                missing.append(f"{symbol}_{tf}")
                print(f"  ✗ {symbol:8s} {tf:6s} - MISSING")
    
    print(f"\nTotal: {len(found)}/{len(SYMBOLS) * len(TIMEFRAMES)} ({len(found) / (len(SYMBOLS) * len(TIMEFRAMES)) * 100:.1f}%)")
    return len(missing) == 0


def check_manipscore():
    """Check ManipScore files (Factor 1)."""
    print("\n" + "=" * 80)
    print("Factor 1 - ManipScore")
    print("=" * 80)
    
    missing = []
    found = []
    
    for symbol in SYMBOLS:
        for tf in TIMEFRAMES:
            file_path = ROOT / "data" / "factors" / "manip" / f"manip_{symbol}_{tf}.parquet"
            
            if file_path.exists():
                found.append(f"{symbol}_{tf}")
                # Get file size and row count
                try:
                    size = file_path.stat().st_size
                    size_str = f"{size / 1024:.0f}K" if size < 1024*1024 else f"{size / (1024*1024):.1f}M"
                    df = pd.read_parquet(file_path)
                    print(f"  ✓ {symbol:8s} {tf:6s} - {size_str:>8s} ({len(df):,} rows)")
                except Exception as e:
                    print(f"  ✓ {symbol:8s} {tf:6s} - ERROR: {e}")
            else:
                missing.append(f"{symbol}_{tf}")
                print(f"  ✗ {symbol:8s} {tf:6s} - MISSING")
    
    print(f"\nTotal: {len(found)}/{len(SYMBOLS) * len(TIMEFRAMES)} ({len(found) / (len(SYMBOLS) * len(TIMEFRAMES)) * 100:.1f}%)")
    return len(missing) == 0


def check_volliqscore():
    """Check VolLiqScore files (Factor 3)."""
    print("\n" + "=" * 80)
    print("Factor 3 - VolLiqScore")
    print("=" * 80)
    
    missing = []
    found = []
    
    for symbol in SYMBOLS:
        for tf in TIMEFRAMES:
            file_path = ROOT / "data" / "factors" / "vol_liq" / f"vol_liq_{symbol}_{tf}.parquet"
            
            if file_path.exists():
                found.append(f"{symbol}_{tf}")
                # Get file size and row count
                try:
                    size = file_path.stat().st_size
                    size_str = f"{size / 1024:.0f}K" if size < 1024*1024 else f"{size / (1024*1024):.1f}M"
                    df = pd.read_parquet(file_path)
                    print(f"  ✓ {symbol:8s} {tf:6s} - {size_str:>8s} ({len(df):,} rows)")
                except Exception as e:
                    print(f"  ✓ {symbol:8s} {tf:6s} - ERROR: {e}")
            else:
                missing.append(f"{symbol}_{tf}")
                print(f"  ✗ {symbol:8s} {tf:6s} - MISSING")
    
    print(f"\nTotal: {len(found)}/{len(SYMBOLS) * len(TIMEFRAMES)} ({len(found) / (len(SYMBOLS) * len(TIMEFRAMES)) * 100:.1f}%)")
    return len(missing) == 0


def main():
    print("\n" + "=" * 80)
    print("DATA COMPLETENESS VERIFICATION")
    print("=" * 80)
    print(f"Symbols: {', '.join(SYMBOLS)}")
    print(f"Timeframes: {', '.join(TIMEFRAMES)}")
    print(f"Expected files per factor: {len(SYMBOLS) * len(TIMEFRAMES)}")
    print()
    
    ofi_ok = check_raw_bars()
    manip_ok = check_manipscore()
    volliq_ok = check_volliqscore()
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Factor 1 (ManipScore):  {'✓ COMPLETE' if manip_ok else '✗ INCOMPLETE'}")
    print(f"Factor 2 (OFI):         {'✓ COMPLETE' if ofi_ok else '✗ INCOMPLETE'}")
    print(f"Factor 3 (VolLiqScore): {'✓ COMPLETE' if volliq_ok else '✗ INCOMPLETE'}")
    print("=" * 80)
    
    if ofi_ok and manip_ok and volliq_ok:
        print("\n🎉 ALL DATA COMPLETE! Ready for analysis.")
    else:
        print("\n⚠️  Some data is missing. Please check the logs above.")


if __name__ == "__main__":
    main()

