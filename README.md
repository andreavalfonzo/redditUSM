# RedditUSM 🎓

> Sistema de minería de datos y análisis de opiniones sobre la Universidad Técnica Federico Santa María mediante publicaciones de Reddit.

---

# 📋 Descripción

RedditUSM es un proyecto académico enfocado en el análisis de opiniones y percepciones sobre la Universidad Técnica Federico Santa María (UTFSM) utilizando publicaciones y comentarios obtenidos desde Reddit.

El objetivo principal es construir un pipeline de minería de datos capaz de:

- Extraer publicaciones relacionadas con la UTFSM
- Procesar lenguaje natural en español
- Detectar sentimientos y emociones
- Identificar tópicos frecuentes
- Analizar tendencias temporales
- Generar visualizaciones y métricas útiles

El proyecto utiliza técnicas de NLP (*Natural Language Processing*), análisis de sentimientos y modelado de tópicos para transformar texto no estructurado en información interpretable.

---

# 🚧 Estado actual del proyecto

Actualmente el proyecto se encuentra en desarrollo inicial.

Ya se encuentra implementado:

- Entorno virtual de Python
- Repositorio GitHub
- Estructura modular del proyecto
- Pipeline de procesamiento funcional
- Limpieza y preprocesamiento de texto
- Análisis exploratorio de datos
- Análisis de sentimientos con `pysentimiento`
- Generación automática de visualizaciones
- Exportación de datasets procesados en CSV

La extracción real desde Reddit será habilitada cuando se obtengan las credenciales oficiales de la API de Reddit.

Actualmente el proyecto utiliza datasets ficticios (`reddit_mock.csv`) para desarrollar y validar el pipeline de procesamiento, debido a que el acceso oficial a la API de Reddit aún se encuentra pendiente de aprobación.

Mientras tanto, se trabaja con datasets de prueba para desarrollar y validar el pipeline de análisis.

---

# 🚀 Características implementadas

- Preprocesamiento de texto manteniendo emojis y expresiones informales
- Limpieza básica de datos textuales
- Análisis exploratorio con pandas
- Análisis de sentimientos usando `pysentimiento`
- Generación automática de visualizaciones
- Exportación automática de resultados procesados

---

# 🚀 Características previstas

- Extracción automatizada de posts y comentarios desde Reddit usando PRAW
- Identificación de tópicos mediante LDA y BERTopic
- Clasificación de texto con SVM y regresión logística
- Clustering semántico con K-Means
- Dashboard interactivo
- Análisis temporal de opiniones

---

# 🗂️ Estructura actual del proyecto

```text
RedditUSM/
│
├── data/
│   ├── raw/
│   │   └── reddit_mock.csv
│   │
│   └── processed/
│       ├── reddit_clean.csv
│       └── reddit_sentiment.csv
│
├── notebooks/
│
├── results/
│   ├── figures/
│   │   └── sentimientos.png
│   │
│   └── reports/
│
├── src/
│   ├── analysis.py
│   ├── classifier.py
│   ├── preprocess.py
│   ├── scraper.py
│   ├── sentiment.py
│   ├── topics.py
│   └── visualize.py
│
├── .gitignore
├── main.py
├── README.md
└── requirements.txt
```

---

# ⚙️ Instalación

## Requisitos

- Python 3.9 o superior
- Cuenta de desarrollador en Reddit
- Git

---

## 1. Clonar el repositorio

```bash
git clone https://github.com/andreavalfonzo/redditUSM.git
cd redditUSM
```

---

## 2. Crear entorno virtual

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### Linux/macOS

```bash
python -m venv .venv
source .venv/bin/activate
```

---

## 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

---

## 4. Configurar variables de entorno

Crear un archivo `.env` basado en `.env.example`.

Ejemplo:

```env
REDDIT_CLIENT_ID=tu_client_id
REDDIT_CLIENT_SECRET=tu_client_secret
REDDIT_USER_AGENT=RedditUSM/1.0
```

---

# 🧪 Uso actual

Actualmente se encuentran implementados los módulos de:

- Preprocesamiento de texto
- Análisis exploratorio de datos
- Análisis de sentimientos
- Visualización de resultados

utilizando datasets de prueba mientras se espera la aprobación de la API de Reddit.

```bash
# Preprocesamiento
python src/preprocess.py

# Análisis exploratorio
python src/analysis.py

# Análisis de sentimientos
python src/sentiment.py

# Visualización
python src/visualize.py
```

Cuando las credenciales de Reddit sean aprobadas, se habilitará la extracción real de publicaciones mediante la API oficial de Reddit.

---

# 📂 Resultados actuales

El pipeline actual genera automáticamente:

- `reddit_clean.csv`
- `reddit_sentiment.csv`
- `sentimientos.png`

Estos archivos contienen:

- Texto procesado
- Clasificación emocional
- Probabilidades de sentimiento
- Visualizaciones iniciales del dataset

---

# 📊 Metodología

| Etapa | Descripción | Herramienta |
|---|---|---|
| Extracción | Descarga de posts y comentarios | PRAW |
| Preprocesamiento | Limpieza y normalización de texto | pandas, regex |
| NLP | Tokenización y análisis lingüístico | spaCy |
| Sentimientos | Clasificación emocional | pysentimiento |
| Tópicos | Descubrimiento de temas | LDA, BERTopic |
| Clasificación | Modelos supervisados | scikit-learn |
| Visualización | Gráficos y métricas | matplotlib, seaborn |

---

# 🧠 Objetivos del proyecto

- Analizar la percepción pública de la UTFSM en Reddit
- Detectar tendencias de opinión estudiantil
- Identificar problemáticas frecuentes
- Analizar evolución temporal de sentimientos
- Aplicar técnicas reales de minería de datos y NLP en español

---

# 📈 Métricas de evaluación

## Clasificación de sentimientos

- F1-Score Macro
- Accuracy
- Precision
- Recall
- Matriz de confusión

## Modelado de tópicos

- Coherencia semántica (Cv Score)
- Silhouette Score
- Calinski-Harabasz Index

---

## 🛠️ Stack tecnológico

![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python)
![PRAW](https://img.shields.io/badge/PRAW-7.x-orange)
![spaCy](https://img.shields.io/badge/spaCy-3.x-09a3d5)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.x-f7931e?logo=scikit-learn)
![BERTopic](https://img.shields.io/badge/BERTopic-latest-blueviolet)

---

# ⚠️ Consideraciones

- El proyecto utiliza únicamente información pública disponible en Reddit.
- No se almacenará información sensible o privada.
- Los datos serán utilizados exclusivamente con fines académicos.
- Los emojis y expresiones informales serán conservados para mantener el contexto emocional del lenguaje.

---

## 📄 Licencia

Este proyecto fue desarrollado con fines académicos en el contexto del curso **TEL354 — Minería de Datos**, Universidad Técnica Federico Santa María.

---

UTFSM · Departamento de Electrónica · Santiago, Chile