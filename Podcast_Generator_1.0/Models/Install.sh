#!/bin/bash

# ===========================
#     Qwen 1.5-7B-Chat
# ===========================
echo ">> 📁 Création de qwen1.5-7B-Chat-GGUF/"
mkdir -p qwen1.5-7B-Chat-GGUF

echo ">> 📥 Téléchargement fichiers Qwen..."
wget -c https://huggingface.co/Qwen/Qwen1.5-7B-Chat-GGUF/resolve/main/README.md -O qwen1.5-7B-Chat-GGUF/README.md
wget -c https://huggingface.co/Qwen/Qwen1.5-7B-Chat-GGUF/resolve/main/LICENSE -O qwen1.5-7B-Chat-GGUF/LICENSE
wget -c https://huggingface.co/Qwen/Qwen1.5-7B-Chat-GGUF/resolve/main/qwen1_5-7b-chat-q8_0.gguf -P qwen1.5-7B-Chat-GGUF

# ===========================
#     Mistral 7B Instruct
# ===========================
echo ">> 📁 Création de Mistral-7B-Instruct-v0.1-GGUF/"
mkdir -p Mistral-7B-Instruct-v0.1-GGUF

echo ">> 📥 Téléchargement fichiers Mistral..."
wget -c https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/README.md -O Mistral-7B-Instruct-v0.1-GGUF/README.md
wget -c https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/config.json -O Mistral-7B-Instruct-v0.1-GGUF/config.json
wget -c https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/mistral-7b-instruct-v0.1.Q8_0.gguf -P Mistral-7B-Instruct-v0.1-GGUF
wget -c https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/mistral-7b-instruct-v0.1.Q4_K_M.gguf -P Mistral-7B-Instruct-v0.1-GGUF

echo ">> ✅ Tous les fichiers ont été placés dans leurs dossiers respectifs."
