@echo off
title YoutubeOff
cd /d "%~dp0"
start "" http://localhost:8756
python app.py
pause
