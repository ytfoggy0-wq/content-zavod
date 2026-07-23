import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent / "src"))
from db import get_connection  # noqa: E402

st.set_page_config(page_title="Контент-завод", layout="wide")
st.title("Контент-завод — витрина рилсов конкурентов")


@st.cache_data(ttl=60)
def load_data() -> pd.DataFrame:
    conn = get_connection()
    query = """
        select
            a.username,
            r.posted_at,
            r.views,
            r.likes,
            r.median_score,
            r.caption,
            r.transcript,
            r.reel_url
        from reels r
        join accounts a on r.account_id = a.id
        order by r.median_score desc nulls last
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df


df = load_data()

accounts = sorted(df["username"].unique())
selected_accounts = st.multiselect("Аккаунты", accounts, default=accounts)

min_score = st.slider(
    "Минимальный median_score", 0.0, float(df["median_score"].max() or 1), 0.0, 0.1
)

filtered = df[df["username"].isin(selected_accounts)]
filtered = filtered[filtered["median_score"].fillna(0) >= min_score]

st.write(f"Роликов: {len(filtered)}")

st.dataframe(
    filtered,
    column_config={
        "reel_url": st.column_config.LinkColumn("Ссылка", display_text="Открыть"),
        "median_score": st.column_config.NumberColumn("Score", format="%.2f"),
        "caption": st.column_config.TextColumn("Подпись", width="medium"),
        "transcript": st.column_config.TextColumn("Транскрибация", width="large"),
        "posted_at": st.column_config.DatetimeColumn("Дата", format="DD.MM.YYYY"),
    },
    hide_index=True,
    use_container_width=True,
)
