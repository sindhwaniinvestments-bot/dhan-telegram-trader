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

def format_daily_digest_alert(active_trades):
    """Formats a daily 9:00 AM summary briefing of all active signals with Activation Date & Current Price."""
    trade_count = len(active_trades)
    date_str = datetime.now().strftime('%Y-%m-%d')
    
    msg = (
        f"☀️ *DAILY 9:00 AM ACTIVE SIGNALS DIGEST*\n"
        f"📅 *Date:* `{date_str}`\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 *Active Signals Monitored:* `{trade_count}`\n"
        f"⚡ *Target R:R:* `3 : 1` (+3R / -1R)\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
    )
    
    if trade_count == 0:
        msg += "🟢 *No active setups open. Waiting for market open entries.*"
    else:
        for idx, (t_id, trade) in enumerate(list(active_trades.items())[:10]):
            direction_emoji = "🟢 LONG" if trade['direction'] == 'LONG' else "🔴 SHORT"
            msg += (
                f"`{idx+1}.` *{trade['symbol']}* ({direction_emoji})\n"
                f"   ├ ⏰ Activated: `{trade.get('entry_date', 'LIVE')}`\n"
                f"   └ Entry: `{trade['entry_price']}` | Curr: `{trade.get('current_price', trade['entry_price'])}` | SL: `{trade['sl_price']}` | TP: `{trade['tp_price']}`\n"
            )
            
        if trade_count > 10:
            msg += f"\n... and `{trade_count - 10}` more active signals tracked."
            
    msg += "\n━━━━━━━━━━━━━━━━━━━━━━\n🤖 *Automated 24/7 Dhan Trade Tracker*"
    return msg
