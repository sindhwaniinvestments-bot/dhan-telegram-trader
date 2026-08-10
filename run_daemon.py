import sys
import io
import time
from datetime import datetime
from trade_agent import EliteTradeTrackerAgent
from telegram_notifier import send_telegram_message, format_daily_digest_alert

# Ensure UTF-8 stdout encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

LOG_FILE = r"d:\Monkeycode\github\daemon_execution.log"

def log_event(message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    formatted = f"[{timestamp}] {message}"
    print(formatted)
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(formatted + "\n")
    except Exception:
        pass

def run_single_cloud_scan():
    """Runs a single cloud scan and dispatches Telegram notifications (for GitHub Actions Cloud Cron)."""
    log_event("☁️ Executing Single Cloud Market Scan & Dispatching Telegram Digest...")
    agent = EliteTradeTrackerAgent(enable_telegram=True)
    active_trades = agent.scan_market_and_track(scan_window_bars=100)
    
    # Send daily briefing digest to Telegram
    digest_msg = format_daily_digest_alert(active_trades)
    send_telegram_message(digest_msg)
    log_event("✅ Cloud Scan & Telegram Dispatch Complete!")

def run_unattended_daemon(poll_interval_seconds=10):
    log_event("🚀 Starting 24/7 Unattended Telegram Trade Tracker Daemon...")
    log_event("   Features: Live Trade Alerts + Daily 9:00 AM Active Signals Digest.")
    
    agent = EliteTradeTrackerAgent(enable_telegram=True)
    last_digest_date = None
    
    while True:
        try:
            now = datetime.now()
            today_str = now.strftime('%Y-%m-%d')
            current_hour = now.hour
            
            active_trades = agent.scan_market_and_track(scan_window_bars=100)
            live_prices = agent.fetch_live_prices()
            agent.evaluate_open_positions(live_prices=live_prices)
            
            # Daily 9:00 AM Digest Check
            if current_hour == 9 and last_digest_date != today_str:
                log_event(f"⏰ 9:00 AM Triggered! Dispatching Daily Active Signals Digest to Telegram...")
                digest_msg = format_daily_digest_alert(active_trades)
                send_telegram_message(digest_msg)
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
