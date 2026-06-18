"""Dashboard HTML served by the API."""
from __future__ import annotations

DASHBOARD_HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Agentic Code Reviewer</title>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
<link href="https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,400;0,500;0,600;0,700;0,800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet"/>
<style>
:root{
  --bg:        #EEF2F7;
  --surface:   #FFFFFF;
  --surface2:  #F8FAFC;
  --border:    #E2E8F0;
  --border2:   #CBD5E1;
  --text:      #0F172A;
  --text2:     #334155;
  --muted:     #64748B;
  --accent:    #6366F1;
  --accent2:   #4F46E5;
  --accent-bg: #EEF2FF;
  --critical:  #DC2626;
  --crit-bg:   #FEF2F2;
  --crit-bdr:  #FECACA;
  --high:      #C2410C;
  --high-bg:   #FFF7ED;
  --high-bdr:  #FED7AA;
  --medium:    #B45309;
  --med-bg:    #FFFBEB;
  --med-bdr:   #FDE68A;
  --low:       #15803D;
  --low-bg:    #F0FDF4;
  --low-bdr:   #BBF7D0;
  --info:      #0369A1;
  --info-bg:   #F0F9FF;
  --info-bdr:  #BAE6FD;
  --shadow-sm: 0 1px 3px rgba(15,23,42,.06),0 1px 2px rgba(15,23,42,.04);
  --shadow:    0 4px 16px rgba(15,23,42,.07),0 2px 4px rgba(15,23,42,.04);
  --shadow-lg: 0 10px 30px rgba(15,23,42,.1),0 4px 8px rgba(15,23,42,.05);
  --radius:    10px;
  --radius-lg: 14px;
}
*,::before,::after{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth;-webkit-font-smoothing:antialiased}
body{
  background:var(--bg);color:var(--text);
  font-family:'Inter',ui-sans-serif,system-ui,sans-serif;
  font-size:14px;line-height:1.6;min-height:100vh;
}

/* Top accent bar */
body::before{
  content:'';position:fixed;top:0;left:0;right:0;height:3px;z-index:999;
  background:linear-gradient(90deg,#6366f1 0%,#8b5cf6 40%,#a855f7 70%,#6366f1 100%);
  background-size:200% 100%;animation:gradient-slide 5s linear infinite;
}
@keyframes gradient-slide{0%{background-position:0}100%{background-position:200%}}

/* Header */
header{
  background:rgba(255,255,255,.92);
  backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);
  border-bottom:1px solid var(--border);
  padding:0 clamp(1rem,5vw,3rem);
  margin-top:3px;
  display:flex;align-items:center;justify-content:space-between;gap:1rem;
  height:56px;position:sticky;top:3px;z-index:50;
}
.brand{display:flex;align-items:center;gap:.75rem}
.logo{
  width:32px;height:32px;border-radius:9px;flex-shrink:0;
  background:linear-gradient(135deg,#6366f1,#8b5cf6);
  display:flex;align-items:center;justify-content:center;
  box-shadow:0 2px 8px rgba(99,102,241,.35),0 0 0 1px rgba(99,102,241,.2);
}
.logo svg{width:15px;height:15px;stroke:#fff;fill:none;stroke-width:2.5;stroke-linecap:round;stroke-linejoin:round}
.brand-info h1{font-size:.9rem;font-weight:700;letter-spacing:-.025em;color:var(--text);line-height:1.2}
.brand-info p{font-size:.7rem;color:var(--muted);margin-top:.05rem}
.header-right{display:flex;align-items:center;gap:.65rem}
.live-badge{
  display:flex;align-items:center;gap:.38rem;font-size:.7rem;font-weight:600;
  color:var(--low);background:var(--low-bg);
  padding:.28rem .7rem;border-radius:999px;border:1px solid var(--low-bdr);
}
.live-dot{width:6px;height:6px;border-radius:50%;background:var(--low);animation:pulse 2s ease infinite}
@keyframes pulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.35;transform:scale(.8)}}
#refresh-label{font-size:.7rem;color:var(--muted);font-variant-numeric:tabular-nums}

/* Layout */
main{
  padding:2.5rem clamp(1rem,5vw,3rem);
  display:flex;flex-direction:column;gap:1.5rem;
  max-width:1440px;width:100%;margin:0 auto;
}

/* Stat cards */
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:1rem}
.stat{
  background:var(--surface);border:1px solid var(--border);
  border-radius:var(--radius-lg);padding:1.4rem 1.5rem;
  box-shadow:var(--shadow-sm);
  transition:box-shadow .2s,transform .2s,border-color .2s;
  cursor:default;position:relative;overflow:hidden;
}
.stat::after{
  content:'';position:absolute;top:0;left:0;right:0;height:3px;
  background:var(--s-color,transparent);border-radius:14px 14px 0 0;
}
.stat:hover{box-shadow:var(--shadow);transform:translateY(-2px);border-color:var(--s-color,var(--border2))}
.stat-icon{
  width:38px;height:38px;border-radius:10px;
  background:var(--s-icon-bg,#F8FAFC);
  border:1px solid var(--s-icon-bdr,var(--border));
  display:flex;align-items:center;justify-content:center;margin-bottom:1rem;
}
.stat-icon svg{width:17px;height:17px;fill:none;stroke:var(--s-icon-clr,var(--muted));stroke-width:1.75;stroke-linecap:round;stroke-linejoin:round}
.stat .num{font-size:2.2rem;font-weight:800;letter-spacing:-.06em;line-height:1;color:var(--s-num-clr,var(--text));font-variant-numeric:tabular-nums}
.stat .lbl{font-size:.68rem;color:var(--muted);text-transform:uppercase;letter-spacing:.09em;margin-top:.45rem;font-weight:600}
.s-reviews{--s-color:#6366f1;--s-icon-bg:#EEF2FF;--s-icon-bdr:#C7D2FE;--s-icon-clr:#4F46E5}
.s-findings{--s-color:#8b5cf6;--s-icon-bg:#F5F3FF;--s-icon-bdr:#DDD6FE;--s-icon-clr:#7C3AED}
.s-critical{--s-color:#DC2626;--s-icon-bg:#FEF2F2;--s-icon-bdr:#FECACA;--s-icon-clr:#DC2626;--s-num-clr:#DC2626}
.s-high{--s-color:#EA580C;--s-icon-bg:#FFF7ED;--s-icon-bdr:#FED7AA;--s-icon-clr:#C2410C;--s-num-clr:#C2410C}
.s-low{--s-color:#15803D;--s-icon-bg:#F0FDF4;--s-icon-bdr:#BBF7D0;--s-icon-clr:#15803D;--s-num-clr:#15803D}

/* Cards */
.card{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius-lg);overflow:hidden;box-shadow:var(--shadow-sm)}
.card-head{
  padding:.9rem 1.4rem;border-bottom:1px solid var(--border);
  display:flex;align-items:center;justify-content:space-between;gap:.5rem;
  background:var(--surface2);
}
.card-head h2{font-size:.68rem;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:var(--muted)}
.card-body{padding:1.4rem}

/* Severity bars */
.sev-grid{display:flex;flex-direction:column;gap:.9rem}
.sev-row{display:grid;grid-template-columns:72px 1fr 90px;align-items:center;gap:1rem}
.sev-label{font-size:.73rem;font-weight:600;text-transform:capitalize;font-family:'JetBrains Mono',monospace}
.bar-track{height:8px;border-radius:999px;background:var(--border);overflow:hidden}
.bar-fill{height:100%;border-radius:999px;width:0;transition:width 1s cubic-bezier(.4,0,.2,1)}
.sev-meta{display:flex;align-items:center;justify-content:flex-end;gap:.4rem}
.sev-count{font-size:.77rem;font-weight:700;font-variant-numeric:tabular-nums;font-family:'JetBrains Mono',monospace}
.sev-pct{font-size:.67rem;color:var(--muted);font-variant-numeric:tabular-nums;font-family:'JetBrains Mono',monospace}
.c-critical{color:var(--critical)}.c-high{color:var(--high)}.c-medium{color:var(--medium)}.c-low{color:var(--low)}.c-info{color:var(--info)}
.b-critical{background:linear-gradient(90deg,#B91C1C,#EF4444)}
.b-high{background:linear-gradient(90deg,#9A3412,#F97316)}
.b-medium{background:linear-gradient(90deg,#92400E,#F59E0B)}
.b-low{background:linear-gradient(90deg,#14532D,#22C55E)}
.b-info{background:linear-gradient(90deg,#075985,#38BDF8)}

/* Table */
.tbl-wrap{overflow-x:auto}
table{width:100%;border-collapse:collapse}
thead th{
  padding:.65rem 1rem;text-align:left;
  font-size:.64rem;font-weight:700;text-transform:uppercase;letter-spacing:.1em;
  color:var(--muted);border-bottom:1px solid var(--border);white-space:nowrap;
  background:var(--surface2);
}
tbody tr.review-row{cursor:pointer;transition:background .1s}
tbody tr.review-row:hover{background:#F5F7FF}
tbody tr.review-row.expanded{background:#EEF2FF}
tbody td{
  padding:.75rem 1rem;font-size:.84rem;
  border-bottom:1px solid var(--border);vertical-align:middle;
  color:var(--text2);
}
tbody tr:last-child td{border-bottom:none}
tr.findings-row td{padding:0;border-bottom:1px solid var(--border)}
.findings-inner{display:none;background:var(--surface2)}
.findings-inner.open{display:block;animation:open .18s ease}
@keyframes open{from{opacity:0;transform:translateY(-4px)}to{opacity:1;transform:none}}
.findings-inner table thead th{background:var(--border);font-size:.62rem}
.findings-inner table tbody td{font-size:.79rem;color:var(--text2)}
.expand-icon{
  display:inline-flex;align-items:center;justify-content:center;
  width:22px;height:22px;border-radius:6px;
  background:var(--border);border:1px solid var(--border2);
  transition:transform .2s,background .15s,border-color .15s;color:var(--muted);
}
.expand-icon svg{width:10px;height:10px;stroke:currentColor;fill:none;stroke-width:2.5;stroke-linecap:round;stroke-linejoin:round}
.expanded .expand-icon{transform:rotate(90deg);background:#EEF2FF;border-color:#C7D2FE;color:var(--accent2)}

/* Pills */
.pill{display:inline-flex;align-items:center;padding:.2rem .55rem;border-radius:6px;font-size:.66rem;font-weight:600;letter-spacing:.03em;white-space:nowrap}
.pill-completed{background:var(--low-bg);color:var(--low);border:1px solid var(--low-bdr)}
.pill-failed{background:var(--crit-bg);color:var(--critical);border:1px solid var(--crit-bdr)}
.pill-running{background:var(--med-bg);color:var(--medium);border:1px solid var(--med-bdr)}
.pill-pending{background:var(--accent-bg);color:var(--accent2);border:1px solid #C7D2FE}
.pill-critical{background:var(--crit-bg);color:var(--critical);border:1px solid var(--crit-bdr)}
.pill-high{background:var(--high-bg);color:var(--high);border:1px solid var(--high-bdr)}
.pill-medium{background:var(--med-bg);color:var(--medium);border:1px solid var(--med-bdr)}
.pill-low{background:var(--low-bg);color:var(--low);border:1px solid var(--low-bdr)}
.pill-info{background:var(--info-bg);color:var(--info);border:1px solid var(--info-bdr)}
.pill-bug{background:#F5F3FF;color:#6D28D9;border:1px solid #DDD6FE}
.pill-security{background:var(--crit-bg);color:var(--critical);border:1px solid var(--crit-bdr)}
.pill-performance{background:var(--high-bg);color:var(--high);border:1px solid var(--high-bdr)}
.pill-style{background:var(--info-bg);color:var(--info);border:1px solid var(--info-bdr)}
.pill-running::before{
  content:'';display:inline-block;width:5px;height:5px;border-radius:50%;
  background:currentColor;margin-right:.35rem;animation:pulse 1.2s ease infinite;
}

/* Misc */
a{color:var(--accent2);text-decoration:none;font-weight:500}
a:hover{text-decoration:underline;color:#3730A3}
.empty{color:var(--muted);text-align:center;padding:3.5rem 1rem;font-size:.84rem;line-height:2.2}
.empty code{
  font-family:'JetBrains Mono',ui-monospace,monospace;font-size:.78rem;
  background:var(--accent-bg);padding:.2rem .55rem;border-radius:5px;
  color:var(--accent2);border:1px solid #C7D2FE;
}
.chip{
  font-size:.67rem;padding:.22rem .65rem;border-radius:6px;
  background:var(--accent-bg);color:var(--accent2);
  border:1px solid #C7D2FE;font-weight:700;font-variant-numeric:tabular-nums;
}
.mono{font-family:'JetBrains Mono',ui-monospace,monospace;font-size:.77rem;color:var(--muted)}
.fw{font-weight:600;color:var(--text)}
.skeleton{
  background:linear-gradient(90deg,#E2E8F0 25%,#EEF2F7 50%,#E2E8F0 75%);
  background-size:200% 100%;animation:shimmer 1.5s infinite;border-radius:6px;
}
@keyframes shimmer{0%{background-position:200% 0}100%{background-position:-200% 0}}

/* Toast */
.toast{
  position:fixed;bottom:1.5rem;right:1.5rem;z-index:200;
  background:var(--surface);border:1px solid var(--crit-bdr);
  color:var(--critical);padding:.8rem 1.1rem;
  border-radius:var(--radius);font-size:.8rem;
  box-shadow:var(--shadow-lg);max-width:340px;display:none;
}
.toast.show{display:flex;align-items:center;gap:.6rem;animation:slideup .25s ease}
@keyframes slideup{from{transform:translateY(10px);opacity:0}to{transform:translateY(0);opacity:1}}

/* Responsive */
@media(max-width:640px){
  .stats{grid-template-columns:repeat(2,1fr)}
  .brand-info p{display:none}
}
@media(prefers-reduced-motion:reduce){
  *,::before,::after{animation-duration:.01ms!important;transition-duration:.01ms!important}
}
</style>
</head>
<body>
<header>
  <div class="brand">
    <div class="logo">
      <svg viewBox="0 0 24 24"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>
    </div>
    <div class="brand-info">
      <h1>Agentic Code Reviewer</h1>
      <p>Local-model PR analysis</p>
    </div>
  </div>
  <div class="header-right">
    <span id="refresh-label"></span>
    <div class="live-badge"><span class="live-dot"></span>Live</div>
  </div>
</header>

<main>
  <div class="stats" id="stats">
    <div class="stat s-reviews">
      <div class="stat-icon">
        <svg viewBox="0 0 24 24"><path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2"/><rect x="9" y="3" width="6" height="4" rx="1"/><line x1="9" y1="12" x2="15" y2="12"/><line x1="9" y1="16" x2="12" y2="16"/></svg>
      </div>
      <div class="num skeleton" style="width:60px;height:34px"></div>
      <div class="lbl">Total Reviews</div>
    </div>
    <div class="stat s-findings">
      <div class="stat-icon">
        <svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
      </div>
      <div class="num skeleton" style="width:60px;height:34px"></div>
      <div class="lbl">Total Findings</div>
    </div>
    <div class="stat s-critical">
      <div class="stat-icon">
        <svg viewBox="0 0 24 24"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
      </div>
      <div class="num skeleton" style="width:44px;height:34px"></div>
      <div class="lbl">Critical</div>
    </div>
    <div class="stat s-high">
      <div class="stat-icon">
        <svg viewBox="0 0 24 24"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
      </div>
      <div class="num skeleton" style="width:44px;height:34px"></div>
      <div class="lbl">High</div>
    </div>
    <div class="stat s-low">
      <div class="stat-icon">
        <svg viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg>
      </div>
      <div class="num skeleton" style="width:44px;height:34px"></div>
      <div class="lbl">Low Risk</div>
    </div>
  </div>

  <div class="card">
    <div class="card-head"><h2>Findings by Severity</h2></div>
    <div class="card-body">
      <div class="sev-grid" id="sev">
        <div class="sev-row">
          <span class="sev-label" style="color:var(--muted)">loading</span>
          <div class="bar-track"><div class="bar-fill skeleton" style="width:100%"></div></div>
          <span class="sev-count" style="color:var(--muted)">—</span>
        </div>
      </div>
    </div>
  </div>

  <div class="card">
    <div class="card-head">
      <h2>Recent Reviews</h2>
      <span class="chip" id="review-count">—</span>
    </div>
    <div class="tbl-wrap">
      <table>
        <thead>
          <tr>
            <th style="width:44px"></th>
            <th>#</th>
            <th>Repository</th>
            <th>PR</th>
            <th>Status</th>
            <th>Findings</th>
            <th>Tokens</th>
            <th>Time</th>
          </tr>
        </thead>
        <tbody id="reviews">
          <tr><td colspan="8" class="empty"><div class="skeleton" style="width:200px;height:14px;margin:0 auto"></div></td></tr>
        </tbody>
      </table>
    </div>
  </div>
</main>

<div class="toast" id="toast">
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
  <span id="toast-msg"></span>
</div>

<script>
function esc(s){var d=document.createElement("div");d.appendChild(document.createTextNode(s==null?"":String(s)));return d.innerHTML;}
var SEV=["critical","high","medium","low","info"];

var ICONS={
  reviews:'<div class="stat-icon"><svg viewBox="0 0 24 24" fill="none" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2"/><rect x="9" y="3" width="6" height="4" rx="1"/><line x1="9" y1="12" x2="15" y2="12"/><line x1="9" y1="16" x2="12" y2="16"/></svg></div>',
  findings:'<div class="stat-icon"><svg viewBox="0 0 24 24" fill="none" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg></div>',
  critical:'<div class="stat-icon"><svg viewBox="0 0 24 24" fill="none" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg></div>',
  high:'<div class="stat-icon"><svg viewBox="0 0 24 24" fill="none" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg></div>',
  low:'<div class="stat-icon"><svg viewBox="0 0 24 24" fill="none" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg></div>'
};

var CHEVRON='<span class="expand-icon"><svg viewBox="0 0 24 24"><polyline points="9 18 15 12 9 6"/></svg></span>';

function pill(cls,txt){return '<span class="pill pill-'+cls+'">'+txt+'</span>'}
function timeAgo(iso){
  if(!iso) return "—";
  var d=Date.now()-new Date(iso).getTime(),m=Math.floor(d/60000);
  if(m<1) return "just now";
  if(m<60) return m+"m ago";
  var h=Math.floor(m/60);
  if(h<24) return h+"h ago";
  return Math.floor(h/24)+"d ago";
}
function animateNum(el,target){
  if(!el) return;
  var dur=700,t0=performance.now();
  function step(t){
    var p=Math.min((t-t0)/dur,1),e=1-Math.pow(1-p,3);
    el.textContent=Math.round(e*target);
    if(p<1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}
function showToast(msg){
  document.getElementById("toast-msg").textContent=msg;
  var t=document.getElementById("toast");
  t.classList.add("show");
  setTimeout(function(){t.classList.remove("show")},4500);
}
function loadFindings(id,tbody){
  fetch("/api/reviews/"+id+"/findings")
    .then(function(r){return r.json()})
    .then(function(data){
      var fs=data.findings||[];
      if(!fs.length){
        tbody.innerHTML='<tr><td colspan="5" class="empty" style="padding:1.5rem">No findings recorded for this review.</td></tr>';
        return;
      }
      tbody.innerHTML=fs.map(function(f){
        var cat=(f.category||"info").toLowerCase();
        var sev=(f.severity||"info").toLowerCase();
        return '<tr>'+
          '<td>'+pill(sev,sev)+'</td>'+
          '<td>'+pill(cat,esc(f.category)||"—")+'</td>'+
          '<td class="mono">'+esc(f.file||"—")+(f.line?':<strong style="color:var(--accent2)">'+esc(f.line)+'</strong>':'')+'</td>'+
          '<td style="max-width:380px;white-space:pre-wrap;font-size:.79rem;color:var(--text)">'+esc(f.message||"")+'</td>'+
          '<td style="max-width:280px;white-space:pre-wrap;font-size:.77rem;color:var(--muted)">'+esc(f.suggested_fix||"")+'</td>'+
          '</tr>';
      }).join("");
    })
    .catch(function(){
      tbody.innerHTML='<tr><td colspan="5" class="empty" style="padding:1.5rem">Failed to load findings.</td></tr>';
    });
}
function toggleFindings(id,rowEl){
  var inner=document.getElementById("fi-"+id);
  if(!inner) return;
  var open=inner.classList.contains("open");
  inner.classList.toggle("open",!open);
  rowEl.classList.toggle("expanded",!open);
  if(!open){
    var tb=inner.querySelector("tbody");
    if(tb&&tb.dataset.loaded!=="1"){
      tb.dataset.loaded="1";
      tb.innerHTML='<tr><td colspan="5" class="empty" style="padding:1.2rem"><div class="skeleton" style="width:160px;height:11px;margin:0 auto"></div></td></tr>';
      loadFindings(id,tb);
    }
  }
}
function renderStats(stats){
  var by=stats.by_severity||{};
  document.getElementById("stats").innerHTML=
    '<div class="stat s-reviews">'+ICONS.reviews+'<div class="num" id="s-rev">0</div><div class="lbl">Total Reviews</div></div>'+
    '<div class="stat s-findings">'+ICONS.findings+'<div class="num" id="s-find">0</div><div class="lbl">Total Findings</div></div>'+
    '<div class="stat s-critical">'+ICONS.critical+'<div class="num" id="s-crit">0</div><div class="lbl">Critical</div></div>'+
    '<div class="stat s-high">'+ICONS.high+'<div class="num" id="s-high">0</div><div class="lbl">High</div></div>'+
    '<div class="stat s-low">'+ICONS.low+'<div class="num" id="s-low">0</div><div class="lbl">Low Risk</div></div>';
  animateNum(document.getElementById("s-rev"),stats.total_reviews||0);
  animateNum(document.getElementById("s-find"),stats.total_findings||0);
  animateNum(document.getElementById("s-crit"),by.critical||0);
  animateNum(document.getElementById("s-high"),by.high||0);
  animateNum(document.getElementById("s-low"),by.low||0);
  var mx=Math.max(1,Math.max.apply(null,SEV.map(function(s){return by[s]||0})));
  var total=SEV.reduce(function(a,s){return a+(by[s]||0)},0)||1;
  document.getElementById("sev").innerHTML=SEV.map(function(s){
    var n=by[s]||0,barPct=((n/mx)*100).toFixed(1),sharePct=((n/total)*100).toFixed(0);
    return '<div class="sev-row">'+
      '<span class="sev-label c-'+s+'">'+s+'</span>'+
      '<div class="bar-track"><div class="bar-fill b-'+s+'" data-pct="'+barPct+'"></div></div>'+
      '<div class="sev-meta"><span class="sev-count c-'+s+'">'+n+'</span><span class="sev-pct">'+sharePct+'%</span></div>'+
      '</div>';
  }).join("");
  requestAnimationFrame(function(){
    document.querySelectorAll(".bar-fill[data-pct]").forEach(function(el){el.style.width=el.dataset.pct+"%"});
  });
}
function renderReviews(reviews){
  document.getElementById("review-count").textContent=reviews.length+" reviews";
  if(!reviews.length){
    document.getElementById("reviews").innerHTML=
      '<tr><td colspan="8" class="empty">No reviews yet.<br/>Run <code>uv run arev review --pr &lt;github-url&gt;</code> to get started.</td></tr>';
    return;
  }
  document.getElementById("reviews").innerHTML=reviews.map(function(r){
    var st=(r.status||"pending").toLowerCase();
    var repo=(r.repo||"").split("/").pop();
    var fc=r.findings_count||0;
    var fcClr=fc>10?"var(--critical)":fc>4?"var(--high)":fc>0?"var(--medium)":"var(--muted)";
    var itok=r.input_tokens||0,otok=r.output_tokens||0;
    var tok=(itok>=1000?(itok/1000).toFixed(1)+"k":String(itok))+" / "+(otok>=1000?(otok/1000).toFixed(1)+"k":String(otok));
    return '<tr class="review-row" onclick="toggleFindings('+r.id+',this)">'+
      '<td>'+CHEVRON+'</td>'+
      '<td class="mono">'+r.id+'</td>'+
      '<td><span class="fw">'+(repo||"—")+'</span></td>'+
      '<td><a href="'+(r.pr_url||"#")+'" target="_blank" rel="noopener" onclick="event.stopPropagation()">#'+(r.pr_number||"?")+'</a></td>'+
      '<td>'+pill(st,st)+'</td>'+
      '<td><span style="font-weight:700;color:'+fcClr+'">'+fc+'</span></td>'+
      '<td class="mono">'+tok+'</td>'+
      '<td style="color:var(--muted);font-size:.78rem">'+timeAgo(r.created_at)+'</td>'+
      '</tr>'+
      '<tr class="findings-row"><td colspan="8">'+
        '<div class="findings-inner" id="fi-'+r.id+'">'+
          '<table><thead><tr><th>Severity</th><th>Category</th><th>Location</th><th>Message</th><th>Suggested Fix</th></tr></thead>'+
          '<tbody></tbody></table>'+
        '</div>'+
      '</td></tr>';
  }).join("");
}
function load(){
  Promise.all([
    fetch("/api/stats").then(function(r){if(!r.ok)throw new Error(r.status);return r.json()}),
    fetch("/api/reviews").then(function(r){if(!r.ok)throw new Error(r.status);return r.json()})
  ]).then(function(res){
    renderStats(res[0]);
    renderReviews(res[1].reviews||[]);
    document.getElementById("refresh-label").textContent="Updated "+timeAgo(new Date().toISOString());
  }).catch(function(err){
    showToast("API error — "+err.message);
    document.getElementById("reviews").innerHTML='<tr><td colspan="8" class="empty">Could not reach API. Check server logs.</td></tr>';
    document.getElementById("refresh-label").textContent="Error";
  });
}
var countdown=30;
load();
setInterval(function(){
  countdown--;
  if(countdown<=0){countdown=30;load();return;}
  var lbl=document.getElementById("refresh-label");
  if(lbl&&!lbl.textContent.startsWith("Updated"))
    lbl.textContent="Refresh in "+countdown+"s";
},1000);
setTimeout(function(){
  var lbl=document.getElementById("refresh-label");
  if(lbl&&lbl.textContent==="")lbl.textContent="Refresh in 30s";
},2500);
</script>
</body>
</html>"""
