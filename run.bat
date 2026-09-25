@echo off
echo Starting GGH System...
cd /d "%~dp0"
venv\Scripts\python.exe manage.py runserver
pause
