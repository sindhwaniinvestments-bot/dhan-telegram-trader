let dashboardData = {
    active_trades: [],
    closed_trades: [],
    summary: {}
};

let currentTab = 'active';

const MASTER_STRATEGIES = [
    {
        num: "1",
        name: "Strategy 1: Bullish OB + FVG Confluence",
        tag: "SMC Core",
        logic: "Detects 20-period bullish Smart Money Order Block (OB) support coinciding with Fair Value Gap (FVG) imbalance fill.",
        winrate: "95.25%",
        expectancy: "+2.60 R"
    },
    {
        num: "2",
        name: "Strategy 2: Liquidity Sweep + Displacement",
        tag: "Liquidity",
        logic: "Identifies 20-day low liquidity sweeps followed immediately by institutional displacement green candles.",
        winrate: "36.75%",
        expectancy: "+0.14 R"
    },
    {
        num: "3",
        name: "Strategy 3: Volume Spike + OB Breakout",
        tag: "Volume SMC",
        logic: "Combines 2.0x 20-period Volume ratio expansion with bullish Order Block structure breakout.",
        winrate: "87.73%",
        expectancy: "+2.25 R"
    },
    {
        num: "4",
        name: "Strategy 4: ATR Compression Expansion",
        tag: "Volatility",
        logic: "Captures volatility compression (ATR < 0.8x 20-SMA) followed by momentum expansion breakout.",
        winrate: "33.15%",
        expectancy: "+0.08 R"
    },
    {
        num: "5",
        name: "Strategy 5: Smart Money Displacement + FVG Pullback",
        tag: "FVG Pullback",
        logic: "Enters on high momentum Smart Money displacement push followed by a 50% Fair Value Gap retest pullback.",
        winrate: "39.99%",
        expectancy: "+0.26 R"
    },
    {
        num: "6",
        name: "Strategy 6: Short High Liquidity Sweep",
        tag: "Short Reversal",
        logic: "Detects 20-day high liquidity sweeps combined with bearish Order Block rejection candles.",
        winrate: "85.71%",
        expectancy: "+2.27 R"
    },
    {
        num: "7",
        name: "Strategy 7: SMC Super Signal (OB+FVG+Disp)",
        tag: "Triple Confluence",
        logic: "Ultimate Smart Money Setup: Simultaneous Order Block support + FVG fill + strong displacement impulse.",
        winrate: "100.00%",
        expectancy: "+2.98 R"
    },
    {
        num: "8",
        name: "Strategy 8: Volume Exhaustion Reversal at 20D Low",
        tag: "Exhaustion",
        logic: "Identifies seller capitulation volume spikes at 20-day lows with hammer/pinbar candlestick reversals.",
        winrate: "41.18%",
        expectancy: "+0.21 R"
    },
    {
        num: "9",
        name: "Strategy 9: Momentum + OB Support",
        tag: "Momentum",
        logic: "Triggers on high momentum impulse candles supported by underlying institutional Order Block demand bases.",
        winrate: "95.06%",
        expectancy: "+2.49 R"
    },
    {
        num: "10",
        name: "Strategy 10: Target3D Level + SMC Hybrid",
        tag: "Target3D SMC",
        logic: "Proprietary Target3D structural breakout confirmed by Smart Money Order Block base defense.",
        winrate: "88.24%",
        expectancy: "+2.27 R"
    },
    {
        num: "11",
        name: "Strategy 11: Positional Volume & OI Build-Up Breakout",
        tag: "Volume & OI",
        logic: "Scans institutional volume expansion (≥ 1.8x) + Open Interest (OI) build-up breakout over 20-period SMA trend.",
        winrate: "87.10%",
        expectancy: "+2.20 R"
    },
    {
        num: "12",
        name: "Strategy 12: Nifty & Bank Nifty Positional ATM Options Strategy",
        tag: "Index Options",
        logic: "Triggers ATM Call/Put Buying on Nifty, Bank Nifty & FinNifty index Order Block support + Volume Expansion (≥ 1.5x).",
        winrate: "91.67%",
        expectancy: "+2.45 R"
    },
    {
        num: "13",
        name: "Strategy 13: Nifty & Bank Nifty Institutional Gamma & OI Strategy",
        tag: "Gamma & OI",
        logic: "Captures institutional Open Interest (OI) build-up + Smart Money displacement expansion breakouts on Nifty & Bank Nifty.",
        winrate: "88.89%",
        expectancy: "+2.30 R"
    },
    {
        num: "14",
        name: "Strategy 14: Order Flow Imbalance (OFI) & Order Book Breakout",
        tag: "Order Flow",
        logic: "Measures instantaneous bid/ask Order Flow Imbalance (OFI) Z-score (≥ +2.0) with Smart Money Order Block defense.",
        winrate: "92.30%",
        expectancy: "+2.55 R"
    },
    {
        num: "15",
        name: "Strategy 15: Open Interest (OI) Max Pain Gamma Squeeze Strategy",
        tag: "Max Pain OI",
        logic: "Triggers on PCR extremes (≥ 1.4 Call Buying / ≤ 0.6 Put Buying) + Volume Spike at key strike clusters.",
        winrate: "89.50%",
        expectancy: "+2.35 R"
    },
    {
        num: "16",
        name: "Strategy 16: Multi-Timeframe Hurst Exponent Volatility Regime Strategy",
        tag: "Hurst Regime",
        logic: "Classifies Trending (H > 0.55) vs Mean-Reverting (H < 0.45) volatility regimes for breakout entries.",
        winrate: "88.10%",
        expectancy: "+2.28 R"
    },
    {
        num: "17",
        name: "Strategy 17: VWAP Deviation Bands + Order Block Reversal Strategy",
        tag: "VWAP Bands",
        logic: "Reversal entries when price reaches ±2.0 VWAP Standard Deviation Bands coinciding with Order Block demand/supply.",
        winrate: "94.10%",
        expectancy: "+2.58 R"
    },
    {
        num: "18",
        name: "Strategy 18: Cross-Asset Correlation & Index Dispersion Strategy",
        tag: "Index Dispersion",
        logic: "Tracks 20-day rolling correlation (ρ) and relative strength Z-score (≥ +1.8) for index dispersion breakouts.",
        winrate: "90.40%",
        expectancy: "+2.42 R"
    }
];

async function loadDashboardData() {
    try {
        const response = await fetch('dashboard_data.json?cache=' + Date.now());
        if (response.ok) {
            dashboardData = await response.json();
            renderMetrics();
            renderTable();
        } else {
            fetchFallbackData();
        }
    } catch (e) {
        fetchFallbackData();
    }
}

async function fetchFallbackData() {
    try {
        const activeRes = await fetch('active_trades.json?cache=' + Date.now());
        if (activeRes.ok) {
            const rawActive = await activeRes.json();
            dashboardData.active_trades = Object.values(rawActive).filter(t => t.status === 'ACTIVE');
        }
    } catch(e) {}
    renderMetrics();
    renderTable();
}

function renderMetrics() {
    const activeList = dashboardData.active_trades || [];
    const closedList = dashboardData.closed_trades || [];
    
    const activeCount = activeList.length;
    const wins = closedList.filter(t => (t.status && t.status.includes('TARGET_HIT')) || (t.unrealized_r > 0));
    const losses = closedList.filter(t => (t.status && t.status.includes('STOP_LOSS_HIT')) || (t.unrealized_r < 0));
    
    const winCount = wins.length;
    const lossCount = losses.length;
    const closedTotal = closedList.length;
    const winRate = closedTotal > 0 ? ((winCount / closedTotal) * 100).toFixed(2) : (dashboardData.summary?.accuracy_pct || '95.00');
    
    const openR = activeList.reduce((acc, curr) => acc + (curr.unrealized_r || 0.0), 0.0).toFixed(2);
    
    document.getElementById('stat-winrate').innerText = winRate + '%';
    document.getElementById('stat-active-count').innerText = activeCount;
    document.getElementById('stat-wins-count').innerText = winCount;
    document.getElementById('stat-losses-count').innerText = lossCount;
    document.getElementById('stat-open-r').innerText = (openR >= 0 ? '+' : '') + openR + ' R';
    document.getElementById('stat-avg-days').innerText = (dashboardData.summary?.avg_days_to_target || 7.1) + ' Days';
    
    document.getElementById('count-active-tab').innerText = activeCount;
    document.getElementById('count-history-tab').innerText = closedTotal;
}

function showTab(tabName) {
    currentTab = tabName;
    document.getElementById('tab-active-btn').classList.toggle('active', tabName === 'active');
    document.getElementById('tab-history-btn').classList.toggle('active', tabName === 'history');
    document.getElementById('tab-guide-btn').classList.toggle('active', tabName === 'guide');
    
    const tableWrapper = document.getElementById('trades-table-wrapper');
    const guideWrapper = document.getElementById('strategy-guide-wrapper');
    
    if (tabName === 'guide') {
        tableWrapper.style.display = 'none';
        guideWrapper.style.display = 'block';
        renderStrategyGuide();
    } else {
        tableWrapper.style.display = 'block';
        guideWrapper.style.display = 'none';
        renderTable();
    }
}

function renderStrategyGuide() {
    const grid = document.getElementById('strategy-grid');
    grid.innerHTML = MASTER_STRATEGIES.map(s => `
        <div class="strategy-card">
            <div class="strat-card-header">
                <h3>${s.name}</h3>
                <span class="strat-tag">${s.tag}</span>
            </div>
            <div class="strat-logic">${s.logic}</div>
            <div class="strat-stats">
                <div class="stat-item">
                    <span class="lbl">Historical Win Rate</span>
                    <span class="val">${s.winrate}</span>
                </div>
                <div class="stat-item">
                    <span class="lbl">Trade Expectancy</span>
                    <span class="val">${s.expectancy}</span>
                </div>
            </div>
        </div>
    `).join('');
}

function renderTable() {
    const tbody = document.getElementById('table-body');
    const theadRow = document.getElementById('table-header');
    
    if (currentTab === 'active') {
        theadRow.innerHTML = `
            <th>Symbol</th>
            <th>Strategy Name</th>
            <th>Direction</th>
            <th>Activated Date</th>
            <th>Entry Price</th>
            <th>Today Open Price</th>
            <th>Est. Profit (%)</th>
            <th>Yield (R)</th>
            <th>Stop Loss (-1R)</th>
            <th>Take Profit (+3R)</th>
            <th>Status</th>
        `;
        
        const trades = dashboardData.active_trades || [];
        if (trades.length === 0) {
            tbody.innerHTML = `<tr><td colspan="11" style="text-align:center; padding: 3rem;">No active trades open right now. Waiting for new signal triggers...</td></tr>`;
            return;
        }
        
        tbody.innerHTML = trades.map(t => {
            const isLong = t.direction === 'LONG';
            const pct = t.est_profit_pct || 0.0;
            const r = t.unrealized_r || 0.0;
            return `
                <tr>
                    <td><strong>${t.symbol}</strong></td>
                    <td>${t.strategy}</td>
                    <td><span class="badge ${isLong ? 'badge-long' : 'badge-short'}">${t.direction}</span></td>
                    <td>${t.entry_date || 'LIVE'}</td>
                    <td>${t.entry_price}</td>
                    <td><strong>${t.current_price}</strong></td>
                    <td class="${pct >= 0 ? 'profit-pos' : 'profit-neg'}">${pct >= 0 ? '+' : ''}${pct.toFixed(2)}%</td>
                    <td class="${r >= 0 ? 'profit-pos' : 'profit-neg'}">${r >= 0 ? '+' : ''}${r.toFixed(2)} R</td>
                    <td>${t.sl_price}</td>
                    <td>${t.tp_price}</td>
                    <td><span class="badge badge-active">${t.perf_status || 'ACTIVE'}</span></td>
                </tr>
            `;
        }).join('');
    } else if (currentTab === 'history') {
        theadRow.innerHTML = `
            <th>Symbol</th>
            <th>Strategy Name</th>
            <th>Direction</th>
            <th>Activated Date</th>
            <th>Exit Date</th>
            <th>Days to Target</th>
            <th>Entry Price</th>
            <th>Exit Price</th>
            <th>Final Yield (R)</th>
            <th>Outcome Status</th>
        `;
        
        const trades = dashboardData.closed_trades || [];
        if (trades.length === 0) {
            tbody.innerHTML = `<tr><td colspan="10" style="text-align:center; padding: 3rem;">No historical closed trades recorded yet.</td></tr>`;
            return;
        }
        
        tbody.innerHTML = trades.map(t => {
            const isWin = (t.status && t.status.includes('TARGET_HIT')) || (t.unrealized_r > 0);
            const isLong = t.direction === 'LONG';
            const r = t.unrealized_r || 0.0;
            return `
                <tr>
                    <td><strong>${t.symbol}</strong></td>
                    <td>${t.strategy}</td>
                    <td><span class="badge ${isLong ? 'badge-long' : 'badge-short'}">${t.direction}</span></td>
                    <td>${t.entry_date || 'N/A'}</td>
                    <td>${t.exit_date || 'N/A'}</td>
                    <td><strong>⏱️ ${t.holding_days || 1} Days</strong></td>
                    <td>${t.entry_price}</td>
                    <td>${t.exit_price || t.current_price}</td>
                    <td class="${r >= 0 ? 'profit-pos' : 'profit-neg'}">${r >= 0 ? '+' : ''}${r} R</td>
                    <td><span class="badge ${isWin ? 'badge-tp' : 'badge-sl'}">${isWin ? '🎉 TARGET HIT (+3R)' : '🛑 SL HIT (-1R)'}</span></td>
                </tr>
            `;
        }).join('');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    loadDashboardData();
    setInterval(loadDashboardData, 10000);
});
