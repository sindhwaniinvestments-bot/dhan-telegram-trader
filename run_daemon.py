import sys
import io
import time
from datetime import datetime
from trade_agent import EliteTradeTrackerAgent
from telegram_notifier import send_all_active_signals_to_telegram

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

LOG_FILE = r"d:\Monkeycode\github\daemon_execution.log"

def log_event(message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    formatted = f"[{timestamp}] {message}"
    try:
        print(formatted)
    except Exception:
        pass
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(formatted + "\n")
    except Exception:
        pass

def run_single_cloud_scan():
    """Runs a single cloud scan and dispatches ALL active stock trade signals + Performance Summary to Telegram."""
    log_event("☁️ Executing Single Cloud Market Scan & Dispatching Performance Summary...")
    agent = EliteTradeTrackerAgent(enable_telegram=True)
    active_trades = agent.scan_market_and_track(scan_window_bars=100)
    perf_summary = agent.get_portfolio_performance_summary()
    
    # Send ALL active stock trade signals + Performance Briefing to Telegram
    send_all_active_signals_to_telegram(active_trades, perf_summary=perf_summary)
    log_event("✅ Cloud Scan & Full Telegram Performance Dispatch Complete!")

def run_unattended_daemon(poll_interval_seconds=10):
    log_event("🚀 Starting 24/7 Unattended Telegram Trade Tracker Daemon...")
    log_event("   Features: Live Trade Alerts + Daily 9:00 AM Full Active Signals Digest & Performance Briefing.")
    
    agent = EliteTradeTrackerAgent(enable_telegram=True)
    last_digest_date = None
    
    while True:
        try:
            now = datetime.now()
            today_str = now.strftime('%Y-%m-%d')
            current_hour = now.hour
            
            active_trades = agent.scan_market_and_track(scan_window_bars=100)
            live_prices = agent.fetch_todays_open_prices()
            agent.evaluate_open_positions(live_prices=live_prices)
            
            # Daily 9:00 AM Digest Check (Sends ALL active stock signals + Performance Briefing)
            if current_hour == 9 and last_digest_date != today_str:
                log_event(f"⏰ 9:00 AM Triggered! Dispatching ALL Active Stock Signals & Performance Briefing to Telegram...")
                perf_summary = agent.get_portfolio_performance_summary()
                send_all_active_signals_to_telegram(active_trades, perf_summary=perf_summary)
                last_digest_date = today_str
                
            time.sleep(poll_interval_seconds)
            
        except Exception as e:
            log_event(f"⚠️ Daemon exception encountered: {e}")
            time.sleep(poll_interval_seconds)

if __name__ == "__main__":
    if "--single-run" in sys.argv:
        run_single_cloud_scan()
    else:
        run_unattended_daemon(poll_interval_seconds=10)
