import pandas as pd


def analizar_datos():
    ruta = "data/processed/reddit_clean.csv"
    df = pd.read_csv(ruta)

    print("\nCantidad de registros:")
    print(len(df))

    print("\nSubreddits:")
    print(df["subreddit"].value_counts())

    print("\nTipos:")
    print(df["tipo"].value_counts())

    print("\nPromedio score:")
    print(df["score"].mean())

    print("\nTextos:")
    print(df[["subreddit", "texto_limpio"]])


if __name__ == "__main__":
    analizar_datos()