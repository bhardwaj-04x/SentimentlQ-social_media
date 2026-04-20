import os
import re
import json
import joblib
import pandas as pd
import nltk
from flask import Flask, render_template, request, jsonify
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
from collections import Counter

nltk.download('stopwords', quiet=True)
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)
nltk.download('wordnet', quiet=True)
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# ── Ownership Constants ───────────────────────────────────────
AUTHOR = "Sakshi Puri"
UID    = "24BET10158"
PROJECT = "Social Media & Sentiment Analysis"

def print_banner():
    """Prints ownership watermark in CMD on every startup."""
    banner = f"""
\033[95m╔══════════════════════════════════════════════════════════╗
║           SOCIAL MEDIA SENTIMENT ANALYZER                ║
╠══════════════════════════════════════════════════════════╣
║  Author  : {AUTHOR:<46} ║
║  UID     : {UID:<46} ║
║  Project : {PROJECT:<46} ║
║  Year    : 2025  |  College Final Project                ║
╠══════════════════════════════════════════════════════════╣
║  Models  : VADER + TextBlob + TF-IDF + Logistic Regr.   ║
║  Stack   : Python | Flask | scikit-learn | Bootstrap 5   ║
╠══════════════════════════════════════════════════════════╣
║  Server  : http://127.0.0.1:5000                         ║
║  © 2025 {AUTHOR} — All Rights Reserved          ║
╚══════════════════════════════════════════════════════════╝\033[0m
"""
    print(banner)

# ── App Setup ─────────────────────────────────────────────────
app = Flask(__name__)
vader = SentimentIntensityAnalyzer()
STOP_WORDS = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'model', 'sentiment_model.pkl')
ml_model = None

def load_model():
    global ml_model
    if os.path.exists(MODEL_PATH):
        ml_model = joblib.load(MODEL_PATH)
        print(f"\033[92m  [OK] ML model loaded from {MODEL_PATH}\033[0m")
    else:
        print("\033[93m  [INFO] Model not found — training now...\033[0m")
        from model.train_model import train_and_save
        ml_model = train_and_save()

def preprocess_text(text):
    text = str(text).lower()
    text = re.sub(r'http\S+|www\S+', '', text)
    text = re.sub(r'@\w+|#\w+', '', text)
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    tokens = text.split()
    return ' '.join([lemmatizer.lemmatize(w) for w in tokens
                     if w not in STOP_WORDS and len(w) > 2])

def analyze_sentiment(text):
    vader_scores = vader.polarity_scores(text)
    compound = vader_scores['compound']
    vader_label = ('positive' if compound >= 0.05
                   else 'negative' if compound <= -0.05 else 'neutral')

    blob = TextBlob(text)
    tb_polarity = blob.sentiment.polarity
    tb_subjectivity = blob.sentiment.subjectivity
    tb_label = ('positive' if tb_polarity > 0.05
                else 'negative' if tb_polarity < -0.05 else 'neutral')

    ml_label, ml_confidence = 'neutral', 0.0
    if ml_model:
        clean = preprocess_text(text)
        ml_label = ml_model.predict([clean])[0]
        proba = ml_model.predict_proba([clean])[0]
        ml_confidence = float(max(proba)) * 100

    votes = Counter([vader_label, tb_label, ml_label])
    final_label = votes.most_common(1)[0][0]

    words = re.sub(r'[^a-zA-Z\s]', '', text.lower()).split()
    keywords = [w for w in words if w not in STOP_WORDS and len(w) > 3]
    word_freq = Counter(keywords).most_common(8)

    return {
        'text': text,
        'final_sentiment': final_label,
        'author': AUTHOR,
        'uid': UID,
        'vader': {
            'label': vader_label,
            'positive': round(vader_scores['pos'] * 100, 1),
            'negative': round(vader_scores['neg'] * 100, 1),
            'neutral':  round(vader_scores['neu'] * 100, 1),
            'compound': round(compound, 4)
        },
        'textblob': {
            'label': tb_label,
            'polarity': round(tb_polarity, 4),
            'subjectivity': round(tb_subjectivity, 4)
        },
        'ml_model': {
            'label': ml_label,
            'confidence': round(ml_confidence, 1)
        },
        'keywords': [{'word': w, 'count': c} for w, c in word_freq],
        'char_count': len(text),
        'word_count': len(text.split())
    }

# ── Page Routes ────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyzer')
def analyzer_page():
    return render_template('analyzer.html')

@app.route('/bulk')
def bulk_page():
    return render_template('bulk.html')

@app.route('/about')
def about_page():
    return render_template('about.html')

# ── API Routes ─────────────────────────────────────────────────
@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    text = data.get('text', '').strip()
    if not text:
        return jsonify({'error': 'Please enter some text to analyze.'}), 400
    if len(text) > 5000:
        return jsonify({'error': 'Text too long — keep under 5000 characters.'}), 400
    print(f"\033[36m  [REQ] Analyze | {AUTHOR} | {UID} | chars={len(text)}\033[0m")
    return jsonify(analyze_sentiment(text))

@app.route('/analyze_bulk', methods=['POST'])
def analyze_bulk():
    data = request.get_json()
    texts = [t.strip() for t in data.get('texts', []) if t.strip()][:50]
    if not texts:
        return jsonify({'error': 'No texts provided.'}), 400
    print(f"\033[36m  [REQ] Bulk | {AUTHOR} | {UID} | count={len(texts)}\033[0m")
    results = [analyze_sentiment(t) for t in texts]
    labels = Counter(r['final_sentiment'] for r in results)
    return jsonify({
        'total': len(results),
        'positive': labels.get('positive', 0),
        'negative': labels.get('negative', 0),
        'neutral':  labels.get('neutral', 0),
        'author': AUTHOR,
        'uid': UID,
        'results': results
    })

@app.route('/demo')
def demo():
    demo_texts = [
        "I absolutely love this product! Best purchase of the year!",
        "Terrible experience. The customer service was awful and rude.",
        "The package arrived today. Product looks as described.",
        "This made my whole week! So grateful and happy right now!",
        "Complete waste of money. Don't buy this garbage.",
        "It works fine. Nothing special but gets the job done.",
        "Incredible results! Way beyond my expectations!",
        "Very disappointed. Expected much better quality.",
        "Weather is cloudy today. Nothing special.",
        "Just got promoted! Dreams really do come true!"
    ]
    results = [analyze_sentiment(t) for t in demo_texts]
    labels = Counter(r['final_sentiment'] for r in results)
    print(f"\033[36m  [REQ] Demo | {AUTHOR} | {UID}\033[0m")
    return jsonify({
        'total': len(results),
        'positive': labels.get('positive', 0),
        'negative': labels.get('negative', 0),
        'neutral':  labels.get('neutral', 0),
        'author': AUTHOR,
        'uid': UID,
        'results': results
    })

if __name__ == '__main__':
    print_banner()
    load_model()
    print(f"\n\033[92m  Starting server — http://127.0.0.1:5000\033[0m")
    print(f"\033[90m  {AUTHOR} | {UID} | {PROJECT}\033[0m\n")
    app.run(debug=True, port=5000)
