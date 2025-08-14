#!/bin/bash
cd "$(dirname "$0")"

echo "Entrez le chemin complet vers le modèle GGUF (.gguf) :"
read MODEL_PATH

if [ ! -f "$MODEL_PATH" ]; then
    echo "[ERREUR] Le fichier n'existe pas : $MODEL_PATH"
    exit 1
fi

python3.11 -m llama_cpp.server --model "$MODEL_PATH" --n_ctx 4096 --n_gpu_layers 100 --port 11434
