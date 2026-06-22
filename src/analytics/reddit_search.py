"""
Reddit Search Module - Usando PullPush.io (archivo histórico de Reddit).
No requiere autenticación. Datos disponibles hasta ~mayo 2025.
Ideal para análisis histórico de sentimientos.
"""
import time
from datetime import datetime, timezone

import requests
import pandas as pd


PULLPUSH_BASE = "https://api.pullpush.io/reddit/search"

DEFAULT_SUBS = [
    "chile", "EducacionChile", "valparaiso", "Santiago",
    "RepublicadeChile", "ChileIT", "AskChile",
]

DEFAULT_TERMINOS = ["USM", "UTFSM", "Santa Maria", "Sansano", "Sansana"]

_HEADERS = {
    "User-Agent": "python:redditUSM:v1.0 (academic research)",
    "Accept": "application/json",
}


# ---------------------------------------------------------------------------
# Core helpers
# ---------------------------------------------------------------------------

def _epoch(year: int, month: int = 1, day: int = 1) -> int:
    """Return a UTC epoch timestamp for the given date."""
    return int(datetime(year, month, day, tzinfo=timezone.utc).timestamp())


def _build_semester_ranges(start_year: int = 2019, end_year: int = 2025):
    """
    Yield (label, after_epoch, before_epoch) tuples for each semester
    (H1 = Jan-Jun, H2 = Jul-Dec) from start_year-H1 through end_year-H1.
    """
    for year in range(start_year, end_year + 1):
        # H1: January 1 → June 30
        yield (
            f"{year}-H1",
            _epoch(year, 1, 1),
            _epoch(year, 7, 1),      # exclusive upper bound
        )
        # H2: July 1 → December 31  (skip if year == end_year)
        if year < end_year:
            yield (
                f"{year}-H2",
                _epoch(year, 7, 1),
                _epoch(year + 1, 1, 1),
            )


# ---------------------------------------------------------------------------
# deep_search_reddit  (with optional after / before epoch filters)
# ---------------------------------------------------------------------------

def deep_search_reddit(query, subreddits, limit=100, *, after=None, before=None):
    """
    Search Reddit historical data via PullPush.io API.
    No authentication required.

    Args:
        query: Search term (e.g., "USM")
        subreddits: List of subreddit names to search
        limit: Max results per subreddit (default 100, max 100 per request)
        after: (optional) Unix epoch – only return posts **after** this time
        before: (optional) Unix epoch – only return posts **before** this time

    Returns:
        pd.DataFrame with columns:
            title, text, score, subreddit, permalink,
            created_utc, num_comments, author
    """
    results = []

    for sub in subreddits:
        print(f"Buscando '{query}' en r/{sub}...", end="")

        url = f"{PULLPUSH_BASE}/submission"
        params = {
            "q": query,
            "subreddit": sub,
            "size": min(limit, 100),
            "sort": "desc",
            "sort_type": "score",
        }
        if after is not None:
            params["after"] = int(after)
        if before is not None:
            params["before"] = int(before)

        try:
            response = requests.get(
                url, params=params, headers=_HEADERS, timeout=30,
            )

            if response.status_code == 200:
                data = response.json()
                posts = data.get("data", [])
                for res in posts:
                    results.append({
                        "title": res.get("title", ""),
                        "text": res.get("selftext", ""),
                        "score": res.get("score", 0),
                        "subreddit": res.get("subreddit", sub),
                        "permalink": res.get("permalink", ""),
                        "created_utc": res.get("created_utc", 0),
                        "num_comments": res.get("num_comments", 0),
                        "author": res.get("author", ""),
                    })
                print(f" {len(posts)} posts.")
            elif response.status_code == 429:
                print(f" Rate limited, esperando 10 s...")
                time.sleep(10)
            else:
                print(f" Error {response.status_code}")

        except requests.exceptions.Timeout:
            print(f" Timeout, continuando...")
        except Exception as e:
            print(f" Error: {e}")

        # Respect PullPush rate limits
        time.sleep(1.5)

    print(f"Búsqueda completada. Total de resultados: {len(results)}")
    return pd.DataFrame(results)


# ---------------------------------------------------------------------------
# deep_search_reddit_timeline
# ---------------------------------------------------------------------------

def deep_search_reddit_timeline(
    subreddits=None,
    terminos=None,
    limit=100,
    start_year=2019,
    end_year=2025,
):
    """
    Search across all subreddits × search terms in 6-month (semester) chunks.

    Args:
        subreddits: List of subreddits  (default: DEFAULT_SUBS)
        terminos:   List of search terms (default: DEFAULT_TERMINOS)
        limit:      Max results per subreddit per term per chunk (max 100)
        start_year: First year to search (default 2019)
        end_year:   Last year to search (default 2025, includes H1)

    Returns:
        pd.DataFrame  – all unique posts with extra columns:
            * ``period``  – semester label, e.g. "2019-H1"
            * ``date``    – ``created_utc`` converted to datetime
    """
    subreddits = subreddits or DEFAULT_SUBS
    terminos = terminos or DEFAULT_TERMINOS

    all_dfs: list[pd.DataFrame] = []
    semesters = list(_build_semester_ranges(start_year, end_year))
    total_chunks = len(semesters) * len(terminos)
    chunk_n = 0

    for label, after_epoch, before_epoch in semesters:
        for term in terminos:
            chunk_n += 1
            print(
                f"\n[{chunk_n}/{total_chunks}] "
                f"Período {label} | término '{term}'"
            )

            df_chunk = deep_search_reddit(
                query=term,
                subreddits=subreddits,
                limit=limit,
                after=after_epoch,
                before=before_epoch,
            )

            if not df_chunk.empty:
                df_chunk["period"] = label
                all_dfs.append(df_chunk)

    if not all_dfs:
        print("\nNo se encontraron resultados en la línea temporal.")
        return pd.DataFrame()

    df_all = pd.concat(all_dfs, ignore_index=True)

    # De-duplicate by permalink (same post may match multiple terms)
    df_all.drop_duplicates(subset=["permalink"], inplace=True)

    # Add a proper datetime column
    if "created_utc" in df_all.columns:
        df_all["date"] = pd.to_datetime(
            df_all["created_utc"], unit="s", utc=True, errors="coerce",
        )

    df_all.sort_values("created_utc", inplace=True, ignore_index=True)
    print(f"\nTimeline completada. Posts únicos: {len(df_all)}")
    return df_all


# ---------------------------------------------------------------------------
# deep_search_comments
# ---------------------------------------------------------------------------

def deep_search_comments(query, subreddits, limit=100, *, after=None, before=None):
    """
    Search Reddit comments via PullPush.io API.

    Args:
        query: Search term
        subreddits: List of subreddit names
        limit: Max results per subreddit
        after: (optional) Unix epoch – only return comments after this time
        before: (optional) Unix epoch – only return comments before this time

    Returns:
        pd.DataFrame with comment data
    """
    results = []

    for sub in subreddits:
        print(f"Buscando comentarios con '{query}' en r/{sub}...", end="")

        url = f"{PULLPUSH_BASE}/comment"
        params = {
            "q": query,
            "subreddit": sub,
            "size": min(limit, 100),
            "sort": "desc",
            "sort_type": "score",
        }
        if after is not None:
            params["after"] = int(after)
        if before is not None:
            params["before"] = int(before)

        try:
            response = requests.get(
                url, params=params, headers=_HEADERS, timeout=30,
            )

            if response.status_code == 200:
                data = response.json()
                comments = data.get("data", [])
                for c in comments:
                    results.append({
                        "body": c.get("body", ""),
                        "score": c.get("score", 0),
                        "subreddit": c.get("subreddit", sub),
                        "permalink": c.get("permalink", ""),
                        "created_utc": c.get("created_utc", 0),
                        "author": c.get("author", ""),
                    })
                print(f" {len(comments)} comentarios.")
            else:
                print(f" Error {response.status_code}")

        except Exception as e:
            print(f" Error: {e}")

        time.sleep(1.5)

    print(f"Búsqueda de comentarios completada. Total: {len(results)}")
    return pd.DataFrame(results)
