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
        f"💲 *Current Price:* `{trade.get('current_price', trade['entry_price'])}`\n"
        f"🛑 *Stop Loss (-1R):* `{trade['sl_price']}`\n"
        f"🎁 *Take Profit (+3R):* `{trade['tp_price']}`\n"
        f"📊 *Risk/Reward:* `3 : 1` (+3R Target)\n"
        f"⚖️ *Position Size:* `{trade['position_size']}` shares ($1,000 Risk)\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🤖 *Automated 24/7 Dhan Trade Tracker*"
    )
    return msg

def format_trade_exit_alert(trade):
    """Formats a markdown alert when a trade hits Stop Loss (-1R) or Take Profit (+3R)."""
    status = trade['status']
    status_emoji = "🎉 TARGET HIT (+3R)" if "TARGET_HIT" in status else "🛑 STOP LOSS HIT (-1R)"
    
    msg = (
        f"📢 *TRADE EXIT NOTIFICATION*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📌 *Symbol:* `{trade['symbol']}`\n"
        f"🏁 *Status:* {status_emoji}\n"
        f"🎯 *Strategy:* {trade['strategy']}\n"
        f"⏰ *Activated At:* `{trade.get('entry_date', 'N/A')}`\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 *Entry Price:* `{trade['entry_price']}`\n"
        f"🚪 *Exit Price:* `{trade['exit_price']}`\n"
        f"📈 *Final Yield:* `{trade['unrealized_r']} R`\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"⏰ *Exit Date:* `{trade.get('exit_date', 'LIVE')}`\n"
        f"🤖 *Automated 24/7 Dhan Trade Tracker*"
    )
    return msg

def send_all_active_signals_to_telegram(active_trades):
    """Formats and sends ALL active stock trade signals to Telegram without truncation."""
    trade_items = list(active_trades.items())
    total_trades = len(trade_items)
    date_str = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    if total_trades == 0:
        msg = f"☀️ *ACTIVE SIGNALS DIGEST* ({date_str})\n━━━━━━━━━━━━━━━━━━━━━━\n🟢 *No active setups open.*"
        send_telegram_message(msg)
        return

    chunk_size = 20
    total_parts = (total_trades + chunk_size - 1) // chunk_size

    for part_idx in range(total_parts):
        start_i = part_idx * chunk_size
        end_i = min((part_idx + 1) * chunk_size, total_trades)
        chunk = trade_items[start_i:end_i]
        
        msg = (
            f"📊 *ACTIVE SIGNALS DIGEST (Part {part_idx + 1}/{total_parts})*\n"
            f"📅 *Timestamp:* `{date_str}`\n"
            f"⚡ *Showing Stocks {start_i + 1} to {end_i} of {total_trades}*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
        )
        
        for idx, (t_id, trade) in enumerate(chunk):
            item_num = start_i + idx + 1
            direction_emoji = "🟢 LONG" if trade['direction'] == 'LONG' else "🔴 SHORT"
            perf = trade.get('perf_status', 'ACTIVE')
            pct = trade.get('est_profit_pct', 0.0)
            
            msg += (
                f"`{item_num}.` *{trade['symbol']}* ({direction_emoji})\n"
                f"   ├ 🎯 `{trade['strategy']}`\n"
                f"   ├ ⏰ Activated: `{trade.get('entry_date', 'LIVE')}`\n"
                f"   ├ 💰 Entry: `{trade['entry_price']}` | Curr: `{trade.get('current_price', trade['entry_price'])}`\n"
                f"   └ 📊 Est: `{pct:+.2f}%` ({trade.get('unrealized_r', 0.0):+.2f}R) | SL: `{trade['sl_price']}` | TP: `{trade['tp_price']}`\n\n"
            )
            
        msg += "━━━━━━━━━━━━━━━━━━━━━━\n🤖 *Automated 24/7 Dhan Trade Tracker*"
        send_telegram_message(msg)

if __name__ == "__main__":
    import json
    active_path = r"d:\Monkeycode\github\active_trades.json"
    if os.path.exists(active_path):
        active = json.load(open(active_path))
        print(f"Sending all {len(active)} active stock signals to Telegram...")
        send_all_active_signals_to_telegram(active)
