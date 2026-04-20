"""
Run this script ONCE to set up the project:
  python setup.py

Works with Python 3.10, 3.11, 3.12, 3.13
"""
import subprocess
import sys
import os

def run(cmd):
    print(f">> {cmd}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"  Warning: command returned code {result.returncode}")

print("=" * 55)
print("  Social Media Sentiment Analyzer - Setup Script")
print("=" * 55)

print(f"\nPython version: {sys.version}")

# Upgrade pip first
print("\n[1/4] Upgrading pip...")
run(f"{sys.executable} -m pip install --upgrade pip")

# Install packages — use requirements.txt (no pinned versions that break on Py3.13)
print("\n[2/4] Installing required packages...")
result = subprocess.run(
    f"{sys.executable} -m pip install -r requirements.txt",
    shell=True
)
if result.returncode != 0:
    print("\n  Retrying with --only-binary to avoid C compiler issues...")
    run(f"{sys.executable} -m pip install --only-binary :all: flask pandas numpy scikit-learn matplotlib seaborn plotly joblib")
    run(f"{sys.executable} -m pip install vaderSentiment textblob nltk wordcloud")

# Download NLTK data
print("\n[3/4] Downloading NLTK language data...")
import nltk
for pkg in ['stopwords', 'punkt', 'punkt_tab', 'wordnet', 'averaged_perceptron_tagger']:
    nltk.download(pkg, quiet=True)
    print(f"  {pkg} OK")

# Train model
print("\n[4/4] Training the ML sentiment model...")
os.chdir(os.path.dirname(os.path.abspath(__file__)))
run(f"{sys.executable} model/train_model.py")

print("\n" + "=" * 55)
print("  Setup complete! Now run:")
print("  python app.py")
print("  Then open: http://127.0.0.1:5000")
print("=" * 55)
