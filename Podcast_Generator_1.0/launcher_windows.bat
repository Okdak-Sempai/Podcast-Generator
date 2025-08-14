@echo off
setlocal ENABLEEXTENSIONS

:: Vérifie que les deux scripts existent
if not exist launcher_server_windows.bat (
    echo [ERREUR] Fichier manquant : launcher_server_windows.bat
    pause
    exit /b 1
)

if not exist launcher_PG_windows.bat (
    echo [ERREUR] Fichier manquant : launcher_PG_windows.bat
    pause
    exit /b 1
)

:: Lance le serveur dans une nouvelle fenêtre
start "Serveur LLM" cmd /k launcher_server_windows.bat

:: Lance l'interface principale dans une autre fenêtre
start "Interface Terminal" cmd /k launcher_PG_windows.bat
