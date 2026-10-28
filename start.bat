@echo off
cd /d "%~dp0"
py -3 run.py --host 127.0.0.1 --port 4173
pause
