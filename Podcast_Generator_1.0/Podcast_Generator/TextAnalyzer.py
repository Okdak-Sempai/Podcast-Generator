"""
TextAnalyzer.py
================

Module d’analyse textuelle du projet Podcast Generator.
Il permet d'effectuer :

- La détection automatique de la langue d'un texte
- Le découpage en chunks de taille contrôlée
- Le résumé de documents entiers, chunk par chunk, en mode RAG-compatible
- L’extraction de mots-clés essentiels à partir d’un contenu textuel
- L’identification des grands thèmes d’un texte ou d’un résumé

Toutes les fonctions reposent sur un wrapper `call_model()`
qui permet d’interroger un modèle local ou un serveur LLM via une API compatible OpenAI.

Les prompts sont entièrement localisés et maintenus dans le fichier `PromptTextAnalyzer.py`.

Le paramètre `output_language` permet de forcer la langue de génération,
indépendamment de celle du texte source.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from Podcast_Generator import SourceImporter
from Podcast_Generator import LocalIAIManager
from Podcast_Generator.PromptTextAnalyzer import PROMPTS_RAG
from Podcast_Generator.SystemEngine import save_text_to_file
import re
import tiktoken
import time
from datetime import datetime

# List Cleaning

def clean_list(items: list[str]) -> list[str]:
    """
    Nettoie une liste de chaînes de texte en supprimant :
    - la casse,
    - les caractères spéciaux,
    - les articles français vides (le, la, les...),
    - les doublons ou entrées trop courtes.

    Args:
        items (list[str]): Liste brute de chaînes à nettoyer.

    Returns:
        list[str]: Liste nettoyée et triée de mots ou concepts pertinents.
    """
    cleaned = set()
    for item in items:
        item = item.lower()
        item = re.sub(r"[^a-zàâçéèêëîïôûùüÿñæœ\s\-]", "", item)
        item = re.sub(r"\b(le|la|les|des|du|de|d|l)\b", "", item)
        item = item.strip()
        if item and len(item) > 2:
            cleaned.add(item)
    return sorted(cleaned)

def clean_raw_concepts(lines: list[str]) -> list[str]:
    """
    Nettoie une liste de concepts extraits par LLM (toutes langues).

    Supprime les préfixes génériques ("mot-clé", "keyword", etc.), les fragments inutiles
    et les doublons. Neutralise les langues pour rester généraliste.

    Args:
        lines (list[str]): Liste brute de chaînes extraites.

    Returns:
        list[str]: Concepts nettoyés, filtrés et dédupliqués.
    """
    # Préfixes qu’on veut ignorer dans toutes les langues
    generic_prefixes = [
        r"^(mot[- ]?clé|keyword|thema|thème|theme|concept|title|titre|topic|sujet)\s*[:：\-–]*\s*",
        r"^(voici|these are|this is|ceci est|以下|這是|これは)\b.*",  # phrases introductives
        r"^(liste de|ensemble de|group[eé] de|group of|list of)\b.*"
    ]

    cleaned = set()
    for line in lines:
        original = line
        line = line.strip().lower()

        # Supprimer les préfixes connus
        for pattern in generic_prefixes:
            line = re.sub(pattern, "", line, flags=re.IGNORECASE)

        # Supprimer les caractères parasites (tiret, bullet, ponctuation excessive)
        line = re.sub(r"^[\-\•\–\—\*]+\s*", "", line)
        line = line.strip(" .:;·—–•")  # ponctuation de fin

        # Filtrage : skip si vide, trop court, ou trop vague
        if line and len(line) >= 3 and not line.startswith("http") and not line.startswith("www"):
            cleaned.add(line)

    return sorted(cleaned)

# Splitting
def split_text_into_chunks(text: str, max_chars: int = 1500) -> list[str]:
    """
    Découpe un texte long en blocs de paragraphes sans dépasser `max_chars`.

    Args:
        text (str): Texte source à découper.
        max_chars (int): Nombre maximal de caractères par chunk.

    Returns:
        list[str]: Liste de blocs textuels.
    """
    paragraphs = text.split("\n")
    chunks = []
    current = ""
    for para in paragraphs:
        if len(current) + len(para) + 1 <= max_chars:
            current += para + "\n"
        else:
            chunks.append(current.strip())
            current = para + "\n"
    if current.strip():
        chunks.append(current.strip())
    return chunks

#Main

def summarize_with_meta_summary(
    text: str,
    backend: str = "server",
    model_path: str = None,
    max_tokens: int = 512,
    chunk_token_limit: int = 1024,
    output_language: str = None,
    tokenizer_model: str = "gpt-3.5-turbo"
) -> list[str]:
    """
    Résume un texte long en deux étapes :
    - Résumés partiels par chunk (découpés en fonction des tokens réels)
    - Résumé final global à partir de tous les résumés intermédiaires

    Args:
        text (str): Texte source à résumer.
        backend (str): "server" ou "local".
        model_path (str): Modèle local à utiliser si backend == "local".
        max_tokens (int): Nombre de tokens à générer par appel.
        chunk_token_limit (int): Nombre max de tokens par chunk (entrée).
        output_language (str): Langue de sortie (sinon détectée automatiquement). "fr"; "en"; "ja"; "zh-tw"; "zh-cn"
        tokenizer_model (str): Modèle pour tiktoken (pour encoder les chunks correctement).

    Returns:
        list[str]: Liste contenant :
            [0] → Résumé global synthétique
            [1:] → Résumés partiels de chaque chunk
    """
    #Timers Start
    start_time = time.time()
    print(f"Début summarize_with_meta_summary : {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    # Si aucun chunk_token_limit explicite, le déduire du modèle local (GGUF)
    if chunk_token_limit is None and backend == "local" and model_path:
        try:
            # On laisse une marge de 20% pour la génération du résumé (context = input + output)
            context_limit = LocalIAIManager.get_context_limit_from_gguf(model_path)
            chunk_token_limit = int(context_limit * 0.8)
            print(f"[Auto] Contexte max détecté : {context_limit} → Limite de découpe utilisée : {chunk_token_limit} tokens")
        except Exception as e:
            print(f"[Avertissement] Impossible de lire n_ctx depuis le modèle : {e}")
            chunk_token_limit = 1024
    elif chunk_token_limit is None:
        chunk_token_limit = 1024  # fallback

    lang = SourceImporter.detect_main_language(text)
    lang_out = (output_language if output_language else lang).strip().lower()
    lang_out = {
        "fra": "fr",
        "fre": "fr",
        "eng": "en",
        "jpn": "ja",
        "jp": "ja",
        "chi_sim": "zh-cn",
        "chi_tra": "zh-tw"
    }.get(lang_out, lang_out)

    if lang_out not in PROMPTS_RAG:
        print(f"[Info] Langue '{lang_out}' non supportée, fallback vers 'en'")
        lang_out = "en"

    prompt_summary = PROMPTS_RAG[lang_out]["summary_rag"]

    # Découpage réel basé sur tiktoken
    enc = tiktoken.encoding_for_model(tokenizer_model)
    words = text.split()
    chunks = []
    current_chunk = []

    for word in words:
        current_chunk.append(word)
        token_count = len(enc.encode(" ".join(current_chunk)))
        if token_count >= chunk_token_limit:
            chunks.append(" ".join(current_chunk))
            current_chunk = []

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    # Résumés partiels
    summaries = []
    for i, chunk in enumerate(chunks):
        print(f"[Chunk {i + 1}/{len(chunks)}] Résumé partiel...")
        prompt = f"{prompt_summary}\n\n---\n{chunk}\n\nRésumé :"
        summaries.append(LocalIAIManager.call_model(prompt, backend=backend, model_path=model_path, max_tokens=max_tokens).strip())

    # Résumé global sur les résumés partiels
    print(f"[Final] Résumé global en cours...")
    joint_summaries = "\n\n".join(summaries)
    final_prompt = f"{prompt_summary}\n\n---\n{joint_summaries}\n\nRésumé final synthétique :"
    global_summary = LocalIAIManager.call_model(final_prompt, backend=backend, model_path=model_path, max_tokens=max_tokens).strip()
    # Timers End
    end_time = time.time()
    elapsed = end_time - start_time
    print(f"Fin summarize_with_meta_summary: {datetime.now().strftime('%Y-%m-%d %H:%M')} — Temps écoulé : {elapsed:.2f} secondes")
    return [global_summary] + summaries

def group_semantic_concepts(concepts: list[str], language: str = "fr", backend="server", model_path=None) -> list[str]:
    """
    Regroupe sémantiquement une liste de concepts similaires.

    Envoie la liste à un LLM local ou distant pour regrouper les concepts
    qui désignent la même idée (ex: "internet", "web", "WWW").

    Args:
        concepts (list[str]): Liste initiale de concepts à regrouper.
        language (str): Langue à utiliser pour le prompt (ex: "fr", "en", etc.).
        backend (str): Backend LLM à utiliser : "server" (par défaut) ou "local".
        model_path (str): Chemin du modèle GGUF si backend == "local".

    Returns:
        list[str]: Concepts regroupés et nettoyés.

    Exemple :
        group_semantic_concepts(["IA", "intelligence artificielle", "machine learning"])
        → ["intelligence artificielle"]
    """
    language = language.strip().lower()

    if language not in PROMPTS_RAG:
        print(f"[Info] Langue '{language}' non supportée pour groupement sémantique, fallback vers 'en'")
        language = "en"

    prompt_instruction = PROMPTS_RAG[language]["grouping"]
    joined_concepts = ", ".join(concepts)
    prompt = f"{prompt_instruction}\n\n{joined_concepts}"
    response = LocalIAIManager.call_model(prompt, backend=backend, model_path=model_path, max_tokens=700)
    try:
        parsed = json.loads(response)
        if isinstance(parsed, list):
            return clean_list(parsed)
    except:
        pass
    return clean_list(concepts)

def extract_concepts(
    text: str,
    mode: str = "keywords",
    backend: str = "server",
    model_path: str = None,
    max_tokens: int = 512,
    output_language: str = None,
    semantic_grouping: bool = False
) -> list[str]:
    """
    Extrait les concepts clés d’un texte sous forme de mots-clés ou de thèmes.

    Selon le `mode`, la fonction demande à un modèle LLM (local ou distant) de générer :
        - une liste de mots-clés (`mode="keywords"`)
        - une liste de thèmes globaux (`mode="themes"`)

    Les résultats sont nettoyés puis optionnellement regroupés sémantiquement.

    Args:
        text (str): Texte source à analyser.
        mode (str): Soit "keywords" (par défaut) soit "themes".
        backend (str): "server" (par défaut) ou "local".
        model_path (str): Requis si backend == "local".
        max_tokens (int): Nombre de tokens générés max par chunk.
        output_language (str): Langue de sortie (sinon détectée automatiquement). "fr"; "en"; "ja"; "zh-tw"; "zh-cn"
        semantic_grouping (bool): Si True, regroupe les concepts proches via LLM.

    Returns:
        list[str]: Liste de mots ou concepts nettoyés, optionnellement regroupés.

    Exemple :
        extract_concepts(text, mode="themes", backend="local", model_path=mistralQ4)
    """
    #Timers Start
    start_time = time.time()
    print(f"Début extract_concepts{mode} : {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    lang = SourceImporter.detect_main_language(text)
    out_lang = (output_language if output_language else lang).strip().lower()

    if out_lang not in PROMPTS_RAG:
        print(f"[Info] Langue '{out_lang}' non supportée, fallback vers 'en'")
        out_lang = "en"

    prompt_key = "keywords" if mode == "keywords" else "themes"
    prompt_body = PROMPTS_RAG[out_lang][prompt_key]

    chunks = split_text_into_chunks(text, max_chars=1500 if mode == "themes" else 1200)
    results = set()

    for i, chunk in enumerate(chunks):
        print(f"[Chunk {i + 1}/{len(chunks)}] → concepts ({mode})...")
        prompt = f"{prompt_body}\n\n---\n{chunk}\n\n{mode.capitalize()} :"
        response = LocalIAIManager.call_model(prompt, backend=backend, model_path=model_path, max_tokens=max_tokens)
        lines = [line.strip("- •\n ") for line in response.strip().split("\n") if line.strip()]
        lines = clean_raw_concepts(lines)
        results.update(lines)

    cleaned = clean_list(list(results))

    # Timers End
    end_time = time.time()
    elapsed = end_time - start_time
    print(f"Fin extract_concepts{mode}: {datetime.now().strftime('%Y-%m-%d %H:%M')} — Temps écoulé : {elapsed:.2f} secondes")

    return group_semantic_concepts(cleaned, language=out_lang, backend=backend, model_path=model_path) if semantic_grouping else cleaned

# Save and Load Results (json)

def save_list_to_json(
    data: list[str],
    suffix: str = "summary",
    path: str = None
) -> str:
    """
    Sauvegarde une liste de chaînes dans un fichier JSON dans un dossier structuré.

    - Dossier par défaut : Result/RSM-YYYYMMDD-HHMM/
    - Fichier : {suffix}.json (ex: summary.json, keywords.json, themes.json)

    Args:
        data (list[str]): Liste de chaînes à sauvegarder.
        suffix (str): Type de fichier ('summary', 'keywords', 'themes').
        path (str, optional): Dossier de destination. Si None, utilise Result/RSM-<datetime>.

    Returns:
        str: Chemin complet du fichier JSON créé.

    Raises:
        ValueError: Si les données ne sont pas une liste de chaînes ou suffix non autorisé.
    """
    allowed_suffixes = {"summary", "keywords", "themes"}
    if suffix not in allowed_suffixes:
        raise ValueError(f"Suffix invalide : '{suffix}'. Valeurs autorisées : {allowed_suffixes}")

    if not isinstance(data, list) or not all(isinstance(item, str) for item in data):
        raise ValueError("Les données doivent être une liste de chaînes de caractères.")

    # Dossier par défaut basé sur timestamp
    if path is None:
        now = datetime.now()
        base_folder = f"RSM-{now.strftime('%Y%m%d-%H%M')}"
        path = Path("Result") / base_folder
    else:
        path = Path(path)

    path.mkdir(parents=True, exist_ok=True)
    file_path = path / f"{suffix}.json"

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return str(file_path)

def load_summary_bundle_from_folder(folder_path: str) -> dict:
    """
    Charge automatiquement les fichiers JSON contenant 'summary', 'keywords' ou 'themes' dans leur nom depuis un dossier.

    Seuls les fichiers ayant les bons suffixes dans leur nom sont pris en compte.
    Tous les autres fichiers JSON (ex: script.json) sont ignorés automatiquement.

    Args:
        folder_path (str): Dossier contenant les fichiers JSON (au moins 3 fichiers valides attendus).

    Returns:
        dict: Dictionnaire {'summary': list[str], 'keywords': list[str], 'themes': list[str]}

    Raises:
        FileNotFoundError: Si un ou plusieurs fichiers attendus sont absents.
        ValueError: Si un fichier est mal formé ou son contenu n'est pas une liste de chaînes.
    """
    folder = Path(folder_path)
    bundle = {"summary": None, "keywords": None, "themes": None}

    # On parcourt tous les fichiers JSON du dossier
    for file in folder.glob("*.json"):
        fname = file.name.lower()

        #  Ne charger que les fichiers attendus
        if not any(key in fname for key in ("summary", "keywords", "themes")):
            continue  # Ignore script.json, metadata.json, etc.

        try:
            with open(file, "r", encoding="utf-8") as f:
                content = json.load(f)

            #  Vérification du contenu : doit être une liste de chaînes
            if not isinstance(content, list) or not all(isinstance(i, str) for i in content):
                raise ValueError(f"{file.name} n’est pas une liste valide de chaînes.")

            if "summary" in fname and bundle["summary"] is None:
                bundle["summary"] = content
            elif "keyword" in fname and bundle["keywords"] is None:
                bundle["keywords"] = content
            elif "theme" in fname and bundle["themes"] is None:
                bundle["themes"] = content

        except Exception as e:
            raise ValueError(f"Erreur de lecture pour {file.name} : {e}")

    # Vérifie que tous les composants sont bien chargés
    missing = [k for k, v in bundle.items() if v is None]
    if missing:
        raise FileNotFoundError(f"Fichiers manquants ou incorrects : {', '.join(missing)}")

    return bundle