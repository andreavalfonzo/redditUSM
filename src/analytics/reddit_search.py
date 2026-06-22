"""
Reddit Search Module - Usando PullPush.io (archivo histórico de Reddit).
No requiere autenticación. Datos disponibles hasta ~mayo 2025.
Ideal para análisis histórico de sentimientos.
"""
import time
import requests
import pandas as pd


PULLPUSH_BASE = "https://api.pullpush.io/reddit/search"


def deep_search_reddit(query, subreddits, limit=100):
    """
    Search Reddit historical data via PullPush.io API.
    No authentication required.

    Args:
        query: Search term (e.g., "USM")
        subreddits: List of subreddit names to search
        limit: Max results per subreddit (default 100, max 100 per request)

    Returns:
        pd.DataFrame with columns: title, text, score, subreddit, permalink, created_utc
    """
    results = []
    headers = {
        "User-Agent": "python:redditUSM:v1.0 (academic research)",
        "Accept": "application/json",
    }

    for sub in subreddits:
        print(f"Buscando '{query}' en r/{sub}...")

        url = f"{PULLPUSH_BASE}/submission"
        params = {
            "q": query,
            "subreddit": sub,
            "size": min(limit, 100),
            "sort": "desc",
            "sort_type": "score",
        }

        try:
            response = requests.get(url, params=params, headers=headers, timeout=30)

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
                print(f"   Encontrados {len(posts)} posts.")
            elif response.status_code == 429:
                print(f"   Rate limited, esperando 10s...")
                time.sleep(10)
            else:
                print(f"   Error {response.status_code} en r/{sub}")

        except requests.exceptions.Timeout:
            print(f"   Timeout en r/{sub}, continuando...")
        except Exception as e:
            print(f"   Error: {e}")

        # Respect PullPush rate limits
        time.sleep(1.5)

    print(f"\nBúsqueda completada. Total de resultados: {len(results)}")
    return pd.DataFrame(results)


def deep_search_comments(query, subreddits, limit=100):
    """
    Search Reddit comments via PullPush.io API.

    Args:
        query: Search term
        subreddits: List of subreddit names
        limit: Max results per subreddit

    Returns:
        pd.DataFrame with comment data
    """
    results = []
    headers = {
        "User-Agent": "python:redditUSM:v1.0 (academic research)",
        "Accept": "application/json",
    }

    for sub in subreddits:
        print(f"Buscando comentarios con '{query}' en r/{sub}...")

        url = f"{PULLPUSH_BASE}/comment"
        params = {
            "q": query,
            "subreddit": sub,
            "size": min(limit, 100),
            "sort": "desc",
            "sort_type": "score",
        }

        try:
            response = requests.get(url, params=params, headers=headers, timeout=30)

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
                print(f"   Encontrados {len(comments)} comentarios.")
            else:
                print(f"   Error {response.status_code} en r/{sub}")

        except Exception as e:
            print(f"   Error: {e}")

        time.sleep(1.5)

    print(f"\nBúsqueda de comentarios completada. Total: {len(results)}")
    return pd.DataFrame(results)
