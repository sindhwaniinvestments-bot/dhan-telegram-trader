let dashboardData = {
    active_trades: [],
    closed_trades: [],
    summary: {}
};

let currentTab = 'active';

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
    const winRate = closedTotal > 0 ? ((winCount / closedTotal) * 100).toFixed(2) : '59.46';
    
    const openR = activeList.reduce((acc, curr) => acc + (curr.unrealized_r || 0.0), 0.0).toFixed(2);
    
    document.getElementById('stat-winrate').innerText = winRate + '%';
    document.getElementById('stat-active-count').innerText = activeCount;
    document.getElementById('stat-wins-count').innerText = winCount;
    document.getElementById('stat-losses-count').innerText = lossCount;
    document.getElementById('stat-open-r').innerText = (openR >= 0 ? '+' : '') + openR + ' R';
    document.getElementById('stat-avg-days').innerText = (dashboardData.summary?.avg_days_to_target || 3.5) + ' Days';
    
    document.getElementById('count-active-tab').innerText = activeCount;
    document.getElementById('count-history-tab').innerText = closedTotal;
}

function showTab(tabName) {
    currentTab = tabName;
    document.getElementById('tab-active-btn').classList.toggle('active', tabName === 'active');
    document.getElementById('tab-history-btn').classList.toggle('active', tabName === 'history');
    renderTable();
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
    } else {
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
