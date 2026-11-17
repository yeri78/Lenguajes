@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0"
if not exist out mkdir out
set "FUENTES="
for %%F in (transporte\*.java) do set "FUENTES=!FUENTES! "%%F""
javac -encoding UTF-8 -d out !FUENTES!
if errorlevel 1 (
  echo No se pudo compilar. Verifica que tengas el JDK 17 o superior instalado ^(comando javac^).
  pause
  exit /b 1
)
java -cp out transporte.Ventana
if errorlevel 1 pause
