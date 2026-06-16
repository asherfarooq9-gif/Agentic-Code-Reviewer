"""Static dashboard HTML served by the API. Fetches /api/* and renders."""
from __future__ import annotations

DASHBOARD_HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Agentic Code Reviewer</title>
<style>
  :root {
    --bg: #0d1117; --panel: #161b22; --line: #21262d;
    --text: #e6edf3; --muted: #8b949e; --accent: #58a6ff;
    --critical:#f85149; --high:#ff7b72; --medium:#d29922; --low:#3fb950; --info:#58a6ff;
  }
  * { box-sizing: border-box; }
  body { margin:0; background:var(--bg); color:var(--text);
    font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; }
  header { padding: 2rem clamp(1rem,5vw,4rem) 1rem; border-bottom:1px solid var(--line); }
  h1 { margin:0; font-size: clamp(1.5rem, 1rem + 2vw, 2.4rem); letter-spacing:-0.02em; }
  header p { color:var(--muted); margin:.4rem 0 0; }
  main { padding: 2rem clamp(1rem,5vw,4rem); display:grid; gap:2rem; }
  .stats { display:grid; grid-template-columns: repeat(auto-fit,minmax(160px,1fr)); gap:1rem; }
  .card { background:var(--panel); border:1px solid var(--line); border-radius:12px; padding:1.2rem 1.4rem; }
  .card .num { font-size:2.2rem; font-weight:700; }
  .card .label { color:var(--muted); font-size:.85rem; text-transform:uppercase; letter-spacing:.05em; }
  .sev-bars { display:flex; flex-direction:column; gap:.5rem; }
  .sev-row { display:grid; grid-template-columns: 90px 1fr 40px; align-items:center; gap:.6rem; }
  .bar { height:10px; border-radius:6px; background:var(--accent); min-width:4px; }
  table { width:100%; border-collapse:collapse; }
  th, td { text-align:left; padding:.7rem .6rem; border-bottom:1px solid var(--line); font-size:.92rem; }
  th { color:var(--muted); font-weight:600; }
  .pill { font-size:.72rem; padding:.15rem .55rem; border-radius:999px; border:1px solid var(--line); }
  .status-completed { color:var(--low); } .status-failed { color:var(--critical); }
  .status-running, .status-pending { color:var(--medium); }
  a { color:var(--accent); text-decoration:none; }
  .empty { color:var(--muted); }
</style>
</head>
<body>
<header>
  <h1>Agentic Code Reviewer</h1>
  <p>Local-model PR review dashboard — reviews, findings, and severity mix.</p>
</header>
<main>
  <section class="stats" id="stats"></section>
  <section class="card">
    <div class="label" style="margin-bottom:.8rem">Findings by severity</div>
    <div class="sev-bars" id="sev"></div>
  </section>
  <section class="card">
    <div class="label" style="margin-bottom:.8rem">Recent reviews</div>
    <table>
      <thead><tr><th>#</th><th>Repo</th><th>PR</th><th>Status</th><th>Findings</th><th>Tokens</th><th>When</th></tr></thead>
      <tbody id="reviews"><tr><td colspan="7" class="empty">Loading…</td></tr></tbody>
    </table>
  </section>
</main>
<script>
const SEV = ["critical","high","medium","low","info"];
const COLOR = {critical:"#f85149",high:"#ff7b72",medium:"#d29922",low:"#3fb950",info:"#58a6ff"};

async function load() {
  const [stats, reviews] = await Promise.all([
    fetch("/api/stats").then(r => r.json()),
    fetch("/api/reviews").then(r => r.json()),
  ]);

  document.getElementById("stats").innerHTML = `
    <div class="card"><div class="num">${stats.total_reviews}</div><div class="label">Reviews</div></div>
    <div class="card"><div class="num">${stats.total_findings}</div><div class="label">Findings</div></div>
    <div class="card"><div class="num">${(stats.by_severity.critical||0)+(stats.by_severity.high||0)}</div><div class="label">Critical + High</div></div>`;

  const max = Math.max(1, ...SEV.map(s => stats.by_severity[s]||0));
  document.getElementById("sev").innerHTML = SEV.map(s => {
    const n = stats.by_severity[s]||0;
    return `<div class="sev-row"><span style="text-transform:capitalize">${s}</span>
      <div class="bar" style="width:${(n/max*100).toFixed(0)}%;background:${COLOR[s]}"></div>
      <span>${n}</span></div>`;
  }).join("");

  const rows = reviews.reviews;
  document.getElementById("reviews").innerHTML = rows.length ? rows.map(r => `
    <tr>
      <td>${r.id}</td>
      <td>${r.repo}</td>
      <td><a href="${r.pr_url}" target="_blank" rel="noopener">#${r.pr_number}</a></td>
      <td class="status-${r.status}"><span class="pill status-${r.status}">${r.status}</span></td>
      <td>${r.findings_count}</td>
      <td>${r.input_tokens}/${r.output_tokens}</td>
      <td>${(r.created_at||"").slice(0,19).replace("T"," ")}</td>
    </tr>`).join("") : '<tr><td colspan="7" class="empty">No reviews yet.</td></tr>';
}
load().catch(e => {
  document.getElementById("reviews").innerHTML =
    '<tr><td colspan="7" class="empty">Failed to load.</td></tr>';
});
</script>
</body>
</html>"""
