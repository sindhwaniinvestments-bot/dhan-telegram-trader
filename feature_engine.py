import pandas as pd
import numpy as np

def compute_atr(df, period=14):
    """Compute Average True Range (ATR)."""
    high = df['high']
    low = df['low']
    close = df['close'].shift(1)
    
    tr1 = high - low
    tr2 = (high - close).abs()
    tr3 = (low - close).abs()
    
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    return atr

def compute_smc_features(df):
    """Engineer quantitative signals based on Smart Money Concepts, Order Blocks, and Volume."""
    df = df.copy()
    
    # ATR & Volatility
    df['atr'] = compute_atr(df)
    df['atr_pct'] = (df['atr'] / df['close']) * 100
    
    # Returns & Momentum
    df['ret_1d'] = df.groupby('symbol')['close'].pct_change()
    df['vol_ma20'] = df.groupby('symbol')['volume'].transform(lambda x: x.rolling(20).mean())
    df['vol_spike'] = df['volume'] > (1.8 * df['vol_ma20'])
    
    # Price Channels & Liquidity Sweeps
    df['rolling_high_20'] = df.groupby('symbol')['high'].transform(lambda x: x.rolling(20).max())
    df['rolling_low_20'] = df.groupby('symbol')['low'].transform(lambda x: x.rolling(20).min())
    
    # Smart Money Signals (Bullish OB, Bearish OB, FVG, Displacement)
    df['buy_ob_clean'] = df['buy_ob'].astype(bool) if 'buy_ob' in df.columns else False
    df['sell_ob_clean'] = df['sell_ob'].astype(bool) if 'sell_ob' in df.columns else False
    df['fvg_bull_clean'] = df['fvg_bull'].astype(bool) if 'fvg_bull' in df.columns else False
    df['disp_clean'] = df['displacement'].astype(bool) if 'displacement' in df.columns else False
    df['swp_low_clean'] = df['swp_low_20'].astype(bool) if 'swp_low_20' in df.columns else False
    df['swp_high_clean'] = df['swp_high_20'].astype(bool) if 'swp_high_20' in df.columns else False

    return df

def calculate_3to1_rr_levels(df, stop_atr_mult=1.0, reward_atr_mult=3.0):
    """Calculate 3:1 Risk-to-Reward Target and Stop-Loss levels based on ATR."""
    df = df.copy()
    # Bullish Setup: SL = Entry - 1*ATR, TP = Entry + 3*ATR
    df['long_sl'] = df['close'] - (stop_atr_mult * df['atr'])
    df['long_tp'] = df['close'] + (reward_atr_mult * df['atr'])
    
    # Bearish Setup: SL = Entry + 1*ATR, TP = Entry - 3*ATR
    df['short_sl'] = df['close'] + (stop_atr_mult * df['atr'])
    df['short_tp'] = df['close'] - (reward_atr_mult * df['atr'])
    
    return df
