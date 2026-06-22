import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from htbuilder import HtmlElement, div, ul, li, br, hr, a, p, img, styles, classes, fonts
from htbuilder.units import percent, px as ht_px
from htbuilder.funcs import rgba, rgb
import os
import sys

# Configurar página
st.set_page_config(
    page_title="r/RedditUSM",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Importar funciones
try:
    from src.analytics.sentiment import analyze_sentiment_advanced, STOPWORDS
    from src.analytics.reddit_search import deep_search_reddit, deep_search_reddit_timeline
except ImportError:
    from analytics.sentiment import analyze_sentiment_advanced, STOPWORDS
    from analytics.reddit_search import deep_search_reddit, deep_search_reddit_timeline

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        transition: transform 0.2s ease;
    }
    .metric-card:hover { transform: translateY(-2px); }
    .metric-title { color: #aaa; font-size: 0.85rem; margin-bottom: 0.4rem; }
    .metric-value { font-size: 1.6rem; font-weight: 700; }
    .period-badge {
        display: inline-block;
        background: rgba(99,110,250,0.15);
        border: 1px solid rgba(99,110,250,0.3);
        border-radius: 6px;
        padding: 0.15rem 0.5rem;
        font-size: 0.8rem;
        color: #636EFA;
    }
</style>
""", unsafe_allow_html=True)

# ── Helpers ───────────────────────────────────────────────────────────────────

@st.cache_data
def load_historical_data():
    paths = [
        "data/processed/reddit_sentiment.csv",
        "../data/processed/reddit_sentiment.csv",
        "src/data/usm_final/datos_entrenamiento_usm.csv",
        "../src/data/usm_final/datos_entrenamiento_usm.csv"
    ]
    for p in paths:
        if os.path.exists(p):
            return pd.read_csv(p)
    return pd.DataFrame()


def map_sentiment_label(val):
    if val in ['POS', 'positive']: return 'Positivo'
    if val in ['NEG', 'negative']: return 'Negativo'
    if val in ['NEU', 'neutral']: return 'Neutro'
    return str(val).capitalize()


SENTIMENT_COLORS = {
    'Positivo': '#00CC96',
    'Negativo': '#EF553B',
    'Neutro': '#636EFA',
}


def _apply_sentiment(df):
    """Add sentiment columns to a DataFrame that has 'full_content'."""
    res_sentiment = df['full_content'].apply(analyze_sentiment_advanced)
    df['sentiment_score'] = [r[0] for r in res_sentiment]
    df['sentiment_label'] = [r[1] for r in res_sentiment]
    df['Etiqueta'] = df['sentiment_label'].apply(map_sentiment_label)
    return df


# ── Dashboard  ────────────────────────────────────────────────────────────────

def render_dashboard(df, key_prefix="default"):
    if df.empty:
        st.warning("No se encontraron datos históricos.")
        return

    # Normalizar columnas
    if 'sentimiento' in df.columns:
        df['sentiment_label'] = df['sentimiento']
    if 'texto_limpio' in df.columns:
        df['full_content'] = df['texto_limpio']
    if 'full_content' not in df.columns and 'title' in df.columns and 'text' in df.columns:
        df['full_content'] = df['title'].fillna('') + " " + df['text'].fillna('')

    df['Etiqueta'] = df['sentiment_label'].apply(map_sentiment_label)

    st.markdown("## Métricas de Sentimiento")
    col1, col2, col3, col4 = st.columns(4)
    total_posts = len(df)

    count_pos = len(df[df['Etiqueta'] == 'Positivo'])
    count_neg = len(df[df['Etiqueta'] == 'Negativo'])
    count_neu = len(df[df['Etiqueta'] == 'Neutro'])

    with col1:
        st.markdown(f"<div class='metric-card'><div class='metric-title'>Posts Analizados</div><div class='metric-value' style='color:#FFF;'>{total_posts}</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-card'><div class='metric-title'>Positivos</div><div class='metric-value' style='color:#00CC96;'>{count_pos} ({count_pos/max(1,total_posts):.1%})</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='metric-card'><div class='metric-title'>Negativos</div><div class='metric-value' style='color:#EF553B;'>{count_neg} ({count_neg/max(1,total_posts):.1%})</div></div>", unsafe_allow_html=True)
    with col4:
        st.markdown(f"<div class='metric-card'><div class='metric-title'>Neutros</div><div class='metric-value' style='color:#636EFA;'>{count_neu} ({count_neu/max(1,total_posts):.1%})</div></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    row1_col1, row1_col2 = st.columns(2)

    with row1_col1:
        st.markdown("### Distribución Global")
        pie_df = pd.DataFrame({
            'Sentimiento': ['Positivo', 'Negativo', 'Neutro'],
            'Cantidad': [count_pos, count_neg, count_neu]
        })
        fig_pie = px.pie(
            pie_df,
            names='Sentimiento',
            values='Cantidad',
            color='Sentimiento',
            color_discrete_map=SENTIMENT_COLORS,
            hole=0.4
        )
        fig_pie.update_layout(margin=dict(t=30, b=0, l=0, r=0), paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#FFF"))
        st.plotly_chart(fig_pie, use_container_width=True)

    with row1_col2:
        if 'subreddit' in df.columns:
            st.markdown("### Por Subreddit")
            sub_counts = df.groupby(['subreddit', 'Etiqueta']).size().reset_index(name='Cantidad')
            fig_bar = px.bar(
                sub_counts, x='subreddit', y='Cantidad', color='Etiqueta',
                color_discrete_map=SENTIMENT_COLORS,
                barmode='group'
            )
            fig_bar.update_layout(margin=dict(t=30, b=0, l=0, r=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#FFF"))
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("La columna 'subreddit' no está disponible.")

    st.markdown("---")
    st.markdown("### WordCloud")
    if 'full_content' in df.columns:
        texto_completo = " ".join(df['full_content'].dropna().astype(str))
        if texto_completo.strip():
            wc = WordCloud(
                width=1200, height=400,
                background_color='#0E1117',
                colormap='Set2',
                stopwords=STOPWORDS
            ).generate(texto_completo)

            fig, ax = plt.subplots(figsize=(15, 5), facecolor='#0E1117')
            ax.imshow(wc, interpolation='bilinear')
            ax.axis('off')
            st.pyplot(fig)

    st.markdown("---")
    st.markdown("### Explorador de Textos")
    search_term = st.text_input("🔍 Filtrar textos...", key=f"explorer_search_{key_prefix}")

    df_display = df.copy()
    if search_term:
        mask = df_display['full_content'].astype(str).str.contains(search_term, case=False, na=False)
        df_display = df_display[mask]

    cols_to_show = ['Etiqueta']
    if 'subreddit' in df_display.columns: cols_to_show.append('subreddit')
    if 'full_content' in df_display.columns: cols_to_show.append('full_content')
    if 'score' in df_display.columns: cols_to_show.append('score')

    st.dataframe(df_display[cols_to_show], use_container_width=True, hide_index=True)


# ── Análisis en Vivo  ────────────────────────────────────────────────────────

def live_analysis_ui():
    st.markdown("## Análisis en Vivo")
    st.write("Busca información usando el archivo histórico de Reddit vía PullPush.io (sin API keys).")

    with st.form("live_search_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            query = st.text_input("Término de Búsqueda", value="USM")
        with col2:
            subs = st.multiselect(
                "Subreddits",
                ["chile", "EducacionChile", "valparaiso", "Santiago", "RepublicadeChile", "ChileIT", "AskChile"],
                default=["chile", "EducacionChile"]
            )
        with col3:
            limit = st.slider("Límite por subreddit", 10, 100, 20)

        submit = st.form_submit_button("🚀 Iniciar Extracción y Análisis")

    if submit:
        if not subs:
            st.warning("Selecciona al menos un subreddit.")
            return

        with st.spinner("Buscando en Reddit y analizando sentimientos..."):
            df_results = deep_search_reddit(query, subs, limit=limit)

            if df_results is None or df_results.empty:
                st.warning("No se encontraron resultados para los parámetros ingresados.")
            else:
                st.success(f"¡Extracción completada! Se analizarán {len(df_results)} posts.")

                df_results['full_content'] = df_results['title'].fillna('') + " " + df_results['text'].fillna('')
                progress = st.progress(0, text="Clasificando sentimientos...")

                res_sentiment = []
                for i, text in enumerate(df_results['full_content']):
                    res_sentiment.append(analyze_sentiment_advanced(text))
                    progress.progress((i + 1) / len(df_results), text=f"Clasificando {i+1}/{len(df_results)}...")

                progress.empty()
                df_results['sentiment_score'] = [r[0] for r in res_sentiment]
                df_results['sentiment_label'] = [r[1] for r in res_sentiment]

                st.markdown("---")
                render_dashboard(df_results, key_prefix="live")


# ── Evolución Temporal ────────────────────────────────────────────────────────

def timeline_analysis_ui():
    st.markdown("## 📅 Evolución Temporal de Sentimientos")
    st.markdown(
        "Analiza cómo cambió la percepción de la USM en Reddit desde la **pandemia (2019)** "
        "hasta la **actualidad (2025)**, semestre a semestre."
    )

    with st.form("timeline_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            start_year = st.selectbox("Año inicio", list(range(2019, 2026)), index=0)
        with col2:
            end_year = st.selectbox("Año fin", list(range(2019, 2026)), index=6)
        with col3:
            limit = st.slider("Posts por subreddit/término/semestre", 10, 100, 50, key="timeline_limit")

        submit = st.form_submit_button("📊 Generar Línea Temporal")

    if submit:
        if start_year > end_year:
            st.error("El año de inicio debe ser menor o igual al año de fin.")
            return

        with st.spinner("Extrayendo datos históricos semestre a semestre... esto puede tomar unos minutos."):
            df_timeline = deep_search_reddit_timeline(
                start_year=start_year,
                end_year=end_year,
                limit=limit,
            )

        if df_timeline.empty:
            st.warning("No se encontraron datos para el rango seleccionado.")
            return

        st.success(f"✅ Se encontraron **{len(df_timeline)}** posts únicos en {start_year}–{end_year}")

        # Apply sentiment analysis
        with st.spinner("Analizando sentimientos..."):
            df_timeline['full_content'] = (
                df_timeline['title'].fillna('') + " " + df_timeline['text'].fillna('')
            )

            progress = st.progress(0, text="Clasificando sentimientos...")
            res_sentiment = []
            for i, text in enumerate(df_timeline['full_content']):
                res_sentiment.append(analyze_sentiment_advanced(text))
                if (i + 1) % 10 == 0 or i == len(df_timeline) - 1:
                    progress.progress(
                        (i + 1) / len(df_timeline),
                        text=f"Clasificando {i+1}/{len(df_timeline)}..."
                    )
            progress.empty()

            df_timeline['sentiment_score'] = [r[0] for r in res_sentiment]
            df_timeline['sentiment_label'] = [r[1] for r in res_sentiment]
            df_timeline['Etiqueta'] = df_timeline['sentiment_label'].apply(map_sentiment_label)

        # ── Metrics row ──
        st.markdown("---")
        st.markdown("### Resumen General")
        m1, m2, m3, m4 = st.columns(4)
        total = len(df_timeline)
        n_pos = len(df_timeline[df_timeline['Etiqueta'] == 'Positivo'])
        n_neg = len(df_timeline[df_timeline['Etiqueta'] == 'Negativo'])
        n_neu = len(df_timeline[df_timeline['Etiqueta'] == 'Neutro'])

        with m1:
            st.markdown(f"<div class='metric-card'><div class='metric-title'>Posts Totales</div><div class='metric-value' style='color:#FFF;'>{total}</div></div>", unsafe_allow_html=True)
        with m2:
            st.markdown(f"<div class='metric-card'><div class='metric-title'>Positivos</div><div class='metric-value' style='color:#00CC96;'>{n_pos} ({n_pos/max(1,total):.1%})</div></div>", unsafe_allow_html=True)
        with m3:
            st.markdown(f"<div class='metric-card'><div class='metric-title'>Negativos</div><div class='metric-value' style='color:#EF553B;'>{n_neg} ({n_neg/max(1,total):.1%})</div></div>", unsafe_allow_html=True)
        with m4:
            st.markdown(f"<div class='metric-card'><div class='metric-title'>Neutros</div><div class='metric-value' style='color:#636EFA;'>{n_neu} ({n_neu/max(1,total):.1%})</div></div>", unsafe_allow_html=True)

        # ── Line chart: counts per semester ──
        st.markdown("---")
        st.markdown("### Evolución de Sentimientos por Semestre")

        period_counts = (
            df_timeline.groupby(['period', 'Etiqueta'])
            .size()
            .reset_index(name='Cantidad')
        )

        fig_line = px.line(
            period_counts, x='period', y='Cantidad', color='Etiqueta',
            color_discrete_map=SENTIMENT_COLORS,
            markers=True,
            labels={'period': 'Período', 'Cantidad': 'Nº de Posts'},
        )
        fig_line.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#FFF"),
            xaxis=dict(title="Período", gridcolor="rgba(255,255,255,0.05)"),
            yaxis=dict(title="Nº de Posts", gridcolor="rgba(255,255,255,0.08)"),
            legend_title_text="Sentimiento",
            hovermode="x unified",
        )
        st.plotly_chart(fig_line, use_container_width=True)

        # ── Stacked area: proportions ──
        st.markdown("### Proporción de Sentimientos en el Tiempo")

        period_totals = df_timeline.groupby('period').size().reset_index(name='total')
        period_props = period_counts.merge(period_totals, on='period')
        period_props['Proporción'] = period_props['Cantidad'] / period_props['total']

        fig_area = px.area(
            period_props, x='period', y='Proporción', color='Etiqueta',
            color_discrete_map=SENTIMENT_COLORS,
            labels={'period': 'Período', 'Proporción': 'Proporción'},
            groupnorm='fraction',
        )
        fig_area.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#FFF"),
            xaxis=dict(title="Período", gridcolor="rgba(255,255,255,0.05)"),
            yaxis=dict(
                title="Proporción",
                gridcolor="rgba(255,255,255,0.08)",
                tickformat=".0%",
            ),
            legend_title_text="Sentimiento",
            hovermode="x unified",
        )
        st.plotly_chart(fig_area, use_container_width=True)

        # ── Summary table ──
        st.markdown("### Detalle por Semestre")

        pivot = period_counts.pivot_table(
            index='period', columns='Etiqueta', values='Cantidad', fill_value=0
        ).reset_index()
        pivot.columns.name = None

        for col in ['Positivo', 'Negativo', 'Neutro']:
            if col not in pivot.columns:
                pivot[col] = 0

        pivot['Total'] = pivot['Positivo'] + pivot['Negativo'] + pivot['Neutro']
        pivot = pivot.rename(columns={'period': 'Período'})
        pivot = pivot[['Período', 'Positivo', 'Negativo', 'Neutro', 'Total']]

        st.dataframe(pivot, use_container_width=True, hide_index=True)

        # ── Hitos contextuales ──
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

        # ── WordCloud de todo el timeline ──
        st.markdown("---")
        st.markdown("### WordCloud del Período Completo")
        texto = " ".join(df_timeline['full_content'].dropna().astype(str))
        if texto.strip():
            wc = WordCloud(
                width=1200, height=400,
                background_color='#0E1117',
                colormap='Set2',
                stopwords=STOPWORDS,
            ).generate(texto)

            fig_wc, ax = plt.subplots(figsize=(15, 5), facecolor='#0E1117')
            ax.imshow(wc, interpolation='bilinear')
            ax.axis('off')
            st.pyplot(fig_wc)


# ── Main  ─────────────────────────────────────────────────────────────────────

def main():
    st.title("📈 r/RedditUSM")
    st.markdown(
        "Analizador de tendencias de opiniones sobre la UTFSM utilizando "
        "**Natural Language Processing (NLP)**. Proyecto destinado al ramo "
        "**TEL 354** (Minería de datos)"
    )

    tab1, tab2, tab3 = st.tabs([
        "📊 Dashboard Histórico",
        "🔍 Análisis en Vivo",
        "📅 Evolución Temporal",
    ])

    with tab1:
        df_hist = load_historical_data()
        render_dashboard(df_hist, key_prefix="hist")

    with tab2:
        live_analysis_ui()

    with tab3:
        timeline_analysis_ui()


if __name__ == "__main__":
    main()
