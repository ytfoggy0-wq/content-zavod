# Разведка: улучшение витрины content-zavod

## Текущее состояние
- Витрина — `app.py`, Streamlit, 61 строка. Одна таблица `st.dataframe` со всеми колонками:
  username, posted_at, views, likes, median_score, caption, transcript, reel_url.
- Фильтры: multiselect по аккаунтам, слайдер по min median_score. Больше ничего.
- Данные из Postgres (`reels` join `accounts`), кэш 60 сек.

## Схема БД (`sql/schema.sql`)
`reels`: id, account_id, reel_url, shortcode, video_url, caption, posted_at, views, likes,
comments, duration_seconds, transcript, median_score, collected_at.
**Нет** колонки под превью-картинку и под описание содержимого видео.

## Пайплайн сбора (`src/collect_reels.py`)
- Apify actor `parseforge/instagram-reel-scraper`. По факту актор отдаёт **22 поля**, включая
  `thumbnailUrl` (обложка ролика) — но `collect_reels.py` его не сохраняет, забирает только
  shortcode/videoUrl/caption/timestamp/views/likes/comments/duration.
- `upsert_reel`: если ролик уже есть — обновляет только views/likes/comments, остальное не трогает.
- **Важно (из памяти проекта):** Apify упёрся в `Monthly usage hard limit exceeded` на бесплатном
  тарифе 2026-07-23. Повторный проход по всем аккаунтам (даже просто чтобы дособрать thumbnailUrl
  для уже собранных 203 роликов) снова расходует лимит и может не пройти до его сброса.
- В БД сейчас: 11/50 аккаунтов, 203 ролика, у ~148 есть score.

## "Описание происходившего в видео"
- В БД есть только `transcript` (аудио через Groq whisper) и `caption` (подпись IG) — оба текстовые,
  ни один не описывает, что видно в кадре.
- Реального анализа видеоряда в пайплайне нет. Чтобы получить именно описание "что происходит в
  видео", нужен отдельный шаг с vision-моделью (кадр/thumbnail → текст) — это новый API-вызов
  (Groq vision или другой), новая колонка в БД, новый скрипт, доп. время на 203+ роликов.

## Точки правки
- `sql/schema.sql` — добавить колонки (thumbnail_url, video_description и т.п.), либо через ALTER.
- `src/collect_reels.py` — сохранять thumbnailUrl из ответа Apify; для новых роликов это бесплатно
  (входит в тот же вызов), для уже собранных 203 — нужен отдельный проход, упирается в лимит Apify.
- `app.py` — редизайн: карточки/грид вместо плоской таблицы (нужно для картинки сбоку — в
  `st.dataframe` картинку рядом со строкой красиво не показать; Streamlit умеет `ImageColumn` в
  dataframe, но текст рядом всё равно обрежется — для "приятного" вида лучше carousel/grid из
  `st.columns` или `st.container` с `st.image` + текстом).
- Нет отдельного бэкенд-сервиса — всё синхронно тянется из Postgres при каждой загрузке страницы.
