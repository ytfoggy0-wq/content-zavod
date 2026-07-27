import json
import os
import re
import time

import httpx
from dotenv import load_dotenv
from groq import Groq

from db import get_connection

load_dotenv()

PAUSE_SECONDS_BETWEEN_REELS = 0.5

TEXT_MODEL = "llama-3.3-70b-versatile"
TEXT_MODEL_FALLBACK = "llama-3.1-8b-instant"

PROMPT_TEMPLATE = (
    "Вот текстовые данные о видео-ролике (Reels):\n\n"
    "{text}\n\n"
    "Верни СТРОГО JSON-массив из 2-4 коротких тегов на русском языке, "
    "описывающих тему/нишу ролика (например: [\"Психология отношений\", \"Личные границы\"]). "
    "Без пояснений, без markdown-обрамления, только сам JSON-массив."
)


def ensure_topics_column(conn):
    with conn.cursor() as cur:
        cur.execute("ALTER TABLE reels ADD COLUMN IF NOT EXISTS topics jsonb")
    conn.commit()


def fetch_pending_reels(conn):
    with conn.cursor() as cur:
        cur.execute(
            """
            select id, caption, video_description, transcript from reels
            where topics is null
              and (video_description is not null or transcript is not null or caption is not null)
            order by id
            """
        )
        return cur.fetchall()


def build_prompt(caption, video_description, transcript) -> str:
    # Некоторые video_description получены от reasoning-модели и вместо короткого
    # описания кадра содержат десятки тысяч символов рассуждений — обрезаем всё
    # на входе, чтобы не упереться в лимит токенов Groq (TPM).
    parts = []
    if caption:
        parts.append(f"Подпись (caption): {caption[:600]}")
    if video_description:
        parts.append(f"Описание кадра (AI vision): {video_description[:600]}")
    if transcript:
        parts.append(f"Транскрипт (начало): {transcript[:600]}")
    text = "\n\n".join(parts)
    return PROMPT_TEMPLATE.format(text=text)


def strip_code_fence(raw: str) -> str:
    raw = raw.strip()
    match = re.match(r"^```(?:json)?\s*(.*?)\s*```$", raw, re.DOTALL)
    if match:
        return match.group(1).strip()
    return raw


def tag_topics(groq_client: Groq, model: str, caption, video_description, transcript) -> list:
    prompt = build_prompt(caption, video_description, transcript)
    response = groq_client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = response.choices[0].message.content
    cleaned = strip_code_fence(raw)
    topics = json.loads(cleaned)
    if not isinstance(topics, list):
        raise ValueError(f"Ответ модели не является списком: {raw!r}")
    return topics


def save_topics(conn, reel_id: int, topics: list):
    with conn.cursor() as cur:
        cur.execute(
            "update reels set topics = %s::jsonb where id = %s",
            (json.dumps(topics, ensure_ascii=False), reel_id),
        )
    conn.commit()


def pick_working_model(groq_client: Groq, caption, video_description, transcript):
    """Пробный вызов на первом ролике. Возвращает (model, topics_for_first_reel)."""
    for model in (TEXT_MODEL, TEXT_MODEL_FALLBACK):
        try:
            topics = tag_topics(groq_client, model, caption, video_description, transcript)
            return model, topics
        except Exception as e:
            print(f"Модель {model} не сработала на тестовом вызове: {e}")
    raise RuntimeError("Ни одна модель Groq не сработала на тестовом вызове")


def main():
    conn = get_connection()
    ensure_topics_column(conn)
    # На машине настроен системный socks4-прокси, который httpx (через trust_env)
    # пытается использовать и падает (socks4 не поддерживается httpx напрямую).
    # Groq API дергаем напрямую, без системного прокси.
    groq_client = Groq(
        api_key=os.environ["GROQ_API_KEY"],
        http_client=httpx.Client(trust_env=False),
    )

    reels = fetch_pending_reels(conn)
    if not reels:
        print("Нет роликов, ожидающих тегирования тем.")
        conn.close()
        return

    first_id, first_caption, first_video_description, first_transcript = reels[0]
    try:
        model, first_topics = pick_working_model(
            groq_client, first_caption, first_video_description, first_transcript
        )
    except Exception as e:
        print(f"Не удалось подобрать рабочую модель Groq: {e}")
        conn.close()
        return

    print(f"Используется модель Groq: {model}")

    done = 0
    errors = 0

    # Первый ролик уже протегирован тестовым вызовом — просто сохраняем и пропускаем в цикле.
    try:
        save_topics(conn, first_id, first_topics)
        done += 1
    except Exception as e:
        errors += 1
        print(f"Ошибка на ролике {first_id}: {e}")

    for reel_id, caption, video_description, transcript in reels[1:]:
        try:
            topics = tag_topics(groq_client, model, caption, video_description, transcript)
            save_topics(conn, reel_id, topics)
            done += 1
        except Exception as e:
            errors += 1
            print(f"Ошибка на ролике {reel_id}: {e}")
            if "rate_limit" in str(e).lower() or "429" in str(e):
                print("Похоже на rate limit — останавливаюсь.")
                break

        time.sleep(PAUSE_SECONDS_BETWEEN_REELS)

    conn.close()
    print(f"Модель: {model}. Проставлено тегов: {done}, ошибок: {errors}")


if __name__ == "__main__":
    main()
