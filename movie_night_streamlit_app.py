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
        --vault-bg: #14051f;
        --vault-purple: #2d0a45;
        --vault-pink: #ff4fd8;
        --vault-cyan: #45f3ff;
        --vault-yellow: #ffd166;
        --vault-cream: #fff3d6;
    }

    .stApp {
        background:
            radial-gradient(circle at 15% 10%, rgba(255, 79, 216, 0.16), transparent 28%),
            radial-gradient(circle at 85% 0%, rgba(69, 243, 255, 0.14), transparent 26%),
            linear-gradient(180deg, #12041d 0%, #230735 52%, #14051f 100%);
        color: var(--vault-cream);
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1120px;
    }

    .hero-card {
        border: 2px solid rgba(255, 79, 216, 0.78);
        border-radius: 24px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        background:
            linear-gradient(135deg, rgba(45, 10, 69, 0.94), rgba(15, 4, 31, 0.92)),
            repeating-linear-gradient(0deg, rgba(255,255,255,0.04), rgba(255,255,255,0.04) 1px, transparent 1px, transparent 7px);
        box-shadow: 0 0 32px rgba(255, 79, 216, 0.22), inset 0 0 22px rgba(69, 243, 255, 0.08);
    }

    .hero-card h1 {
        font-size: clamp(2.35rem, 6vw, 4.5rem);
        line-height: 0.95;
        margin: 0.25rem 0 0.7rem 0;
        color: var(--vault-yellow);
        text-shadow: 3px 3px 0 #5b1b73, 0 0 18px rgba(255, 209, 102, 0.45);
        letter-spacing: 0.03em;
    }

    .hero-card p {
        font-size: 1.15rem;
        max-width: 780px;
        color: #ffeec7;
    }

    .kicker {
        color: var(--vault-cyan);
        text-transform: uppercase;
        letter-spacing: 0.18em;
        font-weight: 800;
        font-size: 0.82rem;
    }

    .vhs-card {
        border: 2px solid rgba(69, 243, 255, 0.65);
        border-radius: 18px;
        padding: 1.05rem 1.15rem;
        margin: 0.8rem 0 1rem 0;
        background: linear-gradient(135deg, rgba(20, 5, 31, 0.98), rgba(47, 8, 72, 0.96));
        box-shadow: 8px 8px 0 rgba(255, 79, 216, 0.22), 0 0 18px rgba(69, 243, 255, 0.1);
    }

    .vhs-label {
        display: inline-block;
        padding: 0.25rem 0.65rem;
        border-radius: 999px;
        background: rgba(255, 79, 216, 0.18);
        border: 1px solid rgba(255, 79, 216, 0.72);
        color: var(--vault-yellow);
        font-size: 0.78rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    div[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1c062b 0%, #090111 100%);
        border-right: 1px solid rgba(255, 79, 216, 0.35);
    }

    div.stButton > button {
        border: 2px solid var(--vault-yellow);
        border-radius: 999px;
        background: linear-gradient(90deg, #ff4fd8, #ffd166);
        color: #1a0624;
        font-weight: 900;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        box-shadow: 0 0 22px rgba(255, 79, 216, 0.35);
    }

    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.055);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 14px;
        padding: 0.6rem;
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


def display_movie_card(index: int, candidate: dict[str, Any]) -> None:
    movie = candidate["movie"]
    details = candidate["details"]
    title = details.get("title") or movie.get("title")
    genres = ", ".join([g["name"] for g in details.get("genres", [])]) or "Unknown"
    runtime = details.get("runtime")
    overview = details.get("overview") or "No overview available. This one is mysterious. Very artsy."

    with st.container(border=True):
        st.markdown(f"<span class='vhs-label'>Staff Pick #{index}</span>", unsafe_allow_html=True)
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


def main() -> None:
    st.set_page_config(page_title="Joey's Video Vault", page_icon="📼", layout="wide")

    st.markdown(RETRO_CSS, unsafe_allow_html=True)

    st.markdown(
        """
        <div class="hero-card">
            <div class="kicker">📼 Now open · Be kind, rewind</div>
            <h1>Joey's Video Vault</h1>
            <p>Welcome to the late-fee-free movie counter. Tell the clerk what kind of night you're having,
            and we'll pull three tapes from the shelves.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    uploaded_file = st.sidebar.file_uploader("📦 Drop off your movie inventory (.xlsx)", type=["xlsx"])
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
        st.header("📼 Clerk Counter")
        st.caption(f"Shelf inventory: {source_label}")
        st.text_input(
            "TMDb API key / secret handshake",
            type="password",
            key="tmdb_api_key",
            help="Optional if your key is stored in Streamlit secrets. The included default key is for your local version only.",
        )

    if not movies:
        st.error("The shelves are empty. Upload your Excel inventory in the sidebar or place MovieList.xlsx next to this app.")
        return

    status_counts = pd.Series([m.get("watch_status") or "Not specified" for m in movies]).value_counts().to_dict()
    st.caption(
        f"Cataloged {len(movies)} tapes from {source_label}. "
        + " | ".join(f"{status}: {count}" for status, count in status_counts.items())
    )

    available_formats = sorted({
        str(movie.get("format")).strip()
        for movie in movies
        if movie.get("format") is not None and not pd.isna(movie.get("format")) and str(movie.get("format")).strip()
    })

    with st.expander("📋 Browse the staff cheat sheet: genres, vibes, and status hints", expanded=True):
        st.write("**Aisles / genres:** " + ", ".join(GENRE_HINTS))
        st.write("**Tonight's energy:** " + ", ".join(VIBE_MAP.keys()))
        st.write("**Shelf tags:** Watched, Unwatched, In progress")
        if available_formats:
            st.write("**Formats on the shelf:** " + ", ".join(available_formats))

    st.markdown(
        """
        <div class="vhs-card">
            <span class="vhs-label">Rental Form</span>
            <p style="margin-top:0.75rem; margin-bottom:0;">Choose your aisle, mood, and house rules. Leave anything as <strong>Any</strong> and the clerk will freestyle.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        genre_choice = st.selectbox("🎞️ Aisle / genre", ["Any"] + GENRE_HINTS)
        vibe_choice = st.selectbox("🕹️ Tonight's vibe", ["Any"] + list(VIBE_MAP.keys()))
        watch_status_choice = st.selectbox("📼 Shelf tag", ["Any", "Watched", "Unwatched", "In progress"])
    with col2:
        min_rating = st.slider("⭐ Minimum critic-counter score", 0.0, 10.0, 0.0, 0.5)
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

    if st.button("📼 Ring up 3 staff picks", type="primary", use_container_width=True):
        api_key = get_api_key()
        if not api_key or api_key == "YOUR_API_KEY":
            st.error("The clerk needs the TMDb secret handshake. Add your API key in the sidebar or Streamlit secrets.")
            return

        with st.spinner("Checking the shelves, blowing dust off the VHS boxes, and warming up the projector..."):
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
                "No tapes made it to the counter. Try loosening a few filters, or check that your Excel file and TMDb API key are working."
            )
            return

        backup_count = sum(1 for item in chosen_movies if item.get("match_type") != "Exact match")
        if len(chosen_movies) < PICKS_TO_SHOW:
            st.warning(
                f"I could only build {len(chosen_movies)} usable option(s). TMDb returned {tmdb_hits} usable movie lookup(s). "
                "Try fewer filters for a fuller rental bag."
            )
        elif backup_count:
            st.info(
                f"Found {exact_count} exact shelf match(es), so I added {backup_count} nearby staff pick(s) to make sure you get three options."
            )

        st.header(f"Tonight's {len(chosen_movies)} staff pick(s)")
        for index, candidate in enumerate(chosen_movies, start=1):
            display_movie_card(index, candidate)


if __name__ == "__main__":
    main()
