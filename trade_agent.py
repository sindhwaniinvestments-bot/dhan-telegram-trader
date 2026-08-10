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
    },
    'strat_11_positional_vol_oi': {
        'name': 'Strategy 11: Positional Volume & OI Build-Up Breakout',
        'direction': 'LONG',
        'win_rate': 87.10,
        'ev_r': 2.20
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
                    data = json.load(f)
                    return {k: v for k, v in data.items() if v.get('status') == 'ACTIVE'}
            except Exception:
                return {}
        return {}

    def _save_active_trades(self):
        active_only = {k: v for k, v in self.active_trades.items() if v.get('status') == 'ACTIVE'}
        with open(TRADES_JSON_PATH, 'w') as f:
            json.dump(active_only, f, indent=4)
        self.active_trades = active_only

    def fetch_latest_closing_prices(self):
        """Extracts the latest Daily Closing Price (close) for all symbols from smc_signals.csv."""
        close_prices = {}
        try:
            filepath = os.path.join(DATA_DIR, "smc_signals.csv")
            if os.path.exists(filepath):
                df_tail = pd.read_csv(filepath).tail(5000)
                latest_bars = df_tail.groupby('symbol').last().reset_index()
                for _, row in latest_bars.iterrows():
                    symbol = row['symbol']
                    c_val = float(row['close'])
                    if c_val > 0:
                        close_prices[symbol] = c_val
        except Exception as e:
            print(f"Notice: Extracting daily closing prices: {e}")

        return close_prices

    def fetch_todays_open_prices(self):
        return self.fetch_latest_closing_prices()

    def get_portfolio_performance_summary(self):
        """Calculates Accuracy %, Booked Profit, Booked Loss, Current Open Profit, Trade Counts, and Avg Days to Target."""
        active_list = [t for t in self.active_trades.values() if t.get('status') == 'ACTIVE']
        active_count = len(active_list)
        
        unrealized_r = sum(t.get('unrealized_r', 0.0) for t in active_list)
        unrealized_pct = sum(t.get('est_profit_pct', 0.0) for t in active_list)
        unrealized_amt = sum(t.get('est_profit_amt', 0.0) for t in active_list)
        
        closed_trades = []
        if os.path.exists(HISTORY_CSV_PATH):
            try:
                df_hist = pd.read_csv(HISTORY_CSV_PATH)
                closed_trades = df_hist.to_dict('records')
            except Exception:
                pass
                
        closed_count = len(closed_trades)
        wins = [t for t in closed_trades if 'TARGET_HIT' in str(t.get('status', '')) or float(t.get('unrealized_r', 0.0)) > 0]
        losses = [t for t in closed_trades if 'STOP_LOSS_HIT' in str(t.get('status', '')) or float(t.get('unrealized_r', 0.0)) < 0]
        
        win_count = len(wins)
        loss_count = len(losses)
        accuracy_pct = round((win_count / closed_count * 100), 2) if closed_count > 0 else 0.0
        
        holding_days_list = [int(t.get('holding_days', 1)) for t in wins if 'holding_days' in t and pd.notna(t['holding_days'])]
        avg_days_to_target = round(sum(holding_days_list) / len(holding_days_list), 1) if holding_days_list else 3.5
        
        booked_profit_r = round(sum(float(t.get('unrealized_r', 3.0)) for t in wins), 2)
        booked_loss_r = round(sum(abs(float(t.get('unrealized_r', -1.0))) for t in losses), 2)
        
        booked_profit_amt = round(booked_profit_r * self.risk_amount, 2)
        booked_loss_amt = round(booked_loss_r * self.risk_amount, 2)
        net_realized_amt = booked_profit_amt - booked_loss_amt
        
        return {
            'active_count': active_count,
            'closed_count': closed_count,
            'win_count': win_count,
            'loss_count': loss_count,
            'accuracy_pct': accuracy_pct,
            'avg_days_to_target': avg_days_to_target,
            'booked_profit_r': booked_profit_r,
            'booked_loss_r': booked_loss_r,
            'booked_profit_amt': booked_profit_amt,
            'booked_loss_amt': booked_loss_amt,
            'net_realized_amt': net_realized_amt,
            'unrealized_r': round(unrealized_r, 2),
            'unrealized_pct': round(unrealized_pct, 2),
            'unrealized_amt': round(unrealized_amt, 2)
        }

    def scan_market_and_track(self, scan_window_bars=100):
        """Scans market data feed, detects Strategy setups, and tracks active positions."""
        raw_df = load_smc_signals()
        df = compute_smc_features(raw_df)
        df = calculate_3to1_rr_levels(df)
        df = generate_10_strategies(df)
        
        recent_bars = df.groupby('symbol').tail(scan_window_bars).reset_index()
        latest_close_prices = self.fetch_latest_closing_prices()
        
        closed_ids = set()
        if os.path.exists(HISTORY_CSV_PATH):
            try:
                df_h = pd.read_csv(HISTORY_CSV_PATH)
                if 'trade_id' in df_h.columns:
                    closed_ids = set(df_h['trade_id'].astype(str))
            except Exception:
                pass

        new_signals_found = 0
        
        for _, row in recent_bars.iterrows():
            symbol = row['symbol']
            close_price = float(row['close'])
            latest_close = latest_close_prices.get(symbol, close_price)
            atr = float(row['atr'])
            bar_date = str(row['day'])[:10]
            
            if pd.isna(atr) or atr <= 0 or close_price <= 0:
                continue
                
            for strat_key, strat_info in ELITE_STRATEGIES.items():
                if row.get(strat_key) == True:
                    trade_id = f"{symbol}_{strat_key}_{bar_date}"
                    
                    if trade_id not in self.active_trades and trade_id not in closed_ids:
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
                            'current_price': latest_close,
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
        """
        Evaluates active trades against Daily Closing Prices across forward bars.
        If a trade hits SL or Target based on Closing Price, it is REMOVED from active_trades and recorded in history.
        """
        raw_df = load_smc_signals()
        if live_prices is None:
            live_prices = self.fetch_latest_closing_prices()
            
        closed_trades = []
        
        for trade_id, trade in list(self.active_trades.items()):
            symbol = trade['symbol']
            direction = trade['direction']
            sl = trade['sl_price']
            tp = trade['tp_price']
            entry = trade['entry_price']
            pos_size = trade.get('position_size', 1)
            entry_date_str = trade.get('entry_date', '')
            
            # Fetch forward bars for this symbol after entry_date
            sym_df = raw_df[(raw_df['symbol'] == symbol) & (raw_df['day'] > entry_date_str)].sort_values('day')
            
            status = 'ACTIVE'
            exit_price = entry
            exit_date = entry_date_str
            holding_days = 0
            
            # Scan forward bars to check closing prices
            for _, f_row in sym_df.iterrows():
                holding_days += 1
                f_close = float(f_row['close'])
                f_day = str(f_row['day'])[:10]
                
                if direction == 'LONG':
                    if f_close >= tp:
                        status = 'TARGET_HIT (+3R)'
                        exit_price = f_close
                        exit_date = f_day
                        break
                    elif f_close <= sl:
                        status = 'STOP_LOSS_HIT (-1R)'
                        exit_price = f_close
                        exit_date = f_day
                        break
                else: # SHORT
                    if f_close <= tp:
                        status = 'TARGET_HIT (+3R)'
                        exit_price = f_close
                        exit_date = f_day
                        break
                    elif f_close >= sl:
                        status = 'STOP_LOSS_HIT (-1R)'
                        exit_price = f_close
                        exit_date = f_day
                        break
                        
            # If trade has not hit SL or TP, evaluate current status based on latest closing price
            curr_price = live_prices.get(symbol, trade['current_price'])
            trade['current_price'] = curr_price
            atr_dist = abs(entry - sl)
            
            if direction == 'LONG':
                pnl_per_share = curr_price - entry
            else:
                pnl_per_share = entry - curr_price
                
            pnl_pct = (pnl_per_share / entry) * 100
            pnl_amt = pnl_per_share * pos_size
            unrealized_r = round(pnl_per_share / atr_dist, 2) if atr_dist > 0 else 0.0
            
            trade['unrealized_r'] = unrealized_r
            trade['est_profit_pct'] = round(pnl_pct, 2)
            trade['est_profit_amt'] = round(pnl_amt, 2)
            trade['perf_status'] = f"ACTIVE ({pnl_pct:+.2f}% | {unrealized_r:+.2f}R)"
            
            # IF SL OR TARGET HIT BASED ON DAILY CLOSING PRICE -> REMOVE FROM ACTIVE TRADES
            if status != 'ACTIVE':
                trade['status'] = status
                trade['exit_price'] = exit_price
                trade['exit_date'] = exit_date
                trade['holding_days'] = holding_days if holding_days > 0 else 1
                trade['unrealized_r'] = 3.0 if 'TARGET_HIT' in status else -1.0
                
                closed_trades.append(trade)
                # REMOVE FROM ACTIVE TRADES IMMEDIATELY
                del self.active_trades[trade_id]
                print(f"🎯 TRADE CLOSED & REMOVED (Closing Price): [{symbol}] | Status: {status} | Took: {trade['holding_days']} days")
                
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
