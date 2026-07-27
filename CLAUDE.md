# content-zavod

Сбор Reels у конкурентов в Instagram, транскрибация и поиск роликов, выстреливших сильнее нормы аккаунта. Подробности — в `README.md`.

## Agent skills

### Issue tracker

Задачи ведутся как markdown-файлы в `.scratch/`. См. `docs/agents/issue-tracker.md`.

### Triage labels

Стандартные пять статусов (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). См. `docs/agents/triage-labels.md`.

### Domain docs

Single-context: `CONTEXT.md` + `docs/adr/` в корне (создаются лениво, по мере необходимости). См. `docs/agents/domain.md`.

## Технические заметки

- **Groq-клиент**: создавай через `Groq(api_key=..., http_client=httpx.Client(trust_env=False))`.
  Без `trust_env=False` httpx подхватывает системный SOCKS-прокси на этой машине и падает
  с `Unknown scheme for proxy URL`. См. `src/tag_topics.py` / `src/generate_ideas.py`.
- **Apify/Groq/Instagram без VPN** — перед `collect_reels.py` и `transcribe_reels.py` нужен
  SOCKS5-прокси (`ALL_PROXY=socks5h://127.0.0.1:10808` и т.д., см. README). Без него —
  `dns error` / зависание на импорте.
- **Groq text-модели**: `tag_topics.py` и `generate_ideas.py` используют РАЗНЫЕ модели
  (`llama-3.3-70b-versatile` и `llama-3.1-8b-instant`) специально, чтобы не делить одну
  дневную квоту токенов (100k TPD легко исчерпывается на ~200 роликах).
