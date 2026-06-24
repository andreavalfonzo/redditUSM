"""
utils.py — Utilidades compartidas entre todas las páginas de r/RedditUSM.
Incluye: CSS global, cargadores de datos, colores, clasificadores temáticos.
"""

import streamlit as st
import pandas as pd
import numpy as np
import re
import os
import sys
import glob

# ── Rutas ─────────────────────────────────────────────────────────────────────

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Asegurar que src/ esté en el path para imports relativos
_src_root = os.path.abspath(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# ── Imports analytics ─────────────────────────────────────────────────────────

try:
    from src.analytics.sentiment import analyze_sentiment_advanced, STOPWORDS
    from src.analytics.reddit_search import deep_search_reddit, deep_search_reddit_timeline
except ImportError:
    from analytics.sentiment import analyze_sentiment_advanced, STOPWORDS
    from analytics.reddit_search import deep_search_reddit, deep_search_reddit_timeline

# ── Colores de sentimiento ────────────────────────────────────────────────────

SENTIMENT_COLORS = {
    "Positivo": "#43d975",
    "Negativo": "#f73942",
    "Neutro":   "#4381c1",
}

SENTIMENT_COLORS_RAW = {
    "positive": "#43d975",
    "negative": "#f73942",
    "neutral":  "#4381c1",
}

# ── CSS global ────────────────────────────────────────────────────────────────

GLOBAL_CSS = """
<style>
    .metric-card {
        background: linear-gradient(135deg, rgb(64, 78, 125) 0%, rgb(64, 78, 125) 100%);
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        transition: transform 0.2s ease;
    }
    .metric-card:hover { transform: translateY(-2px); }
    .metric-title { color: rgba(255,255,255,0.7); font-size: 0.85rem; margin-bottom: 0.4rem; }
    .metric-value { font-size: 1.6rem; font-weight: 700; color: #FFF !important; }
    .period-badge {
        display: inline-block;
        background: rgba(99,110,250,0.15);
        border: 1px solid rgba(99,110,250,0.3);
        border-radius: 6px;
        padding: 0.15rem 0.5rem;
        font-size: 0.8rem;
        color: #636EFA;
    }
    .section-header {
        background: linear-gradient(90deg, rgba(165, 148, 249,0.15) 0%, rgba(0,0,0,0) 100%);
        border-left: 3px solid rgb(165, 148, 249);
        padding: 0.5rem 1rem;
        border-radius: 0 8px 8px 0;
        margin: 1rem 0 0.5rem 0;
    }
</style>
"""


def inject_css():
    """Inyecta el CSS global. Llamar al inicio de cada página."""
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


# ── Helpers de sentimiento ────────────────────────────────────────────────────

def map_sentiment_label(val: str) -> str:
    if val in ("POS", "positive"):  return "Positivo"
    if val in ("NEG", "negative"):  return "Negativo"
    if val in ("NEU", "neutral"):   return "Neutro"
    return str(val).capitalize()


def apply_sentiment(df: pd.DataFrame) -> pd.DataFrame:
    """Añade sentiment_score, sentiment_label y Etiqueta a un DataFrame con 'full_content'."""
    res = df["full_content"].apply(analyze_sentiment_advanced)
    df["sentiment_score"] = [r[0] for r in res]
    df["sentiment_label"] = [r[1] for r in res]
    df["Etiqueta"] = df["sentiment_label"].apply(map_sentiment_label)
    return df


# ── Limpieza de texto ─────────────────────────────────────────────────────────

def limpiar_texto(texto: str) -> str:
    texto = str(texto).lower()
    texto = re.sub(r"http\S+|www\S+", "", texto)
    texto = re.sub(r"[^\w\sáéíóúüñ]", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto


# ── Clasificadores temáticos ──────────────────────────────────────────────────

def asignar_cluster_tematico(row) -> str:
    texto = str(row.get("texto_limpio", "")).lower()
    sentimiento = str(row.get("sentiment_label", "")).lower()

    if any(w in texto for w in ["profe", "profes", "profesor", "profesora", "docente", "catedra", "explicar", "pauta"]):
        return "Profesores y Docencia"
    if any(w in texto for w in ["beca", "baes", "pluxee", "casino", "almuerzo", "comida", "junaeb", "arancel"]):
        return "Becas y Bienestar"
    if any(w in texto for w in ["ansiedad", "estres", "estrés", "colapso", "sueño", "insomnio", "llorar", "crisis", "cansado"]):
        return "Salud Mental y Carga Emocional"
    if any(w in texto for w in ["pucv", "usach", "uchile", "uc", "duoc", "uach", "comparar", "mejor", "peor", "diferencia"]):
        return "Comparaciones Institucionales"
    if sentimiento == "negative" or any(w in texto for w in ["malo", "pesimo", "odio", "rabia", "horrible", "error", "reprobar"]):
        return "Críticas y Frustración General"
    if sentimiento == "positive" or any(w in texto for w in ["bueno", "excelente", "bacan", "bacán", "lograr", "pasar", "feliz"]):
        return "Logros y Experiencias Positivas"
    return "Comunidad y Varios"


def clasificar_tema_rapido(texto: str) -> str:
    texto = str(texto).lower()
    if any(w in texto for w in ["certamen", "certámenes", "ramo", "profe", "malla", "reprobar", "estudiar",
                                 "nota", "gracia", "pasar", "controles", "laboratorio", "informe",
                                 "academic", "coordinador", "reprobe", "pauta", "examen", "asistencia", "clases"]):
        return "Ámbito Académico, Ramos y Docencia"
    if any(w in texto for w in ["ansiedad", "estres", "estrés", "colapso", "salud mental", "psicologo",
                                 "sueño", "depre", "crisis", "llorar", "presion", "psicóloga",
                                 "insomnio", "agotado", "cansado", "sufrir", "frustracion", "panico"]):
        return "Salud Mental, Carga Emocional y Estrés"
    if any(w in texto for w in ["beca", "baes", "pluxee", "casino", "almuerzo", "comida", "junaeb",
                                 "plata", "pagar", "arancel", "cae", "gratuidad", "financiamiento",
                                 "baños", "salas", "campus", "precios", "subsidio"]):
        return "Bienestar, Becas y Servicios de Campus"
    if any(w in texto for w in ["admision", "admisión", "puntaje", "entrar", "matrícula", "requisitos",
                                 "paes", "ingresar", "empleo", "pega", "sueldo", "practica", "práctica",
                                 "egresados", "título", "titulado", "laboral", "empresa", "renta"]):
        return "Admisión, Orientación Vocacional y Mercado Laboral"
    return "Vida Universitaria, Comunidad y Entorno Social"


# ── Cargadores de datos ───────────────────────────────────────────────────────

@st.cache_data
def load_notebook_data() -> pd.DataFrame:
    """
    Carga y combina todos los CSVs por subreddit de src/data/r/.
    Retorna DataFrame con: full_content, sentiment_label, subreddit, texto_limpio.
    """
    candidates = [
        os.path.join(BASE_DIR, "src", "data", "r"),
        os.path.join("src", "data", "r"),
    ]
    all_dfs = []
    for base in candidates:
        if os.path.isdir(base):
            for sub_dir in os.listdir(base):
                sub_path = os.path.join(base, sub_dir)
                if os.path.isdir(sub_path):
                    for csv_file in glob.glob(os.path.join(sub_path, "*.csv")):
                        try:
                            df_sub = pd.read_csv(csv_file)
                            df_sub["subreddit"] = sub_dir
                            all_dfs.append(df_sub)
                        except Exception:
                            pass
            break

    if not all_dfs:
        fallbacks = [
            os.path.join(BASE_DIR, "src", "data", "usm_final", "datos_entrenamiento_usm.csv"),
            "src/data/usm_final/datos_entrenamiento_usm.csv",
        ]
        for p in fallbacks:
            if os.path.exists(p):
                df = pd.read_csv(p)
                df["subreddit"] = "general"
                all_dfs.append(df)
                break

    if not all_dfs:
        return pd.DataFrame()

    df_final = pd.concat(all_dfs, ignore_index=True)

    if "full_content" not in df_final.columns and "texto" in df_final.columns:
        df_final["full_content"] = df_final["texto"]
    if "sentiment_label" not in df_final.columns and "sentimiento" in df_final.columns:
        df_final["sentiment_label"] = df_final["sentimiento"]

    df_final = df_final.dropna(subset=["full_content"]).copy()
    df_final["texto_limpio"] = df_final["full_content"].astype(str).apply(limpiar_texto)
    return df_final


@st.cache_data
def load_historical_data() -> pd.DataFrame:
    paths = [
        "data/processed/reddit_sentiment.csv",
        "../data/processed/reddit_sentiment.csv",
        "src/data/usm_final/datos_entrenamiento_usm.csv",
        "../src/data/usm_final/datos_entrenamiento_usm.csv",
    ]
    for p in paths:
        if os.path.exists(p):
            return pd.read_csv(p)
    return pd.DataFrame()


def get_notebook_last_execution_date() -> str:
    """
    Retorna la fecha y hora de la última ejecución del notebook en formato legible.
    Busca la fecha de modificación del CSV exportado o del propio archivo .ipynb.
    """
    import datetime
    
    candidates = [
        os.path.join(BASE_DIR, "src", "data", "usm_final", "datos_entrenamiento_usm.csv"),
        os.path.join(BASE_DIR, "notebooks", "USM_Sentiment_Analysis.ipynb"),
        "src/data/usm_final/datos_entrenamiento_usm.csv",
        "notebooks/USM_Sentiment_Analysis.ipynb"
    ]
    
    mtimes = []
    for path in candidates:
        if os.path.exists(path):
            mtimes.append(os.path.getmtime(path))
            
    if not mtimes:
        return "Fecha desconocida"
        
    latest_ts = max(mtimes)
    dt = datetime.datetime.fromtimestamp(latest_ts)
    
    meses = [
        "enero", "febrero", "marzo", "abril", "mayo", "junio",
        "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
    ]
    
    fecha_formateada = f"{dt.day} de {meses[dt.month - 1]} de {dt.year}, {dt.hour:02d}:{dt.minute:02d}"
    return fecha_formateada

