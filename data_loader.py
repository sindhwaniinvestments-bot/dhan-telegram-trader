import os
import pandas as pd
import numpy as np

DATA_DIR = r"D:\dhan automation\data"

def load_smc_signals():
    """Load Smart Money Concepts (SMC) signals dataset."""
    filepath = os.path.join(DATA_DIR, "smc_signals.csv")
    if os.path.exists(filepath):
        df = pd.read_csv(filepath)
        df['day'] = pd.to_datetime(df['day'])
        df = df.sort_values(['symbol', 'day']).reset_index(drop=True)
        return df
    else:
        raise FileNotFoundError(f"File not found: {filepath}")

def load_target3d_signals():
    """Load Target3D signals dataset."""
    filepath = os.path.join(DATA_DIR, "target3d_signals.csv")
    if os.path.exists(filepath):
        df = pd.read_csv(filepath)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values(['symbol', 'date']).reset_index(drop=True)
        return df
    else:
        raise FileNotFoundError(f"File not found: {filepath}")

def load_all_datasets():
    """Load and merge core datasets for quantitative analysis."""
    print("Loading SMC signals...")
    smc_df = load_smc_signals()
    print(f"Loaded SMC signals: {len(smc_df):,} rows, {smc_df['symbol'].nunique()} unique symbols.")
    
    print("Loading Target3D signals...")
    target_df = load_target3d_signals()
    print(f"Loaded Target3D signals: {len(target_df):,} rows, {target_df['symbol'].nunique()} unique symbols.")
    
    return smc_df, target_df

if __name__ == "__main__":
    smc, target = load_all_datasets()
    print("SMC Columns:", list(smc.columns))
    print("Target3D Columns:", list(target.columns[:15]))
