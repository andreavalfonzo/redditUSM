"""
pages/timeline.py — Página: Evolución Temporal de Sentimientos
Análisis semestral histórico de la percepción de la USM en Reddit (2019–2025).
"""

import streamlit as st
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import pandas as pd
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils import (
    inject_css,
    map_sentiment_label,
    SENTIMENT_COLORS,
    STOPWORDS,
    analyze_sentiment_advanced,
    deep_search_reddit_timeline,
)

st.set_page_config(page_title="Evolución Temporal · r/RedditUSM", page_icon="📅", layout="wide")
inject_css()

# ── Encabezado ─────────────────────────────────────────────────────────────────

st.title("📅 Evolución Temporal de Sentimientos")
st.markdown(
    "Analiza cómo cambió la percepción de la USM en Reddit desde la **pandemia (2019)** "
    "hasta la **actualidad (2025)**, semestre a semestre."
)

# ── Formulario ─────────────────────────────────────────────────────────────────

with st.form("timeline_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        start_year = st.selectbox("Año inicio", list(range(2019, 2026)), index=0)
    with col2:
        end_year = st.selectbox("Año fin", list(range(2019, 2026)), index=6)
    with col3:
        limit = st.slider("Posts por subreddit/término/semestre", 10, 100, 50, key="timeline_limit")
    submit = st.form_submit_button("📊 Generar Línea Temporal")

if not submit:
    st.stop()

if start_year > end_year:
    st.error("El año de inicio debe ser menor o igual al año de fin.")
    st.stop()

# ── Extracción ─────────────────────────────────────────────────────────────────

with st.spinner("Extrayendo datos históricos semestre a semestre... esto puede tomar unos minutos."):
    df = deep_search_reddit_timeline(start_year=start_year, end_year=end_year, limit=limit)

if df.empty:
    st.warning("No se encontraron datos para el rango seleccionado.")
    st.stop()

st.success(f"✅ Se encontraron **{len(df)}** posts únicos en {start_year}–{end_year}")

# ── Análisis de sentimiento ────────────────────────────────────────────────────

with st.spinner("Analizando sentimientos..."):
    df["full_content"] = df["title"].fillna("") + " " + df["text"].fillna("")
    progress = st.progress(0, text="Clasificando sentimientos...")
    res = []
    for i, text in enumerate(df["full_content"]):
        res.append(analyze_sentiment_advanced(text))
        if (i + 1) % 10 == 0 or i == len(df) - 1:
            progress.progress((i + 1) / len(df), text=f"Clasificando {i+1}/{len(df)}...")
    progress.empty()
    df["sentiment_score"] = [r[0] for r in res]
    df["sentiment_label"] = [r[1] for r in res]
    df["Etiqueta"] = df["sentiment_label"].apply(map_sentiment_label)

# ── Métricas ───────────────────────────────────────────────────────────────────

st.markdown("---")
st.subheader("Resumen General")

total = len(df)
n_pos = (df["Etiqueta"] == "Positivo").sum()
n_neg = (df["Etiqueta"] == "Negativo").sum()
n_neu = (df["Etiqueta"] == "Neutro").sum()

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(f"<div class='metric-card'><div class='metric-title'>Posts Totales</div><div class='metric-value' style='color:#FFF;'>{total}</div></div>", unsafe_allow_html=True)
with m2:
    st.markdown(f"<div class='metric-card'><div class='metric-title'>Positivos</div><div class='metric-value' style='color:#00CC96;'>{n_pos} ({n_pos/max(1,total):.1%})</div></div>", unsafe_allow_html=True)
with m3:
    st.markdown(f"<div class='metric-card'><div class='metric-title'>Negativos</div><div class='metric-value' style='color:#EF553B;'>{n_neg} ({n_neg/max(1,total):.1%})</div></div>", unsafe_allow_html=True)
with m4:
    st.markdown(f"<div class='metric-card'><div class='metric-title'>Neutros</div><div class='metric-value' style='color:#636EFA;'>{n_neu} ({n_neu/max(1,total):.1%})</div></div>", unsafe_allow_html=True)

# ── Línea de evolución ─────────────────────────────────────────────────────────

st.markdown("---")
st.markdown("### Evolución de Sentimientos por Semestre")

period_counts = df.groupby(["period", "Etiqueta"]).size().reset_index(name="Cantidad")

fig_line = px.line(
    period_counts, x="period", y="Cantidad", color="Etiqueta",
    color_discrete_map=SENTIMENT_COLORS, markers=True,
    labels={"period": "Período", "Cantidad": "Nº de Posts"},
)
fig_line.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#FFF"),
    xaxis=dict(title="Período", gridcolor="rgba(255,255,255,0.05)"),
    yaxis=dict(title="Nº de Posts", gridcolor="rgba(255,255,255,0.08)"),
    legend_title_text="Sentimiento", hovermode="x unified",
)
st.plotly_chart(fig_line, use_container_width=True)

# ── Área apilada ───────────────────────────────────────────────────────────────

st.markdown("### Proporción de Sentimientos en el Tiempo")

period_totals = df.groupby("period").size().reset_index(name="total")
period_props  = period_counts.merge(period_totals, on="period")
period_props["Proporción"] = period_props["Cantidad"] / period_props["total"]

fig_area = px.area(
    period_props, x="period", y="Proporción", color="Etiqueta",
    color_discrete_map=SENTIMENT_COLORS,
    labels={"period": "Período", "Proporción": "Proporción"},
    groupnorm="fraction",
)
fig_area.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#FFF"),
    xaxis=dict(title="Período", gridcolor="rgba(255,255,255,0.05)"),
    yaxis=dict(title="Proporción", gridcolor="rgba(255,255,255,0.08)", tickformat=".0%"),
    legend_title_text="Sentimiento", hovermode="x unified",
)
st.plotly_chart(fig_area, use_container_width=True)

# ── Tabla detalle ──────────────────────────────────────────────────────────────

st.markdown("### Detalle por Semestre")

pivot = period_counts.pivot_table(index="period", columns="Etiqueta", values="Cantidad", fill_value=0).reset_index()
pivot.columns.name = None
for col in ["Positivo", "Negativo", "Neutro"]:
    if col not in pivot.columns:
        pivot[col] = 0
pivot["Total"] = pivot["Positivo"] + pivot["Negativo"] + pivot["Neutro"]
pivot = pivot.rename(columns={"period": "Período"})[["Período", "Positivo", "Negativo", "Neutro", "Total"]]
st.dataframe(pivot, use_container_width=True, hide_index=True)

# ── Contexto histórico ─────────────────────────────────────────────────────────

st.markdown("---")
st.markdown("### 🗓️ Contexto Histórico")
st.markdown("""
| Período | Evento |
|---------|--------|
| 2019-H2 | Estallido social en Chile (Oct 2019) |
| 2020-H1 | Inicio de la pandemia COVID-19 (Mar 2020) |
| 2020-H2 | Clases online generalizadas |
| 2021-H1 | Vacunación masiva y clases híbridas |
| 2022-H1 | Retorno progresivo a presencialidad |
| 2023-H1 | Normalización post-pandemia |
| 2024-H1 | Período contemporáneo |
""")

# ── WordCloud ──────────────────────────────────────────────────────────────────

st.markdown("---")
st.markdown("### WordCloud del Período Completo")

texto = " ".join(df["full_content"].dropna().astype(str))
if texto.strip():
    wc = WordCloud(width=1200, height=400, background_color="#0E1117", colormap="Set2", stopwords=STOPWORDS).generate(texto)
    fig_wc, ax = plt.subplots(figsize=(15, 5), facecolor="#0E1117")
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig_wc)
    plt.close(fig_wc)
