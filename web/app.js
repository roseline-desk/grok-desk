async function loadState() {
  document.getElementById("app").innerHTML = `
    <div style="display:flex;justify-content:space-between;align-items:center;padding:16px;">
      <div>Grok Bot ›</div>
      <div class="paper-badge">PAPER</div>
    </div>
    <div class="odometer" style="padding:0 16px;">$200.00</div>
    <div style="color:var(--secondary);padding:0 16px;">+0.00% today</div>
    <div class="card">Agents · 5 running</div>
    <div class="card">Activity · Nothing yet tonight</div>
    <div class="tabbar">
      <div class="tab active">Home</div>
      <div class="tab">Agents</div>
      <div class="tab">Activity</div>
      <div class="tab">Account</div>
    </div>
  `;
}
loadState();
