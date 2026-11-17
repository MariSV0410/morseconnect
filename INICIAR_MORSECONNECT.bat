@echo off
setlocal
cd /d "%~dp0"
title MorseConnect - Servidor

echo ============================================
echo             MORSECONNECT - INICIO
echo ============================================

if not exist ".venv\Scripts\python.exe" (
    echo [1/3] Preparando entorno de Python...
    py -m venv .venv
    if errorlevel 1 goto error
)

 echo [2/3] Activando entorno e instalando dependencias...
call ".venv\Scripts\activate.bat"
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if errorlevel 1 goto error

 echo [3/3] Abriendo MorseConnect...
set HARDWARE_MODE=pico
start "" http://127.0.0.1:5000
python app.py

echo.
echo El servidor se ha detenido.
pause
exit /b 0

:error
echo.
echo No se pudo iniciar. Verifica que Python este instalado y agregado al PATH.
pause
exit /b 1
