#!/usr/bin/env python3
"""
Inspect data schemas for all three factors and raw bars.
"""

import pandas as pd
from pathlib import Path

root = Path("/home/ubuntu/microstructure-three-factor-regime")

print("=" * 80)
print("FACTOR 1 - ManipScore")
print("=" * 80)
manip_file = root / "data/factors/manip/manip_BTCUSD_5min.parquet"
if manip_file.exists():
    df = pd.read_parquet(manip_file)
    print(f"File: {manip_file.name}")
    print(f"Rows: {len(df):,}")
    print(f"Columns: {df.columns.tolist()}")
    print(f"\nFirst 3 rows:")
    print(df.head(3))
    print(f"\nData types:")
    print(df.dtypes)
else:
    print("NOT FOUND")

print("\n" + "=" * 80)
print("FACTOR 2 - OFI (from raw bars)")
print("=" * 80)
ofi_csv = root / "data/raw_bars/bars_with_ofi/BTCUSD_5min_merged_bars_with_ofi.csv"
if ofi_csv.exists():
    df = pd.read_csv(ofi_csv, nrows=5)
    print(f"File: {ofi_csv.name}")
    print(f"Columns: {df.columns.tolist()}")
    print(f"\nFirst 3 rows:")
    print(df.head(3))
else:
    print("NOT FOUND")

print("\n" + "=" * 80)
print("FACTOR 3 - VolLiqScore")
print("=" * 80)
vol_file = root / "data/factors/vol_liq/vol_liq_BTCUSD_5min.parquet"
if vol_file.exists():
    df = pd.read_parquet(vol_file)
    print(f"File: {vol_file.name}")
    print(f"Rows: {len(df):,}")
    print(f"Columns: {df.columns.tolist()}")
    print(f"\nFirst 3 rows:")
    print(df.head(3))
    print(f"\nData types:")
    print(df.dtypes)
else:
    print("NOT FOUND")

print("\n" + "=" * 80)
print("Check OFI subdirectory")
print("=" * 80)
ofi_dir = root / "data/factors/ofi"
if ofi_dir.exists():
    files = list(ofi_dir.glob("*"))
    print(f"Contents: {[f.name for f in files]}")
else:
    print("NOT FOUND")

