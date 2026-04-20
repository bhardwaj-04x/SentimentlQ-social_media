import os, re, json
from datetime import datetime
from collections import Counter
import joblib
import nltk
from flask import (Flask, render_template, request, jsonify,
                   session, redirect, url_for, flash)
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
import database as db

nltk.download('stopwords', quiet=True)
nltk.download('punkt',     quiet=True)
nltk.download('punkt_tab', quiet=True)
nltk.download('wordnet',   quiet=True)
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

AUTHOR  = "Sakshi Puri"
UID     = "24BET10158"
PROJECT = "Social Media & Sentiment Analysis"
SECRET  = "SentimentIQ_Sakshi_24BET10158_2025"

TRENDS_PATH = os.path.join(os.path.dirname(__file__), 'data', 'india_trends.json')

def print_banner():
    print(f"""
\033[95m╔══════════════════════════════════════════════════════════╗
║           SOCIAL MEDIA SENTIMENT ANALYZER                ║
╠══════════════════════════════════════════════════════════╣
║  Author  : {AUTHOR:<46} ║
║  UID     : {UID:<46} ║
║  Project : {PROJECT:<46} ║
║  Year    : 2025  |  College Final Project                ║
╠══════════════════════════════════════════════════════════╣
║  Admin   : username=sakshi  password=Sakshi@2025         ║
║  URL     : http://127.0.0.1:5000                         ║
╚══════════════════════════════════════════════════════════╝\033[0m""")

app = Flask(__name__)
app.secret_key = SECRET

vader      = SentimentIntensityAnalyzer()
STOP_WORDS = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'model', 'sentiment_model.pkl')
ml_model   = None

def load_model():
    global ml_model
    if os.path.exists(MODEL_PATH):
        ml_model = joblib.load(MODEL_PATH)
        print(f"\033[92m  [OK] ML model loaded\033[0m")
    else:
        print("\033[93m  [INFO] Training model...\033[0m")
        from model.train_model import train_and_save
        ml_model = train_and_save()

def preprocess_text(text):
    text = re.sub(r'http\S+|www\S+', '', str(text).lower())
    text = re.sub(r'@\w+|#\w+', '', text)
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    tokens = text.split()
    return ' '.join([lemmatizer.lemmatize(w) for w in tokens
                     if w not in STOP_WORDS and len(w) > 2])

def analyze_sentiment(text):
    vs = vader.polarity_scores(text)
    compound = vs['compound']
    vader_lbl = 'positive' if compound >= 0.05 else 'negative' if compound <= -0.05 else 'neutral'

    blob = TextBlob(text)
    tb_pol = blob.sentiment.polarity
    tb_sub = blob.sentiment.subjectivity
    tb_lbl = 'positive' if tb_pol > 0.05 else 'negative' if tb_pol < -0.05 else 'neutral'

    ml_lbl, ml_conf = 'neutral', 0.0
    if ml_model:
        clean   = preprocess_text(text)
        ml_lbl  = ml_model.predict([clean])[0]
        proba   = ml_model.predict_proba([clean])[0]
        ml_conf = float(max(proba)) * 100

    final = Counter([vader_lbl, tb_lbl, ml_lbl]).most_common(1)[0][0]

    keywords = [w for w in re.sub(r'[^a-zA-Z\s]','',text.lower()).split()
                if w not in STOP_WORDS and len(w) > 3]
    kw_freq  = Counter(keywords).most_common(8)

    return {
        'text': text, 'final_sentiment': final,
        'author': AUTHOR, 'uid': UID,
        'vader':   {'label': vader_lbl, 'positive': round(vs['pos']*100,1),
                    'negative': round(vs['neg']*100,1), 'neutral': round(vs['neu']*100,1),
                    'compound': round(compound,4)},
        'textblob':{'label': tb_lbl, 'polarity': round(tb_pol,4), 'subjectivity': round(tb_sub,4)},
        'ml_model':{'label': ml_lbl, 'confidence': round(ml_conf,1)},
        'keywords':[{'word':w,'count':c} for w,c in kw_freq],
        'char_count': len(text), 'word_count': len(text.split())
    }

# ── Auth helpers ───────────────────────────────────────────────
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'username' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'admin':
            flash('Admin access only.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

# ── Auth Routes ────────────────────────────────────────────────
@app.route('/login', methods=['GET','POST'])
def login():
    if 'username' in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username','').strip().lower()
        password = request.form.get('password','')
        user = db.verify_user(username, password)
        if user:
            session['username'] = user['username']
            session['role']     = user['role']
            print(f"\033[36m  [LOGIN] {user['username']} ({user['role']}) | {UID}\033[0m")
            flash(f"Welcome back, {user['username']}!", 'success')
            return redirect(url_for('admin_dashboard') if user['role']=='admin' else url_for('index'))
        flash('Invalid username or password.', 'error')
    return render_template('login.html')

@app.route('/register_guest', methods=['POST'])
def register_guest():
    username = request.form.get('username','').strip().lower()
    if not re.match(r'^[a-z0-9_]{3,20}$', username):
        flash('Username must be 3–20 characters (letters, numbers, underscore).', 'error')
        return redirect(url_for('login'))
    if username == 'sakshi':
        flash('That username is reserved.', 'error')
        return redirect(url_for('login'))
    if db.create_guest(username):
        session['username'] = username
        session['role']     = 'guest'
        flash(f'Welcome, {username}! You are now logged in as a guest.', 'success')
        return redirect(url_for('index'))
    flash('Username already taken. Try another or log in below.', 'error')
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

# ── Page Routes ────────────────────────────────────────────────
@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/analyzer')
@login_required
def analyzer_page():
    return render_template('analyzer.html')

@app.route('/bulk')
@login_required
def bulk_page():
    return render_template('bulk.html')

@app.route('/about')
@login_required
def about_page():
    return render_template('about.html')

@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    return render_template('admin_dashboard.html',
        stats          = db.get_summary_stats(),
        searches       = db.get_all_searches(100),
        platform_stats = db.get_platform_stats(),
        users          = db.get_all_users()
    )

@app.route('/trends')
@login_required
def social_trends():
    with open(TRENDS_PATH, 'r', encoding='utf-8') as f:
        trends = json.load(f)

    platforms = trends['platforms']
    summary   = trends['india_summary']

    analyzed = {}
    total_phrases = 0
    grand_pos = grand_neg = grand_neu = 0

    for pname, pdata in platforms.items():
        results = []
        for phrase in pdata['trending']:
            r = analyze_sentiment(phrase)
            results.append({
                'text':       phrase,
                'sentiment':  r['final_sentiment'],
                'compound':   r['vader']['compound'],
                'confidence': r['ml_model']['confidence'],
                'polarity':   r['textblob']['polarity']
            })
            if r['final_sentiment'] == 'positive': grand_pos += 1
            elif r['final_sentiment'] == 'negative': grand_neg += 1
            else: grand_neu += 1
            total_phrases += 1
        analyzed[pname] = results

    # Build chart data
    platform_names = list(platforms.keys())
    chart_pos = [sum(1 for r in analyzed[p] if r['sentiment']=='positive') for p in platform_names]
    chart_neg = [sum(1 for r in analyzed[p] if r['sentiment']=='negative') for p in platform_names]
    chart_neu = [sum(1 for r in analyzed[p] if r['sentiment']=='neutral')  for p in platform_names]

    trend_chart_data = {
        'labels': platform_names,
        'positive': chart_pos, 'negative': chart_neg, 'neutral': chart_neu,
        'grand': {'positive': grand_pos, 'negative': grand_neg, 'neutral': grand_neu}
    }

    return render_template('social_trends.html',
        platforms       = platforms,
        analyzed        = analyzed,
        summary         = summary,
        total_phrases   = total_phrases,
        trend_chart_data= trend_chart_data
    )

# ── API Routes ─────────────────────────────────────────────────
@app.route('/analyze', methods=['POST'])
@login_required
def analyze():
    data     = request.get_json()
    text     = data.get('text','').strip()
    platform = data.get('platform','Other')
    if not text:
        return jsonify({'error': 'Please enter some text.'}), 400
    if len(text) > 5000:
        return jsonify({'error': 'Text too long (max 5000 chars).'}), 400
    result = analyze_sentiment(text)
    db.save_search(session['username'], session['role'], text,
                   result['final_sentiment'], platform,
                   result['vader']['compound'], result['ml_model']['confidence'])
    print(f"\033[36m  [SEARCH] {session['username']} | {platform} | {result['final_sentiment']} | {UID}\033[0m")
    return jsonify(result)

@app.route('/analyze_bulk', methods=['POST'])
@login_required
def analyze_bulk():
    data  = request.get_json()
    texts = [t.strip() for t in data.get('texts',[]) if t.strip()][:50]
    platform = data.get('platform','Other')
    if not texts:
        return jsonify({'error': 'No texts provided.'}), 400
    results = [analyze_sentiment(t) for t in texts]
    for r in results:
        db.save_search(session['username'], session['role'], r['text'],
                       r['final_sentiment'], platform,
                       r['vader']['compound'], r['ml_model']['confidence'])
    labels = Counter(r['final_sentiment'] for r in results)
    return jsonify({'total':len(results),'positive':labels.get('positive',0),
                    'negative':labels.get('negative',0),'neutral':labels.get('neutral',0),
                    'author':AUTHOR,'uid':UID,'results':results})

@app.route('/demo')
@login_required
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
    for r in results:
        db.save_search(session['username'], session['role'], r['text'],
                       r['final_sentiment'], 'Demo',
                       r['vader']['compound'], r['ml_model']['confidence'])
    labels = Counter(r['final_sentiment'] for r in results)
    return jsonify({'total':len(results),'positive':labels.get('positive',0),
                    'negative':labels.get('negative',0),'neutral':labels.get('neutral',0),
                    'author':AUTHOR,'uid':UID,'results':results})

# ── Context processor (injects user into all templates) ────────
@app.context_processor
def inject_user():
    return {
        'current_user': session.get('username'),
        'current_role': session.get('role'),
        'is_admin': session.get('role') == 'admin'
    }

if __name__ == '__main__':
    print_banner()
    db.init_db()
    load_model()
    print(f"\n\033[92m  Server: http://127.0.0.1:5000\033[0m")
    print(f"\033[93m  Admin login: username=sakshi  password=Sakshi@2025\033[0m")
    print(f"\033[90m  {AUTHOR} | {UID}\033[0m\n")
    app.run(debug=True, port=5000)
