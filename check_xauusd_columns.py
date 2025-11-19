import pandas as pd
import sys

# Check XAUUSD tick data structure
file_path = "/home/ubuntu/microstructure-three-factor-regime/data/tick_data/symbol=XAUUSD/date=2024-11-01/XAUUSD_2024-11-01.parquet"

try:
    df = pd.read_parquet(file_path)
    print("Columns:", df.columns.tolist())
    print("\nShape:", df.shape)
    print("\nFirst few rows:")
    print(df.head())
    print("\nData types:")
    print(df.dtypes)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)

