import pandas as pd
import matplotlib.pyplot as plt


def visualizar_sentimientos():

    ruta = "data/processed/reddit_sentiment.csv"

    df = pd.read_csv(ruta)

    conteo = df["sentimiento"].value_counts()

    print(conteo)

    plt.figure(figsize=(6, 4))

    conteo.plot(kind="bar")

    plt.title("Distribución de sentimientos")

    plt.xlabel("Sentimiento")

    plt.ylabel("Cantidad")

    plt.tight_layout()

    plt.savefig("results/figures/sentimientos.png")

    plt.show()

    print("\nGráfico guardado en results/figures/")


if __name__ == "__main__":
    visualizar_sentimientos()