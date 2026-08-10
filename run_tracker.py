import sys
import os
import time
import pandas as pd
from datetime import datetime
from trade_agent import EliteTradeTrackerAgent, ELITE_STRATEGIES

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def print_tracker_dashboard(active_trades):
    print("=" * 145)
    print(f"🤖 LIVE ELITE TRADE TRACKER DASHBOARD | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("   Price Feed: Today's Opening Price (open) vs Signal Entry Price (close)")
    print("   Active Strategies: S1 (95.25%), S3 (87.73%), S6 (85.71%), S7 (100%), S9 (95.06%), S10 (88.24%)")
    print("   Risk/Reward Model: 3:1 (+3R Take Profit / -1R Stop Loss)")
    print("=" * 145)
    
    if not active_trades:
        print("   No active trades currently open. Scanning for live setup entries...")
        print("=" * 145)
        return
        
    trades_list = list(active_trades.values())
    df_trades = pd.DataFrame(trades_list)
    
    display_cols = ['symbol', 'strategy', 'direction', 'entry_date', 'entry_price', 'current_price', 'est_profit_pct', 'unrealized_r', 'sl_price', 'tp_price', 'perf_status']
    available_cols = [c for c in display_cols if c in df_trades.columns]
    
    print(df_trades[available_cols].to_string(index=False))
    print("=" * 145)
    
    total_unrealized_r = df_trades['unrealized_r'].sum() if 'unrealized_r' in df_trades.columns else 0.0
    active_count = len(df_trades)
    print(f"Summary: Active Signals Tracked: {active_count} | Combined Portfolio Open Exposure: {round(total_unrealized_r, 2)} R")
    print("=" * 145)

def main():
    agent = EliteTradeTrackerAgent()
    active_trades = agent.scan_market_and_track(scan_window_bars=100)
    open_prices = agent.fetch_todays_open_prices()
    agent.evaluate_open_positions(live_prices=open_prices)
    print_tracker_dashboard(active_trades)

if __name__ == "__main__":
    main()
