@echo off
setlocal ENABLEEXTENSIONS

:: Vérifie que Python 3.11 est disponible via le launcher
py -3.11 --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERREUR] Python 3.11 n'est pas disponible via le launcher 'py'.
    pause
    exit /b 1
)

:: Vérifie version exacte
for /f "tokens=2 delims= " %%i in ('py -3.11 --version') do set PYVER=%%i
echo Version Python detectee : %PYVER%
echo %PYVER% | findstr /r "^3\.11\." >nul
if errorlevel 1 (
    echo [ERREUR] Python 3.11 requis. Version detectee : %PYVER%
    pause
    exit /b 1
)
:: Vérifie que llama-cpp-python est présent dans le dossier
if not exist llama-cpp-python (
    echo [ERREUR] Dossier 'llama-cpp-python' manquant.
    echo Assurez-vous que le module est dans ce dossier et compilé
    pause
    exit /b 1
)

:: Crée un venv si besoin
if not exist venv (
    echo Creation de l'environnement virtuel avec Python 3.11...
    py -3.11 -m venv venv
)

:: Active l'environnement
call venv\Scripts\activate.bat

:: Ajoute le dossier courant dans PYTHONPATH
set PYTHONPATH=%CD%

:: Installe les dépendances
echo Installation des dependances Python...
pip install -r requirements.txt >nul

:: Lance le menu principal
echo.
echo Lancement de l'interface terminal...
py -3.11 -m Podcast_Generator.mainTerminalUI
