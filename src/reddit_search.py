import aiohttp
import asyncio
import pandas as pd

async def deep_search_reddit(query, subreddits, limit=100):
    results = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    async with aiohttp.ClientSession(headers=headers) as session:
        for sub in subreddits:
            print(f"Buscando '{query}' en r/{sub}...")
            url = f"https://www.reddit.com/r/{sub}/search.json?q={query}&limit={limit}&restrict_sr=1&sort=relevance&t=all"
            
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        posts = data.get('data', {}).get('children', [])
                        for p in posts:
                            res = p['data']
                            results.append({
                                'title': res.get('title'),
                                'text': res.get('selftext', ''),
                                'score': res.get('score'),
                                'subreddit': sub,
                                'permalink': res.get('permalink'),
                                'created_utc': res.get('created_utc')
                            })
                        print(f"   Encontrados {len(posts)} posts.")
                    else:
                        print(f"Error {response.status} en r/{sub}")
            except Exception as e:
                print(f"Error: {e}")
            await asyncio.sleep(1)
    return pd.DataFrame(results)

def get_real_reddit_data():
    SUBS = ["chile", "EducacionChile", "valparaiso", "Santiago", "RepublicadeChile", "ChileIT", "Santiago", "AskChile"]
    TERMINOS = ["USM", "UTFSM", "Santa Maria", "Sansano", "Sansana"]

    async def _run():
        all_dfs = []
        for term in TERMINOS:
            df_term = await deep_search_reddit(term, SUBS, limit=100)
            all_dfs.append(df_term)

        if all_dfs:
            df_final = pd.concat(all_dfs, ignore_index=True).drop_duplicates(subset=['permalink'])
            print(f"\nTotal de posts únicos encontrados: {len(df_final)}")
            return df_final
        else:
            print("No se encontraron resultados.")
            return pd.DataFrame()

    return asyncio.run(_run())
