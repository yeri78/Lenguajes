@echo off
cd /d "%~dp0"
python main.py ventana || py main.py ventana
if errorlevel 1 pause
