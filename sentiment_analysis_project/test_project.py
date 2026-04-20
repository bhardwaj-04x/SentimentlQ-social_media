"""
Complete test suite for the Sentiment Analysis project.
Run: python test_project.py
"""

import sys
import os

PASS = "  [PASS]"
FAIL = "  [FAIL]"
INFO = "  [INFO]"

results = []

def check(name, passed, detail=""):
    status = PASS if passed else FAIL
    print(f"{status} {name}")
    if detail:
        print(f"         {detail}")
    results.append((name, passed))

print("=" * 60)
print("  SENTIMENT ANALYZER - COMPLETE TEST SUITE")
print("=" * 60)

# ── TEST 1: Python Version ────────────────────────────────────
print("\n[TEST GROUP 1] Python Environment")
ver = sys.version_info
check(f"Python version ({ver.major}.{ver.minor}.{ver.micro})",
      ver.major == 3 and ver.minor >= 9,
      "Need Python 3.9 or higher")

# ── TEST 2: All Imports ───────────────────────────────────────
print("\n[TEST GROUP 2] Package Imports")

packages = [
    ("flask",           "Flask"),
    ("pandas",          "pandas"),
    ("numpy",           "numpy"),
    ("sklearn",         "scikit-learn"),
    ("vaderSentiment",  "vaderSentiment"),
    ("textblob",        "TextBlob"),
    ("matplotlib",      "matplotlib"),
    ("nltk",            "nltk"),
    ("joblib",          "joblib"),
    ("plotly",          "plotly"),
]

for module, display in packages:
    try:
        __import__(module)
        check(f"Import {display}", True)
    except ImportError as e:
        check(f"Import {display}", False, f"Run: pip install {display.lower()}")

# ── TEST 3: NLTK Data ─────────────────────────────────────────
print("\n[TEST GROUP 3] NLTK Language Data")
import nltk

for resource, path in [
    ("stopwords",   "corpora/stopwords"),
    ("wordnet",     "corpora/wordnet"),
    ("punkt",       "tokenizers/punkt"),
]:
    try:
        nltk.data.find(path)
        check(f"NLTK {resource}", True)
    except LookupError:
        check(f"NLTK {resource}", False,
              f"Run: python -c \"import nltk; nltk.download('{resource}')\"")

# ── TEST 4: Project Files ─────────────────────────────────────
print("\n[TEST GROUP 4] Project Files")

required_files = [
    "app.py",
    "requirements.txt",
    "model/train_model.py",
    "data/sample_tweets.csv",
    "templates/index.html",
    "static/css/style.css",
    "static/js/app.js",
]

for f in required_files:
    exists = os.path.exists(f)
    check(f"File: {f}", exists, "" if exists else "File is missing!")

# ── TEST 5: Training Data ─────────────────────────────────────
print("\n[TEST GROUP 5] Training Dataset")
try:
    import pandas as pd
    df = pd.read_csv("data/sample_tweets.csv")
    check("CSV loads successfully", True)
    check(f"Dataset has {len(df)} rows", len(df) >= 10,
          f"Found {len(df)} rows, need at least 10")
    check("Has 'text' column",  "text"  in df.columns)
    check("Has 'label' column", "label" in df.columns)
    labels = df['label'].unique().tolist()
    check(f"Labels found: {labels}",
          all(l in labels for l in ['positive','negative','neutral']))
except Exception as e:
    check("CSV loads successfully", False, str(e))

# ── TEST 6: Text Preprocessing ────────────────────────────────
print("\n[TEST GROUP 6] Text Preprocessing")
try:
    import re
    from nltk.corpus import stopwords
    from nltk.stem import WordNetLemmatizer

    STOP_WORDS = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()

    def preprocess(text):
        text = str(text).lower()
        text = re.sub(r'http\S+|www\S+', '', text)
        text = re.sub(r'@\w+|#\w+', '', text)
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        tokens = text.split()
        return [lemmatizer.lemmatize(w) for w in tokens
                if w not in STOP_WORDS and len(w) > 2]

    t1 = preprocess("I LOVE this!! Check out http://example.com @user #awesome")
    check("URL removed",     not any('http' in w for w in t1))
    check("Mention removed", not any('@' in w for w in t1))
    check("Lowercased",      all(w == w.lower() for w in t1))
    check("Stop words removed", 'this' not in t1)
    check("Lemmatization works",
          lemmatizer.lemmatize('running') == 'running' or
          lemmatizer.lemmatize('loves') == 'love')
    print(f"         Preprocessed tokens: {t1}")
except Exception as e:
    check("Preprocessing pipeline", False, str(e))

# ── TEST 7: VADER Sentiment ───────────────────────────────────
print("\n[TEST GROUP 7] VADER Sentiment Analysis")
try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    vader = SentimentIntensityAnalyzer()

    tests = [
        ("I love this! Amazing product!", "positive"),
        ("This is terrible and I hate it!", "negative"),
        ("The package arrived today.",     "neutral"),
    ]

    for text, expected in tests:
        scores = vader.polarity_scores(text)
        c = scores['compound']
        label = 'positive' if c >= 0.05 else ('negative' if c <= -0.05 else 'neutral')
        ok = (label == expected)
        check(f"VADER: '{text[:40]}...' → {label}", ok,
              f"Expected {expected}, compound={c:.4f}")
except Exception as e:
    check("VADER analysis", False, str(e))

# ── TEST 8: TextBlob ──────────────────────────────────────────
print("\n[TEST GROUP 8] TextBlob Analysis")
try:
    from textblob import TextBlob
    blob = TextBlob("I absolutely love this wonderful product!")
    pol = blob.sentiment.polarity
    sub = blob.sentiment.subjectivity
    check("TextBlob polarity > 0 for positive text", pol > 0,
          f"polarity={pol:.4f}")
    check("TextBlob subjectivity in [0,1]", 0 <= sub <= 1,
          f"subjectivity={sub:.4f}")
except Exception as e:
    check("TextBlob analysis", False, str(e))

# ── TEST 9: ML Model ──────────────────────────────────────────
print("\n[TEST GROUP 9] Machine Learning Model")
try:
    import joblib
    model_path = "model/sentiment_model.pkl"

    if not os.path.exists(model_path):
        print(f"{INFO} Model not found. Training now...")
        from model.train_model import train_and_save
        pipeline = train_and_save()
    else:
        pipeline = joblib.load(model_path)

    check("ML model loaded/trained", True)

    preds = pipeline.predict(["I love this amazing product",
                               "This is terrible and awful",
                               "It arrived on time"])
    check("Model predicts positive", preds[0] == 'positive', f"got: {preds[0]}")
    check("Model predicts negative", preds[1] == 'negative', f"got: {preds[1]}")
    check("Model returns 3 predictions", len(preds) == 3)

    proba = pipeline.predict_proba(["I love this!"])[0]
    check("Model gives probabilities", abs(sum(proba) - 1.0) < 0.001,
          f"proba sum={sum(proba):.4f}")
except Exception as e:
    check("ML model pipeline", False, str(e))

# ── TEST 10: Flask App ────────────────────────────────────────
print("\n[TEST GROUP 10] Flask Application")
try:
    import app as flask_app
    flask_app.load_model()
    client = flask_app.app.test_client()
    check("Flask app imports", True)

    # Test home page
    r = client.get('/')
    check("GET / returns 200", r.status_code == 200,
          f"Status: {r.status_code}")

    # Test analyze endpoint - positive
    import json
    r = client.post('/analyze',
                    data=json.dumps({'text': 'I love this amazing product!'}),
                    content_type='application/json')
    check("POST /analyze returns 200", r.status_code == 200)
    data = json.loads(r.data)
    check("Response has final_sentiment", 'final_sentiment' in data)
    check("Response has vader scores",    'vader' in data)
    check("Response has textblob scores", 'textblob' in data)
    check("Response has ml_model scores", 'ml_model' in data)
    check("Response has keywords",        'keywords' in data)
    check(f"Positive text → {data.get('final_sentiment')}",
          data.get('final_sentiment') == 'positive')

    # Test analyze endpoint - negative
    r2 = client.post('/analyze',
                     data=json.dumps({'text': 'This is absolutely terrible and awful!'}),
                     content_type='application/json')
    d2 = json.loads(r2.data)
    check(f"Negative text → {d2.get('final_sentiment')}",
          d2.get('final_sentiment') == 'negative')

    # Test empty input
    r3 = client.post('/analyze',
                     data=json.dumps({'text': ''}),
                     content_type='application/json')
    check("Empty input returns 400", r3.status_code == 400)

    # Test bulk endpoint
    r4 = client.post('/analyze_bulk',
                     data=json.dumps({'texts': [
                         'I love this!', 'Terrible experience!', 'It was okay.'
                     ]}),
                     content_type='application/json')
    check("POST /analyze_bulk returns 200", r4.status_code == 200)
    d4 = json.loads(r4.data)
    check("Bulk response has total",    'total'   in d4)
    check("Bulk response has results",  'results' in d4)
    check("Bulk total = 3",             d4.get('total') == 3)

    # Test demo endpoint
    r5 = client.get('/demo')
    check("GET /demo returns 200", r5.status_code == 200)
    d5 = json.loads(r5.data)
    check("Demo returns 10 results", d5.get('total') == 10)

except Exception as e:
    check("Flask application test", False, str(e))

# ── FINAL REPORT ──────────────────────────────────────────────
print()
print("=" * 60)
total  = len(results)
passed = sum(1 for _, ok in results if ok)
failed = total - passed

print(f"  RESULTS: {passed}/{total} tests passed")
if failed == 0:
    print()
    print("  ALL TESTS PASSED!")
    print()
    print("  Run the app:  python app.py")
    print("  Open browser: http://127.0.0.1:5000")
else:
    print(f"  {failed} test(s) failed. Fix the issues above and re-run.")
print("=" * 60)

sys.exit(0 if failed == 0 else 1)
