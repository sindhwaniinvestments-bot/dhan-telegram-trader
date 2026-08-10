import sys
import io
import time
import pandas as pd
from datetime import datetime
from trade_agent import EliteTradeTrackerAgent, ELITE_STRATEGIES

# Ensure UTF-8 stdout encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def print_tracker_dashboard(active_trades):
    print("=" * 110)
    print(f"🤖 LIVE ELITE TRADE TRACKER DASHBOARD | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("   Data Feed: LIVE Stream & Historical Updates (D:\\dhan automation\\data)")
    print("   Active Strategies: S1 (95.25%), S3 (87.73%), S6 (85.71%), S7 (100%), S9 (95.06%), S10 (88.24%)")
    print("   Risk/Reward Model: 3:1 (+3R Take Profit / -1R Stop Loss)")
    print("=" * 110)
    
    if not active_trades:
        print("   No active trades currently open. Scanning for live setup entries...")
        print("=" * 110)
        return
        
    trades_list = list(active_trades.values())
    df_trades = pd.DataFrame(trades_list)
    
    display_cols = ['symbol', 'strategy', 'direction', 'entry_price', 'sl_price', 'tp_price', 'current_price', 'unrealized_r', 'status']
    available_cols = [c for c in display_cols if c in df_trades.columns]
    
    print(df_trades[available_cols].to_string(index=False))
    print("=" * 110)
    
    total_unrealized_r = df_trades['unrealized_r'].sum() if 'unrealized_r' in df_trades.columns else 0.0
    active_count = len(df_trades)
    print(f"Summary: Active Signals Tracked: {active_count} | Combined Portfolio Open Exposure: {round(total_unrealized_r, 2)} R")
    print("=" * 110)

def main():
    agent = EliteTradeTrackerAgent()
    active_trades = agent.scan_market_and_track(scan_window_bars=100)
    live_prices = agent.fetch_live_prices()
    agent.evaluate_open_positions(live_prices=live_prices)
    print_tracker_dashboard(active_trades)

if __name__ == "__main__":
    main()
