import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

import requests
from dotenv import load_dotenv
from groq import Groq

from db import get_connection

load_dotenv()

BATCH_SIZE = 10
PAUSE_SECONDS_BETWEEN_REELS = 2


def fetch_pending_reels(conn):
    with conn.cursor() as cur:
        cur.execute(
            """
            select id, video_url from reels
            where transcript is null and video_url is not null
            limit %s
            """,
            (BATCH_SIZE,),
        )
        return cur.fetchall()


def download_video(video_url: str, dest: Path):
    resp = requests.get(video_url, timeout=60)
    resp.raise_for_status()
    dest.write_bytes(resp.content)


FFMPEG_FALLBACK_PATH = (
    r"C:\Users\ytfog\AppData\Local\Microsoft\WinGet\Packages\\"
    r"Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\\"
    r"ffmpeg-8.1.2-full_build\bin\ffmpeg.exe"
)
FFMPEG_PATH = shutil.which("ffmpeg") or FFMPEG_FALLBACK_PATH


def extract_audio(video_path: Path, audio_path: Path):
    subprocess.run(
        [FFMPEG_PATH, "-y", "-i", str(video_path), "-vn", "-acodec", "mp3", str(audio_path)],
        capture_output=True,
        check=True,
    )


def transcribe(groq_client: Groq, audio_path: Path) -> str:
    with open(audio_path, "rb") as f:
        result = groq_client.audio.transcriptions.create(
            file=(audio_path.name, f.read()),
            model="whisper-large-v3",
        )
    return result.text


def save_transcript(conn, reel_id: int, transcript: str):
    with conn.cursor() as cur:
        cur.execute(
            "update reels set transcript = %s where id = %s", (transcript, reel_id)
        )
    conn.commit()


def main():
    conn = get_connection()
    groq_client = Groq(api_key=os.environ["GROQ_API_KEY"])

    reels = fetch_pending_reels(conn)
    done = 0
    errors = 0

    for reel_id, video_url in reels:
        try:
            with tempfile.TemporaryDirectory() as tmp:
                video_path = Path(tmp) / "video.mp4"
                audio_path = Path(tmp) / "audio.mp3"

                download_video(video_url, video_path)
                extract_audio(video_path, audio_path)
                text = transcribe(groq_client, audio_path)

                save_transcript(conn, reel_id, text)
                done += 1
        except Exception as e:
            errors += 1
            print(f"Ошибка на ролике {reel_id}: {e}")

        time.sleep(PAUSE_SECONDS_BETWEEN_REELS)

    conn.close()
    print(f"Транскрибировано: {done}, ошибок: {errors}")


if __name__ == "__main__":
    main()
