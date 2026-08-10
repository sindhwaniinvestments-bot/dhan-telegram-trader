import sys
import io
import pandas as pd
import numpy as np
from data_loader import load_all_datasets
from feature_engine import compute_smc_features, calculate_3to1_rr_levels
from backtesting_engine import backtest_3to1_strategy
from strategy_agent import generate_10_strategies

# Ensure standard stdout encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def run_quantitative_evaluation():
    print("=" * 80)
    print("AI QUANTITATIVE EVALUATION & 10-STRATEGY BACKTESTING ENGINE")
    print("Data Source: D:\\dhan automation\\data")
    print("Target Parameter: 3:1 Risk-to-Reward (+3R Take Profit / -1R Stop Loss)")
    print("=" * 80)
    
    # 1. Load Data
    try:
        smc_df, target_df = load_all_datasets()
    except Exception as e:
        print(f"Error loading data: {e}")
        return

    # Merge or evaluate SMC dataset
    print("\n[Step 1] Engineering Features & Indicator Levels...")
    df = compute_smc_features(smc_df)
    df = calculate_3to1_rr_levels(df)
    
    print("\n[Step 2] Generating 10 Proprietary Quantitative Strategies...")
    df = generate_10_strategies(df)
    
    print("\n[Step 3] Executing 3:1 Risk-to-Reward Vectorized Backtest across Strategies...\n")
    
    strategies_info = [
        ('Strategy 1: Bullish OB + FVG Confluence', 'strat_1_ob_fvg_confluence', 'long'),
        ('Strategy 2: Liquidity Sweep + Displacement', 'strat_2_sweep_displacement', 'long'),
        ('Strategy 3: Volume Spike + Order Block Breakout', 'strat_3_vol_ob_breakout', 'long'),
        ('Strategy 4: ATR Compression Expansion', 'strat_4_atr_compression_break', 'long'),
        ('Strategy 5: Displacement + FVG Entry', 'strat_5_disp_fvg_entry', 'long'),
        ('Strategy 6: Short High Liquidity Sweep', 'strat_6_short_liquidity_sweep', 'short'),
        ('Strategy 7: SMC Super Signal (OB+FVG+Disp)', 'strat_7_smc_super_signal', 'long'),
        ('Strategy 8: Volume Exhaustion at 20D Low', 'strat_8_vol_exhaustion_low', 'long'),
        ('Strategy 9: Momentum + OB Support', 'strat_9_momentum_ob_support', 'long'),
        ('Strategy 10: Target3D Level + SMC Hybrid', 'strat_10_target3d_smc_hybrid', 'long')
    ]
    
    results_list = []
    
    for name, col_name, direction in strategies_info:
        stats = backtest_3to1_strategy(df, signal_col=col_name, direction=direction, holding_period=10)
        results_list.append({
            'Strategy Name': name,
            'Direction': direction.upper(),
            'Total Trades': stats['total_trades'],
            'Win Rate (%)': stats['win_rate'],
            'Profit Factor': stats['profit_factor'],
            'EV per Trade (R)': stats['ev_r'],
            'Total Yield (R)': stats['total_r'],
            'Max Drawdown (R)': stats['max_drawdown_r']
        })
        
    results_df = pd.DataFrame(results_list)
    
    print("=" * 100)
    print(results_df.to_string(index=False))
    print("=" * 100)
    
    output_path = r"d:\Monkeycode\github\quantitative_10_strategy_report.csv"
    results_df.to_csv(output_path, index=False)
    print(f"\nPerformance report saved successfully to: {output_path}")

if __name__ == "__main__":
    run_quantitative_evaluation()
