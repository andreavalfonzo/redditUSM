"""
🤖 Universal Reddit Scraper - Versión Simplificada para USM
Motor de búsqueda y recolección de datos para minería de sentimientos.
"""
import requests
import pandas as pd
import datetime
import time
import os
import argparse
import sys
from pathlib import Path
from scraper.async_scraper import run_async_scraper
from analytics.sentiment import analyze_sentiment_advanced, STOPWORDS

def main():
    parser = argparse.ArgumentParser(description="🤖 Universal Reddit Scraper (Versión Slim)")
    parser.add_argument("target", help="Subreddit a scrapear")
    parser.add_argument("--limit", type=int, default=100, help="Límite de posts")
    parser.add_argument("--mode", choices=["history", "full"], default="full")
    
    args = parser.parse_args()
    
    print("=" * 50)
    print(f"🚀 Iniciando recolección en r/{args.target}")
    print("=" * 50)
    
    # Ejecutar el motor asíncrono del proyecto
    stats = run_async_scraper(
        target=args.target,
        limit=args.limit,
        is_user=False,
        download_media=False,
        scrape_comments=True
    )
    
    print("\n✅ Recolección completa!")
    print(f"📊 Posts: {stats['posts']}")
    print(f"💬 Comentarios: {stats['comments']}")
    print(f"📂 Datos guardados en: data/r_{args.target}")

if __name__ == "__main__":
    main()
