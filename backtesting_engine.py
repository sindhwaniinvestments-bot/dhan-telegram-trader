import pandas as pd
import numpy as np

def backtest_3to1_strategy(df, signal_col, direction='long', holding_period=10, slippage_pct=0.0005):
    """
    Vectorized and Forward-Scanning Backtester for 3:1 Risk-to-Reward Ratio.
    - Win (+3R): Price reaches Take-Profit before Stop-Loss within holding period.
    - Loss (-1R): Price hits Stop-Loss first within holding period.
    - Neutral: Exit at market price at holding period end if neither hit.
    """
    signals = df[df[signal_col] == True].copy()
    if len(signals) == 0:
        return {
            'total_trades': 0, 'win_rate': 0.0, 'profit_factor': 0.0,
            'ev_r': 0.0, 'total_r': 0.0, 'max_drawdown_r': 0.0
        }
    
    trade_results = []
    
    for idx, row in signals.iterrows():
        symbol = row['symbol']
        entry_price = row['close']
        atr = row['atr']
        if pd.isna(atr) or atr <= 0:
            continue
            
        sl_dist = 1.0 * atr
        tp_dist = 3.0 * atr
        
        if direction == 'long':
            sl_price = entry_price - sl_dist
            tp_price = entry_price + tp_dist
        else:
            sl_price = entry_price + sl_dist
            tp_price = entry_price - tp_dist
            
        # Scan forward bars in the same symbol
        future_bars = df[(df['symbol'] == symbol) & (df.index > idx)].head(holding_period)
        
        outcome_r = 0.0
        hit = False
        
        for f_idx, f_row in future_bars.iterrows():
            f_high = f_row['high']
            f_low = f_row['low']
            f_close = f_row['close']
            
            if direction == 'long':
                # Check TP hit first (optimistic) or SL hit (pessimistic)
                if f_high >= tp_price and f_low <= sl_price:
                    # Both hit in same bar -> assume loss for safety
                    outcome_r = -1.0 - (slippage_pct * entry_price / atr)
                    hit = True
                    break
                elif f_high >= tp_price:
                    outcome_r = +3.0 - (slippage_pct * entry_price / atr)
                    hit = True
                    break
                elif f_low <= sl_price:
                    outcome_r = -1.0 - (slippage_pct * entry_price / atr)
                    hit = True
                    break
            else: # short
                if f_low <= tp_price and f_high >= sl_price:
                    outcome_r = -1.0 - (slippage_pct * entry_price / atr)
                    hit = True
                    break
                elif f_low <= tp_price:
                    outcome_r = +3.0 - (slippage_pct * entry_price / atr)
                    hit = True
                    break
                elif f_high >= sl_price:
                    outcome_r = -1.0 - (slippage_pct * entry_price / atr)
                    hit = True
                    break
                    
        if not hit and len(future_bars) > 0:
            # Market exit at end of window
            last_close = future_bars.iloc[-1]['close']
            if direction == 'long':
                pnl = last_close - entry_price
            else:
                pnl = entry_price - last_close
            outcome_r = pnl / atr
            
        trade_results.append(outcome_r)
        
    if len(trade_results) == 0:
        return {'total_trades': 0, 'win_rate': 0.0, 'profit_factor': 0.0, 'ev_r': 0.0, 'total_r': 0.0, 'max_drawdown_r': 0.0}

    results = np.array(trade_results)
    wins = results[results > 0]
    losses = results[results < 0]
    
    total_trades = len(results)
    win_rate = (len(wins) / total_trades) * 100
    total_r = results.sum()
    ev_r = results.mean()
    
    gross_win = wins.sum() if len(wins) > 0 else 0.0
    gross_loss = abs(losses.sum()) if len(losses) > 0 else 1e-6
    profit_factor = gross_win / gross_loss
    
    # Calculate Max Drawdown in R units
    cum_r = np.cumsum(results)
    peak = np.maximum.accumulate(cum_r)
    drawdown = peak - cum_r
    max_dd = drawdown.max() if len(drawdown) > 0 else 0.0
    
    return {
        'total_trades': total_trades,
        'win_rate': round(win_rate, 2),
        'profit_factor': round(profit_factor, 2),
        'ev_r': round(ev_r, 2),
        'total_r': round(total_r, 2),
        'max_drawdown_r': round(max_dd, 2)
    }
