"""
Analytics module - Sentiment Analysis, Word Clouds, Statistics
"""
import re
import unicodedata
from collections import Counter
from pathlib import Path
import sys

# ... (POSITIVE_WORDS, NEGATIVE_WORDS, INTENSIFIERS unchanged)

# Simple sentiment analysis without external dependencies
POSITIVE_WORDS = {
    'good', 'great', 'awesome', 'excellent', 'amazing', 'love', 'best', 'perfect',
    'nice', 'wonderful', 'fantastic', 'brilliant', 'superb', 'outstanding', 'happy',
    'beautiful', 'helpful', 'thanks', 'thank', 'appreciate', 'recommend', 'interesting',
    'useful', 'cool', 'fun', 'enjoy', 'like', 'loved', 'impressive', 'incredible',
    # Spanish keywords
    'bueno', 'excelente', 'genial', 'increible', 'bacán', 'buena', 'gracias', 'ayuda',
    'interesante', 'util', 'mejor', 'amor', 'feliz', 'perfecto', 'fantastico', 'recomiendo'
}

NEGATIVE_WORDS = {
    'bad', 'terrible', 'awful', 'horrible', 'hate', 'worst', 'poor', 'disappointing',
    'useless', 'waste', 'annoying', 'boring', 'ugly', 'stupid', 'dumb', 'fail',
    'wrong', 'broken', 'sad', 'angry', 'frustrated', 'scam', 'fake', 'trash',
    'pathetic', 'ridiculous', 'disgusting', 'overpriced', 'avoid', 'never',
    # Spanish keywords
    'malo', 'terrible', 'horrible', 'odio', 'peor', 'inutil', 'basura', 'fome', 'mucha',
    'estupido', 'tonto', 'fallo', 'error', 'triste', 'enojado', 'frustrado', 'estafa'
}

INTENSIFIERS = {
    'very', 'really', 'extremely', 'absolutely', 'totally', 'completely',
    # Spanish keywords
    'muy', 'realmente', 'extremadamente', 'absolutamente', 'totalmente', 'completamente'
}

def analyze_sentiment(text):
    """
    Simple sentiment analysis.
    Returns: (score, label)
    - score: -1.0 to 1.0
    - label: 'positive', 'negative', or 'neutral'
    """
    if not text:
        return 0.0, 'neutral'
    
    # Clean and tokenize (supporting Spanish characters)
    word_pattern = re.compile(r'\b[a-zA-ZáéíóúüñÁÉÍÓÚÜÑ]+\b')
    words = word_pattern.findall(text.lower())
    
    if not words:
        return 0.0, 'neutral'
    
    positive_count = 0
    negative_count = 0
    intensifier_next = False
    
    for word in words:
        multiplier = 1.5 if intensifier_next else 1.0
        
        if word in POSITIVE_WORDS:
            positive_count += multiplier
        elif word in NEGATIVE_WORDS:
            negative_count += multiplier
        
        intensifier_next = word in INTENSIFIERS
    
    total = positive_count + negative_count
    if total == 0:
        return 0.0, 'neutral'
    
    score = (positive_count - negative_count) / len(words)
    score = max(-1.0, min(1.0, score * 5))  # Normalize
    
    if score > 0.1:
        label = 'positive'
    elif score < -0.1:
        label = 'negative'
    else:
        label = 'neutral'
    
    return round(score, 3), label

def analyze_posts_sentiment(posts):
    """Analyze sentiment for a list of posts."""
    results = []
    sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
    
    for post in posts:
        text = f"{post.get('title', '')} {post.get('selftext', '')}"
        score, label = analyze_sentiment(text)
        post['sentiment_score'] = score
        post['sentiment_label'] = label
        sentiment_counts[label] += 1
        results.append(post)
    
    return results, sentiment_counts

def analyze_comments_sentiment(comments):
    """Analyze sentiment for comments."""
    results = []
    sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
    
    for comment in comments:
        score, label = analyze_sentiment(comment.get('body', ''))
        comment['sentiment_score'] = score
        comment['sentiment_label'] = label
        sentiment_counts[label] += 1
        results.append(comment)
    
    return results, sentiment_counts

# Comprehensive Stopwords (Spanish + English)
# Chilean slang and variations included
STOPWORDS = {
    # English
    'a', 'about', 'after', 'again', 'all', 'also', 'amp', 'an', 'and', 'any', 'are', 'as', 'at',
    'be', 'because', 'been', 'before', 'being', 'below', 'between', 'but', 'by', 'can', 'com',
    'could', 'deleted', 'did', 'do', 'does', 'during', 'each', 'even', 'few', 'for', 'from',
    'further', 'get', 'got', 'had', 'has', 'have', 'he', 'her', 'here', 'his', 'how', 'http',
    'https', 'i', 'if', 'in', 'into', 'is', 'it', 'its', 'just', 'know', 'like', 'may', 'me',
    'might', 'more', 'most', 'must', 'my', 'myself', 'nan', 'new', 'no', 'nor', 'not', 'of',
    'on', 'once', 'only', 'or', 'other', 'our', 'own', 'people', 'reddit', 'removed', 'same',
    'shall', 'she', 'should', 'so', 'some', 'such', 'than', 'that', 'the', 'their', 'them',
    'then', 'there', 'these', 'they', 'this', 'those', 'through', 'think', 'time', 'to', 'too',
    'two', 'under', 'until', 'up', 'very', 'want', 'was', 'way', 'we', 'were', 'what', 'when',
    'where', 'which', 'while', 'who', 'whom', 'why', 'will', 'with', 'would', 'www', 'year', 'you', 'your',
    # Spanish - Básicas y Conectores
    'acá', 'ahí', 'ahora', 'al', 'algo', 'alguna', 'algunas', 'alguno', 'algunos', 'allá', 'allí',
    'ante', 'antes', 'aquel', 'aquella', 'aquellas', 'aquello', 'aquellos', 'aquí', 'así', 'aun', 'aún',
    'aunque', 'bajo', 'bien', 'bueno', 'cada', 'casa', 'casi', 'caso', 'casos', 'cl', 'como', 'cómo',
    'con', 'conmigo', 'contra', 'contigo', 'creo', 'cual', 'cuál', 'cuales', 'cuáles', 'cuando', 'cuándo',
    'cuanto', 'cuántos', 'da', 'dar', 'dato', 'de', 'decir', 'del', 'desde', 'después', 'día', 'dice',
    'dijo', 'donde', 'dónde', 'dos', 'durante', 'e', 'el', 'él', 'ella', 'ellas', 'ello', 'ellos',
    'en', 'entonces', 'entre', 'era', 'eran', 'es', 'esa', 'ese', 'eso', 'esas', 'esos', 'esta',
    'está', 'estaba', 'estamos', 'están', 'estar', 'estas', 'estás', 'este', 'esto', 'estos', 'estoy',
    'etc', 'fue', 'fueron', 'ha', 'había', 'habían', 'haber', 'hace', 'hacen', 'hacer', 'hacia', 'haciendo',
    'han', 'hasta', 'hay', 'he', 'hecho', 'hola', 'hola.', 'hoy', 'ir', 'jamás', 'junto', 'la', 'las',
    'le', 'les', 'lo', 'los', 'ma', 'mal', 'malo', 'más', 'mas', 'me', 'mi', 'mí', 'mismo', 'misma',
    'mismos', 'mismas', 'mis', 'mientras', 'mucho', 'muchos', 'mucha', 'muchas', 'muy', 'nada', 'ni',
    'no', 'nos', 'nosotras', 'nosotros', 'nunca', 'o', 'otra', 'otro', 'otras', 'otros', 'pa', 'para',
    'parece', 'parte', 'pasa', 'pero', 'poco', 'pocos', 'poda', 'poder', 'podría', 'podrían', 'porque',
    'porqué', 'por', 'post', 'puede', 'pueden', 'puedo', 'puedas', 'puntos', 'punto', 'que', 'qué',
    'quedan', 'queda', 'quien', 'quién', 'quienes', 'quiénes', 'quiero', 'quizá', 'quizás', 're', 'sabe',
    'saben', 'saber', 'sacar', 'se', 'sé', 'según', 'ser', 'será', 'sería', 'si', 'sí', 'siempre',
    'siendo', 'sin', 'sino', 'sobre', 'solo', 'sólo', 'solamente', 'son', 'soy', 'su', 'sus', 'tal',
    'también', 'tambien', 'tan', 'tanta', 'tanto', 'tantos', 'te', 'tenía', 'tenían', 'tiene', 'tienen',
    'tengo', 'ti', 'tipo', 'toda', 'todas', 'todo', 'todos', 'tras', 'u', 'un', 'una', 'unas', 'uno',
    'unos', 'usted', 'ustedes', 'va', 'vale', 'vamos', 'van', 'varios', 'veces', 'ver', 'verdad',
    'vez', 'ves', 'visto', 'voy', 'y', 'ya', 'yo',
    # Informal / Slang / Chilean Context (The "Wea" Family and more)
    'amigo', 'asiq', 'asique', 'chile', 'ctm', 'conchetumare', 'd', 'k', 'pork', 'porq', 'pq', 'q', 'tmb',
    'tula', 'tulon', 'wea', 'weá', 'weas', 'weás', 'weon', 'weón', 'weones', 'weona', 'wear', 'weando',
    'universidad', 'usm', 'u', 'informática', 'informatica', 'civil', 'ingeniería', 'ingenieria', 'ing'
}

def analyze_sentiment_advanced(text):
    """
    Advanced sentiment analysis using pysentimiento (if available).
    Falls back to basic rule-based analysis otherwise.
    """
    try:
        from pysentimiento import create_analyzer
        # We initialize it here for simplicity, but in production we'd use a singleton
        analyzer = create_analyzer(task="sentiment", lang="es")
        result = analyzer.predict(text)
        
        # Map pysentimiento labels to our format
        label_map = {"POS": "positive", "NEG": "negative", "NEU": "neutral"}
        return result.probas.get(result.output, 0), label_map.get(result.output, "neutral")
    except ImportError:
        # Fallback to basic analysis
        return analyze_sentiment(text)
    except Exception:
        return 0.0, "neutral"

def extract_keywords(texts, top_n=50):
    """Extract most common keywords from texts with Unicode normalization."""
    all_words = []
    # Regex for words (including Spanish characters), at least 2 characters
    word_pattern = re.compile(r'\b[a-zA-ZáéíóúüñÁÉÍÓÚÜÑ]{2,}\b')
    
    for text in texts:
        if text:
            # Normalize to NFC (composed) for consistent matching with STOPWORDS
            # This ensures that 'á' is one character regardless of input source
            normalized_text = unicodedata.normalize('NFC', str(text).lower())
            words = word_pattern.findall(normalized_text)
            all_words.extend([w for w in words if w not in STOPWORDS])
    
    return Counter(all_words).most_common(top_n)


def generate_wordcloud_data(texts, top_n=100):
    """Generate word frequency data for word cloud visualization."""
    keywords = extract_keywords(texts, top_n)
    
    if not keywords:
        return []
    
    max_count = keywords[0][1]
    
    return [
        {"text": word, "value": count, "size": int(10 + (count / max_count) * 90)}
        for word, count in keywords
    ]

def calculate_engagement_metrics(posts):
    """Calculate engagement metrics for posts."""
    if not posts:
        return {}
    
    total_posts = len(posts)
    total_score = sum(p.get('score', 0) for p in posts)
    total_comments = sum(p.get('num_comments', 0) for p in posts)
    total_awards = sum(p.get('total_awards', 0) for p in posts)
    
    # Posts with engagement
    engaged_posts = [p for p in posts if p.get('score', 0) > 0 or p.get('num_comments', 0) > 0]
    
    # Top performers
    top_by_score = sorted(posts, key=lambda x: x.get('score', 0), reverse=True)[:10]
    top_by_comments = sorted(posts, key=lambda x: x.get('num_comments', 0), reverse=True)[:10]
    
    # Post type performance
    type_performance = {}
    for post in posts:
        ptype = post.get('post_type', 'unknown')
        if ptype not in type_performance:
            type_performance[ptype] = {'count': 0, 'total_score': 0, 'total_comments': 0}
        type_performance[ptype]['count'] += 1
        type_performance[ptype]['total_score'] += post.get('score', 0)
        type_performance[ptype]['total_comments'] += post.get('num_comments', 0)
    
    for ptype in type_performance:
        count = type_performance[ptype]['count']
        type_performance[ptype]['avg_score'] = type_performance[ptype]['total_score'] / count
        type_performance[ptype]['avg_comments'] = type_performance[ptype]['total_comments'] / count
    
    return {
        'total_posts': total_posts,
        'total_score': total_score,
        'total_comments': total_comments,
        'total_awards': total_awards,
        'avg_score': total_score / total_posts if total_posts else 0,
        'avg_comments': total_comments / total_posts if total_posts else 0,
        'engagement_rate': len(engaged_posts) / total_posts if total_posts else 0,
        'top_by_score': top_by_score,
        'top_by_comments': top_by_comments,
        'type_performance': type_performance
    }

def find_best_posting_times(posts):
    """Analyze best times to post based on engagement."""
    hourly_stats = {}
    daily_stats = {}
    
    for post in posts:
        created = post.get('created_utc', '')
        if not created:
            continue
        
        try:
            # Parse ISO format
            from datetime import datetime
            dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
            hour = dt.hour
            day = dt.strftime('%A')
            
            # Hourly
            if hour not in hourly_stats:
                hourly_stats[hour] = {'count': 0, 'total_score': 0}
            hourly_stats[hour]['count'] += 1
            hourly_stats[hour]['total_score'] += post.get('score', 0)
            
            # Daily
            if day not in daily_stats:
                daily_stats[day] = {'count': 0, 'total_score': 0}
            daily_stats[day]['count'] += 1
            daily_stats[day]['total_score'] += post.get('score', 0)
        except:
            continue
    
    # Calculate averages
    for hour in hourly_stats:
        hourly_stats[hour]['avg_score'] = hourly_stats[hour]['total_score'] / hourly_stats[hour]['count']
    
    for day in daily_stats:
        daily_stats[day]['avg_score'] = daily_stats[day]['total_score'] / daily_stats[day]['count']
    
    # Find best times
    best_hours = sorted(hourly_stats.items(), key=lambda x: x[1]['avg_score'], reverse=True)[:5]
    best_days = sorted(daily_stats.items(), key=lambda x: x[1]['avg_score'], reverse=True)[:3]
    
    return {
        'hourly_stats': hourly_stats,
        'daily_stats': daily_stats,
        'best_hours': [(h, s['avg_score']) for h, s in best_hours],
        'best_days': [(d, s['avg_score']) for d, s in best_days]
    }
