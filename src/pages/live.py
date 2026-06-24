"""
pages/live.py — Página: Análisis en Vivo
Búsqueda y análisis de sentimientos en tiempo real vía PullPush.io.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils import (
    inject_css,
    map_sentiment_label,
    SENTIMENT_COLORS,
    STOPWORDS,
    analyze_sentiment_advanced,
    deep_search_reddit,
)

st.set_page_config(page_title="Análisis en Vivo", page_icon="🔍", layout="wide")
inject_css()

# ── Encabezado ─────────────────────────────────────────────────────────────────

st.title("🔍 Análisis en Vivo")
st.caption("Los nuevos resultados se mostrarán en la página principal 📊 *Todas las métricas*")
st.markdown("Busca información usando el archivo histórico de Reddit vía **PullPush.io** (sin API keys).")

# ── Formulario ─────────────────────────────────────────────────────────────────

with st.form("live_search_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        query = st.text_input("Término de Búsqueda", value="USM")
    with col2:
        subs = st.multiselect(
            "Subreddits",
            ["chile", "EducacionChile", "valparaiso", "Santiago", "RepublicadeChile", "ChileIT", "AskChile"],
            default=["chile", "EducacionChile"],
        )
    with col3:
        limit = st.slider("Límite por subreddit", 10, 100, 20)
    submit = st.form_submit_button("🚀 Iniciar Extracción y Análisis")

if not submit:
    st.stop()

if not subs:
    st.warning("Selecciona al menos un subreddit.")
    st.stop()

# ── Extracción ─────────────────────────────────────────────────────────────────

with st.spinner("Buscando en Reddit y analizando sentimientos..."):
    df = deep_search_reddit(query, subs, limit=limit)

if df is None or df.empty:
    st.warning("No se encontraron resultados para los parámetros ingresados.")
    st.stop()

st.success(f"¡Extracción completada! Se analizarán **{len(df)}** posts.")

df["full_content"] = df["title"].fillna("") + " " + df["text"].fillna("")
progress = st.progress(0, text="Clasificando sentimientos...")

res_sentiment = []
for i, text in enumerate(df["full_content"]):
    res_sentiment.append(analyze_sentiment_advanced(text))
    progress.progress((i + 1) / len(df), text=f"Clasificando {i+1}/{len(df)}...")
progress.empty()

df["sentiment_score"] = [r[0] for r in res_sentiment]
df["sentiment_label"] = [r[1] for r in res_sentiment]
df["Etiqueta"] = df["sentiment_label"].apply(map_sentiment_label)

# ── Dashboard de resultados ────────────────────────────────────────────────────

st.markdown("---")
st.subheader("Métricas de Sentimiento")

total     = len(df)
count_pos = (df["Etiqueta"] == "Positivo").sum()
count_neg = (df["Etiqueta"] == "Negativo").sum()
count_neu = (df["Etiqueta"] == "Neutro").sum()

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(f"<div class='metric-card'><div class='metric-title'>Posts Analizados</div><div class='metric-value' style='color:#FFF;'>{total}</div></div>", unsafe_allow_html=True)
with m2:
    st.markdown(f"<div class='metric-card'><div class='metric-title'>Positivos</div><div class='metric-value' style='color:#00CC96;'>{count_pos} ({count_pos/max(1,total):.1%})</div></div>", unsafe_allow_html=True)
with m3:
    st.markdown(f"<div class='metric-card'><div class='metric-title'>Negativos</div><div class='metric-value' style='color:#EF553B;'>{count_neg} ({count_neg/max(1,total):.1%})</div></div>", unsafe_allow_html=True)
with m4:
    st.markdown(f"<div class='metric-card'><div class='metric-title'>Neutros</div><div class='metric-value' style='color:#636EFA;'>{count_neu} ({count_neu/max(1,total):.1%})</div></div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# Gráficos
row1_l, row1_r = st.columns(2)
with row1_l:
    st.markdown("### Distribución Global")
    pie_df = pd.DataFrame({
        "Sentimiento": ["Positivo", "Negativo", "Neutro"],
        "Cantidad": [count_pos, count_neg, count_neu],
    })
    fig_pie = px.pie(pie_df, names="Sentimiento", values="Cantidad",
                     color="Sentimiento", color_discrete_map=SENTIMENT_COLORS, hole=0.4)
    fig_pie.update_layout(margin=dict(t=30, b=0, l=0, r=0), paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#FFF"))
    st.plotly_chart(fig_pie, use_container_width=True)

with row1_r:
    if "subreddit" in df.columns:
        st.markdown("### Por Subreddit")
        sub_counts = df.groupby(["subreddit", "Etiqueta"]).size().reset_index(name="Cantidad")
        fig_bar = px.bar(sub_counts, x="subreddit", y="Cantidad", color="Etiqueta",
                         color_discrete_map=SENTIMENT_COLORS, barmode="group")
        fig_bar.update_layout(margin=dict(t=30, b=0, l=0, r=0),
                               paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#FFF"))
        st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")
st.markdown("### WordCloud")
texto = " ".join(df["full_content"].dropna().astype(str))
if texto.strip():
    wc = WordCloud(width=1200, height=400, background_color="#0E1117", colormap="Set2", stopwords=STOPWORDS).generate(texto)
    fig_wc, ax = plt.subplots(figsize=(15, 5), facecolor="#0E1117")
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig_wc)
    plt.close(fig_wc)

st.markdown("---")
st.markdown("### Explorador de Textos")
search_term = st.text_input("🔍 Filtrar textos...", key="live_explorer_search")
df_display = df.copy()
if search_term:
    df_display = df_display[df_display["full_content"].astype(str).str.contains(search_term, case=False, na=False)]

cols = ["Etiqueta"]
if "subreddit"    in df_display.columns: cols.append("subreddit")
if "full_content" in df_display.columns: cols.append("full_content")
if "score"        in df_display.columns: cols.append("score")
st.dataframe(df_display[cols], use_container_width=True, hide_index=True)
