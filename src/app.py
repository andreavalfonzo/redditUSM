import streamlit as st
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from htbuilder import HtmlElement, div, ul, li, br, hr, a, p, img, styles, classes, fonts
from htbuilder.units import percent, px as ht_px
from htbuilder.funcs import rgba, rgb
import asyncio
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
    from src.reddit_search import deep_search_reddit
except ImportError:
    from analytics.sentiment import analyze_sentiment_advanced, STOPWORDS
    from reddit_search import deep_search_reddit

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

def render_dashboard(df):
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
            color_discrete_map={'Positivo': '#00CC96', 'Negativo': '#EF553B', 'Neutro': '#636EFA'},
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
                color_discrete_map={'Positivo': '#00CC96', 'Negativo': '#EF553B', 'Neutro': '#636EFA'},
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
    search_term = st.text_input("🔍 Filtrar textos...")
    
    df_display = df.copy()
    if search_term:
        mask = df_display['full_content'].astype(str).str.contains(search_term, case=False, na=False)
        df_display = df_display[mask]
    
    cols_to_show = ['Etiqueta']
    if 'subreddit' in df_display.columns: cols_to_show.append('subreddit')
    if 'full_content' in df_display.columns: cols_to_show.append('full_content')
    if 'score' in df_display.columns: cols_to_show.append('score')
    
    st.dataframe(df_display[cols_to_show], use_container_width=True, hide_index=True)

def live_analysis_ui():
    st.markdown("## Análisis Asíncrono en Vivo")
    st.write("Busca información en tiempo real usando el motor asíncrono de Reddit (Sin necesidad de API keys).")
    
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
            
        submit = st.form_submit_button("Iniciar Extracción y Análisis")
        
    if submit:
        if not subs:
            st.warning("Selecciona al menos un subreddit.")
            return
            
        with st.spinner("Scrapeando Reddit y analizando sentimientos... esto tomará unos segundos."):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            df_results = loop.run_until_complete(deep_search_reddit(query, subs, limit=limit))
            
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
                render_dashboard(df_results)

def main():
    st.title("📈 r/RedditUSM")
    st.markdown("Analizador de tendencias de opiniones sobre la UTFSM utilizando **Natural Language Processing (NLP)**. Proyecto destinado al ramo **TEL 354** (Minería de datos)")
    
    tab1, tab2 = st.tabs(["Dashboard Histórico", "Análisis en Vivo"])
    
    with tab1:
        df_hist = load_historical_data()
        render_dashboard(df_hist)
        
    with tab2:
        live_analysis_ui()

if __name__ == "__main__":
    main()
