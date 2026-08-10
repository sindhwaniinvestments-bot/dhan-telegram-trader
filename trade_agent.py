import os
import glob
import json
import pandas as pd
import numpy as np
from datetime import datetime
from data_loader import load_smc_signals
from feature_engine import compute_smc_features, calculate_3to1_rr_levels
from strategy_agent import generate_10_strategies
from telegram_notifier import send_telegram_message, format_new_trade_alert, format_trade_exit_alert

PORTFOLIO_CAPITAL = 100000.0  # $100,000 baseline capital
RISK_PER_TRADE_PCT = 0.01     # 1% risk per trade ($1,000 risk = -1R)

DATA_DIR = r"D:\dhan automation\data"
TRADES_JSON_PATH = r"d:\Monkeycode\github\active_trades.json"
HISTORY_CSV_PATH = r"d:\Monkeycode\github\trade_history.csv"

ELITE_STRATEGIES = {
    'strat_1_ob_fvg_confluence': {
        'name': 'Strategy 1: Bullish OB + FVG Confluence',
        'direction': 'LONG',
        'win_rate': 95.25,
        'ev_r': 2.60
    },
    'strat_3_vol_ob_breakout': {
        'name': 'Strategy 3: Volume Spike + Order Block Breakout',
        'direction': 'LONG',
        'win_rate': 87.73,
        'ev_r': 2.25
    },
    'strat_6_short_liquidity_sweep': {
        'name': 'Strategy 6: Short High Liquidity Sweep',
        'direction': 'SHORT',
        'win_rate': 85.71,
        'ev_r': 2.27
    },
    'strat_7_smc_super_signal': {
        'name': 'Strategy 7: SMC Super Signal (OB+FVG+Disp)',
        'direction': 'LONG',
        'win_rate': 100.00,
        'ev_r': 2.98
    },
    'strat_9_momentum_ob_support': {
        'name': 'Strategy 9: Momentum + OB Support',
        'direction': 'LONG',
        'win_rate': 95.06,
        'ev_r': 2.49
    },
    'strat_10_target3d_smc_hybrid': {
        'name': 'Strategy 10: Target3D Level + SMC Hybrid',
        'direction': 'LONG',
        'win_rate': 88.24,
        'ev_r': 2.27
    }
}

class EliteTradeTrackerAgent:
    def __init__(self, capital=PORTFOLIO_CAPITAL, risk_pct=RISK_PER_TRADE_PCT, enable_telegram=True):
        self.capital = capital
        self.risk_pct = risk_pct
        self.risk_amount = capital * risk_pct
        self.enable_telegram = enable_telegram
        self.active_trades = self._load_active_trades()

    def _load_active_trades(self):
        if os.path.exists(TRADES_JSON_PATH):
            try:
                with open(TRADES_JSON_PATH, 'r') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_active_trades(self):
        with open(TRADES_JSON_PATH, 'w') as f:
            json.dump(self.active_trades, f, indent=4)

    def fetch_live_prices(self):
        """Fetches latest Last Traded Price (ltp) from live tick files in D:\\dhan automation\\data."""
        latest_prices = {}
        tick_files = glob.glob(os.path.join(DATA_DIR, "ticks_*.csv"))
        
        if tick_files:
            latest_file = max(tick_files, key=os.path.getmtime)
            try:
                df_ticks = pd.read_csv(latest_file).tail(5000)
                price_col = None
                for col in ['ltp', 'last_price', 'close']:
                    if col in df_ticks.columns:
                        price_col = col
                        break
                        
                if price_col and 'symbol' in df_ticks.columns:
                    latest = df_ticks.groupby('symbol').last().reset_index()
                    for _, r in latest.iterrows():
                        val = float(r[price_col])
                        if val > 0:
                            latest_prices[r['symbol']] = val
            except Exception as e:
                print(f"Notice: Reading live tick file {os.path.basename(latest_file)}: {e}")

        return latest_prices

    def scan_market_and_track(self, scan_window_bars=100):
        """Scans live & historical data feed, detects Strategy setups, and tracks positions."""
        raw_df = load_smc_signals()
        df = compute_smc_features(raw_df)
        df = calculate_3to1_rr_levels(df)
        df = generate_10_strategies(df)
        
        recent_bars = df.groupby('symbol').tail(scan_window_bars).reset_index()
        new_signals_found = 0
        
        for _, row in recent_bars.iterrows():
            symbol = row['symbol']
            close_price = float(row['close'])
            atr = float(row['atr'])
            bar_date = str(row['day'])[:10]
            
            if pd.isna(atr) or atr <= 0 or close_price <= 0:
                continue
                
            for strat_key, strat_info in ELITE_STRATEGIES.items():
                if row.get(strat_key) == True:
                    trade_id = f"{symbol}_{strat_key}_{bar_date}"
                    
                    if trade_id not in self.active_trades:
                        direction = strat_info['direction']
                        sl_price = round(close_price - (1.0 * atr) if direction == 'LONG' else close_price + (1.0 * atr), 2)
                        tp_price = round(close_price + (3.0 * atr) if direction == 'LONG' else close_price - (3.0 * atr), 2)
                        
                        risk_per_share = abs(close_price - sl_price)
                        position_size = int(self.risk_amount / risk_per_share) if risk_per_share > 0 else 1
                        
                        new_trade = {
                            'trade_id': trade_id,
                            'symbol': symbol,
                            'strategy': strat_info['name'],
                            'direction': direction,
                            'entry_date': bar_date,
                            'entry_price': close_price,
                            'sl_price': sl_price,
                            'tp_price': tp_price,
                            'risk_amount': self.risk_amount,
                            'position_size': position_size,
                            'status': 'ACTIVE',
                            'perf_status': 'ACTIVE',
                            'current_price': close_price,
                            'unrealized_r': 0.0,
                            'est_profit_pct': 0.0,
                            'est_profit_amt': 0.0
                        }
                        
                        self.active_trades[trade_id] = new_trade
                        new_signals_found += 1
                        print(f"⚡ NEW TRADE SIGNAL: [{symbol}] | Strategy: {strat_info['name']} | Entry: {close_price}")
                        
                        if self.enable_telegram:
                            msg = format_new_trade_alert(new_trade)
                            send_telegram_message(msg)

        self._save_active_trades()
        return self.active_trades

    def evaluate_open_positions(self, live_prices=None):
        """Evaluates active trades against live ltp prices, calculating Estimated Profit % & R-Yield."""
        if live_prices is None:
            live_prices = self.fetch_live_prices()
            
        closed_trades = []
        
        for trade_id, trade in list(self.active_trades.items()):
            symbol = trade['symbol']
            direction = trade['direction']
            sl = trade['sl_price']
            tp = trade['tp_price']
            entry = trade['entry_price']
            pos_size = trade.get('position_size', 1)
            
            curr_price = live_prices.get(symbol, trade['current_price'])
            trade['current_price'] = curr_price
            
            atr_dist = abs(entry - sl)
            
            # Calculate Profit % and $
            if direction == 'LONG':
                pnl_per_share = curr_price - entry
                pnl_pct = (pnl_per_share / entry) * 100
            else: # SHORT
                pnl_per_share = entry - curr_price
                pnl_pct = (pnl_per_share / entry) * 100
                
            pnl_amt = pnl_per_share * pos_size
            unrealized_r = round(pnl_per_share / atr_dist, 2) if atr_dist > 0 else 0.0
            
            trade['unrealized_r'] = unrealized_r
            trade['est_profit_pct'] = round(pnl_pct, 2)
            trade['est_profit_amt'] = round(pnl_amt, 2)
            
            # Performance Status Logic
            status = 'ACTIVE'
            perf_status = f"ACTIVE ({pnl_pct:+.2f}% | {unrealized_r:+.2f}R)"
            
            if direction == 'LONG':
                if curr_price >= tp:
                    status = 'TARGET_HIT (+3R)'
                    perf_status = 'TP HIT (+3.00 R)'
                elif curr_price <= sl:
                    status = 'STOP_LOSS_HIT (-1R)'
                    perf_status = 'SL HIT (-1.00 R)'
            else: # SHORT
                if curr_price <= tp:
                    status = 'TARGET_HIT (+3R)'
                    perf_status = 'TP HIT (+3.00 R)'
                elif curr_price >= sl:
                    status = 'STOP_LOSS_HIT (-1R)'
                    perf_status = 'SL HIT (-1.00 R)'
                    
            trade['perf_status'] = perf_status
            
            if status != 'ACTIVE':
                trade['status'] = status
                trade['exit_price'] = curr_price
                trade['exit_date'] = str(datetime.now())[:10]
                closed_trades.append(trade)
                del self.active_trades[trade_id]
                print(f"🎯 TRADE CLOSED: [{symbol}] | Status: {status} | Final R: {unrealized_r} R")
                
                if self.enable_telegram:
                    msg = format_trade_exit_alert(trade)
                    send_telegram_message(msg)
                
        self._save_active_trades()
        
        if closed_trades:
            self._log_closed_trades(closed_trades)
            
        return self.active_trades

    def _log_closed_trades(self, closed_trades):
        df_closed = pd.DataFrame(closed_trades)
        if os.path.exists(HISTORY_CSV_PATH):
            df_closed.to_csv(HISTORY_CSV_PATH, mode='a', header=False, index=False)
        else:
            df_closed.to_csv(HISTORY_CSV_PATH, index=False)
