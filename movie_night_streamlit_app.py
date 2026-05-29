"""
Movie Night Randomizer - Streamlit App
--------------------------------------
Run locally:
    pip install streamlit pandas openpyxl requests
    streamlit run movie_night_streamlit_app.py

Deploy on Streamlit Community Cloud:
    1. Put this file, requirements.txt, and your MovieList.xlsx file in a GitHub repo.
    2. Add your TMDb API key in Streamlit secrets as:
       TMDB_API_KEY = "your_key_here"
    3. Deploy the app and open it on your iPhone in Safari.
"""

from __future__ import annotations

import random
import html
from pathlib import Path
from typing import Any

import pandas as pd
import requests
import streamlit as st

# Keeps the app usable with the same API key already used in your desktop script.
# For deployment, use Streamlit secrets instead of committing an API key to GitHub.
TMDB_API_KEY_DEFAULT = "b477be91e21ce4d356bafdc4b9c73a4b"
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
        --midnight: #08000f;
        --void: #020104;
        --bruise-purple: #3a145c;
        --neon-purple: #b45cff;
        --neon-teal: #14f7d4;
        --neon-red: #ff174c;
        --warning-amber: #ffd166;
        --paper: #fff0c2;
        --dust: #c9b47a;
        --grave-green: #9dff6e;
    }

    .stApp {
        background:
            radial-gradient(circle at 14% 9%, rgba(255, 23, 76, 0.28), transparent 26%),
            radial-gradient(circle at 86% 7%, rgba(20, 247, 212, 0.16), transparent 24%),
            radial-gradient(circle at 50% 110%, rgba(180, 92, 255, 0.26), transparent 40%),
            repeating-linear-gradient(90deg, rgba(255, 209, 102, 0.035) 0 2px, transparent 2px 28px),
            repeating-linear-gradient(0deg, rgba(255,255,255,0.028) 0 1px, transparent 1px 5px),
            linear-gradient(180deg, #090013 0%, #210716 43%, #09000f 100%);
        color: var(--paper);
    }

    .stApp:before {
        content: "";
        position: fixed;
        inset: 0;
        pointer-events: none;
        background:
            linear-gradient(rgba(255,255,255,0.035) 50%, rgba(0,0,0,0.035) 50%),
            radial-gradient(circle at center, transparent 0%, rgba(0,0,0,0.34) 100%);
        background-size: 100% 4px, 100% 100%;
        z-index: 999999;
        mix-blend-mode: soft-light;
    }

    .block-container {
        padding-top: 1rem;
        padding-bottom: 3rem;
        max-width: 1180px;
    }

    header[data-testid="stHeader"] {
        background: linear-gradient(90deg, rgba(8,0,15,0.98), rgba(58,20,92,0.94), rgba(20, 247, 212, 0.10));
        border-bottom: 3px double rgba(255, 209, 102, 0.72);
        box-shadow: 0 0 22px rgba(255, 23, 76, 0.22);
    }

    [data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stStatusWidget"] {
        color: var(--paper) !important;
    }

    h1, h2, h3, h4, h5, h6, p, span, label, div {
        text-shadow: 0 0 1px rgba(0,0,0,0.4);
    }

    .hero-card {
        position: relative;
        border: 3px double rgba(255, 209, 102, 0.85);
        border-radius: 22px;
        padding: 1.8rem;
        margin-bottom: 1.1rem;
        background:
            linear-gradient(135deg, rgba(10, 3, 18, 0.97), rgba(60, 7, 27, 0.94) 50%, rgba(5, 2, 9, 0.98)),
            repeating-linear-gradient(45deg, rgba(255,209,102,0.06) 0 8px, transparent 8px 18px);
        box-shadow:
            0 0 26px rgba(255, 23, 76, 0.38),
            0 0 52px rgba(20, 247, 212, 0.10),
            inset 0 0 42px rgba(0, 0, 0, 0.82);
        overflow: hidden;
    }

    .hero-card:before {
        content: "BE KIND • REWIND • OR ELSE";
        position: absolute;
        right: -44px;
        top: 24px;
        transform: rotate(18deg);
        color: rgba(255, 209, 102, 0.17);
        font-size: 2.2rem;
        font-weight: 950;
        letter-spacing: 0.08em;
    }

    .hero-card h1 {
        font-size: clamp(2.4rem, 7vw, 5.2rem);
        line-height: 0.9;
        margin: 0.25rem 0 0.7rem 0;
        color: var(--warning-amber);
        text-shadow:
            4px 4px 0 #5f0a22,
            -2px -2px 0 rgba(20, 247, 212, 0.45),
            0 0 18px rgba(255, 23, 76, 0.72),
            0 0 35px rgba(180, 92, 255, 0.45);
        letter-spacing: 0.055em;
    }

    .hero-card p {
        font-size: 1.08rem;
        max-width: 880px;
        color: #fff0c2;
    }

    .kicker {
        color: var(--neon-teal);
        text-transform: uppercase;
        letter-spacing: 0.18em;
        font-weight: 950;
        font-size: 0.82rem;
        text-shadow: 0 0 9px rgba(20,247,212,0.82);
    }

    .neon-directory, .vhs-card, .collection-card {
        border: 2px solid rgba(255, 209, 102, 0.42);
        border-radius: 16px;
        padding: 1rem 1.1rem;
        margin: 0.8rem 0 1rem 0;
        background:
            linear-gradient(135deg, rgba(17, 5, 28, 0.98), rgba(65, 8, 31, 0.95)),
            repeating-linear-gradient(90deg, rgba(20,247,212,0.035) 0 1px, transparent 1px 18px);
        box-shadow: 8px 8px 0 rgba(255, 23, 76, 0.24), 0 0 20px rgba(180, 92, 255, 0.14);
    }

    .vhs-label {
        display: inline-block;
        padding: 0.28rem 0.7rem;
        border-radius: 5px;
        background: linear-gradient(90deg, rgba(255, 23, 76, 0.35), rgba(58, 20, 92, 0.55));
        border: 1px solid rgba(255, 209, 102, 0.82);
        color: var(--warning-amber);
        font-size: 0.76rem;
        font-weight: 950;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        box-shadow: 0 0 11px rgba(255,23,76,0.24);
    }

    div[data-testid="stSidebar"] {
        background:
            linear-gradient(180deg, #08000f 0%, #2b0719 52%, #050008 100%),
            repeating-linear-gradient(45deg, rgba(255,209,102,0.04) 0 8px, transparent 8px 18px);
        border-right: 3px double rgba(255, 209, 102, 0.52);
    }

    div[data-testid="stSidebar"] * { color: var(--paper); }

    /* Big top navigation, intentionally visible on iPhone/Safari. */
    div[role="radiogroup"] {
        background: rgba(5, 0, 10, 0.86);
        border: 2px solid rgba(255, 209, 102, 0.48);
        border-radius: 16px;
        padding: 0.55rem;
        box-shadow: 0 0 22px rgba(20,247,212,0.12), inset 0 0 18px rgba(255,23,76,0.12);
    }

    div[role="radiogroup"] label {
        background: linear-gradient(90deg, rgba(255,23,76,0.20), rgba(58,20,92,0.55));
        border: 1px solid rgba(255, 209, 102, 0.35);
        border-radius: 12px;
        padding: 0.42rem 0.55rem;
        margin-right: 0.25rem;
    }

    div[role="radiogroup"] label:has(input:checked) {
        background: linear-gradient(90deg, rgba(255,23,76,0.72), rgba(20,247,212,0.22));
        border-color: rgba(20, 247, 212, 0.86);
        box-shadow: 0 0 16px rgba(255,23,76,0.35);
    }

    /* Keep Streamlit tabs readable too, if Streamlit renders them in future versions. */
    div[data-baseweb="tab-list"] {
        gap: 0.35rem;
        background: rgba(5, 0, 10, 0.88);
        border: 2px solid rgba(255, 209, 102, 0.42);
        border-radius: 14px;
        padding: 0.4rem;
        position: sticky;
        top: 0.3rem;
        z-index: 999;
        backdrop-filter: blur(6px);
    }

    button[data-baseweb="tab"] {
        color: #fff0c2 !important;
        background: rgba(255, 23, 76, 0.20) !important;
        border: 1px solid rgba(255, 209, 102, 0.35) !important;
        border-radius: 10px !important;
        padding: 0.5rem 0.75rem !important;
        min-height: 2.8rem;
    }

    button[data-baseweb="tab"] p {
        color: #fff0c2 !important;
        font-weight: 950 !important;
        font-size: 0.98rem !important;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(90deg, rgba(255,23,76,0.78), rgba(58,20,92,0.94)) !important;
        border-color: rgba(20, 247, 212, 0.8) !important;
        box-shadow: 0 0 16px rgba(20,247,212,0.25), 0 0 18px rgba(255,23,76,0.35);
    }

    div.stButton > button {
        border: 2px solid var(--warning-amber);
        border-radius: 8px;
        background: linear-gradient(90deg, #ff174c, #ffd166 52%, #14f7d4);
        color: #08000f;
        font-weight: 950;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        box-shadow: 0 0 24px rgba(255, 23, 76, 0.48), 0 0 18px rgba(20,247,212,0.16);
    }

    div[data-testid="stMetric"] {
        background: rgba(8, 0, 15, 0.55);
        border: 1px solid rgba(255, 209, 102, 0.24);
        border-radius: 12px;
        padding: 0.6rem;
    }

    .stSelectbox label, .stSlider label, .stNumberInput label, .stTextInput label, .stSelectSlider label {
        color: #ffd166 !important;
        font-weight: 900 !important;
    }

    @media (max-width: 640px) {
        .block-container { padding-left: 0.75rem; padding-right: 0.75rem; }
        .hero-card { padding: 1.1rem; }
        div[data-baseweb="tab-list"], div[role="radiogroup"] { overflow-x: auto; flex-wrap: nowrap; }
        button[data-baseweb="tab"] { min-width: max-content; }
    }


    .storefront-marquee {
        border: 4px solid rgba(255, 213, 79, 0.95);
        border-radius: 18px;
        padding: 0.95rem 1.1rem;
        margin: 0.9rem 0 1.15rem 0;
        background:
            linear-gradient(90deg, rgba(255,23,76,0.32), rgba(24,5,40,0.98) 28%, rgba(20,247,212,0.22) 70%, rgba(255,209,102,0.22)),
            repeating-linear-gradient(90deg, rgba(255,209,102,0.11) 0 8px, transparent 8px 18px);
        box-shadow: 0 0 28px rgba(255,23,76,0.52), inset 0 0 28px rgba(0,0,0,0.62);
    }

    .storefront-marquee h2 {
        margin: 0;
        color: #ffd166;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        text-shadow: 3px 3px 0 #4b0418, -2px -2px 0 rgba(20,247,212,0.45), 0 0 18px rgba(255,23,76,0.65);
    }

    .dusty-note {
        background: #f4d78a;
        color: #1a0717 !important;
        border: 2px solid #4b0418;
        border-radius: 3px;
        padding: 0.9rem 1rem;
        transform: rotate(-0.5deg);
        box-shadow: 6px 7px 0 rgba(0,0,0,0.32);
        font-weight: 700;
    }

    .shelf-row {
        border-bottom: 18px solid #3b170e;
        box-shadow: 0 12px 0 #160803, 0 0 18px rgba(255,23,76,0.18);
        margin: 0.5rem 0 1.4rem 0;
        padding: 0.35rem 0.35rem 0.75rem 0.35rem;
        background: linear-gradient(180deg, rgba(255,209,102,0.06), rgba(0,0,0,0.18));
    }

    .vhs-shelf-card {
        position: relative;
        min-height: 430px;
        padding: 0.65rem;
        border-radius: 7px;
        background:
            linear-gradient(90deg, #130812 0 10px, #f2d48a 10px 17px, #241029 17px 100%),
            repeating-linear-gradient(0deg, rgba(255,255,255,0.04) 0 2px, transparent 2px 9px);
        border: 2px solid rgba(255, 209, 102, 0.46);
        box-shadow: 7px 7px 0 rgba(0,0,0,0.55), 0 0 18px rgba(180,92,255,0.18);
        overflow: hidden;
    }

    .vhs-shelf-card:before {
        content: "VHS";
        position: absolute;
        top: 0.55rem;
        left: -0.25rem;
        transform: rotate(-90deg);
        color: #130812;
        background: #ffd166;
        padding: 0.08rem 0.35rem;
        font-size: 0.62rem;
        font-weight: 950;
        letter-spacing: 0.1em;
        z-index: 2;
    }

    .vhs-poster-frame {
        background: #07040a;
        border: 3px solid #111;
        border-radius: 5px;
        padding: 0.25rem;
        box-shadow: inset 0 0 0 2px rgba(255,255,255,0.08), 0 0 14px rgba(20,247,212,0.18);
    }

    .vhs-title-strip {
        margin-top: 0.55rem;
        padding: 0.45rem 0.5rem;
        background: #f4d78a;
        color: #1a0717 !important;
        border: 1px dashed #4b0418;
        min-height: 5.2rem;
        font-family: "Courier New", monospace;
        font-size: 0.88rem;
        font-weight: 900;
        line-height: 1.15;
    }

    .vhs-title-strip small {
        display: block;
        margin-top: 0.35rem;
        color: #4b0418 !important;
        font-weight: 800;
    }

    .rental-card-wrap {
        border-radius: 12px;
        border: 2px solid rgba(255,209,102,0.56);
        padding: 0.8rem;
        margin: 1rem 0;
        background:
            linear-gradient(90deg, #150915 0 22px, #f4d78a 22px 34px, #2b0b29 34px 100%),
            repeating-linear-gradient(0deg, rgba(255,255,255,0.04) 0 2px, transparent 2px 8px);
        box-shadow: 9px 9px 0 rgba(0,0,0,0.46), 0 0 22px rgba(255,23,76,0.22);
    }

    .top-nav-help {
        border: 2px dashed rgba(20,247,212,0.8);
        background: rgba(20,247,212,0.10);
        border-radius: 14px;
        padding: 0.75rem 0.9rem;
        color: #fff0c2;
        font-weight: 800;
    }

    /* Extra creepy video-store polish: visible controls and VHS shelf texture. */
    .stRadio [role="radiogroup"] {
        display: flex;
        gap: 0.75rem;
        flex-wrap: wrap;
    }

    .stRadio [role="radiogroup"] label {
        min-width: 240px;
        justify-content: center;
    }

    .stRadio [role="radiogroup"] p {
        color: #fff0c2 !important;
        font-weight: 950 !important;
        font-size: 1.02rem !important;
    }

    .vhs-shelf-card {
        background:
            linear-gradient(90deg, #050006 0 9px, #ff174c 9px 13px, #f4d78a 13px 22px, #1b0621 22px 100%),
            radial-gradient(circle at 30% 18%, rgba(20,247,212,0.12), transparent 24%),
            repeating-linear-gradient(0deg, rgba(255,255,255,0.045) 0 2px, transparent 2px 9px) !important;
    }

    .vhs-poster-frame img {
        filter: contrast(1.08) saturate(0.88) sepia(0.08);
    }

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
    return VALID_WATCH_STATUSES.get(normalized)


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
    from io import BytesIO
    return load_movies(pd.read_excel(BytesIO(file_bytes)))


def load_movies(df: pd.DataFrame) -> list[dict[str, Any]]:
    title_col = get_column_name(df, ["Original Entry", "Full Title", "Movie", "Title"])
    clean_title_col = get_column_name(df, ["Title"])
    year_col = get_column_name(df, ["Year"])
    format_col = get_column_name(df, ["Format", "Movie Type", "Type"])
    watched_col = get_column_name(df, ["Watched?", "Watched", "Watch Status", "Status"])

    if title_col is None:
        # Fallback for the original no-header format: col 0 = title, col 1 = format, col 2 = watched status.
        df = pd.DataFrame(df.values)
        title_col = 0
        clean_title_col = None
        year_col = None
        format_col = 1 if len(df.columns) > 1 else None
        watched_col = 2 if len(df.columns) > 2 else None

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

        movies.append({
            "full_title": raw_title,
            "title": movie_title,
            "year": year,
            "format": row.get(format_col) if format_col is not None else None,
            "watch_status": normalize_watch_status(row.get(watched_col)) if watched_col is not None else None,
        })

    return movies


@st.cache_data(show_spinner=False)
def tmdb_search(movie_title: str, year: int | None, api_key: str) -> dict[str, Any] | None:
    url = "https://api.themoviedb.org/3/search/movie"
    params: dict[str, Any] = {"api_key": api_key, "query": movie_title}
    if year:
        params["year"] = year

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data.get("results"):
            return data["results"][0]
    except Exception:
        return None
    return None


@st.cache_data(show_spinner=False)
def get_movie_details(movie_id: int, api_key: str) -> dict[str, Any]:
    url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    try:
        response = requests.get(url, params={"api_key": api_key}, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception:
        return {}


def poster_url_from_path(poster_path: str | None, width: int = 342) -> str | None:
    if not poster_path:
        return None
    return f"https://image.tmdb.org/t/p/w{width}{poster_path}"


@st.cache_data(show_spinner=False)
def get_movie_poster_url(movie_title: str, year: int | None, api_key: str) -> str | None:
    """Fast, failure-safe poster lookup for the browse shelf.

    The collection page can show many movies at once, so this uses a short
    timeout and fails quietly. That keeps the app from feeling broken if TMDb
    is slow or unreachable.
    """
    if not api_key or not movie_title:
        return None

    url = "https://api.themoviedb.org/3/search/movie"
    params: dict[str, Any] = {"api_key": api_key, "query": movie_title}
    if year:
        params["year"] = year

    try:
        response = requests.get(url, params=params, timeout=0.75)
        response.raise_for_status()
        data = response.json()
        if data.get("results"):
            return poster_url_from_path(data["results"][0].get("poster_path"))
    except Exception:
        return None
    return None


def format_year_for_display(movie: dict[str, Any]) -> str:
    return str(movie.get("year")) if movie.get("year") else "Year unknown"


def normalize_for_search(value: Any) -> str:
    return str(value or "").strip().lower()


def movie_matches(
    details: dict[str, Any],
    genre: str | None = None,
    vibe: str | None = None,
    min_rating: float | None = None,
    min_runtime: int | None = None,
    max_runtime: int | None = None,
    start_year: int | None = None,
    end_year: int | None = None,
) -> bool:
    genres = [g["name"] for g in details.get("genres", [])]
    rating = details.get("vote_average", 0) or 0
    runtime = details.get("runtime", 0) or 0

    release_year = None
    release_date = details.get("release_date", "")
    if release_date:
        try:
            release_year = int(release_date[:4])
        except Exception:
            pass

    if genre and genre.lower() not in [g.lower() for g in genres]:
        return False

    if vibe:
        allowed = VIBE_MAP.get(vibe.lower(), [])
        if allowed and not any(g in genres for g in allowed):
            return False

    if min_rating is not None and rating < min_rating:
        return False
    if min_runtime is not None and runtime and runtime < min_runtime:
        return False
    if max_runtime is not None and runtime and runtime > max_runtime:
        return False
    if start_year is not None and release_year and release_year < start_year:
        return False
    if end_year is not None and release_year and release_year > end_year:
        return False

    return True


def movie_matches_watch_status(movie: dict[str, Any], watch_status: str | None = None) -> bool:
    if not watch_status:
        return True
    return movie.get("watch_status") == watch_status


def get_api_key() -> str:
    try:
        secret_key = st.secrets.get("TMDB_API_KEY", "")
    except Exception:
        secret_key = ""
    return st.session_state.get("tmdb_api_key") or secret_key or TMDB_API_KEY_DEFAULT


def pick_movies(
    movies: list[dict[str, Any]],
    api_key: str,
    genre: str | None,
    vibe: str | None,
    watch_status: str | None,
    min_rating: float | None,
    min_runtime: int | None,
    max_runtime: int | None,
    start_year: int | None,
    end_year: int | None,
) -> tuple[list[dict[str, Any]], int, int]:
    shuffled_movies = movies[:]
    random.shuffle(shuffled_movies)

    exact_matches: list[dict[str, Any]] = []
    close_backup_matches: list[dict[str, Any]] = []
    tmdb_hits = 0

    for movie in shuffled_movies:
        if not movie_matches_watch_status(movie, watch_status):
            continue

        search = tmdb_search(movie["title"], movie["year"], api_key)
        if not search:
            continue

        tmdb_hits += 1
        details = get_movie_details(search["id"], api_key)
        candidate = {"movie": movie, "details": details}

        if movie_matches(
            details,
            genre=genre,
            vibe=vibe,
            min_rating=min_rating,
            min_runtime=min_runtime,
            max_runtime=max_runtime,
            start_year=start_year,
            end_year=end_year,
        ):
            candidate["match_type"] = "Exact match"
            exact_matches.append(candidate)
        else:
            candidate["match_type"] = "Close backup pick"
            close_backup_matches.append(candidate)

    random.shuffle(exact_matches)
    random.shuffle(close_backup_matches)

    chosen_movies: list[dict[str, Any]] = []
    seen_titles: set[str] = set()

    def add_unique_movies(candidates: list[dict[str, Any]]) -> None:
        for candidate in candidates:
            title_key = (
                candidate.get("details", {}).get("title")
                or candidate.get("movie", {}).get("title")
                or ""
            ).strip().lower()
            if not title_key or title_key in seen_titles:
                continue
            chosen_movies.append(candidate)
            seen_titles.add(title_key)
            if len(chosen_movies) >= PICKS_TO_SHOW:
                break

    add_unique_movies(exact_matches)
    if len(chosen_movies) < PICKS_TO_SHOW:
        add_unique_movies(close_backup_matches)

    return chosen_movies, len(exact_matches), tmdb_hits


def display_movie_card(index: int, candidate: dict[str, Any], api_key: str | None = None) -> None:
    movie = candidate["movie"]
    details = candidate["details"]
    title = details.get("title") or movie.get("title")
    genres = ", ".join([g["name"] for g in details.get("genres", [])]) or "Unknown"
    runtime = details.get("runtime")
    overview = details.get("overview") or "No overview available. This one is mysterious. Very artsy. Possibly cursed."
    poster_url = poster_url_from_path(details.get("poster_path"))

    st.markdown("<div class='rental-card-wrap'>", unsafe_allow_html=True)
    with st.container(border=False):
        st.markdown(f"<span class='vhs-label'>Staff Pick #{index}</span>", unsafe_allow_html=True)
        poster_col, info_col = st.columns([1, 3])
        with poster_col:
            if poster_url:
                st.image(poster_url, use_container_width=True)
            else:
                st.markdown(
                    """
                    <div class="collection-card" style="min-height: 220px; display:flex; align-items:center; justify-content:center; text-align:center;">
                        <span class="vhs-label">No Poster<br/>Found</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        with info_col:
            st.subheader(f"📼 {title}")
            st.caption(candidate.get("match_type", "Exact match"))

            col1, col2, col3 = st.columns(3)
            col1.metric("Counter score", f"{details.get('vote_average', 'Unknown')}/10")
            col2.metric("Tape length", f"{runtime} min" if runtime else "Unknown")
            col3.metric("Shelf tag", movie.get("watch_status") or "Not specified")

            st.write(f"**Release date:** {details.get('release_date') or 'Unknown'}")
            st.write(f"**Aisles:** {genres}")
            if movie.get("format") is not None and not pd.isna(movie.get("format")):
                st.write(f"**Format:** {movie.get('format')}")
            st.write(overview)
    st.markdown("</div>", unsafe_allow_html=True)


def display_collection_tab(movies: list[dict[str, Any]], api_key: str) -> None:
    st.markdown(
        """
        <div class="storefront-marquee">
            <h2>🕸️ Browse the Whole Store</h2>
        </div>
        <div class="dusty-note">
            Browse every tape in the collection like VHS boxes sitting on old wooden shelves. Poster art comes from TMDb; use the search light and shelf tags to narrow the aisle.
        </div>
        """,
        unsafe_allow_html=True,
    )

    search_col, status_col, sort_col = st.columns([2, 1, 1])
    with search_col:
        catalog_search = st.text_input("🔦 Search the shelves", placeholder="Try Alien, Batman, 1999, DVD...")
    with status_col:
        catalog_status = st.selectbox("📼 Shelf tag", ["All", "Watched", "Unwatched", "In progress", "Not specified"], key="collection_status")
    with sort_col:
        catalog_sort = st.selectbox("🕸️ Sort by", ["Title A-Z", "Title Z-A", "Year newest", "Year oldest"], key="collection_sort")

    filtered_movies = movies[:]
    if catalog_status != "All":
        if catalog_status == "Not specified":
            filtered_movies = [m for m in filtered_movies if not m.get("watch_status")]
        else:
            filtered_movies = [m for m in filtered_movies if m.get("watch_status") == catalog_status]

    query = normalize_for_search(catalog_search)
    if query:
        filtered_movies = [
            m for m in filtered_movies
            if query in normalize_for_search(m.get("title"))
            or query in normalize_for_search(m.get("full_title"))
            or query in normalize_for_search(m.get("format"))
            or query in normalize_for_search(m.get("watch_status"))
            or query in normalize_for_search(m.get("year"))
        ]

    if catalog_sort == "Title A-Z":
        filtered_movies.sort(key=lambda m: normalize_for_search(m.get("title")))
    elif catalog_sort == "Title Z-A":
        filtered_movies.sort(key=lambda m: normalize_for_search(m.get("title")), reverse=True)
    elif catalog_sort == "Year newest":
        filtered_movies.sort(key=lambda m: m.get("year") or 0, reverse=True)
    elif catalog_sort == "Year oldest":
        filtered_movies.sort(key=lambda m: m.get("year") or 9999)

    st.caption(f"Showing {len(filtered_movies)} of {len(movies)} tapes in the collection.")

    page_size = st.select_slider("Tapes per shelf page", options=[8, 12, 16, 24], value=12)
    load_posters = st.checkbox(
        "🖼️ Load poster art for this shelf page",
        value=False,
        help="Poster art comes from TMDb. Turn this on to pull artwork for the current shelf page; leave it off for instant VHS placeholder boxes.",
    )
    max_page = max(1, (len(filtered_movies) + page_size - 1) // page_size)
    page = st.number_input("Shelf page", min_value=1, max_value=max_page, value=1, step=1)
    start = (page - 1) * page_size
    end = start + page_size
    visible_movies = filtered_movies[start:end]

    if not visible_movies:
        st.warning("This shelf is just dust and one suspicious cobweb. Try a different search or filter.")
        return

    cols_per_row = 4
    for row_start in range(0, len(visible_movies), cols_per_row):
        st.markdown("<div class='shelf-row'>", unsafe_allow_html=True)
        cols = st.columns(cols_per_row)
        for col, movie in zip(cols, visible_movies[row_start:row_start + cols_per_row]):
            with col:
                st.markdown("<div class='vhs-shelf-card'>", unsafe_allow_html=True)
                poster_url = get_movie_poster_url(movie.get("title", ""), movie.get("year"), api_key) if load_posters and api_key else None
                if poster_url:
                    st.markdown("<div class='vhs-poster-frame'>", unsafe_allow_html=True)
                    st.image(poster_url, use_container_width=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.markdown(
                        """
                        <div class="vhs-poster-frame" style="height: 250px; display:flex; align-items:center; justify-content:center; text-align:center;">
                            <span class="vhs-label">Poster<br/>Missing</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                title = html.escape(str(movie.get('title', 'Unknown title')))
                meta = html.escape(f"{format_year_for_display(movie)} · {movie.get('watch_status') or 'Not specified'}")
                fmt = ""
                if movie.get("format") is not None and not pd.isna(movie.get("format")):
                    fmt = f"<small>Format: {html.escape(str(movie.get('format')))}</small>"
                st.markdown(
                    f"<div class='vhs-title-strip'>{title}<small>{meta}</small>{fmt}</div>",
                    unsafe_allow_html=True,
                )
                st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


def main() -> None:
    st.set_page_config(page_title="Joey's Haunted Video Vault", page_icon="📼", layout="wide")

    st.markdown(RETRO_CSS, unsafe_allow_html=True)

    st.markdown(
        """
        <div class="hero-card">
            <div class="kicker">📼 Open until the fog rolls in · Late fees paid in screams</div>
            <h1>Joey's Haunted Video Vault</h1>
            <p>The neon sign is half-burned out. The CRT in the corner plays static. Somewhere between the horror aisle and the staff-only curtain, a dusty clerk is ready to pull three tapes from the forbidden shelf.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    uploaded_file = st.sidebar.file_uploader("📦 Slide your inventory under the door (.xlsx)", type=["xlsx"])
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
        st.header("🧛 Night Clerk Counter")
        st.caption(f"Inventory ledger: {source_label}")
        st.text_input(
            "TMDb API key / back-room password",
            type="password",
            key="tmdb_api_key",
            help="Optional if your key is stored in Streamlit secrets. The included default key is for your local version only.",
        )

    if not movies:
        st.error("The shelves are empty. Upload your Excel inventory in the sidebar or place MovieList.xlsx next to this app.")
        return

    api_key = get_api_key()
    status_counts = pd.Series([m.get("watch_status") or "Not specified" for m in movies]).value_counts().to_dict()
    st.caption(
        f"Cataloged {len(movies)} tapes from {source_label}. "
        + " | ".join(f"{status}: {count}" for status, count in status_counts.items())
    )

    st.markdown("""
        <div class="storefront-marquee">
            <h2>Store Directory</h2>
        </div>
        <div class="top-nav-help">
            Use the buttons below to switch departments. <strong>Browse the Whole Store</strong> is the full movie-list shelf with poster artwork.
        </div>
        """, unsafe_allow_html=True)

    # Big, high-contrast top navigation.
    # Keep the internal option values plain so Streamlit version differences
    # around emoji labels cannot break the section switch.
    active_section = st.radio(
        "Choose your department",
        options=["rental_counter", "browse_store"],
        format_func=lambda value: {
            "rental_counter": "📼 Haunted Rental Counter",
            "browse_store": "🕸️ Browse the Whole Store",
        }[value],
        horizontal=True,
        label_visibility="collapsed",
    )

    if active_section == "rental_counter":
        available_formats = sorted({
            str(movie.get("format")).strip()
            for movie in movies
            if movie.get("format") is not None and not pd.isna(movie.get("format")) and str(movie.get("format")).strip()
        })

        with st.expander("📋 Read the moldy staff cheat sheet", expanded=True):
            st.write("**Cursed aisles / genres:** " + ", ".join(GENRE_HINTS))
            st.write("**Possible moods:** " + ", ".join(VIBE_MAP.keys()))
            st.write("**Shelf tags:** Watched, Unwatched, In progress")
            if available_formats:
                st.write("**Formats in the back room:** " + ", ".join(available_formats))

        st.markdown(
            """
            <div class="vhs-card">
                <span class="vhs-label">Rental Form</span>
                <p style="margin-top:0.75rem; margin-bottom:0;">Choose your aisle, mood, and house rules. Leave anything as <strong>Any</strong> and the clerk will choose from the shadows.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns(2)
        with col1:
            genre_choice = st.selectbox("🩸 Cursed aisle / genre", ["Any"] + GENRE_HINTS)
            vibe_choice = st.selectbox("🕯️ Tonight's omen", ["Any"] + list(VIBE_MAP.keys()))
            watch_status_choice = st.selectbox("📼 Shelf tag", ["Any", "Watched", "Unwatched", "In progress"])
        with col2:
            min_rating = st.slider("⭐ Minimum crypt-critic score", 0.0, 10.0, 0.0, 0.5)
            min_runtime = st.number_input("⏱️ Minimum runtime", min_value=0, max_value=400, value=0, step=5)
            max_runtime = st.number_input("⏳ Maximum runtime", min_value=0, max_value=400, value=0, step=5)

        year_col1, year_col2 = st.columns(2)
        with year_col1:
            start_year = st.number_input("Oldest release year", min_value=1880, max_value=2100, value=1880, step=1)
        with year_col2:
            end_year = st.number_input("Newest release year", min_value=1880, max_value=2100, value=2100, step=1)

        genre = None if genre_choice == "Any" else genre_choice
        vibe = None if vibe_choice == "Any" else vibe_choice
        watch_status = None if watch_status_choice == "Any" else watch_status_choice
        rating_filter = None if min_rating == 0.0 else min_rating
        min_runtime_filter = None if min_runtime == 0 else int(min_runtime)
        max_runtime_filter = None if max_runtime == 0 else int(max_runtime)
        start_year_filter = None if start_year == 1880 else int(start_year)
        end_year_filter = None if end_year == 2100 else int(end_year)

        if max_runtime_filter and min_runtime_filter and max_runtime_filter < min_runtime_filter:
            st.warning("The return slot jammed: maximum runtime is lower than minimum runtime.")
            return

        if end_year_filter and start_year_filter and end_year_filter < start_year_filter:
            st.warning("The time machine is rewinding too hard: newest year is earlier than oldest year.")
            return

        if st.button("📼 Ring the bell for 3 cursed staff picks", type="primary", use_container_width=True):
            if not api_key or api_key == "YOUR_API_KEY":
                st.error("The night clerk needs the TMDb back-room password. Add your API key in the sidebar or Streamlit secrets.")
                return

            with st.spinner("Checking the shelves, listening for whispers behind the horror aisle, and warming up the tracking... 🙃"):
                chosen_movies, exact_count, tmdb_hits = pick_movies(
                    movies=movies,
                    api_key=api_key,
                    genre=genre,
                    vibe=vibe,
                    watch_status=watch_status,
                    min_rating=rating_filter,
                    min_runtime=min_runtime_filter,
                    max_runtime=max_runtime_filter,
                    start_year=start_year_filter,
                    end_year=end_year_filter,
                )

            if not chosen_movies:
                st.error(
                    "No tapes survived the ritual. Try loosening a few filters, or check that your Excel file and TMDb API key are working."
                )
                return

            backup_count = sum(1 for item in chosen_movies if item.get("match_type") != "Exact match")
            if len(chosen_movies) < PICKS_TO_SHOW:
                st.warning(
                    f"I could only drag {len(chosen_movies)} usable option(s) out of the basement. TMDb returned {tmdb_hits} usable movie lookup(s). "
                    "Try fewer filters for a fuller rental bag."
                )
            elif backup_count:
                st.info(
                    f"Found {exact_count} exact shelf match(es), so I added {backup_count} nearby haunted staff pick(s) to make sure you get three options."
                )

            st.header(f"Tonight's {len(chosen_movies)} cursed staff pick(s)")
            for index, candidate in enumerate(chosen_movies, start=1):
                display_movie_card(index, candidate, api_key=api_key)

    if active_section == "browse_store":
        if not api_key or api_key == "YOUR_API_KEY":
            st.warning("Poster art needs the TMDb back-room password. Add your API key in the sidebar or Streamlit secrets. The shelves will still load with VHS placeholders.")
        display_collection_tab(movies, api_key)


if __name__ == "__main__":
    main()
