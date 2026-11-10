// app.js — Plan B poller + basic screens
const hash = location.hash.slice(1);
const params = new URLSearchParams(hash);
let DATA_PATH = params.get("d") || localStorage.getItem("DATA_PATH");
if (DATA_PATH) localStorage.setItem("DATA_PATH", DATA_PATH);

async function loadState() {
  if (!DATA_PATH) {
    document.getElementById("app").innerHTML = "<p>Missing #d= path</p>";
    return;
  }
  try {
    const r = await fetch(`d/${DATA_PATH}/state.json`);
    const s = await r.json();
    document.getElementById("app").innerHTML = `
      <div style="display:flex;justify-content:space-between;align-items:center;">
        <div>Grok Bot ›</div>
        <div class="paper-badge">PAPER</div>
      </div>
      <div class="odometer">$${s.balance.toFixed(2)}</div>
      <div style="color:var(--secondary)">${s.today_pct >= 0 ? "+" : ""}${s.today_pct.toFixed(2)}% today</div>
      <div class="card">Agents · 5 running</div>
      <div class="card">Activity · See all</div>
      <div class="tabbar">
        <div class="tab active">Home</div>
        <div class="tab">Agents</div>
        <div class="tab">Activity</div>
        <div class="tab">Account</div>
      </div>
    `;
  } catch (e) {
    document.getElementById("app").innerHTML = `<div style="color:var(--red)">Desk offline · retrying…</div>`;
  }
}
setInterval(loadState, 15000);
loadState();
