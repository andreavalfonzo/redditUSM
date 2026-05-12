import pandas as pd
from pysentimiento import create_analyzer


def analizar_sentimientos():
    ruta_entrada = "data/processed/reddit_clean.csv"
    ruta_salida = "data/processed/reddit_sentiment.csv"

    df = pd.read_csv(ruta_entrada)

    analyzer = create_analyzer(task="sentiment", lang="es")

    sentimientos = []

    for texto in df["texto_limpio"]:
        resultado = analyzer.predict(texto)

        sentimientos.append({
            "sentimiento": resultado.output,
            "prob_neg": resultado.probas["NEG"],
            "prob_neu": resultado.probas["NEU"],
            "prob_pos": resultado.probas["POS"]
        })

    df_sent = pd.DataFrame(sentimientos)
    df_final = pd.concat([df, df_sent], axis=1)

    df_final.to_csv(ruta_salida, index=False, encoding="utf-8")

    print("\nAnálisis de sentimientos completado.")
    print(df_final[["texto_limpio", "sentimiento", "prob_neg", "prob_neu", "prob_pos"]])
    print(f"\nArchivo guardado en: {ruta_salida}")


if __name__ == "__main__":
    analizar_sentimientos()