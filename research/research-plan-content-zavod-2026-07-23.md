# План ресёрча: контент-завод (анализ Instagram-конкурентов для портфолио)
Дата: 2026-07-23
Тип: B/C (сравнительный + исследовательский) | Решение: Type 1 (архитектура/стек) | Сложность: средняя

## Бриф по глубине

| | |
|---|---|
| **Хочет пользователь** | Средне (1–1.5 часа) |
| **Рекомендую** | Средне |
| **Обоснование** | Стек и архитектура — решение, которое дорого переделывать (Type 1), но пользователь новичок в коде без готового мнения о стеке, а тема (Instagram-скрапинг + LLM-транскрибация + витрина данных) хорошо покрыта готовыми open-source примерами. Глубокий 2-3 часовой ресёрч избыточен для портфолио-проекта — важнее быстро найти рабочую основу и не написать всё с нуля. |
| **Итоговый режим** | Средне, ~1–1.5 часа, 4-6 этапов, TRAP-подобная структура |

## Исследовательский вопрос (PICO)

P (контекст): Портфолио-проект «контент-завод» — новичок в коде, нужен рабочий MVP, бесплатный/почти бесплатный стек (epify + groq free tier), собирающий рилсы 50 Instagram-конкурентов и показывающий их в сортируемой веб-таблице по метрике «просмотры / медиана просмотров».

I (что изучаем): Готовые open-source решения для Instagram-контент-анализа/competitor-tracking (скрапинг + БД + витрина), возможности и лимиты epify API, лучшие практики LLM-транскрибации через groq free tier, простой стек БД+таблица-веб-интерфейс для новичка.

C (с чем сравниваем): Писать пайплайн с нуля вручную (Instagram scraping libs типа instaloader/apify) vs готовые open-source "content factory" / "reels analyzer" repo; Supabase/Postgres+простой фронт vs no-code (Airtable/Baserow) vs Google Sheets как витрина.

O (что измеряем): Скорость выхода на рабочий MVP, простота для новичка, стоимость (должно остаться бесплатным/почти бесплатным), корректность метрики успешности ролика, доступность данных (не забанят ли аккаунт/API).

T (горизонт): Актуальность 2025–2026 (Instagram API/scraping правила и лимиты быстро меняются, epify — конкретный узкий сервис, важно проверить его текущее состояние).

Итоговый вопрос: В контексте портфолио-MVP с новичком-разработчиком и почти нулевым бюджетом, как лучше собрать систему competitor-анализа Instagram Reels (сбор через epify → транскрибация через groq → БД → сортируемая веб-витрина) — на основе готовых open-source решений, и какой стек для БД+интерфейса самый быстрый в освоении?

## Гипотезы

H1: Есть готовые open-source проекты вида "Instagram Reels scraper + analytics dashboard" (или более широкие "social media content analyzer"), которые можно форкнуть и адаптировать под epify/groq, а не писать весь пайплайн с нуля.

H2: Для новичка самый быстрый путь к витрине с сортировкой — Supabase (Postgres + автогенерируемый веб-интерфейс/Table Editor) в связке с простым скриптом на Python, а не кастомный фронтенд.

H3: Метрику "просмотры/медиана" нужно считать не просто по аккаунту в среднем, а по скользящей медиане последних N роликов (нормализация на рост/падение аккаунта со временем) — это стандартная практика в существующих inflencer-analytics инструментах.

H4 (альтернативная): epify имеет жёсткие лимиты/нестабильное API, и более надёжной бесплатной альтернативой окажется другой сервис (Apify Instagram Scraper free tier, instaloader, RapidAPI Instagram unofficial API) — стоит проверить это адверсариально.

## Методология

TRAP-подобная структура (Problem Definition уже сделан выше → Landscape → Competitive/Tool Deep-dive → Stack Evaluation → Metric Research → Adversarial). Это средний масштаб: 5 этапов + adversarial проход, ~10-14 запросов, инструменты — Exa (семантический поиск open-source решений) + WebFetch (документация epify/groq/Supabase) + GitHub code search.

## Этапы выполнения

### Этап 1: Landscape — готовые open-source решения (~20 мин)
**Цель:** найти существующие open-source репозитории "Instagram content factory / competitor analyzer / reels scraper + dashboard", которые можно взять за основу.
**Инструмент:** Exa (`web_search_exa`), GitHub code search
**Запросы:**
- `open source Instagram Reels competitor analysis dashboard github`
- `Instagram content factory scraper transcription database dashboard github`
- `site:github.com "instagram" "reels" "scraper" "dashboard" OR "analytics"`
- `site:github.com "instagram" "viral score" OR "views to median" reels`
- `awesome list instagram scraping tools 2025 2026`
**Ожидаемый результат:** 3-6 кандидатов repo с описанием архитектуры (язык, БД, есть ли veб-интерфейс), пригодных для форка/вдохновения.

### Этап 2: epify — возможности, лимиты, альтернативы (~15 мин)
**Цель:** понять реальные лимиты epify free tier ($5 бонус), формат API (какие данные отдаёт по рилсу: views, likes, дата, ссылка, длительность), надёжность/риски бана.
**Инструмент:** WebFetch (официальный сайт/доки epify), Exa
**Запросы:**
- `epify.com Instagram API pricing documentation`
- `epify Instagram scraper API reviews reddit OR twitter experience`
- `epify API limitations rate limits gotchas`
- `Apify Instagram Scraper free tier vs epify comparison`
**Ожидаемый результат:** таблица лимитов/цены/формата ответа epify + минимум одна проверенная альтернатива на случай проблем.

### Этап 3: Транскрибация через groq — практика и подводные камни (~10 мин)
**Цель:** узнать, как обычно организуют пайплайн "видео → аудио → Whisper на groq" в бесплатных лимитах, какие есть скрипты-примеры.
**Инструмент:** Exa, GitHub code search
**Запросы:**
- `groq whisper API free tier transcription video pipeline example github`
- `extract audio from instagram reel ffmpeg transcribe groq whisper tutorial`
- `groq API rate limits free tier 2025 2026 whisper-large-v3`
**Ожидаемый результат:** рабочий паттерн кода (видео→mp3→groq whisper→текст) и актуальные цифры лимитов.

### Этап 4: Стек БД + веб-витрина для новичка (~20 мин)
**Цель:** выбрать связку БД+интерфейс, которая даст сортируемую таблицу с минимумом кода для новичка.
**Инструмент:** Exa, официальная документация (WebFetch)
**Запросы:**
- `Supabase table editor as internal dashboard sortable filterable no-code`
- `best beginner friendly stack database plus web table dashboard Python 2025`
- `Streamlit vs Retool vs Supabase Studio internal data table dashboard comparison`
- `Airtable vs Supabase vs Google Sheets for content analytics dashboard`
**Ожидаемый результат:** сравнительная таблица 3 вариантов стека (порог входа / стоимость / гибкость сортировки-фильтрации / насколько легко добавить транскрибацию и ссылку на видео).

### Этап 5: Метрика успешности (просмотры/медиана) (~10 мин)
**Цель:** проверить, как в индустрии/аналитических инструментах считают "нормализованную виральность" ролика относительно аккаунта.
**Инструмент:** Exa
**Запросы:**
- `viral score reels views divided by median views formula influencer analytics`
- `how to measure reel performance relative to account average views engagement rate normalization`
- `instagram analytics tools "median views" OR "outlier score" methodology`
**Ожидаемый результат:** конкретная формула (например, views / rolling median of last N posts) с обоснованием, почему медиана лучше среднего (устойчивость к выбросам).

### Этап 6: Adversarial проход — риски и ограничения (~15 мин)
**Цель:** найти доказательства против дефолтных гипотез — где именно такой проект может сломаться.
**Запросы:**
- `Instagram scraping legal risk OR account ban third-party API 2025 2026`
- `epify OR similar instagram api service shut down OR unreliable complaints`
- `groq free tier rate limit too low for production complaints reddit`
- `"content factory" reels reverse engineering ethical legal considerations`
**Ожидаемый результат:** список конкретных рисков (бан аккаунтов-доноров, юридические вопросы репоста контента конкурентов, нестабильность бесплатных лимитов) с рекомендацией, как их обойти или на что явно указать пользователю.

## Критерии завершения
- [ ] Найдено минимум 3 open-source репозитория/проекта, пригодных как основа или референс
- [ ] Понятны реальные лимиты epify (цифры: запросов/$ или запросов/день) и есть fallback-вариант
- [ ] Понятен рабочий паттерн видео→аудио→groq транскрибация с актуальными лимитами
- [ ] Есть сравнительная таблица минимум 3 вариантов стека БД+витрина с рекомендацией под новичка
- [ ] Есть конкретная формула метрики "просмотры/медиана" с обоснованием
- [ ] Adversarial-проход завершён — минимум 3 конкретных риска названы явно

## Итоговый артефакт
Документ-рекомендация (markdown) с:
1. Кратким summary архитектуры пайплайна (epify → БД → groq → БД → веб-витрина)
2. Конкретной рекомендацией по стеку (с учётом уровня новичка)
3. Списком 2-3 open-source репозиториев для старта/вдохновения (с ссылками)
4. Формулой метрики успешности
5. Списком рисков и как их избежать
6. Следующим шагом: что делать в новом чате (или прямо предложение вызвать `/make-tz` для ТЗ на реализацию)

## Нужно от пользователя
Ничего блокирующего — весь ресёрч можно выполнить без доступа пользователя. Аккаунт epify/groq понадобится только на этапе реализации, не ресёрча.

## Оценка времени
Общее: ~1.5 часа (субагент выполнит параллельно/последовательно, отчёт придёт единым сообщением)
