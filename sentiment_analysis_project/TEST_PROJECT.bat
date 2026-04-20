@echo off
title SentimentIQ Tests - Sakshi Puri - UID: 24BET10158
color 0E
cls

echo.
echo  ============================================================
echo   SOCIAL MEDIA SENTIMENT ANALYZER - TEST SUITE
echo  ============================================================
echo   Author  : Sakshi Puri
echo   UID     : 24BET10158
echo   Project : Social Media ^& Sentiment Analysis
echo  ============================================================
echo.

if exist venv\Scripts\activate.bat ( call venv\Scripts\activate.bat )

python test_project.py

echo.
echo  ============================================================
echo   Tests complete  ^|  Sakshi Puri  ^|  UID: 24BET10158
echo  ============================================================
pause
