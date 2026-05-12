import pandas as pd
import re


def limpiar_texto(texto):

    """
    Limpia texto manteniendo emojis para análisis emocional.
    """

    if pd.isna(texto):
        return ""

    texto = str(texto)

    # Eliminar URLs
    texto = re.sub(r"http\S+|www\S+", "", texto)

    # Eliminar espacios repetidos
    texto = re.sub(r"\s+", " ", texto).strip()

    return texto


def procesar_datos():

    ruta_entrada = "data/raw/reddit_mock.csv"
    ruta_salida = "data/processed/reddit_clean.csv"

    df = pd.read_csv(ruta_entrada)

    print("\nDataset original:")
    print(df.head())

    # Crear nueva columna limpia
    df["texto_limpio"] = df["texto"].apply(limpiar_texto)

    print("\nTexto procesado:")
    print(df[["texto", "texto_limpio"]])

    # Guardar resultado
    df.to_csv(ruta_salida, index=False, encoding="utf-8")

    print(f"\nArchivo guardado en: {ruta_salida}")


if __name__ == "__main__":
    procesar_datos()