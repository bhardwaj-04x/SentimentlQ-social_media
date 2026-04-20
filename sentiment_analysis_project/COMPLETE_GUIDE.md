# Complete Installation, Setup & Testing Guide
## Social Media Sentiment Analysis — College Project

---

# PART 1 — WHAT EACH PACKAGE DOES

Before installing, understand WHY each package is needed:

| Package | Version | What It Does | Used For |
|---------|---------|--------------|----------|
| **flask** | 3.0.0 | Python web framework — turns your code into a website | Runs the web server, handles browser requests |
| **pandas** | 2.1.4 | Data manipulation library — works like Excel in Python | Reads CSV dataset, organizes data into tables |
| **numpy** | 1.26.2 | Numerical computing — fast math arrays | Math calculations, array operations |
| **scikit-learn** | 1.3.2 | Main ML library — has 100+ algorithms | TF-IDF vectorizer + Logistic Regression classifier |
| **vaderSentiment** | 3.3.2 | NLP tool built specifically for social media | Analyzes slang, emojis, ALL CAPS, punctuation!!! |
| **textblob** | 0.17.1 | Simple NLP — polarity and subjectivity scores | Second opinion on sentiment + measures objectivity |
| **matplotlib** | 3.8.2 | Creates graphs and charts in Python | Generates chart images on the backend |
| **seaborn** | 0.13.0 | Beautiful statistical charts (built on matplotlib) | Prettier visualizations |
| **wordcloud** | 1.9.3 | Generates word cloud images from text | Visual keyword representation |
| **plotly** | 5.18.0 | Interactive charts for web | Clickable, zoomable charts in browser |
| **nltk** | 3.8.1 | Natural Language Toolkit — core NLP library | Stopwords list, tokenization, lemmatization |
| **joblib** | 1.3.2 | Saves/loads Python objects to disk | Saves trained ML model so you don't retrain every time |

---

# PART 2 — STEP-BY-STEP INSTALLATION (WINDOWS)

## Step 1 — Install Python

1. Open your browser and go to: **https://www.python.org/downloads/**
2. Click the big yellow button **"Download Python 3.12.x"** (latest version)
3. Run the downloaded `.exe` file
4. **VERY IMPORTANT:** On the first screen, check the box that says **"Add Python to PATH"**
5. Click **"Install Now"**
6. Wait for installation to finish, then click Close

**Verify installation:**
Open Command Prompt (press `Win + R`, type `cmd`, press Enter) and type:
```
python --version
```
You should see something like: `Python 3.12.3`

If you see an error, Python is not in PATH — reinstall and make sure to check "Add to PATH".

---

## Step 2 — Open the Project Folder in Command Prompt

**Method 1 (Easy):**
1. Open File Explorer
2. Navigate to your `sentiment_analysis_project` folder
3. Click on the address bar at the top
4. Type `cmd` and press Enter
5. Command Prompt opens directly in that folder!

**Method 2 (Manual):**
```
cd "C:\Users\YourName\OneDrive\Desktop\Sakshi Project\sentiment_analysis_project"
```
Replace `YourName` with your actual Windows username.

Confirm you're in the right folder:
```
dir
```
You should see files like `app.py`, `requirements.txt`, etc.

---

## Step 3 — Create a Virtual Environment

A virtual environment is like a "clean room" for your project — packages installed here don't affect the rest of your computer.

```
python -m venv venv
```

This creates a folder called `venv` inside your project.

**Activate the virtual environment:**
```
venv\Scripts\activate
```

Your command prompt will now show `(venv)` at the start:
```
(venv) C:\...\sentiment_analysis_project>
```

> **Note:** Every time you open a new Command Prompt to run this project, you must activate the venv again with `venv\Scripts\activate`

---

## Step 4 — Install All Packages

With venv activated, run:
```
pip install -r requirements.txt
```

This reads the `requirements.txt` file and installs everything automatically.

**OR** use the one-click batch file:
```
INSTALL_WINDOWS.bat
```
Double-click it in File Explorer — it does everything automatically!

**What you'll see while installing:**
```
Collecting flask==3.0.0
  Downloading flask-3.0.0-py3-none-any.whl (99 kB)
Installing collected packages: flask, ...
Successfully installed flask-3.0.0
```

This takes **2-5 minutes** depending on your internet speed.

---

## Step 5 — Download NLTK Language Data

NLTK needs to download language files (stopwords, dictionary, etc.):
```
python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt'); nltk.download('wordnet'); nltk.download('averaged_perceptron_tagger')"
```

You'll see:
```
[nltk_data] Downloading package stopwords...
[nltk_data]   Unzipping corpora/stopwords.zip.
[nltk_data] Downloading package punkt...
...
```

---

## Step 6 — Train the Machine Learning Model

```
python model\train_model.py
```

You'll see:
```
=== Model Training Complete ===
Accuracy: 0.8000

Classification Report:
              precision    recall  f1-score   support
    negative       0.80      0.80      0.80         5
     neutral       0.75      0.75      0.75         4
    positive       0.83      0.83      0.83         6

Model saved to: model/sentiment_model.pkl
```

This creates `model/sentiment_model.pkl` — the saved trained model file.

---

## Step 7 — Start the Application

```
python app.py
```

You'll see:
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
 * Press CTRL+C to quit
```

Open your browser and go to: **http://127.0.0.1:5000**

---

# PART 3 — HOW TO TEST THE PROJECT

## Method 1 — Automated Test Suite (Recommended)

Run the complete test suite:
```
python test_project.py
```

Or double-click: **`TEST_PROJECT.bat`**

**Expected output:**
```
============================================================
  SENTIMENT ANALYZER - COMPLETE TEST SUITE
============================================================

[TEST GROUP 1] Python Environment
  [PASS] Python version (3.12.3)

[TEST GROUP 2] Package Imports
  [PASS] Import Flask
  [PASS] Import pandas
  [PASS] Import numpy
  [PASS] Import scikit-learn
  [PASS] Import vaderSentiment
  [PASS] Import TextBlob
  [PASS] Import matplotlib
  [PASS] Import nltk
  [PASS] Import joblib
  [PASS] Import plotly

[TEST GROUP 3] NLTK Language Data
  [PASS] NLTK stopwords
  [PASS] NLTK wordnet
  [PASS] NLTK punkt

[TEST GROUP 4] Project Files
  [PASS] File: app.py
  [PASS] File: requirements.txt
  [PASS] File: model/train_model.py
  [PASS] File: data/sample_tweets.csv
  [PASS] File: templates/index.html
  [PASS] File: static/css/style.css
  [PASS] File: static/js/app.js

[TEST GROUP 5] Training Dataset
  [PASS] CSV loads successfully
  [PASS] Dataset has 50 rows
  [PASS] Has 'text' column
  [PASS] Has 'label' column
  [PASS] Labels found: ['positive', 'negative', 'neutral']

[TEST GROUP 6] Text Preprocessing
  [PASS] URL removed
  [PASS] Mention removed
  [PASS] Lowercased
  [PASS] Stop words removed
  [PASS] Lemmatization works

[TEST GROUP 7] VADER Sentiment Analysis
  [PASS] VADER: 'I love this! Amazing product!...' → positive
  [PASS] VADER: 'This is terrible and I hate it!...' → negative
  [PASS] VADER: 'The package arrived today....' → neutral

[TEST GROUP 8] TextBlob Analysis
  [PASS] TextBlob polarity > 0 for positive text
  [PASS] TextBlob subjectivity in [0,1]

[TEST GROUP 9] Machine Learning Model
  [PASS] ML model loaded/trained
  [PASS] Model predicts positive
  [PASS] Model predicts negative
  [PASS] Model returns 3 predictions
  [PASS] Model gives probabilities

[TEST GROUP 10] Flask Application
  [PASS] Flask app imports
  [PASS] GET / returns 200
  [PASS] POST /analyze returns 200
  [PASS] Response has final_sentiment
  [PASS] Response has vader scores
  [PASS] Response has textblob scores
  [PASS] Response has ml_model scores
  [PASS] Response has keywords
  [PASS] Positive text → positive
  [PASS] Negative text → negative
  [PASS] Empty input returns 400
  [PASS] POST /analyze_bulk returns 200
  [PASS] Bulk response has total
  [PASS] Bulk response has results
  [PASS] Bulk total = 3
  [PASS] GET /demo returns 200
  [PASS] Demo returns 10 results

============================================================
  RESULTS: 42/42 tests passed

  ALL TESTS PASSED!

  Run the app:  python app.py
  Open browser: http://127.0.0.1:5000
============================================================
```

## Method 2 — Manual Browser Testing

After starting the app (`python app.py`), open **http://127.0.0.1:5000** and test these:

### Test A — Single Positive Text
1. Click the **"Single Text"** tab
2. Type: `I absolutely love this product! Best purchase ever!`
3. Click **"Analyze Sentiment"**
4. Expected: Green "POSITIVE" result, VADER compound > 0.5

### Test B — Single Negative Text
1. Type: `This is the worst experience of my life. Completely terrible!`
2. Click **"Analyze Sentiment"**
3. Expected: Red "NEGATIVE" result

### Test C — Neutral Text
1. Type: `The package arrived today. It is as described in the listing.`
2. Click **"Analyze Sentiment"**
3. Expected: Blue "NEUTRAL" result

### Test D — Bulk Analysis
1. Click the **"Bulk Analysis"** tab
2. Paste these lines:
   ```
   I love this so much!
   Absolutely terrible, never again!
   It was okay, nothing special.
   Best day of my life!
   Waste of time and money.
   ```
3. Click **"Analyze All"**
4. Expected: Pie chart and bar chart showing 2 positive, 2 negative, 1 neutral

### Test E — Live Demo
1. Click the **"Demo"** tab
2. Click **"Run Demo"**
3. Expected: 10 sample results with charts

## Method 3 — API Testing with Python

Open a NEW terminal (keep the app running in the first one):

```python
import requests

# Test 1: Single positive text
r = requests.post('http://127.0.0.1:5000/analyze', json={
    'text': 'I love this! Amazing experience!'
})
print(r.json())

# Test 2: Single negative text
r = requests.post('http://127.0.0.1:5000/analyze', json={
    'text': 'Terrible service. I hate this.'
})
print(r.json()['final_sentiment'])  # should print: negative

# Test 3: Bulk analysis
r = requests.post('http://127.0.0.1:5000/analyze_bulk', json={
    'texts': [
        'Amazing product!',
        'Worst experience ever.',
        'It is what it is.'
    ]
})
data = r.json()
print(f"Positive: {data['positive']}, Negative: {data['negative']}, Neutral: {data['neutral']}")
```

---

# PART 4 — HOW THE CODE WORKS (EXPLANATION)

## 4.1 Text Preprocessing Pipeline

```
Input:  "I LOVE this!! Check out http://shop.com @JohnDoe #amazing"

Step 1 - Lowercase:
        "i love this!! check out http://shop.com @johndoe #amazing"

Step 2 - Remove URLs:
        "i love this!! check out  @johndoe #amazing"

Step 3 - Remove @mentions and #hashtags:
        "i love this!!  check out  "

Step 4 - Remove punctuation/numbers:
        "i love this  check out  "

Step 5 - Tokenize (split into words):
        ["i", "love", "this", "check", "out"]

Step 6 - Remove stop words (common words like "i", "this", "out"):
        ["love", "check"]

Step 7 - Lemmatize (reduce to base form):
        ["love", "check"]

Output: "love check"
```

**Stop words** are very common words that carry no sentiment:
> "i, me, my, myself, we, our, you, he, she, it, is, are, was, were, be, been, being, have, has, had, do, does, did, will, would, could, should, may, might, shall, can, the, a, an, and, but, or, for, nor, on, at, to, from, by, of, in, out, up, down, with, about, than, so, yet, both, either, whether, if, as, until, while, after, before, since, this, that, these, those, it, its..."

## 4.2 VADER (Valence Aware Dictionary and sEntiment Reasoner)

VADER uses a **manually crafted dictionary** of 7,500+ words with pre-assigned sentiment scores.

Example scores:
```
"love"      → +3.2
"excellent" → +3.1
"terrible"  → -2.6
"hate"      → -2.5
"okay"      →  0.0
```

**Special rules VADER applies:**
- `LOVE` (all caps) scores higher than `love`
- `love!!!` (exclamation marks) boosts the score
- `not love` (negation) flips the score to negative
- `barely love` (diminishers) reduces the positive score
- `:)` or `😊` emoji are recognized as positive

**Output:**
```python
{'neg': 0.0, 'neu': 0.296, 'pos': 0.704, 'compound': 0.8074}
```
- `pos/neu/neg` — percentage of text that is positive/neutral/negative
- `compound` — overall score from -1.0 (most negative) to +1.0 (most positive)
- If compound >= 0.05 → POSITIVE
- If compound <= -0.05 → NEGATIVE
- Otherwise → NEUTRAL

## 4.3 TextBlob

TextBlob uses **pattern matching** from a large linguistic database.

**Output:**
```python
Sentiment(polarity=0.5, subjectivity=0.6)
```
- `polarity` — from -1.0 (negative) to +1.0 (positive)
- `subjectivity` — from 0.0 (objective/factual) to 1.0 (subjective/opinion)

Example:
- "The sky is blue" → polarity=0, subjectivity=0 (objective fact)
- "I absolutely love this!" → polarity=0.9, subjectivity=0.9 (strong opinion)

## 4.4 Machine Learning Model (TF-IDF + Logistic Regression)

### Step A: TF-IDF Vectorizer

TF-IDF converts text to numbers that a machine can understand.

**TF** = Term Frequency — how often a word appears in THIS document
**IDF** = Inverse Document Frequency — how rare the word is across ALL documents

```
Text: "I love love love this product"

Word counts: love=3, product=1
TF(love) = 3/6 = 0.5

If "love" appears in 10 out of 1000 documents:
IDF(love) = log(1000/10) = 2

TF-IDF(love) = 0.5 × 2 = 1.0  ← high score, important word
```

Common words like "the", "is" appear in ALL documents → IDF is very low → TF-IDF ≈ 0
Rare meaningful words get high TF-IDF scores.

With **ngrams (1,2)**, it also captures pairs of words:
- "not good" is captured as one feature (bigram)
- Without bigrams, "not" and "good" would be separate

### Step B: Logistic Regression

After TF-IDF, each text becomes a vector of ~5000 numbers.

Logistic Regression learns the **weight** (importance) of each word for each class:

```
"love"    → positive weight: +2.3, negative weight: -1.8
"hate"    → positive weight: -2.1, negative weight: +2.7
"okay"    → positive weight: +0.1, negative weight: -0.1
"amazing" → positive weight: +3.1, negative weight: -2.0
```

For a new text, it multiplies each word's TF-IDF score by its weight, sums them up, and picks the class with the highest score.

**Why Logistic Regression?**
- Fast to train and predict
- Works well with sparse data (most words are absent → 0s)
- Easy to understand
- Good baseline before trying neural networks

## 4.5 Ensemble Voting

```
Text: "This product is absolutely amazing!"

VADER    → POSITIVE ✓
TextBlob → POSITIVE ✓
ML Model → POSITIVE ✓

Vote: 3/3 → FINAL: POSITIVE (strong confidence)

---

Text: "An average product, not great but not bad."

VADER    → NEUTRAL
TextBlob → POSITIVE   (disagrees slightly)
ML Model → NEUTRAL

Vote: 2/3 → FINAL: NEUTRAL
```

Using 3 models and taking the majority makes the system more **robust** — one model being wrong doesn't break the result.

---

# PART 5 — PROJECT FILE EXPLANATION

## app.py — The Main Application

```python
# Creates the Flask web application
app = Flask(__name__)

# Loads all 3 analysis tools
vader = SentimentIntensityAnalyzer()  # VADER
# TextBlob is used inline
# ML model is loaded from file

# Routes (URLs the browser can visit):
@app.route('/')             # → shows the main webpage
@app.route('/analyze')      # → analyzes single text (POST request)
@app.route('/analyze_bulk') # → analyzes multiple texts (POST request)
@app.route('/demo')         # → runs demo with 10 sample texts (GET request)
```

## model/train_model.py — ML Training

```python
# 1. Loads the CSV dataset
# 2. Preprocesses all texts
# 3. Splits 80% for training, 20% for testing
# 4. Creates Pipeline: TF-IDF → Logistic Regression
# 5. Trains (fits) the pipeline on training data
# 6. Tests accuracy on test data
# 7. Saves model to sentiment_model.pkl
```

## templates/index.html — The Webpage

Uses **Jinja2 templating** (Flask's HTML engine):
```html
{{ url_for('static', filename='css/style.css') }}
```
This generates the correct URL to the CSS file automatically.

## static/js/app.js — Frontend Logic

Sends text to the Flask API using **fetch** (modern browser API):
```javascript
const response = await fetch('/analyze', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ text: inputText })
});
const data = await response.json();
// data contains: final_sentiment, vader, textblob, ml_model, keywords
```

Then uses **Chart.js** to render the charts in the browser.

---

# PART 6 — TROUBLESHOOTING

## Problem: `python` not recognized
```
'python' is not recognized as an internal or external command
```
**Fix:** Reinstall Python and check "Add Python to PATH"
Or try: `py app.py` instead of `python app.py`

## Problem: Module not found
```
ModuleNotFoundError: No module named 'flask'
```
**Fix:** You forgot to activate the virtual environment
```
venv\Scripts\activate
pip install -r requirements.txt
```

## Problem: Port already in use
```
OSError: [Errno 98] Address already in use
```
**Fix:** Another app is using port 5000
```python
# In app.py, change the last line to use a different port:
app.run(debug=True, port=5001)
# Then open: http://127.0.0.1:5001
```

## Problem: NLTK data missing
```
LookupError: Resource stopwords not found.
```
**Fix:**
```
python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt'); nltk.download('wordnet')"
```

## Problem: Model file missing
```
FileNotFoundError: model/sentiment_model.pkl not found
```
**Fix:** Train the model first:
```
python model\train_model.py
```

## Problem: `venv\Scripts\activate` gives an error
```
cannot be loaded because running scripts is disabled
```
**Fix:** Open PowerShell as Administrator and run:
```
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
Then try activating again.

---

# PART 7 — QUICK REFERENCE COMMANDS

```bash
# First time setup
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt'); nltk.download('wordnet')"
python model\train_model.py

# Every time after setup
venv\Scripts\activate
python app.py
# Open: http://127.0.0.1:5000

# Run tests
python test_project.py

# Stop the server
Press CTRL + C in the terminal

# Deactivate virtual environment
deactivate
```

---

# PART 8 — BATCH FILES (WINDOWS ONE-CLICK)

| File | What It Does |
|------|-------------|
| `INSTALL_WINDOWS.bat` | Complete first-time setup (double-click once) |
| `RUN_APP.bat` | Starts the web app (double-click to run) |
| `TEST_PROJECT.bat` | Runs all tests (double-click to test) |

---

*Social Media Sentiment Analysis | College Project | Python + Flask + ML*
