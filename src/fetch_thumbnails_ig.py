import html
import re
import time

import requests

from db import get_connection

PAUSE_SECONDS_BETWEEN_REELS = 1
REQUEST_HEADERS = {
    # Instagram отдаёт og:image только соцсетевым краулерам (для превью при шаринге),
    # обычным браузерным User-Agent показывает JS-заглушку без метатегов.
    "User-Agent": "facebookexternalhit/1.1"
}
OG_IMAGE_RE = re.compile(r'<meta[^>]+property="og:image"[^>]+content="([^"]+)"')


def fetch_pending_reels(conn):
    with conn.cursor() as cur:
        cur.execute(
            "select id, reel_url from reels where thumbnail_url is null order by id"
        )
        return cur.fetchall()


def extract_og_image(page_html: str) -> str | None:
    match = OG_IMAGE_RE.search(page_html)
    return html.unescape(match.group(1)) if match else None


def save_thumbnail(conn, reel_id: int, thumbnail_url: str):
    with conn.cursor() as cur:
        cur.execute(
            "update reels set thumbnail_url = %s where id = %s", (thumbnail_url, reel_id)
        )
    conn.commit()


def main():
    conn = get_connection()
    reels = fetch_pending_reels(conn)
    done = 0
    errors = 0

    for reel_id, reel_url in reels:
        try:
            resp = requests.get(reel_url, headers=REQUEST_HEADERS, timeout=30)
            resp.raise_for_status()
            thumbnail_url = extract_og_image(resp.text)

            if thumbnail_url:
                save_thumbnail(conn, reel_id, thumbnail_url)
                done += 1
            else:
                errors += 1
                print(f"Ролик {reel_id}: og:image не найден в разметке")
        except Exception as e:
            errors += 1
            print(f"Ошибка на ролике {reel_id}: {e}")

        time.sleep(PAUSE_SECONDS_BETWEEN_REELS)

    conn.close()
    print(f"Превью собрано: {done}, ошибок: {errors}")


if __name__ == "__main__":
    main()
