import pandas as pd
import numpy as np

def generate_10_strategies(df):
    """
    Formulates 10 Proprietary Quantitative Strategies tailored to SMC, Order Blocks,
    Fair Value Gaps, Liquidity Sweeps, and Price Action signals.
    """
    df = df.copy()
    
    # Strategy 1: Bullish Order Block + Fair Value Gap Confluence
    df['strat_1_ob_fvg_confluence'] = df['buy_ob_clean'] & df['fvg_bull_clean']
    
    # Strategy 2: Liquidity Sweep of 20-Day Low + Displacement Reversal
    df['strat_2_sweep_displacement'] = df['swp_low_clean'] & df['disp_clean']
    
    # Strategy 3: Volume Spike + Bullish Order Block Breakout
    df['strat_3_vol_ob_breakout'] = df['vol_spike'] & df['buy_ob_clean']
    
    # Strategy 4: High Volatility ATR Compression Breakout
    df['strat_4_atr_compression_break'] = (df['atr_pct'] < df['atr_pct'].rolling(20).mean()) & df['disp_clean']
    
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
        
    return df
