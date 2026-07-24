import os
import time

import requests
from dotenv import load_dotenv

from db import get_connection

load_dotenv()

BATCH_SIZE = 10
PAUSE_SECONDS_BETWEEN_REELS = 2
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
VISION_MODEL = "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free"
PROMPT = (
    "Коротко, в 1-2 предложениях, по-русски опиши, что происходит на этом кадре "
    "видео (что видно в кадре, какое действие или сцена)."
)


def fetch_pending_reels(conn):
    with conn.cursor() as cur:
        cur.execute(
            """
            select id, thumbnail_url from reels
            where thumbnail_url is not null and video_description is null
            limit %s
            """,
            (BATCH_SIZE,),
        )
        return cur.fetchall()


def describe(api_key: str, thumbnail_url: str) -> str:
    response = requests.post(
        OPENROUTER_URL,
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "model": VISION_MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": PROMPT},
                        {"type": "image_url", "image_url": {"url": thumbnail_url}},
                    ],
                }
            ],
        },
        timeout=60,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"].strip()


def save_description(conn, reel_id: int, description: str):
    with conn.cursor() as cur:
        cur.execute(
            "update reels set video_description = %s where id = %s", (description, reel_id)
        )
    conn.commit()


def main():
    conn = get_connection()
    api_key = os.environ["OPENROUTER_API_KEY"]

    reels = fetch_pending_reels(conn)
    done = 0
    errors = 0

    for reel_id, thumbnail_url in reels:
        try:
            description = describe(api_key, thumbnail_url)
            save_description(conn, reel_id, description)
            done += 1
        except Exception as e:
            errors += 1
            print(f"Ошибка на ролике {reel_id}: {e}")

        time.sleep(PAUSE_SECONDS_BETWEEN_REELS)

    conn.close()
    print(f"Описано: {done}, ошибок: {errors}")


if __name__ == "__main__":
    main()
