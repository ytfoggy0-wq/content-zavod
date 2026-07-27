import json
from pathlib import Path

from dotenv import load_dotenv

from db import get_connection

load_dotenv()

OUTPUT_PATH = Path(__file__).parent.parent / "docs" / "reels_export.json"


def fetch_reels(conn):
    with conn.cursor() as cur:
        cur.execute(
            """
            select
                a.username,
                r.posted_at,
                r.views,
                r.likes,
                r.median_score,
                r.caption,
                r.transcript,
                r.thumbnail_url,
                r.video_description,
                r.reel_url,
                r.topics,
                r.adaptation_idea
            from reels r
            join accounts a on a.id = r.account_id
            order by r.id
            """
        )
        return cur.fetchall()


def row_to_dict(row) -> dict:
    (
        username,
        posted_at,
        views,
        likes,
        median_score,
        caption,
        transcript,
        thumbnail_url,
        video_description,
        reel_url,
        topics,
        adaptation_idea,
    ) = row

    return {
        "username": username,
        "posted_at": posted_at.isoformat() if posted_at else None,
        "views": views,
        "likes": likes,
        "median_score": float(median_score) if median_score is not None else None,
        "caption": caption,
        "transcript": transcript,
        "thumbnail_url": thumbnail_url,
        "video_description": video_description,
        "reel_url": reel_url,
        "topics": topics if topics is not None else [],
        "adaptation_idea": adaptation_idea,
    }


def main():
    conn = get_connection()
    rows = fetch_reels(conn)
    conn.close()

    data = [row_to_dict(row) for row in rows]

    OUTPUT_PATH.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    print(f"Экспортировано роликов: {len(data)}")


if __name__ == "__main__":
    main()
