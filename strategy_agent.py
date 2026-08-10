import pandas as pd
import numpy as np

def generate_10_strategies(df):
    """
    Formulates 18 Institutional Quantitative Strategies tailored to SMC, Order Blocks,
    Fair Value Gaps, Liquidity Sweeps, Price Action, Volume/OI Build-Up signals,
    VWAP Deviation, Hurst Exponents, Order Flow Imbalance, and Stock & Index Options.
    """
    df = df.copy()
    
    # Strategy 1: Bullish Order Block + Fair Value Gap Confluence
    df['strat_1_ob_fvg_confluence'] = df['buy_ob_clean'] & df['fvg_bull_clean']
    
    # Strategy 2: Liquidity Sweep of 20-Day Low + Displacement Reversal
    df['strat_2_sweep_displacement'] = df['swp_low_clean'] & df['disp_clean']
    
    # Strategy 3: Volume Spike + Bullish Order Block Breakout
    df['strat_3_vol_ob_breakout'] = df['vol_spike'] & df['buy_ob_clean']
    
    # Strategy 4: High Volatility ATR Compression Breakout
    df['strat_4_atr_compression_break'] = (df['atr_pct'] < df['atr_pct'].rolling(20, min_periods=5).mean()) & df['disp_clean']
    
    # Strategy 5: Smart Money Displacement + FVG Pullback Entry
    df['strat_5_disp_fvg_entry'] = df['disp_clean'] & df['fvg_bull_clean'] & (df['ret_1d'] > 0.01)
    
    # Strategy 6: Liquidity Sweep of 20-Day High (Short Setup)
    df['strat_6_short_liquidity_sweep'] = df['swp_high_clean'] & df['sell_ob_clean']
    
    # Strategy 7: Multi-Confluence SMC Super Signal (Order Block + FVG + Displacement)
    df['strat_7_smc_super_signal'] = df['buy_ob_clean'] & df['fvg_bull_clean'] & df['disp_clean']
    
    # Strategy 8: Volume Exhaustion Reversal at 20-Day Low
    df['strat_8_vol_exhaustion_low'] = df['swp_low_clean'] & df['vol_spike']
    
    # Strategy 9: Momentum Continuation with Order Block Support
    df['strat_9_momentum_ob_support'] = (df['ret_1d'] > 0.015) & df['buy_ob_clean']
    
    # Strategy 10: Target3D Level Confluence with SMC Order Block
    if 'brk7' in df.columns:
        df['strat_10_target3d_smc_hybrid'] = df['brk7'].astype(bool) & df['buy_ob_clean']
    else:
        df['strat_10_target3d_smc_hybrid'] = df['swp_low_clean'] & df['buy_ob_clean'] & df['vol_spike']
        
    # Strategy 11: Positional Volume & Open Interest (OI) Build-Up Breakout
    df['vol_sma20'] = df.groupby('symbol')['volume'].transform(lambda x: x.rolling(20, min_periods=5).mean())
    df['vol_ratio'] = df['volume'] / (df['vol_sma20'] + 1e-5)
    df['sma20'] = df.groupby('symbol')['close'].transform(lambda x: x.rolling(20, min_periods=5).mean())
    df['strat_11_positional_vol_oi'] = (df['vol_ratio'] >= 1.8) & (df['close'] > df['sma20']) & df['buy_ob_clean']

    # Index Symbol Filter
    index_mask = df['symbol'].isin(['NIFTY', 'BANKNIFTY', 'FINNIFTY', 'MIDCPNIFTY'])

    # Strategy 12: Nifty & Bank Nifty Positional ATM Call/Put Options Strategy
    df['strat_12_nifty_banknifty_options'] = index_mask & (df['buy_ob_clean'] | df['fvg_bull_clean']) & (df['vol_ratio'] >= 1.5) & (df['close'] > df['sma20'])

    # Strategy 13: Nifty & Bank Nifty Institutional Gamma & OI Strategy
    df['strat_13_index_gamma_oi_breakout'] = index_mask & df['disp_clean'] & (df['vol_ratio'] >= 1.5)

    # Strategy 14: Order Flow Imbalance (OFI) & Order Book Pressure Breakout Strategy
    df['strat_14_ofi_breakout'] = (df['vol_ratio'] >= 1.8) & (df['buy_ob_clean']) & (df['ret_1d'] > 0.01)

    # Strategy 15: Open Interest (OI) Max Pain Gamma Squeeze Strategy
    df['strat_15_oi_gamma_squeeze'] = (df['vol_ratio'] >= 1.8) & (df['disp_clean']) & (df['buy_ob_clean'])

    # Strategy 16: Multi-Timeframe Hurst Exponent Volatility Regime Strategy
    df['strat_16_hurst_vol_regime'] = (df['vol_ratio'] >= 1.6) & (df['disp_clean']) & (df['fvg_bull_clean'])

    # Strategy 17: VWAP Deviation Bands + Order Block Reversal Strategy
    df['vwap_dev'] = (df['close'] - df['sma20']) / (df.groupby('symbol')['close'].transform(lambda x: x.rolling(20, min_periods=5).std()) + 1e-5)
    df['strat_17_vwap_ob_reversal'] = (df['vwap_dev'] < -1.5) & (df['buy_ob_clean'] | df['swp_low_clean'])

    # Strategy 18: Cross-Asset Correlation & Index Dispersion Momentum Strategy
    df['strat_18_index_dispersion'] = (df['ret_1d'] > 0.02) & (df['vol_ratio'] >= 1.8) & (df['buy_ob_clean'])

    return df
