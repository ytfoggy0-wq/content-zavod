import os
import time
from pathlib import Path

from apify_client import ApifyClient
from dotenv import load_dotenv

from db import get_connection

load_dotenv()

ACTOR_ID = "parseforge/instagram-reel-scraper"
MAX_REELS_PER_ACCOUNT = 20
PAUSE_SECONDS_BETWEEN_ACCOUNTS = 3

ACCOUNTS_FILE = Path(__file__).parent.parent / "config" / "accounts.txt"


def load_accounts() -> list[str]:
    with open(ACCOUNTS_FILE, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def ensure_account(conn, username: str) -> int:
    with conn.cursor() as cur:
        cur.execute(
            "insert into accounts (username) values (%s) on conflict (username) do nothing",
            (username,),
        )
        cur.execute("select id from accounts where username = %s", (username,))
        account_id = cur.fetchone()[0]
    conn.commit()
    return account_id


def upsert_reel(conn, account_id: int, item: dict) -> bool:
    """Returns True if this is a new reel, False if it already existed (updated)."""
    reel_url = item["reelUrl"]

    with conn.cursor() as cur:
        cur.execute("select id from reels where reel_url = %s", (reel_url,))
        existing = cur.fetchone()

        if existing:
            cur.execute(
                "update reels set views = %s, likes = %s, comments = %s, thumbnail_url = %s where reel_url = %s",
                (
                    item.get("viewCount"),
                    item.get("likeCount"),
                    item.get("commentCount"),
                    item.get("thumbnailUrl"),
                    reel_url,
                ),
            )
            conn.commit()
            return False

        cur.execute(
            """
            insert into reels
                (account_id, reel_url, shortcode, video_url, caption, posted_at,
                 views, likes, comments, duration_seconds, thumbnail_url)
            values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                account_id,
                reel_url,
                item.get("shortcode"),
                item.get("videoUrl"),
                item.get("caption"),
                item.get("timestamp"),
                item.get("viewCount"),
                item.get("likeCount"),
                item.get("commentCount"),
                item.get("duration"),
                item.get("thumbnailUrl"),
            ),
        )
        conn.commit()
        return True


def main():
    apify = ApifyClient(os.environ["APIFY_TOKEN"])
    conn = get_connection()

    accounts = load_accounts()
    total_new = 0
    total_updated = 0

    for username in accounts:
        account_id = ensure_account(conn, username)

        run = apify.actor(ACTOR_ID).call(
            run_input={
                "urls": [username],
                "maxItems": MAX_REELS_PER_ACCOUNT,
                "skipPinnedReels": False,
                "commentsPerReel": 0,
            }
        )
        items = apify.dataset(run.default_dataset_id).list_items().items

        for item in items:
            is_new = upsert_reel(conn, account_id, item)
            total_new += is_new
            total_updated += not is_new

        print(f"{username}: обработано {len(items)} роликов")
        time.sleep(PAUSE_SECONDS_BETWEEN_ACCOUNTS)

    conn.close()
    print(f"Готово. Аккаунтов: {len(accounts)}, новых роликов: {total_new}, обновлено: {total_updated}")


if __name__ == "__main__":
    main()
