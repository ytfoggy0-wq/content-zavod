import numpy as np

from db import get_connection

WINDOW = 20
MIN_PREVIOUS_REELS = 5


def main():
    conn = get_connection()
    updated = 0

    with conn.cursor() as cur:
        cur.execute("select id from accounts")
        account_ids = [row[0] for row in cur.fetchall()]

    for account_id in account_ids:
        with conn.cursor() as cur:
            cur.execute(
                """
                select id, views, posted_at from reels
                where account_id = %s
                order by posted_at asc
                """,
                (account_id,),
            )
            rows = cur.fetchall()

        views_history = []
        for reel_id, views, _posted_at in rows:
            previous = views_history[-WINDOW:]
            if views is not None and len(previous) >= MIN_PREVIOUS_REELS:
                median_views = float(np.median(previous))
                score = round(views / median_views, 2) if median_views else None
            else:
                score = None

            with conn.cursor() as cur:
                cur.execute(
                    "update reels set median_score = %s where id = %s",
                    (score, reel_id),
                )
            conn.commit()
            updated += 1

            if views is not None:
                views_history.append(views)

    conn.close()
    print(f"Обновлено median_score для {updated} роликов")


if __name__ == "__main__":
    main()
