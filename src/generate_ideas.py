import os
import time

import httpx
from dotenv import load_dotenv
from groq import Groq

from db import get_connection

load_dotenv()

PAUSE_SECONDS_BETWEEN_REELS = 0.4

# Отдельная модель от tag_topics.py (llama-3.3-70b-versatile) — та уже упёрлась
# в дневной лимит токенов Groq. Эта задача не должна конкурировать за ту же квоту.
TEXT_MODEL = "llama-3.1-8b-instant"

MAX_IDEA_LENGTH = 300

PROMPT_TEMPLATE = (
    "Вот текстовые данные о видео-ролике (Reels) конкурента:\n\n"
    "{text}\n\n"
    "Ты консультируешь стоматологическую клинику/врача-стоматолога, которая анализирует "
    "контент конкурентов из других ниш, чтобы находить удачные приёмы и адаптировать их под себя. "
    "В 1-2 коротких предложениях на русском языке предложи, как именно стоматологическая клиника "
    "может повторить конкретно этот формат/приём/крючок ролика в своей теме. "
    "Пиши конкретно и по делу, без воды: что именно снять, что показать, какую фразу произнести "
    "(например: «сними...», «покажи...», «используй фразу...»). "
    "Не пиши общие советы вроде «сделай что-то похожее». "
    "Ответь только самой идеей, без вступлений и пояснений."
)


def ensure_adaptation_idea_column(conn):
    with conn.cursor() as cur:
        cur.execute("ALTER TABLE reels ADD COLUMN IF NOT EXISTS adaptation_idea text")
    conn.commit()


def fetch_pending_reels(conn):
    with conn.cursor() as cur:
        cur.execute(
            """
            select id, caption, video_description, transcript, topics from reels
            where adaptation_idea is null
              and (video_description is not null or transcript is not null or caption is not null)
            order by id
            """
        )
        return cur.fetchall()


def build_prompt(caption, video_description, transcript, topics) -> str:
    parts = []
    if caption:
        parts.append(f"Подпись (caption): {caption[:600]}")
    if video_description:
        parts.append(f"Описание кадра (AI vision): {video_description[:600]}")
    if transcript:
        parts.append(f"Транскрипт (начало): {transcript[:600]}")
    if topics:
        parts.append(f"Темы: {', '.join(topics)}")
    text = "\n\n".join(parts)
    return PROMPT_TEMPLATE.format(text=text)


def generate_idea(groq_client: Groq, model: str, caption, video_description, transcript, topics) -> str:
    prompt = build_prompt(caption, video_description, transcript, topics)
    response = groq_client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = response.choices[0].message.content.strip()
    if len(raw) > MAX_IDEA_LENGTH:
        raw = raw[:MAX_IDEA_LENGTH].rstrip() + "…"
    return raw


def save_idea(conn, reel_id: int, idea: str):
    with conn.cursor() as cur:
        cur.execute(
            "update reels set adaptation_idea = %s where id = %s",
            (idea, reel_id),
        )
    conn.commit()


def main():
    conn = get_connection()
    ensure_adaptation_idea_column(conn)
    # На машине настроен системный socks-прокси, который httpx (через trust_env)
    # пытается использовать и падает. Groq API дергаем напрямую, без системного прокси.
    groq_client = Groq(
        api_key=os.environ["GROQ_API_KEY"],
        http_client=httpx.Client(trust_env=False),
    )

    reels = fetch_pending_reels(conn)
    if not reels:
        print("Нет роликов, ожидающих генерации идей адаптации.")
        conn.close()
        return

    print(f"Используется модель Groq: {TEXT_MODEL}")
    print(f"К обработке: {len(reels)} роликов")

    done = 0
    errors = 0

    for reel_id, caption, video_description, transcript, topics in reels:
        try:
            idea = generate_idea(groq_client, TEXT_MODEL, caption, video_description, transcript, topics)
            save_idea(conn, reel_id, idea)
            done += 1
        except Exception as e:
            errors += 1
            print(f"Ошибка на ролике {reel_id}: {e}")
            if "rate_limit" in str(e).lower() or "429" in str(e):
                print("Похоже на rate limit — останавливаюсь.")
                break

        time.sleep(PAUSE_SECONDS_BETWEEN_REELS)

    conn.close()
    print(f"Готово. Сгенерировано идей: {done}, ошибок: {errors}")


if __name__ == "__main__":
    main()
