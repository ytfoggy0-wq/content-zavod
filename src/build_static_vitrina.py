import json
from pathlib import Path

DOCS = Path(__file__).parent.parent / "docs"
DATA_FILE = DOCS / "reels_export.json"
OUT_FILES = [DOCS / "vitrina.html", DOCS / "index.html"]

TEMPLATE = """<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Контент-завод — витрина</title>
<style>
  :root {
    --bg: #0a0b12;
    --surface: rgba(255,255,255,0.05);
    --surface-2: rgba(255,255,255,0.08);
    --ink: #f5f5f8;
    --ink-dim: #9aa0b0;
    --line: rgba(255,255,255,0.11);
    --accent: #fb8a4c;
    --accent-2: #f4406e;
    --accent-gradient: linear-gradient(135deg, #fb923c, #f43f5e);
    --accent-ink: #ffffff;
    --accent-soft: rgba(251,138,76,0.14);
    --accent-line: rgba(251,138,76,0.38);
    --glass-blur: blur(18px) saturate(160%);
    --shadow: 0 1px 2px rgba(0,0,0,0.3), 0 2px 10px rgba(0,0,0,0.35);
    --shadow-pop: 0 16px 40px rgba(0,0,0,0.55);
    --shadow-hover: 0 10px 28px rgba(0,0,0,0.5), 0 0 0 1px rgba(251,138,76,0.18), 0 0 36px rgba(244,64,110,0.14);
    --duration-fast: 150ms;
    --duration-normal: 220ms;
    --duration-slow: 380ms;
    --ease: cubic-bezier(0.4, 0, 0.2, 1);
  }
  * { box-sizing: border-box; }
  @media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
      animation-duration: 0.01ms !important;
      animation-iteration-count: 1 !important;
      transition-duration: 0.01ms !important;
      scroll-behavior: auto !important;
    }
  }
  html, body { max-width: 100%; overflow-x: hidden; }
  body {
    margin: 0;
    background: var(--bg);
    color: var(--ink);
    font-family: -apple-system, "Segoe UI", Roboto, Arial, sans-serif;
    font-size: 15px;
    position: relative;
  }
  body::before, body::after {
    content: '';
    position: fixed;
    border-radius: 50%;
    filter: blur(110px);
    z-index: -1;
    pointer-events: none;
  }
  body::before {
    width: 560px; height: 560px;
    background: #fb923c;
    opacity: 0.24;
    top: -180px; left: -140px;
  }
  body::after {
    width: 620px; height: 620px;
    background: #7c3aed;
    opacity: 0.22;
    bottom: -220px; right: -160px;
  }
  .mono { font-family: ui-monospace, "Cascadia Mono", Consolas, monospace; font-variant-numeric: tabular-nums; }
  .wrap { max-width: 1000px; margin: 0 auto; padding: 2.4rem 1.5rem 4rem; }

  header {
    display: flex;
    flex-wrap: wrap;
    align-items: baseline;
    justify-content: space-between;
    gap: 1rem;
    margin-bottom: 0.3rem;
  }
  h1 {
    font-family: Bahnschrift, "Arial Narrow", sans-serif;
    font-size: clamp(1.35rem, 1.1rem + 1.2vw, 1.8rem);
    font-weight: 600;
    margin: 0;
  }
  #count { color: var(--ink-dim); font-size: 0.9rem; }

  .tagline { color: var(--ink-dim); font-size: 0.95rem; margin: 0.2rem 0 0.9rem; }

  details.legend {
    margin-bottom: 1.4rem;
  }
  details.legend summary {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    cursor: pointer;
    color: var(--ink-dim);
    font-size: 0.85rem;
    list-style: none;
  }
  details.legend summary::-webkit-details-marker { display: none; }
  details.legend summary:hover { color: var(--ink); }
  .info-dot {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 15px;
    height: 15px;
    border-radius: 50%;
    background: var(--surface-2);
    color: var(--ink-dim);
    font-size: 0.65rem;
    font-style: italic;
    font-family: Georgia, serif;
  }
  .legend-body {
    color: var(--ink-dim);
    font-size: 0.9rem;
    line-height: 1.55;
    max-width: 720px;
    margin-top: 0.6rem;
    padding: 0.9rem 1.1rem;
    background: var(--surface);
    backdrop-filter: var(--glass-blur);
    -webkit-backdrop-filter: var(--glass-blur);
    border: 1px solid var(--line);
    border-radius: 10px;
  }
  .legend-body strong { color: var(--ink); }

  details.summary-panel { margin-bottom: 1.4rem; }
  details.summary-panel summary {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    cursor: pointer;
    color: var(--ink-dim);
    font-size: 0.85rem;
    list-style: none;
  }
  details.summary-panel summary::-webkit-details-marker { display: none; }
  details.summary-panel summary:hover { color: var(--ink); }
  .accounts-table {
    margin-top: 0.6rem;
    background: var(--surface);
    backdrop-filter: var(--glass-blur);
    -webkit-backdrop-filter: var(--glass-blur);
    border: 1px solid var(--line);
    border-radius: 10px;
    overflow: hidden;
  }
  .accounts-table table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
  .accounts-table th, .accounts-table td {
    text-align: left;
    padding: 0.55rem 0.9rem;
    border-bottom: 1px solid var(--line);
  }
  .accounts-table th {
    color: var(--ink-dim);
    font-size: 0.7rem;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    font-weight: 600;
  }
  .accounts-table tr:last-child td { border-bottom: none; }
  .accounts-table td.num { font-family: ui-monospace, monospace; }

  .controls {
    background: var(--surface);
    backdrop-filter: var(--glass-blur);
    -webkit-backdrop-filter: var(--glass-blur);
    border: 1px solid var(--line);
    border-radius: 14px;
    padding: 1.1rem 1.3rem;
    margin-bottom: 1.4rem;
    box-shadow: var(--shadow);
  }
  .control-group + .control-group {
    margin-top: 0.9rem;
    padding-top: 0.9rem;
    border-top: 1px solid var(--line);
  }
  .group-label {
    font-size: 0.7rem;
    letter-spacing: 0.07em;
    text-transform: uppercase;
    color: var(--ink-dim);
    font-family: ui-monospace, monospace;
    margin-bottom: 0.55rem;
  }
  .group-row {
    display: flex;
    flex-wrap: wrap;
    gap: 1.4rem;
    align-items: flex-end;
  }
  .control { display: flex; flex-direction: column; gap: 0.35rem; }
  .control span.sublabel {
    font-size: 0.72rem;
    color: var(--ink-dim);
  }
  .control input[type="number"] {
    background: var(--bg);
    border: 1px solid var(--line);
    border-radius: 6px;
    padding: 0.45rem 0.6rem;
    color: var(--ink);
    font-size: 0.92rem;
    width: 90px;
  }
  .seg {
    display: flex;
    border: 1px solid var(--line);
    border-radius: 7px;
    overflow-x: auto;
    overflow-y: hidden;
    max-width: 100%;
    scrollbar-width: none;
  }
  .seg::-webkit-scrollbar { display: none; }
  .seg button {
    background: var(--bg);
    border: none;
    border-right: 1px solid var(--line);
    padding: 0.45rem 0.7rem;
    color: var(--ink-dim);
    font-size: 0.84rem;
    cursor: pointer;
    flex: none;
    white-space: nowrap;
    transition: background var(--duration-fast) var(--ease), color var(--duration-fast) var(--ease), transform var(--duration-fast) var(--ease);
  }
  .seg button:active { transform: scale(0.96); }
  .seg button:last-child { border-right: none; }
  .seg button.active { background: var(--accent-gradient); color: var(--accent-ink); font-weight: 600; }
  .seg button:hover:not(.active) { color: var(--ink); }

  details.dropdown { position: relative; }
  details.dropdown summary {
    list-style: none;
    cursor: pointer;
    background: var(--bg);
    border: 1px solid var(--line);
    border-radius: 6px;
    padding: 0.45rem 0.8rem;
    font-size: 0.85rem;
    color: var(--ink);
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
  }
  details.dropdown summary::-webkit-details-marker { display: none; }
  details.dropdown summary::after { content: '▾'; color: var(--ink-dim); font-size: 0.7rem; }
  details.dropdown[open] summary::after { content: '▴'; }
  #accountChecks {
    display: flex;
    flex-wrap: wrap;
    gap: 0.4rem;
    max-width: 560px;
    margin-top: 0.6rem;
    padding: 0.7rem;
    background: var(--bg);
    border: 1px solid var(--line);
    border-radius: 8px;
  }
  #accountChecks label {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    font-size: 0.8rem;
    color: var(--ink);
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 999px;
    padding: 0.2rem 0.6rem 0.2rem 0.4rem;
    cursor: pointer;
  }
  #accountChecks input { cursor: pointer; }
  button#resetBtn {
    background: none;
    border: none;
    color: var(--ink-dim);
    font-size: 0.85rem;
    cursor: pointer;
    text-decoration: underline;
    text-underline-offset: 2px;
    padding: 0.45rem 0;
  }
  button#resetBtn:hover { color: var(--ink); }
  label.fav-toggle {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    font-size: 0.85rem;
    color: var(--ink);
    cursor: pointer;
    padding-bottom: 0.45rem;
  }
  label.fav-toggle input { cursor: pointer; }
  button.pagebtn {
    background: none;
    border: 1px solid var(--line);
    border-radius: 6px;
    padding: 0.45rem 0.9rem;
    color: var(--ink-dim);
    font-size: 0.85rem;
    cursor: pointer;
    transition: color var(--duration-fast) var(--ease), border-color var(--duration-fast) var(--ease), transform var(--duration-fast) var(--ease);
  }
  button.pagebtn:hover:not(:disabled) { color: var(--ink); border-color: var(--ink-dim); }
  button.pagebtn:active:not(:disabled) { transform: scale(0.96); }
  button.pagebtn:disabled { opacity: 0.4; cursor: default; }

  .grid {
    display: flex;
    flex-direction: column;
    gap: 1.1rem;
  }
  @keyframes cardIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
  }
  .card {
    display: flex;
    align-items: stretch;
    gap: 1.2rem;
    background: var(--surface);
    backdrop-filter: var(--glass-blur);
    -webkit-backdrop-filter: var(--glass-blur);
    border: 1px solid var(--line);
    border-radius: 16px;
    padding: 1.1rem;
    box-shadow: var(--shadow);
    animation: cardIn var(--duration-slow) var(--ease) backwards;
    transition: box-shadow var(--duration-normal) var(--ease), transform var(--duration-normal) var(--ease), border-color var(--duration-normal) var(--ease);
  }
  .card:hover { box-shadow: var(--shadow-hover); transform: translateY(-2px); border-color: rgba(251,138,76,0.3); }
  .card:nth-child(1) { animation-delay: 0ms; }
  .card:nth-child(2) { animation-delay: 30ms; }
  .card:nth-child(3) { animation-delay: 60ms; }
  .card:nth-child(4) { animation-delay: 90ms; }
  .card:nth-child(5) { animation-delay: 120ms; }
  .card:nth-child(6) { animation-delay: 150ms; }
  .card:nth-child(7) { animation-delay: 180ms; }
  .card:nth-child(8) { animation-delay: 210ms; }
  .card:nth-child(9) { animation-delay: 240ms; }
  .card:nth-child(10) { animation-delay: 270ms; }
  .card:nth-child(11) { animation-delay: 300ms; }
  .card:nth-child(12) { animation-delay: 330ms; }
  .card .thumb {
    width: 210px;
    min-width: 210px;
    min-height: 240px;
    border-radius: 11px;
    overflow: hidden;
    background: var(--surface-2);
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--ink-dim);
    font-size: 0.75rem;
    text-align: center;
  }
  .card .thumb img { width: 100%; height: 100%; object-fit: cover; object-position: center 12%; display: block; transition: transform var(--duration-slow) var(--ease); }
  .card:hover .thumb img { transform: scale(1.04); }
  .card .body { flex: 1; min-width: 0; max-width: 780px; display: flex; flex-direction: column; }
  .card .headrow {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 0.8rem;
    margin-bottom: 0.5rem;
  }
  .card h3 { margin: 0; font-size: 1.02rem; font-weight: 600; }
  .card .footer-row {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin-top: auto;
  }
  .bookmark-btn {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 7px;
    padding: 0.45rem 0.8rem;
    cursor: pointer;
    font-size: 0.85rem;
    color: var(--ink-dim);
    transition: color var(--duration-fast) var(--ease), border-color var(--duration-fast) var(--ease), background var(--duration-fast) var(--ease), transform var(--duration-fast) var(--ease);
  }
  .bookmark-btn .star { font-size: 1rem; line-height: 1; }
  .bookmark-btn:hover { color: var(--ink); border-color: var(--ink-dim); }
  .bookmark-btn:active { transform: scale(0.96); }
  .bookmark-btn.active {
    color: var(--accent);
    border-color: var(--accent-line);
    background: var(--accent-soft);
  }

  .score-badge {
    position: relative;
    flex: none;
    background: var(--accent-soft);
    border: 1px solid var(--accent-line);
    border-radius: 10px;
    padding: 0.4rem 0.8rem;
    text-align: right;
  }
  .score-badge .score-value {
    font-family: ui-monospace, monospace;
    font-weight: 800;
    font-size: 1.55rem;
    line-height: 1.1;
    background: var(--accent-gradient);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
  }
  details.score-tip summary {
    list-style: none;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;
    font-size: 0.62rem;
    font-weight: 600;
    letter-spacing: 0.03em;
    text-transform: uppercase;
    color: var(--accent);
    opacity: 0.85;
  }
  details.score-tip summary::-webkit-details-marker { display: none; }
  details.score-tip .info-dot { background: var(--accent); color: var(--accent-ink); }
  details.score-tip .tooltip-pop {
    position: absolute;
    top: 100%;
    right: 0;
    margin-top: 0.4rem;
    width: 230px;
    background: #17131f;
    backdrop-filter: var(--glass-blur);
    -webkit-backdrop-filter: var(--glass-blur);
    border: 1px solid var(--line);
    border-radius: 10px;
    box-shadow: var(--shadow-pop);
    padding: 0.75rem 0.85rem;
    font-size: 0.78rem;
    line-height: 1.45;
    color: var(--ink-dim);
    text-align: left;
    z-index: 20;
  }
  .card .topics {
    display: flex;
    flex-wrap: wrap;
    gap: 0.3rem;
    margin-bottom: 0.5rem;
  }
  .card .topics .pill {
    font-size: 0.72rem;
    color: var(--ink-dim);
    background: var(--surface-2);
    border-radius: 999px;
    padding: 0.15rem 0.55rem;
  }
  .card .metrics { color: var(--ink-dim); font-size: 0.82rem; margin-bottom: 0.5rem; }
  .card .idea-box {
    display: flex;
    gap: 0.5rem;
    background: var(--accent-soft);
    border: 1px solid var(--accent-line);
    border-radius: 8px;
    padding: 0.55rem 0.75rem;
    font-size: 0.83rem;
    line-height: 1.45;
    margin-bottom: 0.6rem;
  }
  .card .idea-box .idea-emoji { flex: none; }
  .card .idea-box .idea-text strong { color: var(--ink); }
  .card .desc { font-size: 0.9rem; line-height: 1.5; margin-bottom: 0.5rem; }
  .card details.transcript { font-size: 0.82rem; color: var(--ink-dim); margin-bottom: 0.6rem; }
  .card details.transcript summary { cursor: pointer; color: var(--ink); }
  .card .spacer { flex: 1; }
  .card a.open-link {
    display: inline-block;
    align-self: flex-start;
    background: var(--accent-gradient);
    color: var(--accent-ink);
    text-decoration: none;
    font-size: 0.85rem;
    font-weight: 600;
    border-radius: 7px;
    padding: 0.45rem 0.9rem;
    transition: opacity var(--duration-fast) var(--ease), transform var(--duration-fast) var(--ease);
  }
  .card a.open-link:hover { opacity: 0.9; }
  .card a.open-link:active { transform: scale(0.96); }
  .pagination { display: flex; align-items: center; gap: 0.8rem; justify-content: center; margin-top: 1.5rem; }
  a:focus-visible, button:focus-visible, input:focus-visible {
    outline: 2px solid var(--accent);
    outline-offset: 2px;
    border-radius: 4px;
  }
  @media (max-width: 640px) {
    .wrap { padding: 1.6rem 1rem 3rem; }
    header { gap: 0.3rem 1rem; }
    .controls { padding: 1rem; }
    .group-row { flex-direction: column; align-items: stretch; gap: 0.9rem; }
    .control { width: 100%; }
    .seg { width: 100%; }
    details.dropdown, details.dropdown summary { width: 100%; }
    #accountChecks { max-width: 100%; }
    .card { flex-direction: column; }
    .card .thumb { width: 100%; min-width: 0; min-height: 0; aspect-ratio: 9 / 16; }
    .card .body { max-width: 100%; }
    .headrow { flex-wrap: wrap; }
    .score-badge { text-align: left; }
    details.score-tip .tooltip-pop { right: auto; left: 0; }
    .footer-row { flex-wrap: wrap; }
  }
</style>
</head>
<body>
<div class="wrap">
  <header>
    <h1>Контент-завод — витрина</h1>
    <span id="count" class="mono"></span>
  </header>
  <p class="tagline">Ролики конкурентов, которые выстрелили сильнее обычного для своего аккаунта.</p>

  <details class="legend">
    <summary><span class="info-dot">i</span> Как читать Score</summary>
    <div class="legend-body">
      <strong>Score</strong> показывает, во сколько раз ролик набрал больше просмотров, чем обычно у этого аккаунта.
      Считается как просмотры ролика делить на медиану просмотров его последних (до 20) роликов.
      Score 5 значит — в 5 раз больше обычного для аккаунта: чем выше число, тем сильнее ролик выстрелил на фоне своих же прошлых видео.
    </div>
  </details>

  <details class="summary-panel">
    <summary><span class="info-dot">i</span> Сводка по аккаунтам</summary>
    <div class="accounts-table" id="accountsTable"></div>
  </details>

  <div class="controls">
    <div class="control-group">
      <div class="group-label">Показывать</div>
      <div class="group-row">
        <div class="control">
          <span class="sublabel">Сортировка</span>
          <div class="seg" id="sortSeg">
            <button data-sort="score" class="active">Score</button>
            <button data-sort="views">Просмотры</button>
            <button data-sort="date">Дата</button>
          </div>
        </div>
        <div class="control">
          <span class="sublabel">Период</span>
          <div class="seg" id="periodSeg">
            <button data-period="all" class="active">Всё время</button>
            <button data-period="today">Сегодня</button>
            <button data-period="week">Неделя</button>
            <button data-period="month">Месяц</button>
            <button data-period="year">Год</button>
          </div>
        </div>
      </div>
    </div>

    <div class="control-group">
      <div class="group-label">Фильтры</div>
      <div class="group-row">
        <div class="control">
          <span class="sublabel">Мин. score</span>
          <input type="number" id="minScore" step="0.1" value="0" />
        </div>
        <div class="control">
          <span class="sublabel">Аккаунты</span>
          <details class="dropdown" id="accountsDropdown">
            <summary><span id="accountsSummary"></span></summary>
            <div id="accountChecks"></div>
          </details>
        </div>
        <div class="control">
          <span class="sublabel">&nbsp;</span>
          <label class="fav-toggle"><input type="checkbox" id="favOnly" /> ★ Только избранное</label>
        </div>
        <button id="resetBtn">Сбросить фильтры</button>
      </div>
    </div>
  </div>

  <div class="grid" id="grid"></div>

  <div class="pagination">
    <button class="pagebtn" id="prevBtn">← Назад</button>
    <span id="pageInfo" class="mono"></span>
    <button class="pagebtn" id="nextBtn">Вперёд →</button>
  </div>
</div>

<script id="reels-data" type="application/json">__DATA__</script>
<script>
  const allData = JSON.parse(document.getElementById('reels-data').textContent);
  const accounts = [...new Set(allData.map(r => r.username))].sort();
  const CARDS_PER_PAGE = 12;
  const SCORE_TIP = 'Во сколько раз ролик набрал больше просмотров, чем обычно у этого аккаунта (просмотры делить на медиану последних до 20 роликов).';

  let activeAccounts = new Set(accounts);
  let page = 1;
  let sortMode = 'score';
  let periodMode = 'all';
  let favOnly = false;

  const BOOKMARKS_KEY = 'cz_bookmarks';
  let bookmarks = new Set();
  try {
    bookmarks = new Set(JSON.parse(localStorage.getItem(BOOKMARKS_KEY) || '[]'));
  } catch (e) { bookmarks = new Set(); }

  function saveBookmarks() {
    try { localStorage.setItem(BOOKMARKS_KEY, JSON.stringify([...bookmarks])); } catch (e) {}
  }

  function renderAccountsTable() {
    const rows = accounts.map(a => {
      const reels = allData.filter(r => r.username === a);
      const scores = reels.map(r => r.median_score).filter(v => v !== null && v !== undefined);
      const avg = scores.length ? scores.reduce((s, v) => s + v, 0) / scores.length : null;
      const hits = scores.filter(v => v >= 2).length;
      return { a, count: reels.length, avg, hits };
    }).sort((x, y) => (y.avg ?? -Infinity) - (x.avg ?? -Infinity));

    const table = `
      <table>
        <thead><tr><th>Аккаунт</th><th>Роликов</th><th>Средний score</th><th>Хитов (score ≥ 2)</th></tr></thead>
        <tbody>
          ${rows.map(r => `
            <tr>
              <td>@${escapeHtml(r.a)}</td>
              <td class="num">${r.count}</td>
              <td class="num">${r.avg !== null ? r.avg.toFixed(2) : '—'}</td>
              <td class="num">${r.hits}</td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    `;
    document.getElementById('accountsTable').innerHTML = table;
  }

  function isMusicOnlyTranscript(text) {
    if (!text) return true;
    const cleaned = (text || '').trim();
    if (!cleaned) return true;
    const words = cleaned.match(/\\p{L}+/gu) || [];
    return words.length <= 2;
  }

  document.getElementById('sortSeg').addEventListener('click', (e) => {
    const btn = e.target.closest('button[data-sort]');
    if (!btn) return;
    sortMode = btn.dataset.sort;
    document.querySelectorAll('#sortSeg button').forEach(b => b.classList.toggle('active', b === btn));
    page = 1;
    render();
  });

  document.getElementById('periodSeg').addEventListener('click', (e) => {
    const btn = e.target.closest('button[data-period]');
    if (!btn) return;
    periodMode = btn.dataset.period;
    document.querySelectorAll('#periodSeg button').forEach(b => b.classList.toggle('active', b === btn));
    page = 1;
    render();
  });

  const accountChecksEl = document.getElementById('accountChecks');
  function updateAccountsSummary() {
    document.getElementById('accountsSummary').textContent = `${activeAccounts.size} из ${accounts.length}`;
  }
  accounts.forEach(a => {
    const label = document.createElement('label');
    const cb = document.createElement('input');
    cb.type = 'checkbox';
    cb.checked = true;
    cb.value = a;
    cb.addEventListener('change', () => {
      if (cb.checked) activeAccounts.add(a); else activeAccounts.delete(a);
      updateAccountsSummary();
      page = 1;
      render();
    });
    label.appendChild(cb);
    label.appendChild(document.createTextNode(a));
    accountChecksEl.appendChild(label);
  });
  updateAccountsSummary();

  document.getElementById('resetBtn').addEventListener('click', () => {
    document.getElementById('minScore').value = 0;
    activeAccounts = new Set(accounts);
    accountChecksEl.querySelectorAll('input').forEach(cb => cb.checked = true);
    updateAccountsSummary();
    sortMode = 'score';
    periodMode = 'all';
    document.querySelectorAll('#sortSeg button').forEach(b => b.classList.toggle('active', b.dataset.sort === 'score'));
    document.querySelectorAll('#periodSeg button').forEach(b => b.classList.toggle('active', b.dataset.period === 'all'));
    page = 1;
    render();
  });

  document.getElementById('minScore').addEventListener('input', () => { page = 1; render(); });
  document.getElementById('prevBtn').addEventListener('click', () => { page -= 1; render(); });
  document.getElementById('nextBtn').addEventListener('click', () => { page += 1; render(); });
  document.getElementById('favOnly').addEventListener('change', (e) => { favOnly = e.target.checked; page = 1; render(); });

  document.getElementById('grid').addEventListener('click', (e) => {
    const btn = e.target.closest('.bookmark-btn');
    if (!btn) return;
    const url = btn.dataset.url;
    if (bookmarks.has(url)) bookmarks.delete(url); else bookmarks.add(url);
    saveBookmarks();
    render();
  });

  function escapeHtml(s) {
    return (s || '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  }

  function formatDate(iso) {
    if (!iso) return '';
    const datePart = iso.split('T')[0];
    const [y, m, d] = datePart.split('-');
    return `${d}.${m}.${y}`;
  }

  function periodStartDate(mode) {
    const now = new Date();
    const start = new Date(now);
    if (mode === 'today') {
      start.setHours(0, 0, 0, 0);
    } else if (mode === 'week') {
      start.setDate(start.getDate() - 7);
    } else if (mode === 'month') {
      start.setMonth(start.getMonth() - 1);
    } else if (mode === 'year') {
      start.setFullYear(start.getFullYear() - 1);
    } else {
      return null;
    }
    return start;
  }

  function render() {
    const minScore = parseFloat(document.getElementById('minScore').value) || 0;
    const periodStart = periodStartDate(periodMode);

    let rows = allData.filter(r => {
      if (!activeAccounts.has(r.username)) return false;
      if ((r.median_score ?? 0) < minScore) return false;
      if (favOnly && !bookmarks.has(r.reel_url)) return false;
      if (periodStart) {
        if (!r.posted_at) return false;
        const posted = new Date(r.posted_at);
        if (isNaN(posted) || posted < periodStart) return false;
      }
      return true;
    });

    rows.sort((a, b) => {
      if (sortMode === 'views') {
        const va = a.views ?? -Infinity;
        const vb = b.views ?? -Infinity;
        return vb - va;
      }
      if (sortMode === 'date') {
        const va = a.posted_at ? new Date(a.posted_at).getTime() : -Infinity;
        const vb = b.posted_at ? new Date(b.posted_at).getTime() : -Infinity;
        return vb - va;
      }
      const va = a.median_score ?? -Infinity;
      const vb = b.median_score ?? -Infinity;
      return vb - va;
    });

    const scores = rows.map(r => r.median_score).filter(v => v !== null && v !== undefined).sort((a, b) => a - b);
    const topThreshold = scores.length ? scores[Math.floor(scores.length * 0.9)] : null;

    document.getElementById('count').textContent = `Роликов: ${rows.length} / ${allData.length}`;

    const totalPages = Math.max(1, Math.ceil(rows.length / CARDS_PER_PAGE));
    if (page > totalPages) page = totalPages;
    if (page < 1) page = 1;
    const start = (page - 1) * CARDS_PER_PAGE;
    const pageRows = rows.slice(start, start + CARDS_PER_PAGE);

    document.getElementById('pageInfo').textContent = `Стр. ${page} / ${totalPages}`;
    document.getElementById('prevBtn').disabled = page <= 1;
    document.getElementById('nextBtn').disabled = page >= totalPages;

    const grid = document.getElementById('grid');
    grid.innerHTML = pageRows.map(r => {
      const score = r.median_score;
      const badge = (score !== null && score !== undefined && topThreshold !== null && score >= topThreshold) ? ' 🔥' : '';
      const scoreText = (score !== null && score !== undefined) ? `×${score.toFixed(2)}` : '—';
      const viewsText = (r.views ?? null) !== null ? r.views.toLocaleString('ru-RU') : '—';
      const likesText = (r.likes ?? null) !== null ? r.likes.toLocaleString('ru-RU') : '—';
      const dateText = r.posted_at ? ` · ${formatDate(r.posted_at)}` : '';
      const thumb = r.thumbnail_url
        ? `<img src="${r.thumbnail_url}" alt="" loading="lazy" />`
        : 'Превью недоступно';
      const desc = r.video_description || r.caption || '';
      const hasTranscript = r.transcript && !isMusicOnlyTranscript(r.transcript);
      const transcriptBlock = hasTranscript
        ? `<details class="transcript"><summary>Транскрибация</summary>${escapeHtml(r.transcript)}</details>`
        : '';
      const topicsList = Array.isArray(r.topics) ? r.topics.filter(Boolean) : [];
      const topicsBlock = topicsList.length
        ? `<div class="topics">${topicsList.map(t => `<span class="pill">${escapeHtml(t)}</span>`).join('')}</div>`
        : '';
      const isBookmarked = bookmarks.has(r.reel_url);
      const ideaBlock = r.adaptation_idea
        ? `<div class="idea-box"><span class="idea-emoji">💡</span><span class="idea-text"><strong>Идея для нас:</strong> ${escapeHtml(r.adaptation_idea)}</span></div>`
        : '';

      return `
        <div class="card">
          <div class="thumb">${thumb}</div>
          <div class="body">
            <div class="headrow">
              <h3>@${escapeHtml(r.username)}${badge}</h3>
              <div class="score-badge">
                <details class="score-tip">
                  <summary>к норме <span class="info-dot">i</span></summary>
                  <div class="tooltip-pop">${SCORE_TIP}</div>
                </details>
                <div class="score-value">${scoreText}</div>
              </div>
            </div>
            ${topicsBlock}
            <div class="metrics">${viewsText} просмотров · ${likesText} лайков${dateText}</div>
            <div class="desc">${escapeHtml(desc)}</div>
            ${ideaBlock}
            ${transcriptBlock}
            <div class="spacer"></div>
            <div class="footer-row">
              <a class="open-link" href="${r.reel_url}" target="_blank" rel="noopener">Открыть в Instagram</a>
              <button class="bookmark-btn${isBookmarked ? ' active' : ''}" data-url="${r.reel_url}">
                <span class="star">${isBookmarked ? '★' : '☆'}</span>${isBookmarked ? 'В избранном' : 'В избранное'}
              </button>
            </div>
          </div>
        </div>
      `;
    }).join('');
  }

  renderAccountsTable();
  render();
</script>
</body>
</html>
"""


def main():
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    html = TEMPLATE.replace("__DATA__", json.dumps(data, ensure_ascii=False))
    for out in OUT_FILES:
        out.write_text(html, encoding="utf-8")
        print(f"written {out}")


if __name__ == "__main__":
    main()
