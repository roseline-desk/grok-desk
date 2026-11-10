async function refresh() {
  try {
    const r = await fetch("/api/state");
    const s = await r.json();
    document.getElementById("app").innerHTML = `
      <div style="display:flex;justify-content:space-between;align-items:center;padding:16px;">
        <div>Grok Bot ›</div>
        <div class="paper-badge">${s.mode}</div>
      </div>
      <div class="odometer" style="padding:0 16px;">$${s.balance.toFixed(2)}</div>
      <div style="color:var(--secondary);padding:0 16px;">${s.today_pct >= 0 ? "+" : ""}${s.today_pct.toFixed(2)}% today</div>
      <div class="card">Agents · ${s.agents_running} running</div>
      <div class="card">Activity · ${s.activity_count} events tonight</div>
      <div class="tabbar">
        <div class="tab active">Home</div>
        <div class="tab">Agents</div>
        <div class="tab">Activity</div>
        <div class="tab">Account</div>
      </div>
    `;
  } catch (e) {
    document.getElementById("app").innerHTML = `<div style="padding:16px;color:#ff453a">Desk offline</div>`;
  }
}
setInterval(refresh, 10000);
refresh();
