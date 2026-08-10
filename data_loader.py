import os
import pandas as pd
import numpy as np

DATA_DIR = r"D:\dhan automation\data"

# Official NSE F&O Indices
FO_INDICES = {'NIFTY', 'BANKNIFTY', 'FINNIFTY', 'MIDCPNIFTY'}

def load_smc_signals(fo_only=True):
    """Load Smart Money Concepts (SMC) signals dataset, strictly filtering for F&O Stocks & Indices."""
    filepath = os.path.join(DATA_DIR, "smc_signals.csv")
    if os.path.exists(filepath):
        df = pd.read_csv(filepath)
        df['day'] = pd.to_datetime(df['day'])
        
        if fo_only:
            # Filter out non-F&O cash-only stocks (e.g. SME, BE, ST series)
            df = df[~df['symbol'].str.contains('-SME|-BE|-ST', regex=True, na=False)].reset_index(drop=True)
            
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
    print("Loading SMC signals (F&O Stocks & Indices Only)...")
    smc_df = load_smc_signals(fo_only=True)
    print(f"Loaded SMC signals: {len(smc_df):,} rows, {smc_df['symbol'].nunique()} unique F&O & Index symbols.")
    
    print("Loading Target3D signals...")
    target_df = load_target3d_signals()
    print(f"Loaded Target3D signals: {len(target_df):,} rows, {target_df['symbol'].nunique()} unique symbols.")
    
    return smc_df, target_df

if __name__ == "__main__":
    smc, target = load_all_datasets()
    print("SMC Columns:", list(smc.columns))
    print("Target3D Columns:", list(target.columns[:15]))
