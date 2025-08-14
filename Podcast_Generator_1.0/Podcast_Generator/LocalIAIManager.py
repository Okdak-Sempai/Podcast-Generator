"""
LocalIAIManager.py
===================

Ce module fournit une interface unifiée pour interroger soit :
- Un modèle local GGUF chargé via llama-cpp,
- Soit un serveur local compatible OpenAI API (llama-cpp-server).

Fonctions principales :
- Envoyer des prompts à un modèle local en mémoire (GGUF).
- Envoyer des prompts à un serveur HTTP local (mode OpenAI compatible).
- Lire la limite de contexte (n_ctx) supportée par un modèle GGUF.
- Sélectionner dynamiquement le backend ("local" ou "server") selon les besoins.

Utilisation :
- Permet d'intégrer facilement des modèles LLM locaux dans des pipelines RAG ou de génération de texte.
- Supporte le contrôle du nombre de tokens et de la température de génération.

Notes :
- Le serveur local attendu pour `server` est accessible par défaut sur `http://localhost:11434`.
"""


from llama_cpp import Llama
import requests

# FR transformer → 'sentence-transformers/all-MiniLM-L6-v2'
# EN transformer → 'thenlper/gte-small'
# CN/JP transformer → 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'

mistralQ4 = "Models/Mistral-7B-Instruct-v0.1-GGUF/mistral-7b-instruct-v0.1.Q4_K_M.gguf"
mistralQ8 = "Models/Mistral-7B-Instruct-v0.1-GGUF/mistral-7b-instruct-v0.1.Q8_0.gguf"
Qwen1o5 = "Models/Qwen1.5-7B-Chat-GGUF/qwen1_5-7b-chat-q8_0.gguf"
Qwen2o5 = "Models/qwen2.5-7b-instruct-q8_0.gguf"
mistralQQ = Qwen2o5
NemoQ4 = "Models/Mistral-Nemo-Instruct-2407-Q4_K_M.gguf"
NemoQ8 = "Models/Mistral-Nemo-Instruct-2407-Q8_0.gguf"


#python -m llama_cpp.server --model "Models/Mistral-Nemo-Instruct-2407-Q8_0.gguf" --n_ctx 4096 --n_gpu_layers 100 --port 11434
#python -m llama_cpp.server --model "Models/Mistral-7B-Instruct-v0.1-GGUF/mistral-7b-instruct-v0.1.Q4_K_M.gguf" --n_ctx 4096 --n_gpu_layers 100 --port 11434
#python -m llama_cpp.server --model "Models/Qwen1.5-7B-Chat-GGUF/qwen1_5-7b-chat-q8_0.gguf" --n_ctx 4096 --n_gpu_layers 100 --port 11434
#python -m llama_cpp.server --model "Models/qwen2.5-7b-instruct-q8_0.gguf" --n_ctx 4096 --n_gpu_layers 100 --port 11434

def query_local_model(prompt: str, model_path: str, max_tokens: int = 1024) -> str:
    """
    Envoie un prompt à un modèle GGUF local et retourne la réponse textuelle.

    Args:
        prompt (str): Prompt à envoyer au modèle.
        model_path (str): Chemin vers le fichier GGUF du modèle.
        max_tokens (int): Nombre max de tokens générés en sortie.

    Returns:
        str: Réponse textuelle du modèle.
    """
    llm = Llama(
        model_path=model_path,
        n_ctx=32768,
        n_gpu_layers=60,
        verbose=True

        #n_ctx=4096,
        #n_gpu_layers=10,
        #verbose=False
    )

    result = llm(prompt, max_tokens=max_tokens)
    return result["choices"][0]["text"].strip()


def query_server_local(prompt: str, max_tokens: int = 512, temperature: float = 0.7) -> str:
    """
    Envoie un prompt à un serveur llama-cpp local lancé avec n'importe quel modèle (mode OpenAI-compatible).

    Args:
        prompt (str): Texte à envoyer.
        max_tokens (int): Nombre max de tokens générés (par défaut : 512).
        temperature (float): Température de génération (par défaut : 0.7).

    Returns:
        str: Réponse générée par le modèle actuellement chargé dans le serveur.
    """
    endpoint = "http://localhost:11434/v1/chat/completions"
    headers = {"Content-Type": "application/json"}

    payload = {
        "model": "default",  # nom par défaut si aucun --alias n’a été précisé
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": temperature
    }

    try:
        response = requests.post(endpoint, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()

    except requests.exceptions.RequestException as e:
        return f"[Erreur] Impossible d'interroger le modèle : {e}"


def get_context_limit_from_gguf(model_path: str) -> int:
    """
    Récupère la limite de contexte (n_ctx) d’un modèle local GGUF via llama-cpp.

    Args:
        model_path (str): Chemin vers le modèle GGUF.

    Returns:
        int: Nombre maximum de tokens en entrée (n_ctx).
    """
    llm = Llama(model_path=model_path, n_ctx=1)  # n_ctx ici ne change pas la vraie valeur lue
    return llm.n_ctx()


def call_model(prompt: str, backend: str = "server", model_path: str = None, max_tokens: int = 512, temperature: float = 0.7) -> str:
    """
    Wrapper unifié pour interroger un modèle local (GGUF) ou distant (serveur).

    Args:
        prompt (str): Le prompt à envoyer au modèle.
        backend (str): "server" (par défaut) ou "local".
        model_path (str): Requis si backend == "local".
        max_tokens (int): Nombre de tokens générés maximum.
        temperature (float): Température de génération (creativity).

    Returns:
        str: Réponse textuelle du modèle.
    """
    if backend == "local":
        if not model_path:
            raise ValueError("model_path requis pour un backend local.")
        return query_local_model(prompt, model_path=model_path, max_tokens=max_tokens)
    elif backend == "server":
        return query_server_local(prompt, max_tokens=max_tokens, temperature=temperature)
    else:
        raise ValueError(f"Backend inconnu : {backend}")