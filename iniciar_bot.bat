@echo off
title Escape Room Bot
chcp 65001 > nul

echo Iniciando Escape Room Bot...
echo.

call "%~dp0.venv\Scripts\activate.bat"

if errorlevel 1 (
    echo No se pudo activar el entorno virtual.
    echo Ejecuta primero instalar_dependencias.bat
    echo.
    pause
    exit /b
)

python "%~dp0main.py"

echo.
echo El bot se ha detenido.
pause