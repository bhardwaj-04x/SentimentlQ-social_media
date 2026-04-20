@echo off
title SentimentIQ - Sakshi Puri - UID: 24BET10158
color 0A
cls

echo.
echo  ============================================================
echo   SOCIAL MEDIA SENTIMENT ANALYZER
echo  ============================================================
echo   Author  : Sakshi Puri
echo   UID     : 24BET10158
echo   Project : Social Media ^& Sentiment Analysis
echo   Year    : 2025  ^|  College Final Project
echo  ============================================================
echo.

if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo  [OK] Virtual environment activated.
) else (
    echo  [INFO] No venv found, using system Python.
)

echo.
echo  [INFO] Starting Flask web server...
echo  [INFO] Open your browser at: http://127.0.0.1:5000
echo.
echo  Author : Sakshi Puri  ^|  UID : 24BET10158
echo  Press CTRL+C to stop the server.
echo  ============================================================
echo.

python app.py
pause
