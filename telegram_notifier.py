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

def send_telegram_message(message_text):
    """Sends a formatted markdown message to the configured Telegram Chat / Channel."""
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
                print(f"✅ Telegram Alert Sent Successfully to Chat ID: {chat_id}")
                return True
            else:
                print(f"❌ Telegram API Error: {res_json}")
                return False
    except Exception as e:
        print(f"❌ Failed to send Telegram message: {e}")
        return False

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
        f"⏰ *Exit Date:* `{trade.get('exit_date', 'LIVE')}`\n"
        f"🤖 *Automated 24/7 Dhan Trade Tracker*"
    )
    return msg

def send_all_active_signals_to_telegram(active_trades, perf_summary=None):
    """Formats and sends STRICTLY ACTIVE stock trade signals + Performance Metrics to Telegram (excluding closed SL/TP hit trades)."""
    open_active_trades = {k: v for k, v in active_trades.items() if v.get('status') == 'ACTIVE'}
    trade_items = list(open_active_trades.items())
    total_trades = len(trade_items)
    date_str = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    if perf_summary:
        summary_header = (
            f"📈 *PORTFOLIO PERFORMANCE & STRICTLY OPEN SIGNALS*\n"
            f"📅 *Timestamp:* `{date_str}`\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🎯 *Strategy Accuracy:* `{perf_summary['accuracy_pct']}%`\n"
            f"⏱️ *Avg Days to Target:* `{perf_summary.get('avg_days_to_target', 3.5)} Days`\n"
            f"🟢 *Booked Profit (+3R Hits):* `+{perf_summary['booked_profit_r']} R` (`+${perf_summary['booked_profit_amt']:,.2f}`)\n"
            f"🛑 *Booked Loss (-1R Hits):* `-{perf_summary['booked_loss_r']} R` (`-${perf_summary['booked_loss_amt']:,.2f}`)\n"
            f"📈 *Current Open Profit:* `{perf_summary['unrealized_r']:+.2f} R` (`{perf_summary['unrealized_pct']:+.2f}%`)\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🔢 *Trade Counts:* Open Positions: `{perf_summary['active_count']}` | Target Hits: `{perf_summary['win_count']}` | Stop Hits: `{perf_summary['loss_count']}`\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
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
            
        msg += "━━━━━━━━━━━━━━━━━━━━━━\n🤖 *Automated 24/7 Dhan Trade Tracker*"
        send_telegram_message(msg)
