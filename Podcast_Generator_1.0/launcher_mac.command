#!/bin/bash
cd "$(dirname "$0")"

# Vérifie que Python 3.11 est installé
if ! command -v python3.11 &> /dev/null
then
    echo "[ERREUR] Python 3.11 n'est pas installé ou pas dans le PATH."
    exit 1
fi

# Crée l'environnement virtuel s'il n'existe pas
if [ ! -d "venv" ]; then
    echo "Création de l'environnement virtuel avec Python 3.11..."
    python3.11 -m venv venv
fi

# Active l'environnement virtuel
source venv/bin/activate

# Installe les dépendances
echo "Installation des dépendances Python..."
pip install -r requirements.txt

# Lance l'application principale
echo "Lancement de l'interface terminal..."
python3.11 -m Podcast_Generator.mainTerminalUI
