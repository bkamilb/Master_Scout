@echo off
title ScoutLab Pro Baslatici
cd /d "%~dp0"
echo Sanal ortam aktif ediliyor...
call venv\Scripts\activate
echo ScoutLab Pro baslatiliyor...
streamlit run app.py
pause