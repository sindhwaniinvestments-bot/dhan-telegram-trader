import sys
import os
import time
import pandas as pd
from datetime import datetime
from trade_agent import EliteTradeTrackerAgent, ELITE_STRATEGIES

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def print_tracker_dashboard(agent, active_trades):
    perf = agent.get_portfolio_performance_summary()
    
    print("=" * 145)
    print(f"🤖 LIVE ELITE TRADE TRACKER DASHBOARD | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   🎯 Strategy Accuracy (Win Rate): {perf['accuracy_pct']}%")
    print(f"   🟢 Booked Profit (+3R Hits): +{perf['booked_profit_r']} R (+${perf['booked_profit_amt']:,.2f})")
    print(f"   🛑 Booked Loss (-1R Hits): -{perf['booked_loss_r']} R (-${perf['booked_loss_amt']:,.2f})")
    print(f"   📈 Current Open Profit: {perf['unrealized_r']:+.2f} R ({perf['unrealized_pct']:+.2f}% | +${perf['unrealized_amt']:,.2f})")
    print(f"   🔢 Trade Counts: Active Open: {perf['active_count']} | Target Hits (+3R): {perf['win_count']} | Stop Hits (-1R): {perf['loss_count']} | Total Analyzed: {perf['active_count'] + perf['closed_count']}")
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

def main():
    agent = EliteTradeTrackerAgent()
    active_trades = agent.scan_market_and_track(scan_window_bars=100)
    open_prices = agent.fetch_todays_open_prices()
    agent.evaluate_open_positions(live_prices=open_prices)
    print_tracker_dashboard(agent, active_trades)

if __name__ == "__main__":
    main()
