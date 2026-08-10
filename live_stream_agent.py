import sys
import io
import time
import pandas as pd
from datetime import datetime
from trade_agent import EliteTradeTrackerAgent
from run_tracker import print_tracker_dashboard

# Ensure UTF-8 stdout encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def run_live_loop(poll_interval_seconds=5):
    print("=" * 110)
    print("⚡ LAUNCHING LIVE STREAMING TRADE TRACKER AGENT")
    print(f"   Listening to continuous market updates in D:\\dhan automation\\data every {poll_interval_seconds}s...")
    print("   Press Ctrl+C to stop.")
    print("=" * 110)
    
    agent = EliteTradeTrackerAgent()
    
    cycle = 0
    while True:
        try:
            cycle += 1
            print(f"\n[Cycle #{cycle} - {datetime.now().strftime('%H:%M:%S')}] Polling Live Market Feed...")
            
            # Scan for new signals (including Strategy 7)
            active_trades = agent.scan_market_and_track(scan_window_bars=100)
            
            # Fetch live prices from tick stream & evaluate positions
            live_prices = agent.fetch_live_prices()
            agent.evaluate_open_positions(live_prices=live_prices)
            
            # Display live dashboard
            print_tracker_dashboard(active_trades)
            
            time.sleep(poll_interval_seconds)
            
        except KeyboardInterrupt:
            print("\n🛑 Live Agent Stopped by User.")
            break
        except Exception as e:
            print(f"⚠️ Live Agent Notice: {e}")
            time.sleep(poll_interval_seconds)

if __name__ == "__main__":
    run_live_loop(poll_interval_seconds=5)
