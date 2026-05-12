import praw
import pandas as pd
from datetime import datetime

# Aquí conectaremos tus credenciales después
def conectar_reddit():
    return praw.Reddit(
        client_id="TU_ID_AQUI",
        client_secret="TU_SECRET_AQUI",
        user_agent="script:OpinionUSM:v1.0 (by /u/TouristFun2343)"
    )

def extraer_datos(nombre_subreddit, limite=10):
    reddit = conectar_reddit()
    subreddit = reddit.subreddit(nombre_subreddit)
    
    lista_posts = []
    
    print(f"Buscando posts en r/{nombre_subreddit}...")
    
    for post in subreddit.hot(limit=limite):
        lista_posts.append({
            "titulo": post.title,
            "puntuacion": post.score,
            "url": post.url,
            "fecha": datetime.fromtimestamp(post.created_utc)
        })
    
    # Crear un DataFrame de Pandas (ideal para minería de datos)
    df = pd.DataFrame(lista_posts)
    
    # Guardar en un CSV para usar en Excel o Power BI
    nombre_archivo = f"datos_{nombre_subreddit}.csv"
    df.to_csv(nombre_archivo, index=False, encoding='utf-8')
    print(f"¡Éxito! Datos guardados en {nombre_archivo}")

# Ejemplo de uso:
# extraer_datos("chile", limite=5)