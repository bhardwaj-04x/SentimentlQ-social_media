@echo off
title SentimentIQ Setup - Sakshi Puri - UID: 24BET10158
color 0A
cls

echo.
echo  ============================================================
echo   SOCIAL MEDIA SENTIMENT ANALYZER - WINDOWS SETUP
echo  ============================================================
echo   Author  : Sakshi Puri
echo   UID     : 24BET10158
echo   Project : Social Media ^& Sentiment Analysis
echo   Year    : 2025  ^|  College Final Project
echo  ============================================================
echo.

echo [STEP 1] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo  ERROR: Python not found! Install from https://python.org
    echo  IMPORTANT: Check "Add Python to PATH" during install.
    pause & exit /b 1
)
python --version
echo  Python found!
echo.

echo [STEP 2] Checking pip...
pip --version >nul 2>&1
if errorlevel 1 ( python -m ensurepip --upgrade )
echo  pip is ready.
echo.

echo [STEP 3] Creating virtual environment...
if exist venv (
    echo  Already exists, skipping.
) else (
    python -m venv venv
    echo  Virtual environment created.
)
echo.

echo [STEP 4] Activating virtual environment...
call venv\Scripts\activate.bat
echo  Activated!
echo.

echo [STEP 5] Upgrading pip...
python -m pip install --upgrade pip --quiet
echo  pip upgraded.
echo.

echo [STEP 6] Installing packages (Python 3.13 compatible)...
echo  This takes 2-5 minutes. Please wait...
echo.
pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo  Retrying with --only-binary flag...
    pip install --only-binary :all: flask pandas numpy scikit-learn matplotlib seaborn plotly joblib
    pip install vaderSentiment textblob nltk wordcloud
)
echo.
echo  All packages installed!
echo.

echo [STEP 7] Downloading NLTK language data...
python -c "import nltk; nltk.download('stopwords',quiet=True); nltk.download('punkt',quiet=True); nltk.download('punkt_tab',quiet=True); nltk.download('wordnet',quiet=True); print('  NLTK data ready!')"
echo.

echo [STEP 8] Training the Machine Learning model...
python model\train_model.py
echo.

echo  ============================================================
echo   SETUP COMPLETE!  ^|  Sakshi Puri  ^|  UID: 24BET10158
echo  ============================================================
echo.
echo   Run the app:   double-click RUN_APP.bat
echo   Open browser:  http://127.0.0.1:5000
echo.
echo  ============================================================
pause
