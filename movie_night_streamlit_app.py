from __future__ import annotations

import math
import random
from io import BytesIO
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

SCRIPT_DIR = Path(__file__).parent
PICKS_TO_SHOW = 3

VIBE_MAP = {
    "feel good": ["Comedy", "Family", "Animation"],
    "dark": ["Horror", "Thriller", "Crime"],
    "mind bending": ["Science Fiction", "Mystery"],
    "action packed": ["Action", "Adventure"],
    "romantic": ["Romance"],
    "emotional": ["Drama"],
    "scary": ["Horror"],
    "funny": ["Comedy"],
    "epic": ["Adventure", "Fantasy"],
    "space": ["Science Fiction"],
    "crime": ["Crime"],
}

GENRE_HINTS = [
    "Action", "Adventure", "Animation", "Comedy", "Crime", "Documentary",
    "Drama", "Family", "Fantasy", "History", "Horror", "Music",
    "Mystery", "Romance", "Science Fiction", "Thriller", "War", "Western",
]

VALID_WATCH_STATUSES = {
    "watched": "Watched",
    "w": "Watched",
    "unwatched": "Unwatched",
    "u": "Unwatched",
    "in progress": "In progress",
    "in-progress": "In progress",
    "inprogress": "In progress",
    "progress": "In progress",
    "p": "In progress",
}

RETRO_CSS = """
<style>
    :root {
        --wall: #241316;
        --wall-2: #341b22;
        --cream: #fff1c9;
        --sunset: #ff8c42;
        --hot-pink: #ff4fa3;
        --cyan: #49d7ff;
        --mint: #7dffb2;
        --wood: #8b4f2c;
        --wood-dark: #4c2717;
        --label: #f5d56e;
        --label-ink: #2b160f;
    }
    .stApp {
        background:
            radial-gradient(circle at 10% 8%, rgba(255,79,163,0.18), transparent 25%),
            radial-gradient(circle at 92% 12%, rgba(73,215,255,0.16), transparent 24%),
            radial-gradient(circle at 50% 92%, rgba(255,140,66,0.18), transparent 34%),
            repeating-linear-gradient(135deg, rgba(255,255,255,0.018), rgba(255,255,255,0.018) 2px, transparent 2px, transparent 16px),
            linear-gradient(180deg, var(--wall) 0%, var(--wall-2) 52%, #1d1115 100%);
        color: var(--cream);
    }
    .block-container { max-width: 1260px; padding-top: 1rem; padding-bottom: 3rem; }
    header[data-testid="stHeader"] {
        background:
            linear-gradient(90deg, rgba(36,19,22,0.94), rgba(58,27,37,0.94)),
            repeating-linear-gradient(90deg, rgba(255,255,255,0.05), rgba(255,255,255,0.05) 1px, transparent 1px, transparent 20px);
        border-bottom: 3px solid rgba(255,140,66,0.7);
        backdrop-filter: blur(6px);
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(52,27,34,0.98), rgba(30,17,22,0.98));
        border-right: 3px solid rgba(139,79,44,0.7);
    }
    h1, h2, h3, .stMarkdown, p, label, [data-testid="stMetricValue"], [data-testid="stMetricLabel"] { color: var(--cream); }
    [data-baseweb="select"] > div, [data-testid="stNumberInput"] input, [data-testid="stTextInput"] input {
        background: rgba(255,241,201,0.08) !important;
        color: var(--cream) !important;
        border-color: rgba(255,140,66,0.35) !important;
    }
    div[role="radiogroup"] {
        background: rgba(255,241,201,0.06);
        border: 2px solid rgba(255,140,66,0.42);
        border-radius: 18px;
        padding: 0.5rem 0.75rem;
        box-shadow: inset 0 0 20px rgba(0,0,0,0.22);
    }
    .hero-card {
        border: 3px solid rgba(255,140,66,0.9);
        border-radius: 24px;
        padding: 1.35rem 1.5rem;
        margin-bottom: 1rem;
        background:
            linear-gradient(135deg, rgba(77,35,29,0.96), rgba(31,18,24,0.96)),
            repeating-linear-gradient(90deg, rgba(255,255,255,0.035), rgba(255,255,255,0.035) 2px, transparent 2px, transparent 22px);
        box-shadow: 0 0 24px rgba(255,79,163,0.18), 0 12px 30px rgba(0,0,0,0.35), inset 0 0 26px rgba(255,214,112,0.06);
    }
    .hero-title {
        font-size: 2.25rem;
        font-weight: 900;
        color: var(--cream);
        margin-bottom: 0.35rem;
        letter-spacing: 0.02em;
        text-shadow: 3px 3px 0 rgba(255,79,163,0.45), -2px -2px 0 rgba(73,215,255,0.22);
    }
    .hero-sub { font-size: 1rem; line-height: 1.5; margin-bottom: 0.7rem; }
    .marquee { display: inline-block; padding: 0.28rem 0.7rem; margin: 0.15rem 0.35rem 0.15rem 0; border-radius: 999px; background: rgba(255,241,201,0.11); border: 1px solid rgba(255,241,201,0.18); color: var(--cream); font-size: 0.9rem; }
    .section-kicker { margin: 1rem 0 0.55rem; padding: 0.55rem 0.9rem; border-left: 6px solid var(--hot-pink); background: linear-gradient(90deg, rgba(255,140,66,0.16), rgba(73,215,255,0.08)); border-radius: 10px; font-weight: 900; letter-spacing: 0.04em; text-transform: uppercase; box-shadow: inset 0 0 12px rgba(0,0,0,0.18); }
    .shelf-rule { margin: 0.6rem 0 1rem; height: 24px; border-radius: 8px 8px 14px 14px; background: linear-gradient(180deg, #b36b3e 0%, var(--wood) 42%, var(--wood-dark) 100%); box-shadow: inset 0 3px 1px rgba(255,255,255,0.15), inset 0 -5px 12px rgba(0,0,0,0.42), 0 10px 18px rgba(0,0,0,0.34); }
    .vhs-card { position: relative; min-height: 226px; border-radius: 18px 10px 10px 18px; overflow: hidden; border: 2px solid rgba(255,241,201,0.12); background: linear-gradient(165deg, rgba(25,25,31,0.98), rgba(8,8,12,0.98)); box-shadow: 0 12px 24px rgba(0,0,0,0.38), inset 7px 0 0 rgba(255,255,255,0.035), inset 0 1px 0 rgba(255,255,255,0.08); margin-bottom: 1rem; }
    .vhs-card:before { content: ""; position: absolute; top: 0; left: 14px; bottom: 0; width: 8px; background: linear-gradient(180deg, var(--cyan), var(--hot-pink), var(--sunset)); opacity: 0.9; }
    .vhs-topband { height: 24px; background: linear-gradient(90deg, var(--hot-pink), var(--sunset), var(--cyan)); opacity: 0.95; margin-left: 22px; }
    .vhs-inner { display: grid; grid-template-columns: 94px 1fr; gap: 0.85rem; padding: 0.78rem 0.78rem 0.78rem 1.35rem; align-items: stretch; }
    .vhs-poster-shell { position: relative; border-radius: 10px; background: #080808; border: 3px solid rgba(255,241,201,0.12); min-height: 150px; overflow: hidden; box-shadow: inset 0 0 0 5px rgba(255,255,255,0.03), inset 0 0 20px rgba(0,0,0,0.55), 0 0 0 1px rgba(255,140,66,0.18); transform: rotate(-0.35deg); }
    .vhs-poster-shell img { width: 100%; height: 100%; object-fit: cover; display: block; filter: saturate(1.08) contrast(1.04); }
    .vhs-spine-tag { position: absolute; left: 0; right: 0; bottom: 0; background: rgba(7,7,8,0.86); color: var(--label); text-align: center; font-size: 0.68rem; letter-spacing: 0.16em; padding: 0.25rem 0.2rem; font-weight: 900; }
    .vhs-info { display: flex; flex-direction: column; gap: 0.35rem; min-width: 0; }
    .vhs-title { font-size: 1rem; font-weight: 900; color: var(--cream); line-height: 1.2; margin: 0; }
    .vhs-subtitle { font-size: 0.76rem; color: #e0c98f; margin: 0; letter-spacing: 0.03em; }
    .vhs-pill-row { display: flex; flex-wrap: wrap; gap: 0.32rem; margin-top: 0.1rem; }
    .vhs-pill { display: inline-block; padding: 0.18rem 0.45rem; border-radius: 999px; background: rgba(255,241,201,0.08); border: 1px solid rgba(255,241,201,0.12); color: var(--cream); font-size: 0.68rem; white-space: nowrap; }
    .vhs-overview { font-size: 0.76rem; line-height: 1.4; color: #f0dfb1; margin-top: 0.2rem; display: -webkit-box; -webkit-line-clamp: 4; -webkit-box-orient: vertical; overflow: hidden; }
    .vhs-foot { margin-top: auto; display: flex; justify-content: space-between; align-items: center; gap: 0.4rem; padding-top: 0.35rem; }
    .vhs-label { display: inline-block; background: linear-gradient(180deg, #ffe68e, var(--label)); color: var(--label-ink); font-weight: 900; font-size: 0.68rem; letter-spacing: 0.06em; padding: 0.22rem 0.45rem; border-radius: 6px; box-shadow: 1px 1px 0 rgba(0,0,0,0.28); }
    .vhs-match { color: var(--mint); font-size: 0.68rem; font-weight: 800; text-align: right; text-shadow: 0 0 10px rgba(125,255,178,0.24); }
    .poster-missing { width: 100%; min-height: 150px; display: flex; align-items: center; justify-content: center; text-align: center; background: linear-gradient(180deg, #282129, #090909); color: #e0c98f; font-size: 0.72rem; padding: 0.6rem; }
    .browse-note { color: #e6cfa0; font-size: 0.92rem; margin-top: -0.2rem; margin-bottom: 0.7rem; }
    button[kind="primary"] { background: linear-gradient(90deg, var(--hot-pink), var(--sunset)) !important; border: 2px solid rgba(255,241,201,0.35) !important; color: #fff8dc !important; font-weight: 900 !important; box-shadow: 0 0 18px rgba(255,79,163,0.28) !important; }
</style>
"""


def clean_title(title: Any) -> str:
    title = str(title).strip()
    if "(" in title:
        return title.split("(")[0].strip()
    return title


def extract_year(title: Any) -> int | None:
    try:
        title = str(title)
        start = title.rfind("(")
        end = title.rfind(")")
        return int(title[start + 1:end])
    except Exception:
        return None


def normalize_header(value: Any) -> str:
    return str(value).strip().lower().replace("?", "")


def normalize_watch_status(value: Any) -> str | None:
    if value is None or pd.isna(value):
        return None
    normalized = str(value).strip().lower()
    if not normalized:
        return None
    return VALID_WATCH_STATUSES.get(normalized, str(value).strip())


def get_column_name(df: pd.DataFrame, possible_names: list[str]) -> Any | None:
    normalized_lookup = {normalize_header(column): column for column in df.columns}
    for name in possible_names:
        match = normalized_lookup.get(normalize_header(name))
        if match is not None:
            return match
    return None


def find_default_excel_file() -> Path | None:
    preferred_names = ["MovieList.xlsx", "MovieList(2).xlsx", "Updated List of Movies 5_28_26.xlsx"]
    for name in preferred_names:
        path = SCRIPT_DIR / name
        if path.exists():
            return path
    matches = sorted(SCRIPT_DIR.glob("MovieList*.xlsx"))
    return matches[0] if matches else None


@st.cache_data(show_spinner=False)
def load_movies_from_path(path: str) -> list[dict[str, Any]]:
    return load_movies(pd.read_excel(path))


@st.cache_data(show_spinner=False)
def load_movies_from_upload(file_bytes: bytes) -> list[dict[str, Any]]:
    return load_movies(pd.read_excel(BytesIO(file_bytes)))


def load_movies(df: pd.DataFrame) -> list[dict[str, Any]]:
    title_col = get_column_name(df, ["Original Entry", "Full Title", "Movie", "Title"])
    clean_title_col = get_column_name(df, ["Title"])
    year_col = get_column_name(df, ["Year"])
    format_col = get_column_name(df, ["Format", "Movie Type", "Type"])
    watched_col = get_column_name(df, ["Watched?", "Watched", "Watch Status", "Status"])
    rating_col = get_column_name(df, ["TMDB Rating", "Rating"])
    genre_col = get_column_name(df, ["Genre", "Genres"])
    runtime_col = get_column_name(df, ["Runtime (min)", "Runtime", "Runtime Min"])
    overview_col = get_column_name(df, ["Overview", "Description", "Plot"])
    release_col = get_column_name(df, ["Release Date", "Date"])
    cover_url_col = get_column_name(df, ["Cover URL", "Poster URL", "Cover Image"])
    poster_path_col = get_column_name(df, ["Poster Path"])

    if title_col is None:
        df = pd.DataFrame(df.values)
        title_col = 0
        clean_title_col = None
        year_col = None
        format_col = 1 if len(df.columns) > 1 else None
        watched_col = 2 if len(df.columns) > 2 else None
        rating_col = genre_col = runtime_col = overview_col = release_col = cover_url_col = poster_path_col = None

    movies: list[dict[str, Any]] = []

    for _, row in df.iterrows():
        raw_title = row.get(title_col)
        if raw_title is None or pd.isna(raw_title):
            continue

        raw_title = str(raw_title).strip()
        if not raw_title or raw_title.lower() == "nan":
            continue

        if clean_title_col is not None and clean_title_col != title_col and not pd.isna(row.get(clean_title_col)):
            movie_title = str(row.get(clean_title_col)).strip()
        else:
            movie_title = clean_title(raw_title)

        if year_col is not None and not pd.isna(row.get(year_col)):
            try:
                year = int(float(row.get(year_col)))
            except Exception:
                year = extract_year(raw_title)
        else:
            year = extract_year(raw_title)

        rating = None
        if rating_col is not None and not pd.isna(row.get(rating_col)):
            try:
                rating = float(row.get(rating_col))
            except Exception:
                rating = None

        runtime = None
        if runtime_col is not None and not pd.isna(row.get(runtime_col)):
            try:
                runtime = int(float(row.get(runtime_col)))
            except Exception:
                runtime = None

        release_date = None
        if release_col is not None and not pd.isna(row.get(release_col)):
            value = row.get(release_col)
            if isinstance(value, pd.Timestamp):
                release_date = value.strftime("%Y-%m-%d")
            else:
                release_date = str(value).strip()

        poster_url = None
        if cover_url_col is not None and not pd.isna(row.get(cover_url_col)):
            poster_url = str(row.get(cover_url_col)).strip()
        elif poster_path_col is not None and not pd.isna(row.get(poster_path_col)):
            poster_path = str(row.get(poster_path_col)).strip()
            if poster_path:
                if poster_path.startswith("http"):
                    poster_url = poster_path
                else:
                    poster_url = f"https://image.tmdb.org/t/p/w342{poster_path}"

        movies.append({
            "full_title": raw_title,
            "title": movie_title,
            "year": year,
            "format": row.get(format_col) if format_col is not None else None,
            "watch_status": normalize_watch_status(row.get(watched_col)) if watched_col is not None else None,
            "rating": rating,
            "genres": str(row.get(genre_col)).strip() if genre_col is not None and not pd.isna(row.get(genre_col)) else None,
            "runtime": runtime,
            "overview": str(row.get(overview_col)).strip() if overview_col is not None and not pd.isna(row.get(overview_col)) else None,
            "release_date": release_date,
            "poster_url": poster_url,
        })

    return movies


def movie_matches(
    movie: dict[str, Any],
    genre: str | None = None,
    vibe: str | None = None,
    watch_status: str | None = None,
    min_rating: float | None = None,
    min_runtime: int | None = None,
    max_runtime: int | None = None,
    start_year: int | None = None,
    end_year: int | None = None,
) -> bool:
    genres_text = movie.get("genres") or ""
    genres_list = [g.strip() for g in genres_text.split(",") if g.strip()]
    rating = movie.get("rating")
    runtime = movie.get("runtime")
    year = movie.get("year")

    if watch_status and movie.get("watch_status") != watch_status:
        return False
    if genre and genre.lower() not in [g.lower() for g in genres_list]:
        return False
    if vibe:
        allowed = VIBE_MAP.get(vibe.lower(), [])
        if allowed and not any(g.lower() in [x.lower() for x in genres_list] for g in allowed):
            return False
    if min_rating is not None and rating is not None and rating < min_rating:
        return False
    if min_runtime is not None and runtime is not None and runtime < min_runtime:
        return False
    if max_runtime is not None and runtime is not None and runtime > max_runtime:
        return False
    if start_year is not None and year is not None and year < start_year:
        return False
    if end_year is not None and year is not None and year > end_year:
        return False
    return True


def pick_movies(
    movies: list[dict[str, Any]],
    genre: str | None,
    vibe: str | None,
    watch_status: str | None,
    min_rating: float | None,
    min_runtime: int | None,
    max_runtime: int | None,
    start_year: int | None,
    end_year: int | None,
) -> tuple[list[dict[str, Any]], int]:
    shuffled = movies[:]
    random.shuffle(shuffled)

    exact_matches: list[dict[str, Any]] = []
    backup_matches: list[dict[str, Any]] = []

    for movie in shuffled:
        if watch_status and movie.get("watch_status") != watch_status:
            continue

        candidate = {"movie": movie}
        if movie_matches(movie, genre, vibe, watch_status, min_rating, min_runtime, max_runtime, start_year, end_year):
            candidate["match_type"] = "Exact match"
            exact_matches.append(candidate)
        else:
            backup_ok = True
            if min_rating is not None and movie.get("rating") is not None and movie.get("rating") < min_rating:
                backup_ok = False
            if min_runtime is not None and movie.get("runtime") is not None and movie.get("runtime") < min_runtime:
                backup_ok = False
            if max_runtime is not None and movie.get("runtime") is not None and movie.get("runtime") > max_runtime + 20:
                backup_ok = False
            if start_year is not None and movie.get("year") is not None and movie.get("year") < start_year - 5:
                backup_ok = False
            if end_year is not None and movie.get("year") is not None and movie.get("year") > end_year + 5:
                backup_ok = False
            if backup_ok:
                candidate["match_type"] = "Close backup pick"
                backup_matches.append(candidate)

    random.shuffle(exact_matches)
    random.shuffle(backup_matches)

    picks: list[dict[str, Any]] = []
    seen: set[str] = set()
    for pool in (exact_matches, backup_matches):
        for item in pool:
            title_key = (item["movie"].get("title") or "").strip().lower()
            if not title_key or title_key in seen:
                continue
            seen.add(title_key)
            picks.append(item)
            if len(picks) >= PICKS_TO_SHOW:
                return picks, len(exact_matches)
    return picks, len(exact_matches)


def crop_text(text: str | None, length: int = 180) -> str:
    if not text:
        return "No dusty back-cover blurb was found for this tape."
    clean = " ".join(str(text).split())
    if len(clean) <= length:
        return clean
    return clean[: length - 3].rstrip() + "..."


def metric_pill(text: str | None) -> str:
    return f'<span class="vhs-pill">{text}</span>' if text else ""


def render_vhs_card(movie: dict[str, Any], label: str, match_type: str | None = None) -> None:
    title = movie.get("title") or movie.get("full_title") or "Unknown Title"
    year = str(movie.get("year")) if movie.get("year") else "Year unknown"
    runtime_text = f"{movie.get('runtime')} min" if movie.get("runtime") else None
    rating_text = f"⭐ {movie.get('rating'):.1f}" if movie.get("rating") is not None else None
    status_text = movie.get("watch_status") or "Status unknown"
    format_text = str(movie.get("format")).strip() if movie.get("format") is not None and not pd.isna(movie.get("format")) else None
    poster_url = movie.get("poster_url")
    genres = crop_text(movie.get("genres"), 64)
    overview = crop_text(movie.get("overview"), 180)
    release_date = movie.get("release_date") or "Unknown release"

    poster_html = (
        f'<img src="{poster_url}" alt="{title} poster">' if poster_url else '<div class="poster-missing">NO POSTER<br>FOUND</div>'
    )

    pills = "".join([
        metric_pill(year),
        metric_pill(runtime_text),
        metric_pill(rating_text),
        metric_pill(status_text),
        metric_pill(format_text),
    ])

    match_html = f'<div class="vhs-match">{match_type}</div>' if match_type else ""

    html = f"""
    <div class="vhs-card">
        <div class="vhs-topband"></div>
        <div class="vhs-inner">
            <div class="vhs-poster-shell">
                {poster_html}
                <div class="vhs-spine-tag">VHS</div>
            </div>
            <div class="vhs-info">
                <div class="vhs-label">{label}</div>
                <p class="vhs-title">{title}</p>
                <p class="vhs-subtitle">{release_date} • {genres}</p>
                <div class="vhs-pill-row">{pills}</div>
                <div class="vhs-overview">{overview}</div>
                <div class="vhs-foot">
                    <div class="vhs-label">STAFF SHELF</div>
                    {match_html}
                </div>
            </div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_hero(movies: list[dict[str, Any]], source_label: str) -> None:
    status_counts = pd.Series([m.get("watch_status") or "Not specified" for m in movies]).value_counts().to_dict()
    chips = "".join([f'<span class="marquee">{status}: {count}</span>' for status, count in status_counts.items()])
    st.markdown(
        f"""
        <div class="hero-card">
            <div class="hero-title">📼 Joey's Video Vault & Tape Rental</div>
            <div class="hero-sub">
                Welcome back to the neighborhood video shop: wood shelves, neon signs, staff picks, and one very committed clerk.
                Pick your mood, browse the aisles, and let the counter recommend three tapes for movie night.
            </div>
            <div class="hero-sub"><strong>Loaded from:</strong> {source_label}</div>
            <div>{chips}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_filters(movies: list[dict[str, Any]]) -> dict[str, Any]:
    available_formats = sorted({
        str(movie.get("format")).strip()
        for movie in movies
        if movie.get("format") is not None and not pd.isna(movie.get("format")) and str(movie.get("format")).strip()
    })

    with st.expander("🎞️ Need ideas? Open the counter guide", expanded=False):
        st.write("**Genres:** " + ", ".join(GENRE_HINTS))
        st.write("**Vibes:** " + ", ".join(VIBE_MAP.keys()))
        st.write("**Watched status:** Watched, Unwatched, In progress")
        if available_formats:
            st.write("**Formats in your list:** " + ", ".join(available_formats))

    st.markdown('<div class="section-kicker">Choose tonight\'s cursed rental criteria</div>', unsafe_allow_html=True)
    st.markdown('<div class="shelf-rule"></div>', unsafe_allow_html=True)

    left, right = st.columns(2)
    with left:
        genre_choice = st.selectbox("Aisle / genre", ["Any"] + GENRE_HINTS)
        vibe_choice = st.selectbox("Late-night vibe", ["Any"] + list(VIBE_MAP.keys()))
        watch_status_choice = st.selectbox("Shelf tag", ["Any", "Watched", "Unwatched", "In progress"])
    with right:
        min_rating = st.slider("Critic-counter score", 0.0, 10.0, 0.0, 0.5)
        min_runtime = st.number_input("Minimum runtime (minutes)", min_value=0, max_value=400, value=0, step=5)
        max_runtime = st.number_input("Maximum runtime (minutes)", min_value=0, max_value=400, value=0, step=5)

    year_col1, year_col2 = st.columns(2)
    with year_col1:
        start_year = st.number_input("Released after", min_value=1880, max_value=2100, value=1880, step=1)
    with year_col2:
        end_year = st.number_input("Released before", min_value=1880, max_value=2100, value=2100, step=1)

    return {
        "genre": None if genre_choice == "Any" else genre_choice,
        "vibe": None if vibe_choice == "Any" else vibe_choice,
        "watch_status": None if watch_status_choice == "Any" else watch_status_choice,
        "min_rating": None if min_rating == 0.0 else min_rating,
        "min_runtime": None if min_runtime == 0 else int(min_runtime),
        "max_runtime": None if max_runtime == 0 else int(max_runtime),
        "start_year": None if start_year == 1880 else int(start_year),
        "end_year": None if end_year == 2100 else int(end_year),
    }


def render_pick_section(movies: list[dict[str, Any]]) -> None:
    filters = render_filters(movies)

    if filters["max_runtime"] and filters["min_runtime"] and filters["max_runtime"] < filters["min_runtime"]:
        st.warning("Maximum runtime is lower than minimum runtime. Even the late-fee machine can't bend time that way.")
        return
    if filters["end_year"] and filters["start_year"] and filters["end_year"] < filters["start_year"]:
        st.warning("The end year comes before the start year. That aisle is blocked by a stack of returns.")
        return

    if st.button("📼 Ring up 3 staff picks", type="primary", use_container_width=True):
        picks, exact_count = pick_movies(movies, **filters)
        if not picks:
            st.error("No tapes matched those rules. Loosen a filter or two and ask the clerk again.")
            return

        backup_count = sum(1 for item in picks if item.get("match_type") != "Exact match")
        if backup_count:
            st.info(f"I found {exact_count} exact shelf match(es), so I added {backup_count} nearby backup pick(s) to fill the counter.")

        st.markdown('<div class="section-kicker">Tonight\'s three haunted staff picks</div>', unsafe_allow_html=True)
        st.markdown('<div class="shelf-rule"></div>', unsafe_allow_html=True)
        cols = st.columns(3)
        for idx, item in enumerate(picks, start=1):
            with cols[(idx - 1) % 3]:
                render_vhs_card(item["movie"], f"STAFF PICK #{idx}", item.get("match_type"))


def render_browse_section(movies: list[dict[str, Any]]) -> None:
    st.markdown('<div class="section-kicker">Browse the whole store</div>', unsafe_allow_html=True)
    st.markdown('<div class="browse-note">Each movie is tucked into a tape-box card so you can scan the aisles like an old-school rental shelf.</div>', unsafe_allow_html=True)
    st.markdown('<div class="shelf-rule"></div>', unsafe_allow_html=True)

    search_col, status_col, sort_col, size_col = st.columns([2.4, 1.2, 1.2, 1.0])
    with search_col:
        search_text = st.text_input("Search the shelves", placeholder="Type a title, genre, or year...")
    with status_col:
        browse_status = st.selectbox("Shelf tag", ["All", "Watched", "Unwatched", "In progress"], key="browse_status")
    with sort_col:
        sort_by = st.selectbox("Sort by", ["Title A-Z", "Year newest", "Year oldest"], key="browse_sort")
    with size_col:
        per_page = st.selectbox("Tapes per shelf", [6, 9, 12, 15], index=1, key="browse_per_page")

    filtered: list[dict[str, Any]] = []
    query = search_text.strip().lower()
    for movie in movies:
        if browse_status != "All" and movie.get("watch_status") != browse_status:
            continue
        if query:
            haystack = " ".join([
                str(movie.get("title") or ""),
                str(movie.get("genres") or ""),
                str(movie.get("year") or ""),
                str(movie.get("format") or ""),
            ]).lower()
            if query not in haystack:
                continue
        filtered.append(movie)

    if sort_by == "Title A-Z":
        filtered.sort(key=lambda m: (str(m.get("title") or "").lower(), m.get("year") or 0))
    elif sort_by == "Year newest":
        filtered.sort(key=lambda m: (m.get("year") or 0, str(m.get("title") or "").lower()), reverse=True)
    else:
        filtered.sort(key=lambda m: (m.get("year") or 9999, str(m.get("title") or "").lower()))

    if not filtered:
        st.warning("This shelf is empty. Try a different search or loosen the filter.")
        return

    total_pages = max(1, math.ceil(len(filtered) / per_page))
    page = st.number_input("Shelf page", min_value=1, max_value=total_pages, value=1, step=1)
    start = (page - 1) * per_page
    end = start + per_page
    page_movies = filtered[start:end]

    st.caption(f"Showing {start + 1}-{min(end, len(filtered))} of {len(filtered)} tapes.")

    cols = st.columns(3)
    for idx, movie in enumerate(page_movies):
        with cols[idx % 3]:
            render_vhs_card(movie, "ON THE SHELF")


def main() -> None:
    st.set_page_config(page_title="Joey's Video Vault", page_icon="📼", layout="wide")
    st.markdown(RETRO_CSS, unsafe_allow_html=True)

    uploaded_file = st.sidebar.file_uploader("Upload your movie Excel file", type=["xlsx"])
    default_excel = find_default_excel_file()

    if uploaded_file is not None:
        movies = load_movies_from_upload(uploaded_file.getvalue())
        source_label = uploaded_file.name
    elif default_excel is not None:
        movies = load_movies_from_path(str(default_excel))
        source_label = default_excel.name
    else:
        movies = []
        source_label = "No movie list loaded"

    with st.sidebar:
        st.header("Back Room")
        st.caption(f"Movie list: {source_label}")
        st.write("Inventory is pulled from your spreadsheet, just like the store ledger behind the counter.")

    if not movies:
        st.error("No movies found. Upload your Excel file in the sidebar or place MovieList.xlsx next to this app.")
        return

    render_hero(movies, source_label)

    nav = st.radio(
        "Store directory",
        ["📼 Rental Counter", "🎬 Browse the Whole Store"],
        horizontal=True,
        key="top_nav",
        label_visibility="visible",
    )

    if nav == "📼 Rental Counter":
        render_pick_section(movies)
    else:
        render_browse_section(movies)


if __name__ == "__main__":
    main()
