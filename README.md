# RedditUSM 🎓

> Análisis de opiniones sobre la Universidad Técnica Federico Santa María a partir de publicaciones en Reddit.

---

## 📋 Descripción

RedditUSM es un sistema de análisis de opiniones (*sentiment analysis*) que extrae y procesa publicaciones de Reddit relacionadas con la UTFSM. El proyecto aplica técnicas de procesamiento de lenguaje natural (NLP) y aprendizaje automático para identificar tendencias, tópicos y sentimientos expresados por la comunidad.

---

## 🚀 Características

- Scraping automatizado de posts y comentarios desde Reddit (PRAW)
- Análisis de sentimientos con modelos de lenguaje (pysentimiento / RoBERTa)
- Modelado de tópicos con LDA y BERTopic
- Clasificación de textos con SVM y regresión logística
- Clustering semántico con K-Means
- Pipeline modular y reproducible

---

## 🗂️ Estructura del proyecto

```
RedditUSM/
├── data/
│   ├── raw/               # Datos crudos descargados de Reddit
│   └── processed/         # Datos limpios y preprocesados
├── notebooks/
│   ├── 01_scraping.ipynb
│   ├── 02_preprocessing.ipynb
│   ├── 03_sentiment.ipynb
│   ├── 04_topic_modeling.ipynb
│   └── 05_classification.ipynb
├── src/
│   ├── scraper.py         # Módulo de extracción de datos
│   ├── preprocess.py      # Limpieza y normalización de texto
│   ├── sentiment.py       # Análisis de sentimientos
│   ├── topics.py          # Modelado de tópicos
│   └── classifier.py      # Modelos de clasificación
├── results/
│   ├── figures/           # Visualizaciones generadas
│   └── reports/           # Reportes y métricas
├── requirements.txt
├── .env.example
└── README.md
```

---

## ⚙️ Instalación

### Prerrequisitos

- Python 3.9+
- Cuenta de desarrollador en Reddit ([Reddit Apps](https://www.reddit.com/prefs/apps))

### Pasos

```bash
# 1. Clonar el repositorio
git clone https://github.com/usuario/RedditUSM.git
cd RedditUSM

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate        # Linux/macOS
# venv\Scripts\activate         # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar credenciales de Reddit
cp .env.example .env
# Editar .env con tus credenciales de la Reddit API
```

### Variables de entorno (`.env`)

```env
REDDIT_CLIENT_ID=tu_client_id
REDDIT_CLIENT_SECRET=tu_client_secret
REDDIT_USER_AGENT=RedditUSM/1.0
```

---

## 🧪 Uso

```bash
# Ejecutar scraping
python src/scraper.py --query "UTFSM" --subreddit "chile" --limit 500

# Preprocesar datos
python src/preprocess.py

# Análisis de sentimientos
python src/sentiment.py

# Modelado de tópicos
python src/topics.py --method bertopic
```

O bien, ejecutar los notebooks en orden desde la carpeta `notebooks/`.

---

## 📊 Metodología

| Etapa | Técnica | Herramienta |
|---|---|---|
| Extracción | Web scraping via API | PRAW |
| Preprocesamiento | Tokenización, lematización | spaCy |
| Sentimientos | Clasificación con transformer | pysentimiento |
| Tópicos | LDA / BERTopic | Gensim, BERTopic |
| Clustering | K-Means semántico | scikit-learn |
| Clasificación | SVM, Regresión Logística | scikit-learn |

---

## 📈 Métricas de evaluación

- **Coherencia de tópicos:** Cv score
- **Clasificación:** F1-macro, precisión, recall
- **Clustering:** Silhouette score, índice Calinski-Harabasz

---

## 🛠️ Stack tecnológico

![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python)
![PRAW](https://img.shields.io/badge/PRAW-7.x-orange)
![spaCy](https://img.shields.io/badge/spaCy-3.x-09a3d5)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.x-f7931e?logo=scikit-learn)
![BERTopic](https://img.shields.io/badge/BERTopic-latest-blueviolet)

---

## 📄 Licencia

Este proyecto fue desarrollado con fines académicos en el contexto del curso **TEL354 — Minería de Datos**, Universidad Técnica Federico Santa María.

---

UTFSM · Departamento de Electrónica · Santiago, Chile
