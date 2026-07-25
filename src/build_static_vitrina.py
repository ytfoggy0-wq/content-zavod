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
    --bg: #f0eee9;
    --surface: #ffffff;
    --surface-2: #e7e4dc;
    --ink: #14171a;
    --ink-dim: #5b6266;
    --line: rgba(20,23,26,0.14);
    --accent: #d9530a;
    --accent-ink: #ffffff;
  }
  @media (prefers-color-scheme: dark) {
    :root {
      --bg: #0b0d0f;
      --surface: #14181c;
      --surface-2: #1b2025;
      --ink: #eef1f0;
      --ink-dim: #93a0a6;
      --line: rgba(238,241,240,0.12);
      --accent: #ff6a2c;
      --accent-ink: #17110b;
    }
  }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    background: var(--bg);
    color: var(--ink);
    font-family: -apple-system, "Segoe UI", Roboto, Arial, sans-serif;
    font-size: 15px;
  }
  .mono { font-family: ui-monospace, "Cascadia Mono", Consolas, monospace; font-variant-numeric: tabular-nums; }
  .wrap { max-width: 1400px; margin: 0 auto; padding: 2rem 1.5rem 4rem; }
  header {
    display: flex;
    flex-wrap: wrap;
    align-items: baseline;
    justify-content: space-between;
    gap: 1rem;
    margin-bottom: 1.5rem;
  }
  h1 {
    font-family: Bahnschrift, "Arial Narrow", sans-serif;
    font-size: 1.6rem;
    font-weight: 600;
    margin: 0;
  }
  #count { color: var(--ink-dim); font-size: 0.9rem; }

  .controls {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
    align-items: flex-end;
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin-bottom: 1.2rem;
  }
  .control { display: flex; flex-direction: column; gap: 0.35rem; }
  .control label {
    font-size: 0.72rem;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: var(--ink-dim);
    font-family: ui-monospace, monospace;
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
  #accountChecks {
    display: flex;
    flex-wrap: wrap;
    gap: 0.4rem;
    max-width: 640px;
  }
  #accountChecks label {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    font-size: 0.8rem;
    color: var(--ink);
    border: 1px solid var(--line);
    border-radius: 999px;
    padding: 0.2rem 0.6rem 0.2rem 0.4rem;
    cursor: pointer;
  }
  #accountChecks input { cursor: pointer; }
  button#resetBtn, button.pagebtn {
    background: none;
    border: 1px solid var(--line);
    border-radius: 6px;
    padding: 0.45rem 0.9rem;
    color: var(--ink-dim);
    font-size: 0.85rem;
    cursor: pointer;
  }
  button#resetBtn:hover, button.pagebtn:hover:not(:disabled) { color: var(--ink); border-color: var(--ink-dim); }
  button.pagebtn:disabled { opacity: 0.4; cursor: default; }

  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 1rem;
  }
  .card {
    display: flex;
    gap: 1rem;
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 10px;
    padding: 1rem;
  }
  .card .thumb {
    width: 110px;
    min-width: 110px;
    height: 110px;
    border-radius: 8px;
    overflow: hidden;
    background: var(--surface-2);
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--ink-dim);
    font-size: 0.75rem;
    text-align: center;
  }
  .card .thumb img { width: 100%; height: 100%; object-fit: cover; }
  .card .body { flex: 1; min-width: 0; }
  .card h3 { margin: 0 0 0.3rem; font-size: 1rem; font-weight: 600; }
  .card .metrics { color: var(--ink-dim); font-size: 0.82rem; margin-bottom: 0.4rem; }
  .card .metrics .score { color: var(--accent); font-weight: 600; font-family: ui-monospace, monospace; }
  .card .desc { font-size: 0.88rem; margin-bottom: 0.4rem; }
  .card details { font-size: 0.82rem; color: var(--ink-dim); margin-bottom: 0.5rem; }
  .card details summary { cursor: pointer; color: var(--ink); }
  .card a.open-link {
    display: inline-block;
    color: var(--accent);
    text-decoration: none;
    font-size: 0.85rem;
    border: 1px solid var(--line);
    border-radius: 6px;
    padding: 0.3rem 0.7rem;
  }
  .card a.open-link:hover { text-decoration: underline; }
  .pagination { display: flex; align-items: center; gap: 0.8rem; justify-content: center; margin-top: 1.5rem; }
  a:focus-visible, button:focus-visible, input:focus-visible {
    outline: 2px solid var(--accent);
    outline-offset: 2px;
  }
</style>
</head>
<body>
<div class="wrap">
  <header>
    <h1>Контент-завод — витрина</h1>
    <span id="count" class="mono"></span>
  </header>

  <div class="controls">
    <div class="control">
      <label>Мин. score</label>
      <input type="number" id="minScore" step="0.1" value="0" />
    </div>
    <div class="control">
      <label>Аккаунты</label>
      <div id="accountChecks"></div>
    </div>
    <button id="resetBtn">Сбросить фильтры</button>
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

  let activeAccounts = new Set(accounts);
  let page = 1;

  const accountChecksEl = document.getElementById('accountChecks');
  accounts.forEach(a => {
    const label = document.createElement('label');
    const cb = document.createElement('input');
    cb.type = 'checkbox';
    cb.checked = true;
    cb.value = a;
    cb.addEventListener('change', () => {
      if (cb.checked) activeAccounts.add(a); else activeAccounts.delete(a);
      page = 1;
      render();
    });
    label.appendChild(cb);
    label.appendChild(document.createTextNode(a));
    accountChecksEl.appendChild(label);
  });

  document.getElementById('resetBtn').addEventListener('click', () => {
    document.getElementById('minScore').value = 0;
    activeAccounts = new Set(accounts);
    accountChecksEl.querySelectorAll('input').forEach(cb => cb.checked = true);
    page = 1;
    render();
  });

  document.getElementById('minScore').addEventListener('input', () => { page = 1; render(); });
  document.getElementById('prevBtn').addEventListener('click', () => { page -= 1; render(); });
  document.getElementById('nextBtn').addEventListener('click', () => { page += 1; render(); });

  function escapeHtml(s) {
    return (s || '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  }

  function formatDate(iso) {
    if (!iso) return '';
    const datePart = iso.split('T')[0];
    const [y, m, d] = datePart.split('-');
    return `${d}.${m}.${y}`;
  }

  function render() {
    const minScore = parseFloat(document.getElementById('minScore').value) || 0;

    let rows = allData.filter(r => {
      if (!activeAccounts.has(r.username)) return false;
      if ((r.median_score ?? 0) < minScore) return false;
      return true;
    });

    rows.sort((a, b) => {
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
      const scoreText = (score !== null && score !== undefined) ? score.toFixed(2) : '—';
      const viewsText = (r.views ?? null) !== null ? r.views.toLocaleString('ru-RU') : '—';
      const likesText = (r.likes ?? null) !== null ? r.likes.toLocaleString('ru-RU') : '—';
      const dateText = r.posted_at ? ` · ${formatDate(r.posted_at)}` : '';
      const thumb = r.thumbnail_url
        ? `<img src="${r.thumbnail_url}" alt="" loading="lazy" />`
        : 'Превью недоступно';
      const desc = r.video_description || r.caption || '';
      const transcriptBlock = r.transcript
        ? `<details><summary>Транскрибация</summary>${escapeHtml(r.transcript)}</details>`
        : '';

      return `
        <div class="card">
          <div class="thumb">${thumb}</div>
          <div class="body">
            <h3>@${escapeHtml(r.username)}${badge}</h3>
            <div class="metrics">Score <span class="score">${scoreText}</span> · ${viewsText} просмотров · ${likesText} лайков${dateText}</div>
            <div class="desc">${escapeHtml(desc)}</div>
            ${transcriptBlock}
            <a class="open-link" href="${r.reel_url}" target="_blank" rel="noopener">Открыть в Instagram</a>
          </div>
        </div>
      `;
    }).join('');
  }

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
