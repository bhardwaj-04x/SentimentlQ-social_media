# Social Media Sentiment Analysis
### College Project | Machine Learning + NLP + Flask Web App

---

## What This Project Does

This project analyzes the **emotional tone** (positive, negative, or neutral) of any social media post, tweet, product review, or text using **three different AI/ML techniques**:

| Method | Description |
|--------|-------------|
| **VADER** | Rule-based NLP model built for social media text |
| **TextBlob** | Pattern-based library giving polarity + subjectivity |
| **TF-IDF + Logistic Regression** | Trained ML model on labeled data |

The final sentiment is decided by a **majority vote** from all three models.

---

## Features

- Single text analysis with detailed breakdown
- Bulk analysis of up to 50 texts at once
- Live demo with 10 pre-built examples
- Interactive charts (pie chart + bar chart)
- Keyword extraction from text
- Word count, char count, subjectivity score
- Clean, modern web interface

---

## Project Structure

```
sentiment_analysis_project/
|
|-- app.py                  # Main Flask web application
|-- setup.py                # One-click setup script
|-- requirements.txt        # All Python dependencies
|
|-- model/
|   |-- train_model.py      # ML model training script
|   |-- sentiment_model.pkl # Saved model (auto-generated)
|
|-- data/
|   |-- sample_tweets.csv   # Labeled training dataset
|
|-- templates/
|   |-- index.html          # Main web page (Jinja2 template)
|
|-- static/
|   |-- css/style.css       # Styling
|   |-- js/app.js           # Frontend JavaScript
```

---

## How to Install & Run

### Step 1 — Install Python
Download Python 3.9 or newer from https://python.org/downloads
During installation, check "Add Python to PATH"

Verify in terminal:
```
python --version
```

### Step 2 — Download / Clone the Project
Place the `sentiment_analysis_project` folder on your Desktop or anywhere you prefer.

### Step 3 — Open Terminal in the Project Folder
- **Windows:** Right-click the folder → "Open in Terminal" or open CMD and type:
  ```
  cd "C:\Users\YourName\Desktop\sentiment_analysis_project"
  ```
- **Mac/Linux:**
  ```
  cd ~/Desktop/sentiment_analysis_project
  ```

### Step 4 — Create a Virtual Environment (Recommended)
```bash
python -m venv venv

# Activate on Windows:
venv\Scripts\activate

# Activate on Mac/Linux:
source venv/bin/activate
```

### Step 5 — Run the Setup Script (One-time Only)
```bash
python setup.py
```
This will:
- Install all required packages
- Download NLTK language data
- Train and save the ML model

### Step 6 — Start the Web Application
```bash
python app.py
```

### Step 7 — Open in Browser
Open your browser and go to:
```
http://127.0.0.1:5000
```

---

## Manual Installation (if setup.py fails)

```bash
pip install flask pandas numpy scikit-learn vaderSentiment textblob matplotlib seaborn wordcloud plotly nltk joblib

python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt'); nltk.download('wordnet')"

python model/train_model.py

python app.py
```

---

## How the ML Model Works

```
Raw Text
   |
   v
[Preprocessing]
  - Lowercase
  - Remove URLs, @mentions, #hashtags
  - Remove punctuation
  - Remove stop words (the, is, at, ...)
  - Lemmatization (running -> run)
   |
   v
[TF-IDF Vectorizer]
  - Converts text to numerical feature matrix
  - Uses top 5000 words + bigrams
   |
   v
[Logistic Regression Classifier]
  - Trained on labeled positive/negative/neutral data
  - Predicts class + confidence probability
   |
   v
Final Label + Confidence %
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main web page |
| `/analyze` | POST | Analyze single text |
| `/analyze_bulk` | POST | Analyze multiple texts |
| `/demo` | GET | Run demo with sample texts |

### Example API usage (Python):
```python
import requests

response = requests.post('http://127.0.0.1:5000/analyze', json={
    'text': 'I absolutely love this product!'
})
print(response.json())
```

---

## Technologies Used

| Technology | Purpose |
|------------|---------|
| Python 3.9+ | Core programming language |
| Flask | Web framework (backend) |
| scikit-learn | Machine learning (TF-IDF + Logistic Regression) |
| VADER | Social media sentiment analysis |
| TextBlob | NLP — polarity & subjectivity |
| NLTK | Text preprocessing |
| pandas / numpy | Data manipulation |
| Chart.js | Interactive frontend charts |
| HTML / CSS / JS | Frontend UI |

---

## Sample Output

Input: `"I love this product! Best purchase ever!"`

```
Final Sentiment: POSITIVE

VADER:     compound = 0.8074  → positive
TextBlob:  polarity = 0.6875  → positive
ML Model:  label = positive, confidence = 94.2%

Keywords: love, product, best, purchase
```

---

## Possible Extensions (for future work)

- Connect to Twitter/X API for real-time tweet analysis
- Add aspect-based sentiment (product, service, delivery)
- Use BERT/transformers for better accuracy
- Add language detection and multilingual support
- Export results to CSV/PDF report
- Deploy to cloud (Heroku, AWS, Google Cloud)

---

## Author

**Project:** Social Media and Sentiment Analysis  
**Subject:** Machine Learning / Natural Language Processing  
**Tools:** Python, Flask, scikit-learn, VADER, TextBlob
