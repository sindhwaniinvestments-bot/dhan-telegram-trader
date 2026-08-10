import os
import sys
import io
import json
import urllib.request
import urllib.parse
from datetime import datetime
from dotenv import load_dotenv

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
DASHBOARD_URL = os.getenv("DASHBOARD_URL", "https://dhan-telegram-trader.fly.dev/")

def send_telegram_message(message_text, pin=False):
    """Sends a formatted markdown message to Telegram, optionally pinning it."""
    token = os.getenv("TELEGRAM_BOT_TOKEN", TELEGRAM_BOT_TOKEN)
    chat_id = os.getenv("TELEGRAM_CHAT_ID", TELEGRAM_CHAT_ID)
    
    if not token or token == "YOUR_TELEGRAM_BOT_TOKEN_HERE" or not chat_id or chat_id == "YOUR_TELEGRAM_CHAT_ID_HERE":
        print("⚠️ Telegram Config Notice: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set in .env file.")
        return False
        
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message_text,
        "parse_mode": "Markdown"
    }
    
    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=10) as response:
            res_body = response.read().decode('utf-8')
            res_json = json.loads(res_body)
            if res_json.get("ok"):
                message_id = res_json["result"]["message_id"]
                print(f"✅ Telegram Message Sent Successfully (ID: {message_id})")
                
                if pin:
                    pin_url = f"https://api.telegram.org/bot{token}/pinChatMessage"
                    pin_payload = {"chat_id": chat_id, "message_id": message_id, "disable_notification": False}
                    pin_data = json.dumps(pin_payload).encode('utf-8')
                    pin_req = urllib.request.Request(pin_url, data=pin_data, headers={'Content-Type': 'application/json'})
                    with urllib.request.urlopen(pin_req, timeout=10) as pin_res:
                        pin_json = json.loads(pin_res.read().decode('utf-8'))
                        if pin_json.get("ok"):
                            print(f"📌 Telegram Message Successfully Pinned!")
                return True
            else:
                print(f"❌ Telegram API Error: {res_json}")
                return False
    except Exception as e:
        print(f"❌ Failed to send Telegram message: {e}")
        return False

def format_master_strategy_catalog():
    """Formats the official Master Strategy Guide to be pinned in Telegram."""
    msg = (
        f"📌 *MASTER QUANTITATIVE STRATEGY GUIDE*\n"
        f"🤖 *Dhan 24/7 Automated Trade Tracker*\n"
        f"🌐 *Fly.io Live Web Dashboard:* [View Active & Historical Signals]({DASHBOARD_URL})\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"⚡ *Core Risk Model:* `3 : 1` (+3R Take Profit / -1R Stop Loss)\n"
        f"⚖️ *Position Size:* `1% Risk per Trade` ($1,000 Risk = 1R)\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        f"🟢 *Strategy 1: Bullish OB + FVG Confluence*\n"
        f"├ 🎯 Logic: Order Block support + Fair Value Gap imbalance fill\n"
        f"└ 📊 Win Rate: `95.25%` | Expectancy: `+2.60 R` per trade\n\n"
        
        f"🟢 *Strategy 2: Liquidity Sweep + Displacement*\n"
        f"├ 🎯 Logic: 20-Day low liquidity sweep + Institutional displacement\n"
        f"└ 📊 Win Rate: `36.75%` | Expectancy: `+0.14 R` per trade\n\n"
        
        f"🟢 *Strategy 3: Volume Spike + OB Breakout*\n"
        f"├ 🎯 Logic: 2.0x Volume expansion + Order Block breakout\n"
        f"└ 📊 Win Rate: `87.73%` | Expectancy: `+2.25 R` per trade\n\n"
        
        f"🟢 *Strategy 4: ATR Compression Expansion*\n"
        f"├ 🎯 Logic: Volatility squeeze compression + ATR expansion breakout\n"
        f"└ 📊 Win Rate: `33.15%` | Expectancy: `+0.08 R` per trade\n\n"
        
        f"🟢 *Strategy 5: Displacement + FVG Pullback*\n"
        f"├ 🎯 Logic: Smart Money displacement push + FVG pullback entry\n"
        f"└ 📊 Win Rate: `39.99%` | Expectancy: `+0.26 R` per trade\n\n"
        
        f"🔴 *Strategy 6: Short High Liquidity Sweep*\n"
        f"├ 🎯 Logic: 20-Day high sweep + Bearish Order Block reversal\n"
        f"└ 📊 Win Rate: `85.71%` | Expectancy: `+2.27 R` per trade\n\n"
        
        f"⭐ *Strategy 7: SMC Super Signal (OB+FVG+Disp)*\n"
        f"├ 🎯 Logic: Triple confluence of Order Block + FVG + Displacement\n"
        f"└ 📊 Win Rate: `100.00%` | Expectancy: `+2.98 R` per trade\n\n"
        
        f"🟢 *Strategy 8: Volume Exhaustion at 20D Low*\n"
        f"├ 🎯 Logic: Seller capitulation + high volume reversal at key support\n"
        f"└ 📊 Win Rate: `41.18%` | Expectancy: `+0.21 R` per trade\n\n"
        
        f"🟢 *Strategy 9: Momentum + OB Support*\n"
        f"├ 🎯 Logic: High momentum impulse + Order Block base defense\n"
        f"└ 📊 Win Rate: `95.06%` | Expectancy: `+2.49 R` per trade\n\n"
        
        f"🟢 *Strategy 10: Target3D Level + SMC Hybrid*\n"
        f"├ 🎯 Logic: Proprietary Target3D level breakout + Order Block\n"
        f"└ 📊 Win Rate: `88.24%` | Expectancy: `+2.27 R` per trade\n\n"
        
        f"🚀 *Strategy 11: Positional Volume & OI Build-Up Breakout*\n"
        f"├ 🎯 Logic: Institutional Volume spike + Open Interest build-up\n"
        f"└ 📊 Win Rate: `87.10%` | Expectancy: `+2.20 R` per trade\n\n"
        
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🌐 *Fly.io Live Web Dashboard:* {DASHBOARD_URL}"
    )
    return msg

def format_new_trade_alert(trade):
    """Formats a rich markdown alert for a new elite trade setup."""
    direction_emoji = "🟢 LONG" if trade['direction'] == 'LONG' else "🔴 SHORT"
    msg = (
        f"🚀 *ELITE TRADE SIGNAL DETECTED*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📌 *Symbol:* `{trade['symbol']}`\n"
        f"📈 *Direction:* {direction_emoji}\n"
        f"🎯 *Strategy:* {trade['strategy']}\n"
        f"⏰ *Activated At:* `{trade.get('entry_date', 'LIVE')}`\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 *Entry Price:* `{trade['entry_price']}`\n"
        f"💲 *Today Open Price:* `{trade.get('current_price', trade['entry_price'])}`\n"
        f"🛑 *Stop Loss (-1R):* `{trade['sl_price']}`\n"
        f"🎁 *Take Profit (+3R):* `{trade['tp_price']}`\n"
        f"📊 *Risk/Reward:* `3 : 1` (+3R Target)\n"
        f"⚖️ *Position Size:* `{trade['position_size']}` shares ($1,000 Risk)\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🌐 *Fly.io Live Web Dashboard:* [View All Trades]({DASHBOARD_URL})\n"
        f"🤖 *Automated 24/7 Dhan Trade Tracker*"
    )
    return msg

def format_trade_exit_alert(trade):
    """Formats a markdown alert when a trade hits Stop Loss (-1R) or Take Profit (+3R), displaying days to target."""
    status = trade['status']
    status_emoji = "🎉 TARGET HIT (+3R)" if "TARGET_HIT" in status else "🛑 STOP LOSS HIT (-1R)"
    holding_days = trade.get('holding_days', 1)
    
    msg = (
        f"📢 *TRADE EXIT NOTIFICATION*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📌 *Symbol:* `{trade['symbol']}`\n"
        f"🏁 *Status:* {status_emoji}\n"
        f"🎯 *Strategy:* {trade['strategy']}\n"
        f"⏱️ *Days to Achieve Target:* `{holding_days} Days`\n"
        f"⏰ *Activated Date:* `{trade.get('entry_date', 'N/A')}`\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 *Entry Price:* `{trade['entry_price']}`\n"
        f"🚪 *Exit Price:* `{trade['exit_price']}`\n"
        f"📈 *Final Yield:* `{trade['unrealized_r']} R`\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🌐 *Fly.io Historical Signals:* [View Closed Trades]({DASHBOARD_URL})\n"
        f"🤖 *Automated 24/7 Dhan Trade Tracker*"
    )
    return msg

def send_all_active_signals_to_telegram(active_trades, perf_summary=None):
    """Formats and sends STRICTLY ACTIVE stock trade signals + Performance Metrics to Telegram."""
    open_active_trades = {k: v for k, v in active_trades.items() if v.get('status') == 'ACTIVE'}
    trade_items = list(open_active_trades.items())
    total_trades = len(trade_items)
    date_str = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    if perf_summary:
        summary_header = (
            f"📈 *PORTFOLIO PERFORMANCE & STRICTLY OPEN SIGNALS*\n"
            f"📅 *Timestamp:* `{date_str}`\n"
            f"🌐 *Fly.io Web Dashboard:* [View Active & Historical Signals]({DASHBOARD_URL})\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🎯 *Strategy Accuracy:* `{perf_summary['accuracy_pct']}%`\n"
            f"⏱️ *Avg Days to Target:* `{perf_summary.get('avg_days_to_target', 3.5)} Days`\n"
            f"🟢 *Booked Profit (+3R Hits):* `+{perf_summary['booked_profit_r']} R` (`+${perf_summary['booked_profit_amt']:,.2f}`)\n"
            f"🛑 *Booked Loss (-1R Hits):* `-{perf_summary['booked_loss_r']} R` (`-${perf_summary['booked_loss_amt']:,.2f}`)\n"
            f"📈 *Current Open Profit:* `{perf_summary['unrealized_r']:+.2f} R` (`{perf_summary['unrealized_pct']:+.2f}%`)\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🔢 *Trade Counts:* Open Positions: `{perf_summary['active_count']}` | Target Hits: `{perf_summary['win_count']}` | Stop Hits: `{perf_summary['loss_count']}`\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🌐 *Fly.io Dashboard URL:* {DASHBOARD_URL}\n"
            f"🤖 *Automated 24/7 Dhan Trade Tracker*"
        )
        send_telegram_message(summary_header)
        
    if total_trades == 0:
        return

    chunk_size = 15
    total_parts = (total_trades + chunk_size - 1) // chunk_size

    for part_idx in range(total_parts):
        start_i = part_idx * chunk_size
        end_i = min((part_idx + 1) * chunk_size, total_trades)
        chunk = trade_items[start_i:end_i]
        
        msg = (
            f"📊 *STRICTLY OPEN ACTIVE SIGNALS (Part {part_idx + 1}/{total_parts})*\n"
            f"⚡ *Showing Open Stocks {start_i + 1} to {end_i} of {total_trades}*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
        )
        
        for idx, (t_id, trade) in enumerate(chunk):
            item_num = start_i + idx + 1
            direction_emoji = "🟢 LONG" if trade['direction'] == 'LONG' else "🔴 SHORT"
            pct = trade.get('est_profit_pct', 0.0)
            strat_clean = str(trade['strategy']).replace('*', '').replace('_', ' ')
            
            msg += (
                f"`{item_num}.` *{trade['symbol']}* ({direction_emoji})\n"
                f"   ├ 🎯 `{strat_clean}`\n"
                f"   ├ ⏰ Activated: `{trade.get('entry_date', 'LIVE')}`\n"
                f"   ├ 💰 Entry: `{trade['entry_price']}` | Today Open: `{trade.get('current_price', trade['entry_price'])}`\n"
                f"   └ 📊 Est: `{pct:+.2f}%` ({trade.get('unrealized_r', 0.0):+.2f}R) | SL: `{trade['sl_price']}` | TP: `{trade['tp_price']}`\n\n"
            )
            
        msg += f"━━━━━━━━━━━━━━━━━━━━━━\n🌐 *Fly.io Live Web Dashboard:* {DASHBOARD_URL}\n🤖 *Automated 24/7 Dhan Trade Tracker*"
        send_telegram_message(msg)

if __name__ == "__main__":
    catalog_msg = format_master_strategy_catalog()
    send_telegram_message(catalog_msg, pin=True)
