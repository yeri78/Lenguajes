@echo off
setlocal
cd /d "%~dp0"
node src\main.js ventana
if errorlevel 1 pause
