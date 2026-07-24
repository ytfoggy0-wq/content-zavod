import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent / "src"))
from db import get_connection  # noqa: E402

st.set_page_config(page_title="Контент-завод", layout="wide")
st.title("Контент-завод")
st.caption("Ролики конкурентов, которые выстрелили сильнее обычной нормы аккаунта")

CARDS_PER_PAGE = 12
TOP_SCORE_QUANTILE = 0.9


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
            r.thumbnail_url,
            r.video_description,
            r.reel_url
        from reels r
        join accounts a on r.account_id = a.id
        order by r.median_score desc nulls last
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df


df = load_data()

with st.sidebar:
    st.header("Фильтры")
    accounts = sorted(df["username"].unique())
    selected_accounts = st.multiselect("Аккаунты", accounts, default=accounts)
    max_score = df["median_score"].max()
    min_score = st.slider(
        "Минимальный score", 0.0, float(max_score) if pd.notna(max_score) else 1.0, 0.0, 0.1
    )

filtered = df[df["username"].isin(selected_accounts)]
filtered = filtered[filtered["median_score"].fillna(0) >= min_score]
filtered = filtered.sort_values("median_score", ascending=False, na_position="last")

top_score_threshold = filtered["median_score"].quantile(TOP_SCORE_QUANTILE)

st.write(f"Роликов: {len(filtered)}")

total_pages = max(1, -(-len(filtered) // CARDS_PER_PAGE))
page = 1
if total_pages > 1:
    page = st.number_input("Страница", min_value=1, max_value=total_pages, value=1, step=1)

page_start = (page - 1) * CARDS_PER_PAGE
page_rows = filtered.iloc[page_start : page_start + CARDS_PER_PAGE]

for _, row in page_rows.iterrows():
    with st.container(border=True):
        image_col, info_col = st.columns([1, 3])

        with image_col:
            if row["thumbnail_url"]:
                st.image(row["thumbnail_url"], use_container_width=True)
            else:
                st.write("Превью недоступно")

        with info_col:
            score = row["median_score"]
            badge = " 🔥" if pd.notna(score) and pd.notna(top_score_threshold) and score >= top_score_threshold else ""
            score_text = f"{score:.2f}" if pd.notna(score) else "—"
            views_text = f"{row['views']:,.0f}" if pd.notna(row["views"]) else "—"
            likes_text = f"{row['likes']:,.0f}" if pd.notna(row["likes"]) else "—"
            date_text = f" · {row['posted_at']:%d.%m.%Y}" if pd.notna(row["posted_at"]) else ""
            st.subheader(f"@{row['username']}{badge}")
            st.write(f"Score **{score_text}** · {views_text} просмотров · {likes_text} лайков{date_text}")

            if row["video_description"]:
                st.write(row["video_description"])
            elif row["caption"]:
                st.write(row["caption"])

            if row["transcript"]:
                with st.expander("Транскрибация"):
                    st.write(row["transcript"])

            st.link_button("Открыть в Instagram", row["reel_url"])
