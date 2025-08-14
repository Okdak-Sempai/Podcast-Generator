@echo off
setlocal ENABLEEXTENSIONS

:: Demande le chemin du modèle
set /p RAW_PATH=Entrez le chemin complet vers le modèle GGUF (.gguf) :

:: Supprime les guillemets éventuels de la saisie
set MODEL_PATH=%RAW_PATH:"=%

:: Vérifie que le fichier existe
if not exist "%MODEL_PATH%" (
    echo [ERREUR] Le fichier n'existe pas : %MODEL_PATH%
    pause
    exit /b 1
)

:: Lancement du serveur
echo Lancement de llama_cpp.server...
python -m llama_cpp.server --model "%MODEL_PATH%" --n_ctx 4096 --n_gpu_layers 100 --port 11434
