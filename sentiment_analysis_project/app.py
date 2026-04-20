import os, re, json, hashlib, random
from datetime import datetime, timedelta
from collections import Counter
import joblib
import nltk
from flask import (Flask, render_template, request, jsonify,
                   session, redirect, url_for, flash)
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
import database as db
import social_fetcher as sf

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

# ── Social Media URL Analysis ──────────────────────────────────
def parse_social_url(url):
    """Extract platform and username from a social media profile URL."""
    url = url.strip()
    if not url.startswith('http'):
        url = 'https://' + url
    patterns = [
        (r'instagram\.com/([^/?#\s]+)', 'Instagram'),
        (r'(?:twitter|x)\.com/([^/?#\s]+)', 'Twitter/X'),
        (r'youtube\.com/@([^/?#\s]+)', 'YouTube'),
        (r'youtube\.com/user/([^/?#\s]+)', 'YouTube'),
        (r'youtube\.com/channel/([^/?#\s]+)', 'YouTube'),
        (r'facebook\.com/([^/?#\s]+)', 'Facebook'),
        (r'tiktok\.com/@([^/?#\s]+)', 'TikTok'),
        (r'linkedin\.com/in/([^/?#\s]+)', 'LinkedIn'),
    ]
    skip = {'p', 'reel', 'stories', 'tv', 'explore', 'watch', 'shorts'}
    for pattern, platform in patterns:
        m = re.search(pattern, url, re.IGNORECASE)
        if m:
            uname = m.group(1).rstrip('/')
            if uname.lower() not in skip:
                return platform, uname
    return None, None

def generate_social_analytics(username, platform, real_followers=None):
    """Produce consistent simulated 30-day engagement analytics for a social profile."""
    seed = int(hashlib.md5(f"{username.lower()}{platform}".encode()).hexdigest(), 16) % (2**32)
    rng = random.Random(seed)

    cfg = {
        'Instagram': (50000, 3000, 150),
        'Twitter/X': (20000, 800,  60),
        'YouTube':   (80000, 6000, 400),
        'Facebook':  (30000, 1500, 80),
        'TikTok':    (200000,15000, 800),
        'LinkedIn':  (8000,  200,  25),
    }.get(platform, (40000, 2000, 100))

    base_followers, base_likes, base_comments = cfg
    base_followers = real_followers if real_followers else rng.randint(int(base_followers * 0.05), base_followers)
    base_likes     = rng.randint(int(base_likes * 0.05),     base_likes)
    base_comments  = rng.randint(int(base_comments * 0.05),  base_comments)

    trend = rng.choice(['growing', 'declining', 'stable', 'volatile'])

    dates, followers_d, likes_d, comments_d, engagement_d = [], [], [], [], []
    cur = base_followers
    for i in range(30):
        dates.append((datetime.now() - timedelta(days=29 - i)).strftime('%b %d'))
        if trend == 'growing':
            cur += int(rng.uniform(0.001, 0.006) * cur)
        elif trend == 'declining':
            cur = max(100, cur - int(rng.uniform(0.001, 0.005) * cur))
        elif trend == 'volatile':
            cur = max(100, cur + int(rng.uniform(-0.015, 0.020) * cur))
        else:
            cur = max(100, cur + int(rng.uniform(-0.003, 0.004) * cur))
        followers_d.append(cur)
        day_likes    = max(0, int(base_likes    * rng.uniform(0.4, 2.0)))
        day_comments = max(0, int(base_comments * rng.uniform(0.3, 2.2)))
        likes_d.append(day_likes)
        comments_d.append(day_comments)
        engagement_d.append(round((day_likes + day_comments) / max(cur, 1) * 100, 3))

    def pct_change(recent, prev):
        return round((recent - prev) / max(abs(prev), 1) * 100, 1)

    f_chg  = pct_change(sum(followers_d[-7:]) / 7, sum(followers_d[-14:-7]) / 7)
    l_chg  = pct_change(sum(likes_d[-7:]) / 7,     sum(likes_d[-14:-7]) / 7)
    c_chg  = pct_change(sum(comments_d[-7:]) / 7,  sum(comments_d[-14:-7]) / 7)
    e_chg  = pct_change(sum(engagement_d[-7:]) / 7, sum(engagement_d[-14:-7]) / 7)

    issues, insights = [], []
    if f_chg < -5:
        issues.append({'type': 'danger', 'metric': 'Followers',
            'icon': 'people-fill',
            'message': f'Followers dropped {abs(f_chg):.1f}% in the last 7 days. Review recent posts for controversial content or reduced posting frequency.'})
    elif f_chg > 8:
        insights.append({'type': 'success', 'metric': 'Followers',
            'icon': 'graph-up-arrow',
            'message': f'Followers grew {f_chg:.1f}% week-over-week. Strong momentum — consider boosting top-performing posts.'})

    if e_chg < -15:
        issues.append({'type': 'warning', 'metric': 'Engagement',
            'icon': 'heart-fill',
            'message': f'Engagement rate fell {abs(e_chg):.1f}%. Audience may not be resonating with recent content. Try interactive formats (polls, Q&A, carousels).'})
    elif e_chg > 20:
        insights.append({'type': 'success', 'metric': 'Engagement',
            'icon': 'lightning-charge-fill',
            'message': f'Engagement surged {e_chg:.1f}%. Analyze top posts and replicate successful content patterns.'})

    if l_chg < -20:
        issues.append({'type': 'warning', 'metric': 'Likes',
            'icon': 'hand-thumbs-up-fill',
            'message': f'Likes per post down {abs(l_chg):.1f}%. Content quality or relevance may have declined. A/B test different formats.'})

    if c_chg < -25:
        issues.append({'type': 'info', 'metric': 'Comments',
            'icon': 'chat-dots-fill',
            'message': f'Comments dropped {abs(c_chg):.1f}%. Community interaction is declining. Post conversation-starter questions to re-engage.'})
    elif c_chg > 30:
        insights.append({'type': 'success', 'metric': 'Comments',
            'icon': 'chat-heart-fill',
            'message': f'Comments up {c_chg:.1f}%. High community interaction — respond to comments to maintain this momentum.'})

    if not issues and not insights:
        insights.append({'type': 'info', 'metric': 'Overall',
            'icon': 'check-circle-fill',
            'message': 'Account metrics are stable. Maintain a consistent posting schedule and engage with your audience daily.'})

    health = max(0, min(100, 50 + min(25, max(-25, f_chg)) + min(25, max(-25, e_chg / 2))))

    return {
        'username': username, 'platform': platform, 'trend': trend,
        'current_followers': followers_d[-1],
        'followers_change': f_chg,
        'avg_likes': round(sum(likes_d[-7:]) / 7),
        'likes_change': l_chg,
        'avg_comments': round(sum(comments_d[-7:]) / 7),
        'comments_change': c_chg,
        'engagement_rate': round(sum(engagement_d[-7:]) / 7, 2),
        'engagement_change': e_chg,
        'health_score': round(health),
        'issues': issues, 'insights': insights,
        'chart_data': {
            'dates': dates,
            'followers': followers_d,
            'likes': likes_d,
            'comments': comments_d,
            'engagement': engagement_d,
        }
    }

@app.route('/social')
@login_required
def social_analyzer():
    return render_template('social_analyzer.html')

@app.route('/analyze_social_url', methods=['POST'])
@login_required
def analyze_social_url():
    data = request.get_json()
    url  = (data.get('url') or '').strip()
    if not url:
        return jsonify({'error': 'Please enter a social media profile URL.'}), 400

    # ── Real data fetch ────────────────────────────────────────
    account  = sf.fetch_account(url)
    platform = account.get('platform', 'Unknown')

    if platform == 'Unknown' and not account.get('success'):
        _, _, _ = sf.parse_url(url)  # re-parse just for handle detection
        return jsonify({'error': account.get('error', 'Unrecognised URL. Try a direct profile link.')}), 400

    handle   = account.get('handle', 'unknown')
    real_fol = account.get('followers') or 0

    # ── Sentiment on real bio/description ──────────────────────
    bio_text = (account.get('description') or account.get('name') or '').strip()
    sent = analyze_sentiment(bio_text) if bio_text else {
        'final_sentiment': 'neutral',
        'vader': {'compound': 0, 'positive': 0, 'negative': 0, 'neutral': 100},
        'textblob': {'polarity': 0, 'subjectivity': 0, 'label': 'neutral'},
        'ml_model': {'label': 'neutral', 'confidence': 0},
        'keywords': [],
    }

    # ── Real issue detection ────────────────────────────────────
    issues   = sf.detect_issues(account, sent)
    eng_rate, eng_status, eng_bench = sf.estimate_engagement(account)

    # ── Growth simulation (based on real follower count) ────────
    g_labels, g_values = sf.simulate_growth(real_fol or 5000, platform)

    # ── 30-day engagement simulation (charts) ───────────────────
    sim = generate_social_analytics(handle, platform, real_followers=real_fol or None)

    db.save_search(session['username'], session['role'],
                   f"[Account Audit] {platform}: @{handle}",
                   sent['final_sentiment'], platform,
                   sent['vader']['compound'], sent['ml_model']['confidence'])
    print(f"\033[36m  [SOCIAL] {session['username']} | {platform} @{handle} | {UID}\033[0m")

    return jsonify({
        # Profile (real)
        'success':       account.get('success', False),
        'partial':       account.get('partial', False),
        'fetch_error':   account.get('error', ''),
        'platform':      platform,
        'name':          account.get('name', handle),
        'handle':        handle,
        'description':   account.get('description', ''),
        'followers':     real_fol,
        'followers_fmt': account.get('followers_fmt', str(real_fol)),
        'following':     account.get('following'),
        'following_fmt': sf._fmt(account.get('following') or 0),
        'posts_count':   account.get('posts_count'),
        'posts_label':   account.get('posts_label', 'Posts'),
        'avatar_url':    account.get('avatar_url', ''),
        'extra':         account.get('extra', {}),
        # Sentiment (real)
        'bio_sentiment': sent['final_sentiment'],
        'bio_compound':  round(sent['vader']['compound'], 3),
        'bio_polarity':  round(sent['textblob']['polarity'], 3),
        # Issues (real)
        'issues': issues,
        # Engagement estimate
        'engagement': {'rate': eng_rate, 'status': eng_status, 'benchmark': eng_bench},
        # Growth chart (real count, simulated curve)
        'growth_labels': g_labels,
        'growth_values': g_values,
        # 30-day engagement simulation
        'trend':             sim['trend'],
        'health_score':      sim['health_score'],
        'current_followers': real_fol if real_fol else sim['current_followers'],
        'followers_change':  sim['followers_change'],
        'avg_likes':         sim['avg_likes'],
        'likes_change':      sim['likes_change'],
        'avg_comments':      sim['avg_comments'],
        'comments_change':   sim['comments_change'],
        'engagement_rate':   sim['engagement_rate'],
        'engagement_change': sim['engagement_change'],
        'chart_data':        sim['chart_data'],
        'author': AUTHOR, 'uid': UID,
    })

@app.route('/delete_search/<int:search_id>', methods=['POST'])
@login_required
@admin_required
def delete_search_route(search_id):
    db.delete_search(search_id)
    print(f"\033[31m  [DELETE] Search #{search_id} deleted by {session['username']} | {UID}\033[0m")
    return jsonify({'ok': True})

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
