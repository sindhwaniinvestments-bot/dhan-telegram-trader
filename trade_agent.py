import os
import json
import pandas as pd
import numpy as np
from datetime import datetime
from data_loader import load_smc_signals
from feature_engine import compute_smc_features, calculate_3to1_rr_levels
from strategy_agent import generate_10_strategies
from telegram_notifier import (
    send_telegram_message,
    format_new_trade_alert,
    format_trade_exit_alert
)

ACTIVE_TRADES_JSON_PATH = r"d:\Monkeycode\github\active_trades.json"
HISTORY_CSV_PATH = r"d:\Monkeycode\github\trade_history.csv"
DASHBOARD_JSON_PATH = r"d:\Monkeycode\github\dashboard_data.json"

# Filtered Strategies: ONLY High-Accuracy Strategies (>= 50% Win Rate)
ALL_HIGH_ACCURACY_STRATEGIES = {
    'strat_1_ob_fvg_confluence': {'name': 'Strategy 1: Bullish OB + FVG Confluence', 'direction': 'LONG', 'winrate': '88.10%'},
    'strat_3_vol_ob_breakout': {'name': 'Strategy 3: Volume Spike + Order Block Breakout', 'direction': 'LONG', 'winrate': '86.13%'},
    'strat_6_short_liquidity_sweep': {'name': 'Strategy 6: Short High Liquidity Sweep', 'direction': 'SHORT', 'winrate': '92.86%'},
    'strat_7_smc_super_signal': {'name': 'Strategy 7: SMC Super Signal (OB+FVG+Disp)', 'direction': 'LONG', 'winrate': '100.00%'},
    'strat_9_momentum_ob_support': {'name': 'Strategy 9: Momentum + OB Support', 'direction': 'LONG', 'winrate': '91.36%'},
    'strat_10_target3d_smc_hybrid': {'name': 'Strategy 10: Target3D Level + SMC Hybrid', 'direction': 'LONG', 'winrate': '100.00%'},
    'strat_11_positional_vol_oi': {'name': 'Strategy 11: Positional Volume & OI Build-Up Breakout', 'direction': 'LONG', 'winrate': '85.61%'},
    'strat_13_index_gamma_oi_breakout': {'name': 'Strategy 13: Nifty & Bank Nifty Institutional Gamma & OI Strategy', 'direction': 'LONG', 'winrate': '52.17%'},
    'strat_14_ofi_breakout': {'name': 'Strategy 14: Order Flow Imbalance (OFI) & Order Book Breakout', 'direction': 'LONG', 'winrate': '90.57%'},
    'strat_15_oi_gamma_squeeze': {'name': 'Strategy 15: Open Interest (OI) Max Pain Gamma Squeeze Strategy', 'direction': 'LONG', 'winrate': '86.36%'},
    'strat_18_index_dispersion': {'name': 'Strategy 18: Cross-Asset Correlation & Index Dispersion Strategy', 'direction': 'LONG', 'winrate': '96.15%'}
}
ALL_18_STRATEGIES = ALL_HIGH_ACCURACY_STRATEGIES
ALL_11_STRATEGIES = ALL_HIGH_ACCURACY_STRATEGIES

class EliteTradeTrackerAgent:
    """
    Elite Agent tracking strictly HIGH-ACCURACY strategies (>= 50% Win Rate) on F&O Stocks & Indices.
    Strictly evaluates Target (+3R) & Stop Loss (-1R) based on Daily Closing Prices.
    """
    def __init__(self, risk_amount=1000.0, enable_telegram=True):
        self.risk_amount = risk_amount
        self.enable_telegram = enable_telegram
        self.active_trades = self._load_active_trades()

    def _load_active_trades(self):
        if os.path.exists(ACTIVE_TRADES_JSON_PATH):
            try:
                with open(ACTIVE_TRADES_JSON_PATH, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Error loading active_trades.json: {e}")
        return {}

    def _save_active_trades(self):
        try:
            with open(ACTIVE_TRADES_JSON_PATH, 'w') as f:
                json.dump(self.active_trades, f, indent=4)
        except Exception as e:
            print(f"⚠️ Error saving active_trades.json: {e}")

    def fetch_latest_closing_prices(self):
        """Fetches the latest daily closing price for every F&O stock and index symbol."""
        raw_df = load_smc_signals(fo_only=True)
        latest_prices = {}
        if not raw_df.empty:
            last_rows = raw_df.groupby('symbol').tail(1)
            for _, row in last_rows.iterrows():
                latest_prices[row['symbol']] = float(row['close'])
        return latest_prices

    def scan_market_and_track(self, scan_window_bars=100):
        """
        Scans HIGH-ACCURACY strategies (>= 50% Win Rate).
        Evaluates every signal against forward daily closing prices.
        If Target (+3R) or Stop Loss (-1R) is hit on closing price, archives to History.
        """
        raw_df = load_smc_signals(fo_only=True)
        df = compute_smc_features(raw_df)
        df = calculate_3to1_rr_levels(df)
        df = generate_10_strategies(df)
        
        # Group by symbol for fast forward scanning
        df_by_sym = {sym: group.sort_values('day') for sym, group in df.groupby('symbol')}
        
        closed_history_ids = set()
        if os.path.exists(HISTORY_CSV_PATH):
            try:
                df_h = pd.read_csv(HISTORY_CSV_PATH)
                if 'trade_id' in df_h.columns:
                    closed_history_ids = set(df_h['trade_id'].astype(str))
            except Exception:
                pass
                
        new_active_trades = {}
        new_closed_trades = []
        
        for symbol, sym_df in df_by_sym.items():
            latest_close = float(sym_df.iloc[-1]['close'])
            recent_sym_df = sym_df.tail(scan_window_bars)
            
            for _, row in recent_sym_df.iterrows():
                close_price = float(row['close'])
                atr = float(row['atr'])
                bar_date = str(row['day'])[:10]
                
                if pd.isna(atr) or atr <= 0 or close_price <= 0:
                    continue
                    
                for strat_key, strat_info in ALL_HIGH_ACCURACY_STRATEGIES.items():
                    if row.get(strat_key) == True:
                        trade_id = f"{symbol}_{strat_key}_{bar_date}"
                        
                        if trade_id in closed_history_ids:
                            continue
                            
                        direction = strat_info['direction']
                        sl_price = round(close_price - (1.0 * atr) if direction == 'LONG' else close_price + (1.0 * atr), 2)
                        tp_price = round(close_price + (3.0 * atr) if direction == 'LONG' else close_price - (3.0 * atr), 2)
                        
                        risk_per_share = abs(close_price - sl_price)
                        position_size = int(self.risk_amount / risk_per_share) if risk_per_share > 0 else 1
                        
                        # Evaluate forward daily closing prices
                        future_bars = sym_df[sym_df['day'] > bar_date]
                        
                        status = 'ACTIVE'
                        exit_price = latest_close
                        exit_date = bar_date
                        holding_days = 0
                        
                        for _, f_row in future_bars.iterrows():
                            holding_days += 1
                            f_close = float(f_row['close'])
                            f_day = str(f_row['day'])[:10]
                            
                            if direction == 'LONG':
                                if f_close >= tp_price:
                                    status = 'TARGET_HIT (+3R)'
                                    exit_price = f_close
                                    exit_date = f_day
                                    break
                                elif f_close <= sl_price:
                                    status = 'STOP_LOSS_HIT (-1R)'
                                    exit_price = f_close
                                    exit_date = f_day
                                    break
                            else: # SHORT
                                if f_close <= tp_price:
                                    status = 'TARGET_HIT (+3R)'
                                    exit_price = f_close
                                    exit_date = f_day
                                    break
                                elif f_close >= sl_price:
                                    status = 'STOP_LOSS_HIT (-1R)'
                                    exit_price = f_close
                                    exit_date = f_day
                                    break
                                    
                        atr_dist = abs(close_price - sl_price)
                        if direction == 'LONG':
                            pnl_per_share = latest_close - close_price
                        else:
                            pnl_per_share = close_price - latest_close
                            
                        pnl_pct = (pnl_per_share / close_price) * 100
                        pnl_amt = pnl_per_share * position_size
                        unrealized_r = round(pnl_per_share / atr_dist, 2) if atr_dist > 0 else 0.0
                        
                        trade_record = {
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
                            'status': status,
                            'perf_status': f"ACTIVE ({pnl_pct:+.2f}% | {unrealized_r:+.2f}R)" if status == 'ACTIVE' else status,
                            'current_price': latest_close,
                            'unrealized_r': 3.0 if 'TARGET_HIT' in status else (-1.0 if 'STOP_LOSS_HIT' in status else unrealized_r),
                            'est_profit_pct': round(pnl_pct, 2),
                            'est_profit_amt': round(pnl_amt, 2),
                            'exit_price': exit_price,
                            'exit_date': exit_date,
                            'holding_days': max(1, holding_days)
                        }
                        
                        if status == 'ACTIVE':
                            new_active_trades[trade_id] = trade_record
                        else:
                            new_closed_trades.append(trade_record)
                            closed_history_ids.add(trade_id)

        self.active_trades = new_active_trades
        self._save_active_trades()
        
        if new_closed_trades:
            self._log_closed_trades(new_closed_trades)
            
        self.export_dashboard_json()
        return self.active_trades

    def evaluate_open_positions(self, live_prices=None):
        """Re-evaluates existing active trades against latest daily closing prices."""
        return self.scan_market_and_track(scan_window_bars=100)

    def _log_closed_trades(self, closed_trades):
        df_closed = pd.DataFrame(closed_trades)
        if os.path.exists(HISTORY_CSV_PATH):
            df_closed.to_csv(HISTORY_CSV_PATH, mode='a', header=False, index=False)
        else:
            df_closed.to_csv(HISTORY_CSV_PATH, index=False)

    def get_portfolio_performance_summary(self):
        """Computes live portfolio performance summary."""
        closed_trades = []
        if os.path.exists(HISTORY_CSV_PATH):
            try:
                df_h = pd.read_csv(HISTORY_CSV_PATH)
                # Keep ONLY high-accuracy strategies in history
                valid_names = set(s['name'] for s in ALL_HIGH_ACCURACY_STRATEGIES.values())
                df_h = df_h[df_h['strategy'].isin(valid_names)]
                closed_trades = df_h.to_dict('records')
            except Exception:
                pass

        open_trades = [t for t in self.active_trades.values() if t.get('status') == 'ACTIVE']
        active_count = len(open_trades)
        
        unrealized_r = sum(float(t.get('unrealized_r', 0.0)) for t in open_trades)
        unrealized_pct = sum(float(t.get('est_profit_pct', 0.0)) for t in open_trades)
        unrealized_amt = sum(float(t.get('est_profit_amt', 0.0)) for t in open_trades)
        
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

    def export_dashboard_json(self):
        """Exports JSON payload for the Web Application Dashboard."""
        summary = self.get_portfolio_performance_summary()
        
        open_active = [t for t in self.active_trades.values() if t.get('status') == 'ACTIVE']
        
        closed_trades = []
        if os.path.exists(HISTORY_CSV_PATH):
            try:
                df_h = pd.read_csv(HISTORY_CSV_PATH)
                valid_names = set(s['name'] for s in ALL_HIGH_ACCURACY_STRATEGIES.values())
                df_h = df_h[df_h['strategy'].isin(valid_names)]
                df_h = df_h.drop_duplicates(subset=['trade_id'], keep='last')
                closed_trades = df_h.to_dict('records')
            except Exception as e:
                print(f"⚠️ Error reading trade_history.csv: {e}")

        payload = {
            "summary": summary,
            "active_trades": open_active,
            "closed_trades": closed_trades
        }
        
        try:
            with open(DASHBOARD_JSON_PATH, 'w') as f:
                json.dump(payload, f, indent=4)
            print(f"📊 Web Dashboard Data Exported Successfully to {DASHBOARD_JSON_PATH}")
        except Exception as e:
            print(f"❌ Failed to export dashboard_data.json: {e}")

if __name__ == "__main__":
    agent = EliteTradeTrackerAgent(enable_telegram=False)
    agent.scan_market_and_track(scan_window_bars=100)
    agent.export_dashboard_json()
