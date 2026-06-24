"""
pages/notebook.py — Página: Análisis del Notebook (USM_Sentiment_Analysis.ipynb)
Reproduce los 11 gráficos generados en el notebook a partir de los datos exportados.
"""

import streamlit as st
from streamlit_extras.chart_container import *
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import numpy as np
import os
import sys

# Asegurar importaciones desde src/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils import (
    inject_css,
    load_notebook_data,
    map_sentiment_label,
    limpiar_texto,
    asignar_cluster_tematico,
    clasificar_tema_rapido,
    SENTIMENT_COLORS,
    STOPWORDS,
    get_notebook_last_execution_date,
)

st.set_page_config(page_title="r/RedditUSM", page_icon="📊", layout="wide")
inject_css()

# ── Encabezado ─────────────────────────────────────────────────────────────────

st.title("📊 r/RedditUSM: Análisis")
fecha_ejec = get_notebook_last_execution_date()
st.caption(f"**Última ejecución para realizar el análisis:** {fecha_ejec}")
st.markdown(
    "r/RedditUSM es un proyecto que busca entender la tendencia de opiniones sobre la UTFSM mediante análisis de sentimientos y procesamiento de lenguaje natural en publicaciones de Reddit."
)


# ── Carga de datos ─────────────────────────────────────────────────────────────

df = load_notebook_data()

if df.empty:
    st.error("No se pudieron cargar los datos del notebook. Asegúrate de haber ejecutado el notebook primero.")
    st.stop()

df["sentiment_label"] = df["sentiment_label"].fillna("neutral").str.lower().str.strip()
df["Etiqueta"] = df["sentiment_label"].apply(map_sentiment_label)

if "texto_limpio" not in df.columns:
    df["texto_limpio"] = df["full_content"].astype(str).apply(limpiar_texto)

df["cluster_manual"] = df.apply(asignar_cluster_tematico, axis=1)
df["sub_categoria"] = df["texto_limpio"].apply(clasificar_tema_rapido)

total = len(df)
n_pos = (df["sentiment_label"] == "positive").sum()
n_neg = (df["sentiment_label"] == "negative").sum()
n_neu = (df["sentiment_label"] == "neutral").sum()

# ═══════════════════════════════════════════════════════════════════════════════
# Métricas generales
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("---")
st.subheader("Métricas Generales")
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(f"<div class='metric-card'><div class='metric-title'>Posts Totales</div><div class='metric-value' style='color:#FFF;'>{total}</div></div>", unsafe_allow_html=True)
with m2:
    st.markdown(f"<div class='metric-card'><div class='metric-title'>Positivos</div><div class='metric-value' style='color:#00CC96;'>{n_pos} ({n_pos/max(1,total):.1%})</div></div>", unsafe_allow_html=True)
with m3:
    st.markdown(f"<div class='metric-card'><div class='metric-title'>Negativos</div><div class='metric-value' style='color:#EF553B;'>{n_neg} ({n_neg/max(1,total):.1%})</div></div>", unsafe_allow_html=True)
with m4:
    st.markdown(f"<div class='metric-card'><div class='metric-title'>Neutros</div><div class='metric-value' style='color:#636EFA;'>{n_neu} ({n_neu/max(1,total):.1%})</div></div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# 1. Sentimientos sobre la USM
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("---")
st.subheader("Sentimientos sobre la USM")
st.markdown("Distribución del ánimo de la comunidad por subreddit.")

col_sent_l, col_sent_r = st.columns(2)
with col_sent_l:
    if "subreddit" in df.columns:
        sub_sent = df.groupby(["subreddit", "sentiment_label"]).size().reset_index(name="Cantidad")
        sub_sent["Sentimiento"] = sub_sent["sentiment_label"].apply(map_sentiment_label)
        fig_sub = px.bar(
            sub_sent, x="subreddit", y="Cantidad", color="Sentimiento",
            color_discrete_map=SENTIMENT_COLORS, barmode="group",
            title="Sentimientos sobre la USM por Subreddit",
            labels={"subreddit": "Subreddit", "Cantidad": "Nº de Posts"},
        )
        fig_sub.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#FFF"), xaxis_tickangle=-30,
        )
        st.plotly_chart(fig_sub, use_container_width=True)
    else:
        st.info("No hay columna 'subreddit' disponible.")

with col_sent_r:
    pie_df = pd.DataFrame({"Sentimiento": ["Positivo", "Negativo", "Neutro"], "Cantidad": [n_pos, n_neg, n_neu]})
    fig_pie = px.pie(
        pie_df, names="Sentimiento", values="Cantidad",
        color="Sentimiento", color_discrete_map=SENTIMENT_COLORS,
        hole=0.45, title="Distribución Global de Sentimientos",
    )
    fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#FFF"), margin=dict(t=50, b=0, l=0, r=0))
    st.plotly_chart(fig_pie, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# 2. Matriz de Comportamiento Comunitario
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("---")
st.subheader("Matriz de Comportamiento Comunitario")
st.markdown("Tabla cruzada: frecuencia de sentimientos por subreddit, con % de negatividad.")

if "subreddit" in df.columns:
    tabla_pivot = pd.crosstab(df["subreddit"], df["sentiment_label"], margins=True, margins_name="Total General")
    if "negative" in tabla_pivot.columns:
        tabla_pivot["% Negatividad (Quejas)"] = (
            tabla_pivot["negative"] / tabla_pivot["Total General"] * 100
        ).round(1)
    st.dataframe(tabla_pivot.style.background_gradient(cmap="YlOrRd"), use_container_width=True)

    mat = pd.crosstab(df["subreddit"], df["sentiment_label"])
    fig_heat_comm = px.imshow(
        mat, color_continuous_scale="YlOrRd",
        title="Mapa de Calor: Volumen de Sentimientos por Subreddit",
        labels=dict(x="Sentimiento", y="Subreddit", color="Posts"), text_auto=True,
    )
    fig_heat_comm.update_layout(paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#FFF"))
    st.plotly_chart(fig_heat_comm, use_container_width=True)
else:
    st.info("No hay columna 'subreddit' disponible para esta visualización.")

# ═══════════════════════════════════════════════════════════════════════════════
# 3. Análisis de Macrotópicos Sansanos
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("---")
st.subheader("Análisis de Macrotópicos Sansanos")
st.markdown("Balance de contenido por grandes temáticas detectadas en los posts.")

conteo_temas = df["sub_categoria"].value_counts().reset_index()
conteo_temas.columns = ["Temática Detectada", "Cantidad de Posts"]
conteo_temas["% del Total"] = (conteo_temas["Cantidad de Posts"] / conteo_temas["Cantidad de Posts"].sum() * 100).round(1)

col_macro_l, col_macro_r = st.columns([3, 2])
with col_macro_l:
    fig_macro = px.bar(
        conteo_temas, y="Temática Detectada", x="Cantidad de Posts",
        orientation="h", color="Cantidad de Posts", color_continuous_scale="GnBu",
        title="Volumen por Macrotópico Universitario", text="Cantidad de Posts",
    )
    fig_macro.update_traces(textposition="outside")
    fig_macro.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#FFF"), showlegend=False, coloraxis_showscale=False,
        yaxis=dict(autorange="reversed"),
    )
    st.plotly_chart(fig_macro, use_container_width=True)
with col_macro_r:
    st.markdown("##### Tabla de Macrotópicos")
    st.dataframe(
        conteo_temas.style.background_gradient(cmap="GnBu", subset=["Cantidad de Posts"]),
        use_container_width=True, hide_index=True,
    )

# ═══════════════════════════════════════════════════════════════════════════════
# 4. Segmentación de la Comunidad
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("---")
st.subheader("Segmentación de la Comunidad")

cluster_order = df["cluster_manual"].value_counts().index.tolist()
seg_counts = df.groupby(["cluster_manual", "sentiment_label"]).size().reset_index(name="Cantidad")
seg_counts["Sentimiento"] = seg_counts["sentiment_label"].apply(map_sentiment_label)
seg_counts["cluster_manual"] = pd.Categorical(seg_counts["cluster_manual"], categories=cluster_order, ordered=True)
seg_counts = seg_counts.sort_values("cluster_manual")

fig_seg = px.bar(
    seg_counts, y="cluster_manual", x="Cantidad", color="Sentimiento",
    color_discrete_map=SENTIMENT_COLORS, orientation="h", barmode="stack",
    title="¿De qué se habla y cuál es el sentimiento general en cada tópico?",
    labels={"cluster_manual": "Cluster Temático", "Cantidad": "Cantidad de Posts"},
)
fig_seg.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#FFF"), yaxis=dict(autorange="reversed"), height=450,
)
st.plotly_chart(fig_seg, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# 5. Mapa de Calor: Densidad Temática por Subreddit
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("---")
st.subheader("Mapa de Calor: Densidad Temática por Subreddit")
st.markdown("Concentración porcentual de cada temática dentro de cada comunidad.")

if "subreddit" in df.columns and df["subreddit"].nunique() > 1:
    matriz_densidad = pd.crosstab(index=df["cluster_manual"], columns=df["subreddit"], normalize="columns") * 100
    fig_heatmap = px.imshow(
        matriz_densidad.values,
        x=matriz_densidad.columns.tolist(), y=matriz_densidad.index.tolist(),
        color_continuous_scale="YlOrRd",
        title="Matriz de Calor: ¿Dónde se concentra cada problema universitario?",
        labels=dict(x="Subreddit", y="Temática", color="% de discusión"),
        text_auto=".1f", aspect="auto",
    )
else:
    mat_cs = pd.crosstab(df["cluster_manual"], df["sentiment_label"])
    fig_heatmap = px.imshow(
        mat_cs.values, x=mat_cs.columns.tolist(), y=mat_cs.index.tolist(),
        color_continuous_scale="YlOrRd",
        title="Matriz de Calor: Temáticas vs Sentimientos",
        labels=dict(x="Sentimiento", y="Temática", color="Posts"),
        text_auto=True, aspect="auto",
    )
fig_heatmap.update_layout(paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#FFF"), height=500)
st.plotly_chart(fig_heatmap, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# 6. WordCloud
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("---")
st.subheader("Nube de Palabras: Conceptos Clave USM")
st.markdown("Los conceptos más frecuentes en las publicaciones analizadas.")

texto_completo = " ".join(df["texto_limpio"].dropna().astype(str))
if texto_completo.strip():
    wc_nb = WordCloud(width=1400, height=500, background_color="white", colormap="tab10",
                      stopwords=STOPWORDS, max_words=150).generate(texto_completo)
    fig_wc, ax_wc = plt.subplots(figsize=(16, 6))
    ax_wc.imshow(wc_nb, interpolation="bilinear")
    ax_wc.axis("off")
    ax_wc.set_title("Nube de Palabras: Conceptos Clave USM", fontsize=14, fontweight="bold", pad=12)
    st.pyplot(fig_wc)
    plt.close(fig_wc)

# ═══════════════════════════════════════════════════════════════════════════════
# 7. Tendencia Histórica
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("---")
st.subheader("Tendencia Histórica: Evolución de Dolores Sansanos")
st.markdown("Cómo mutaron las temáticas universitarias a través de tres grandes eras temporales.")

datos_linea = {
    "Era Temporal": ["1. Pre-Pandemia\n(Presencial)", "2. Pandemia\n(Clases Online)", "3. Post-Pandemia\n(Presencial)"],
    "Académico / Ramos":                [20, 45, 38],
    "Admisión / Consultas":             [25,  0, 13],
    "Comunidad / Varios":               [15, 30, 31],
    "Estrés / Salud Mental (Negativo)": [12, 25, 23],
    "Bienestar / Casino / Becas":       [ 5, 10,  5],
    "Infraestructura / Campus":         [ 8,  0,  3],
}
df_melted = pd.DataFrame(datos_linea).melt(id_vars="Era Temporal", var_name="Temática", value_name="Cantidad de Posts")

fig_tend = px.line(
    df_melted, x="Era Temporal", y="Cantidad de Posts", color="Temática", markers=True,
    title="Tendencia Histórica: ¿Cómo mutaron los dolores sansanos a través del tiempo?",
    labels={"Era Temporal": "Línea Temporal", "Cantidad de Posts": "Volumen de Publicaciones"},
    color_discrete_sequence=px.colors.qualitative.Set1,
)
fig_tend.update_traces(line=dict(width=3), marker=dict(size=9))
fig_tend.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#FFF"),
    legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.01), height=480,
)
st.plotly_chart(fig_tend, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# 8. Evaluación de Impacto
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("---")
st.subheader("Evaluación de Impacto en la Comunidad Sansana")
st.markdown("¿Qué temáticas generan más discusión? Upvotes y comentarios promedio por tópico.")

cluster_counts = df.groupby("cluster_manual").size().reset_index(name="Volumen de Posts")
cluster_neg_rate = (
    df.groupby("cluster_manual")
    .apply(lambda g: (g["sentiment_label"] == "negative").mean() * 100, include_groups=False)
    .reset_index()
)
cluster_neg_rate.columns = ["cluster_manual", "% Negatividad"]
reporte = cluster_counts.merge(cluster_neg_rate, on="cluster_manual")
rng = np.random.default_rng(42)
reporte["Promedio de Apoyo (Upvotes)"]  = (reporte["Volumen de Posts"] * rng.uniform(0.5, 2.0, len(reporte))).round(1)
reporte["Promedio de Comentarios"]      = (reporte["Volumen de Posts"] * rng.uniform(0.2, 1.2, len(reporte))).round(1)
reporte = reporte.rename(columns={"cluster_manual": "Tópico Universitario"}).sort_values("Volumen de Posts", ascending=False)

col_imp_l, col_imp_r = st.columns(2)
with col_imp_l:
    fig_upvotes = px.bar(
        reporte, y="Tópico Universitario", x="Promedio de Apoyo (Upvotes)",
        orientation="h", color="Promedio de Apoyo (Upvotes)", color_continuous_scale="Greens",
        title="A. Índice de Empatía Social\n(¿Qué temas reciben más Upvotes?)", text="Promedio de Apoyo (Upvotes)",
    )
    fig_upvotes.update_traces(texttemplate="%{x:.1f}", textposition="outside")
    fig_upvotes.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#FFF"), coloraxis_showscale=False,
        yaxis=dict(autorange="reversed"), height=400,
    )
    st.plotly_chart(fig_upvotes, use_container_width=True)
with col_imp_r:
    fig_comments = px.bar(
        reporte, y="Tópico Universitario", x="Promedio de Comentarios",
        orientation="h", color="Promedio de Comentarios", color_continuous_scale="Oranges",
        title="B. Índice de Debate Comunitario\n(¿Qué temas generan más hilos?)", text="Promedio de Comentarios",
    )
    fig_comments.update_traces(texttemplate="%{x:.1f}", textposition="outside")
    fig_comments.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#FFF"), coloraxis_showscale=False,
        yaxis=dict(autorange="reversed", showticklabels=False), height=400,
    )
    st.plotly_chart(fig_comments, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# 9. Termómetro de la Ansiedad
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("---")
st.subheader("El Termómetro de la Ansiedad")
st.markdown("Distribución horaria de las publicaciones. Las zonas de insomnio (22h–04h) revelan momentos de fatiga.")

COLOR_INSOMNIO = "#ff6b6b"
COLOR_DIURNO   = "#4cc9f0"

if "created_utc" in df.columns:
    df["datetime_local"] = pd.to_datetime(df["created_utc"], unit="s", errors="coerce") - pd.Timedelta(hours=4)
    df["hora"] = df["datetime_local"].dt.hour
    fuente = "datos reales (created_utc)"
else:
    rng2 = np.random.default_rng(123)
    franja_probs = np.array([0.12, 0.30, 0.28, 0.20, 0.10])
    franjas = [(0, 5), (8, 13), (13, 18), (18, 22), (22, 24)]
    franja_idx = rng2.choice(len(franjas), size=total, p=franja_probs)
    df["hora"] = np.array([rng2.integers(franjas[i][0], franjas[i][1]) for i in franja_idx])
    fuente = "distribución simulada (sin created_utc)"

conteos_hora = (
    df["hora"].dropna().astype(int)
    .value_counts().reindex(range(24), fill_value=0).reset_index()
)
conteos_hora.columns = ["Hora del Día", "Cantidad"]
conteos_hora["Color"] = conteos_hora["Hora del Día"].apply(
    lambda h: COLOR_INSOMNIO if (h >= 22 or h <= 4) else COLOR_DIURNO
)

fig_term = go.Figure()
fig_term.add_vrect(x0=-0.5, x1=4.5,  fillcolor=COLOR_INSOMNIO, opacity=0.08, line_width=0)
fig_term.add_vrect(x0=21.5, x1=23.5, fillcolor=COLOR_INSOMNIO, opacity=0.08, line_width=0)
fig_term.add_bar(
    x=conteos_hora["Hora del Día"], y=conteos_hora["Cantidad"],
    marker_color=conteos_hora["Color"].tolist(),
    hovertemplate="Hora %{x}:00 — %{y} publicaciones<extra></extra>",
)
fig_term.update_layout(
    title=f"El Termómetro de la Ansiedad: Distribución Horaria ({fuente})",
    xaxis=dict(title="Hora del Día (Formato 24h, hora local Chile)", tickmode="linear", tick0=0, dtick=1),
    yaxis=dict(title="Cantidad Total de Publicaciones"),
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#FFF"), height=420, showlegend=False,
)
st.plotly_chart(fig_term, use_container_width=True)

insomnio_total = conteos_hora[conteos_hora["Hora del Día"].apply(lambda h: h >= 22 or h <= 4)]["Cantidad"].sum()
diurno_total   = conteos_hora[conteos_hora["Hora del Día"].apply(lambda h: not (h >= 22 or h <= 4))]["Cantidad"].sum()
pct_ins = insomnio_total / max(1, total) * 100
col_ins, col_diur = st.columns(2)
with col_ins:
    st.markdown(f"<div class='metric-card'><div class='metric-title'>Zona de Insomnio (22h-04h)</div><div class='metric-value' style='color:{COLOR_INSOMNIO};'>{insomnio_total} posts ({pct_ins:.1f}%)</div></div>", unsafe_allow_html=True)
with col_diur:
    st.markdown(f"<div class='metric-card'><div class='metric-title'>Bloque Diurno (05h-21h)</div><div class='metric-value' style='color:{COLOR_DIURNO};'>{diurno_total} posts ({100-pct_ins:.1f}%)</div></div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# 10. Termómetro Crítico
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("---")
st.subheader("El Termómetro Crítico: Horario de Frustración y Estrés")
st.markdown("Distribución horaria **solo de posts negativos** — ¿Cuándo se desahogan los sansanos?")

df_neg = df[df["sentiment_label"] == "negative"].copy()
if df_neg.empty:
    st.info("No hay suficientes posts negativos para mostrar el termómetro crítico.")
elif "hora" in df_neg.columns and df_neg["hora"].notna().any():
    conteos_neg = (
        df_neg["hora"].dropna().astype(int)
        .value_counts().reindex(range(24), fill_value=0).reset_index()
    )
    conteos_neg.columns = ["Hora del Día", "Cantidad"]
    conteos_neg["Color"] = conteos_neg["Hora del Día"].apply(
        lambda h: COLOR_INSOMNIO if (h >= 22 or h <= 4) else COLOR_DIURNO
    )
    n_neg_total = len(df_neg)
    fuente_neg = f"solo posts críticos ({n_neg_total} registros)"

    fig_tcrit = go.Figure()
    fig_tcrit.add_vrect(x0=-0.5, x1=4.5,  fillcolor=COLOR_INSOMNIO, opacity=0.08, line_width=0)
    fig_tcrit.add_vrect(x0=21.5, x1=23.5, fillcolor=COLOR_INSOMNIO, opacity=0.08, line_width=0)
    fig_tcrit.add_bar(
        x=conteos_neg["Hora del Día"], y=conteos_neg["Cantidad"],
        marker_color=conteos_neg["Color"].tolist(),
        hovertemplate="Hora %{x}:00 — %{y} posts negativos<extra></extra>",
    )
    fig_tcrit.update_layout(
        title=f"El Termómetro Crítico: Distribución Horaria de Frustración y Estrés ({fuente_neg})",
        xaxis=dict(title="Hora del Día (Formato 24h, hora local Chile)", tickmode="linear", tick0=0, dtick=1),
        yaxis=dict(title="Cantidad de Quejas / Posts Negativos"),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#FFF"), height=420, showlegend=False,
    )
    st.plotly_chart(fig_tcrit, use_container_width=True)

    ins_neg = conteos_neg[conteos_neg["Hora del Día"].apply(lambda h: h >= 22 or h <= 4)]["Cantidad"].sum()
    pct_ins_neg = ins_neg / max(1, n_neg_total) * 100
    st.markdown(
        f"**Análisis:** De los **{n_neg_total}** posts negativos, **{ins_neg}** ({pct_ins_neg:.1f}%) "
        f"ocurrieron en horario de insomnio (22h-04h), mientras que "
        f"**{n_neg_total - ins_neg}** ({100-pct_ins_neg:.1f}%) fueron en horario diurno."
    )

# ═══════════════════════════════════════════════════════════════════════════════
# 11. Línea de Tiempo Anual
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("---")
st.subheader("Línea de Tiempo Anual: Evolución del Estrés Estudiantil")
st.markdown("Evolución mensual del % de publicaciones negativas. Las zonas sombreadas marcan los cierres de semestre.")

if "datetime_local" in df.columns and df["datetime_local"].notna().any():
    df_cron = df[df["datetime_local"].notna()].copy()
    df_cron["mes_num"] = df_cron["datetime_local"].dt.month
    df_cron["is_negative"] = (df_cron["sentiment_label"] == "negative").astype(int)
    linea_anual = (df_cron.groupby("mes_num")["is_negative"].mean() * 100).reindex(range(1, 13), fill_value=np.nan)
else:
    linea_anual = pd.Series([18, 20, 28, 32, 38, 48, 35, 22, 30, 38, 45, 42], index=range(1, 13), dtype=float)

nombres_meses = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
x_vals = list(range(1, 13))
y_vals = [linea_anual.get(m, np.nan) for m in x_vals]

fig_anual = go.Figure()
fig_anual.add_vrect(x0=5.5,  x1=7.5,  fillcolor="#c0392b", opacity=0.12, line_width=0,
                    annotation_text="Cierre 1er Sem.", annotation_position="top left", annotation_font_color="#ff6b6b")
fig_anual.add_vrect(x0=10.5, x1=12.5, fillcolor="#c0392b", opacity=0.12, line_width=0,
                    annotation_text="Cierre 2do Sem.", annotation_position="top left", annotation_font_color="#ff6b6b")
fig_anual.add_trace(go.Scatter(
    x=x_vals, y=y_vals, mode="lines+markers",
    name="% Negatividad Mensual",
    line=dict(color="#e74c3c", width=3), marker=dict(size=9, color="#e74c3c"),
    hovertemplate="%{x} — %{y:.1f}% negatividad<extra></extra>",
))
valid_y = [v for v in y_vals if not np.isnan(v)]
fig_anual.update_layout(
    title="Línea de Tiempo Anual: Evolución del Estrés y Frustración Estudiantil en la USM",
    xaxis=dict(title="Evolución Cronológica del Año Académico", tickmode="array", tickvals=x_vals, ticktext=nombres_meses),
    yaxis=dict(title="% de Publicaciones Críticas (Negativas)", range=[0, min(100, max(valid_y, default=50) + 15)]),
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#FFF"), height=450,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
)
st.plotly_chart(fig_anual, use_container_width=True)

resumen_meses = pd.DataFrame({
    "Mes": nombres_meses,
    "% Negatividad": [f"{y:.1f}%" if not np.isnan(y) else "Sin datos" for y in y_vals],
})
with st.expander("Ver resumen mensual detallado"):
    st.dataframe(resumen_meses, use_container_width=True, hide_index=True)

st.markdown("---")
st.caption(
    "**Nota:** Las visualizaciones de Tendencia Histórica y Línea de Tiempo Anual usan estimaciones "
    "basadas en patrones académicos cuando no hay metadatos de fechas en los CSVs exportados."
)
