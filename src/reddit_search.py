"""
Backward-compatible wrapper around analytics.reddit_search.

app.py imports ``deep_search_reddit`` from here as an **async** function
and calls it via ``asyncio``.  This shim keeps that contract by wrapping
the synchronous PullPush implementation in an async adapter.

All new code should import directly from ``analytics.reddit_search``.
"""
import asyncio
import pandas as pd

from analytics.reddit_search import (           # canonical implementations
    deep_search_reddit as _deep_search_sync,
    deep_search_comments,
    deep_search_reddit_timeline,
    DEFAULT_SUBS,
    DEFAULT_TERMINOS,
)


async def deep_search_reddit(query, subreddits, limit=100):
    """Async wrapper so existing ``app.py`` call-sites keep working."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        None, lambda: _deep_search_sync(query, subreddits, limit),
    )


def get_real_reddit_data():
    """Convenience function that searches all default terms × subreddits."""
    SUBS = DEFAULT_SUBS
    TERMINOS = DEFAULT_TERMINOS

    async def _run():
        all_dfs = []
        for term in TERMINOS:
            df_term = await deep_search_reddit(term, SUBS, limit=100)
            all_dfs.append(df_term)

        if all_dfs:
            df_final = pd.concat(all_dfs, ignore_index=True).drop_duplicates(
                subset=["permalink"],
            )
            print(f"\nTotal de posts únicos encontrados: {len(df_final)}")
            return df_final
        else:
            print("No se encontraron resultados.")
            return pd.DataFrame()

    return asyncio.run(_run())
