@echo off
title Instalar dependencias del Escape Room Bot
chcp 65001 > nul

echo Instalando dependencias del Escape Room Bot...
echo.

call "%~dp0.venv\Scripts\activate.bat"

if errorlevel 1 (
    echo No se encontro el entorno virtual.
    echo Intentando crear el entorno virtual...
    python -m venv "%~dp0.venv"
    call "%~dp0.venv\Scripts\activate.bat"
)

python -m pip install --upgrade pip
python -m pip install -r "%~dp0requirements.txt"

echo.
echo Dependencias instaladas o actualizadas.
pause