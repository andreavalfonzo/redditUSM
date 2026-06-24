"""
app.py — Punto de entrada de r/RedditUSM.
Define la navegación lateral con st.navigation y registra las páginas.
"""

import streamlit as st

# Definir páginas con st.Page (cada una tiene su propio set_page_config)
pg_notebook = st.Page("pages/notebook.py",  title="Todas las métricas", icon="📊", default=True)
pg_live     = st.Page("pages/live.py",      title="Análisis en Vivo",icon="🔍")
pg_timeline = st.Page("pages/timeline.py",  title="Evolución Temporal",icon="📅")

# Navegación lateral agrupada
nav = st.navigation(
    {
        "Análisis": [pg_notebook],
        "Búsqueda": [pg_live, pg_timeline],
    }
)

st.sidebar.markdown(
    """
    <div style="font-size:0.78rem; color: rgba(120, 120, 120,0.75); line-height:1.7;">
        <b style="color:rgba(210,210,210,0.9);">TEL 354 · Minería de Datos</b><br>
        Byron Agurto<br>
        Andrea Alfonzo<br>
        Gabriela Trigo<br>
        <span style="font-size:0.72rem; opacity:0.6;">© Todos los derechos reservados</span>
    </div>
    """,
    unsafe_allow_html=True,
)

nav.run()
