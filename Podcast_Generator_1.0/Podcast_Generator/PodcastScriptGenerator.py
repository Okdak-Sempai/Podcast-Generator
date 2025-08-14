"""
PodcastScriptGenerator.py
==========================

Ce module gère la création, la sauvegarde, le chargement et la manipulation de scripts de podcast
dans le projet Podcast Generator.

Rôles principaux :
- Générer un script narratif structuré (INTRO, 4 parties, OUTRO) à partir d'une synthèse RAG.
- Sauvegarder et charger les scripts au format JSON.
- Associer dynamiquement des personnages à des voix pour la synthèse vocale.
- Normaliser, parser et modifier les fichiers de dialogue préparés pour l'audio.

Utilisation :
- Appelé après l'étape d'analyse (`TextAnalyzer.py`) pour construire un scénario de podcast.
- Les scripts générés sont utilisés ensuite par `PodcastDialogueGenerator.py` et `PodcastGeneratorAudio.py`.

Notes :
- Ce module utilise les embeddings `sentence-transformers` pour affiner les contenus choisis.
- Compatible multilingue (français, anglais, japonais, chinois).

This module builds and manages podcast scripts based on RAG summaries, preparing them
for dialogue generation and voice synthesis in the Podcast Generator pipeline.
"""


import os
import re
import json
from pathlib import Path
from datetime import datetime
from Podcast_Generator.TextAnalyzer import load_summary_bundle_from_folder
from Podcast_Generator.LocalIAIManager import call_model, get_context_limit_from_gguf
from Podcast_Generator.SourceImporter import detect_main_language
from Podcast_Generator.PromptTextAnalyzer import PROMPTS_RAG
from Podcast_Generator.SystemEngine import save_text_to_file
from Podcast_Generator.TonePresetManager import load_tone_presets
from sentence_transformers import SentenceTransformer, util
import gender_guesser.detector as gender
import time
from datetime import datetime

# === CONFIGURATION
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
model = SentenceTransformer(EMBEDDING_MODEL)
tone_presets = load_tone_presets()
tone_list = list(tone_presets.keys())
tone_embeddings = model.encode(tone_list, normalize_embeddings=True)

# Initialisation du modèle d'embedding
model = SentenceTransformer(EMBEDDING_MODEL)

def create_script_rag_modulaire(folder_path: str, style: str = None, model_path: str = None, backend: str = "server", output_language: str = None, max_tokens: int = None) -> dict:
    """
       Génère un script narratif structuré (INTRO, 4 PARTIES, OUTRO) à partir d'un dossier contenant un bundle de résumés RAG.

       Args:
           folder_path (str): Chemin vers le dossier contenant 'summary.json', 'keywords.json', 'themes.json'.
           style (str, optional): Style narratif imposé (ex: "pédagogique"). Choisi automatiquement si None.
           model_path (str, optional): Chemin du modèle local GGUF à utiliser si backend == "local".
           backend (str, optional): Mode d'exécution ("server" par défaut ou "local").
           output_language (str, optional): Langue de génération ("fr", "en", "ja", "zh-cn", "zh-tw"). Auto-détection si None.
           max_tokens (int, optional): Nombre maximal de tokens pour chaque génération. Déduit automatiquement si None.

       Returns:
           dict: Dictionnaire avec 3 clés :
               - 'intro': Introduction (str)
               - 'parts': Liste de 4 parties (list[dict] avec 'title' et 'content')
               - 'outro': Conclusion (str)

       Remarques:
           - Optimise les extraits utilisés en fonction de leur similarité avec le résumé principal.
           - Utilise une génération multilingue avec fallback français.
       """
    #Timers Start
    start_time = time.time()
    print(f"Début create_script_rag_modulaire : {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    bundle = load_summary_bundle_from_folder(folder_path)
    summary_main = bundle["summary"][0]
    keywords = bundle["keywords"]
    themes = bundle["themes"]
    chunks = bundle["summary"][1:]

    # Choix dynamique du top_k basé sur le nombre de chunks
    total_chunks = len(chunks)
    top_k = min(5, max(1, total_chunks // 5)) if total_chunks > 0 else 0

    if chunks:
        embeddings = model.encode(chunks, convert_to_tensor=True, normalize_embeddings=True)
        query = f"{summary_main} {' '.join(themes)} {' '.join(keywords)}"
        query_embedding = model.encode(query, convert_to_tensor=True, normalize_embeddings=True)
        hits = util.semantic_search(query_embedding, embeddings, top_k=top_k)
        top_chunks = [chunks[hit["corpus_id"]] for hit in hits[0]]
    else:
        top_chunks = []

    lang = (output_language or detect_main_language(summary_main)).strip().lower()
    lang_map = {"fra": "fr", "eng": "en", "jpn": "ja", "chi_sim": "zh-cn", "chi_tra": "zh-tw"}
    lang = lang_map.get(lang, lang)

    if not style:
        style = {
            "fr": "pédagogique",
            "en": "educational",
            "ja": "教育的なスタイル",
            "zh-cn": "教育风格",
            "zh-tw": "教育風格"
        }.get(lang, "educational")

    if lang not in PROMPTS_RAG:
        lang = "fr"

    if backend == "local" and model_path and max_tokens is None:
        try:
            context_limit = get_context_limit_from_gguf(model_path)
            max_tokens = int(context_limit * 0.9)
        except Exception:
            max_tokens = 1024
    elif max_tokens is None:
        max_tokens = 1024

    prompt_template = PROMPTS_RAG[lang]["podcast_script"]
    top_chunks_str = "\n- " + "\n- ".join(top_chunks) if top_chunks else "(aucun chunk disponible)"
    context = {
        "style": style,
        "summary": summary_main,
        "top_chunks": top_chunks_str,
        "themes": ", ".join(themes),
        "keywords": ", ".join(keywords)
    }

    instructions = {
        "fr": "Rédige uniquement en français.",
        "en": "Write only in English.",
        "ja": "日本語で書いてください。",
        "zh-cn": "请只用中文撰写。",
        "zh-tw": "請只用繁體中文撰寫。"
    }
    lang_instruction = instructions.get(lang, "Write only in English.")

    def generate_part(label: str, extra: str = "") -> str:
        prompt = prompt_template.format(**context)
        if label == "intro":
            prompt += "\n\nGénère uniquement l'introduction."
        elif label == "outro":
            prompt += f"\n\nVoici les 4 parties précédentes :\n{extra}\n\nGénère uniquement l'OUTRO."
        else:
            prompt += f"\n\n{extra}\n\nGénère uniquement la PARTIE {label}."
        prompt += f"\n\n{lang_instruction}"
        return call_model(prompt, backend=backend, model_path=model_path, max_tokens=max_tokens)

    script = {"intro": "", "parts": [], "outro": ""}
    # Timers Start
    start_time = time.time()
    print(f"Début [Création] → INTRO: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    script["intro"] = generate_part("intro").strip()
    # Timers End
    end_time = time.time()
    elapsed = end_time - start_time
    print(f"Fin  [Création] → INTRO: {datetime.now().strftime('%Y-%m-%d %H:%M')} — Temps écoulé : {elapsed:.2f} secondes")

    for i in range(1, 5):
        # Timers Start
        start_time = time.time()
        print(f"[Création] → PARTIE {i}: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        previous = script["parts"][-1]["content"] if script["parts"] else ""
        part_raw = generate_part(str(i), extra=previous).strip()
        script["parts"].append({"title": f"{i}. Partie {i}", "content": part_raw})
        # Timers End
        end_time = time.time()
        elapsed = end_time - start_time
        print(f"Fin [Création] → PARTIE {i}: {datetime.now().strftime('%Y-%m-%d %H:%M')} — Temps écoulé : {elapsed:.2f} secondes")

    # Timers Start
    start_time = time.time()
    print(f"[Création] → OUTRO: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    all_parts_text = "\n\n".join(p["content"] for p in script["parts"])
    script["outro"] = generate_part("outro", extra=all_parts_text).strip()
    # Timers End
    end_time = time.time()
    elapsed = end_time - start_time
    print(f"Fin  [Création] → OUTRO: {datetime.now().strftime('%Y-%m-%d %H:%M')} — Temps écoulé : {elapsed:.2f} secondes")


    # Timers End
    end_time = time.time()
    elapsed = end_time - start_time
    print(f"Fin create_script_rag_modulaire: {datetime.now().strftime('%Y-%m-%d %H:%M')} — Temps écoulé : {elapsed:.2f} secondes")

    return script

def save_script_to_json(script: dict, folder: str, filename: str = None, lang: str = "fr") -> str:
    """
    Sauvegarde un script de podcast au format JSON dans le dossier spécifié.

    Args:
        script (dict): Script complet avec 'intro', 'parts' et 'outro'.
        folder (str): Dossier de destination.
        filename (str, optional): Nom du fichier JSON. Par défaut 'script_<lang>.json'.
        lang (str, optional): Langue du script, utilisée pour le nom de fichier si filename est None.

    Returns:
        str: Chemin complet vers le fichier JSON sauvegardé.

    Raises:
        ValueError: Si le script ne contient pas les clés requises ('intro', 'parts', 'outro').
    """

    expected_keys = {"intro", "parts", "outro"}
    if not expected_keys.issubset(script.keys()):
        raise ValueError("Script incomplet : doit contenir 'intro', 'parts', et 'outro'.")

    path = Path(folder)
    path.mkdir(parents=True, exist_ok=True)
    if filename is None:
        filename = f"script_{lang}.json"

    file_path = path / filename
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(script, f, indent=2, ensure_ascii=False)

    return str(file_path)

def load_script_from_json(file_path: str) -> dict:
    """
       Charge un script de podcast depuis un fichier JSON existant.

       Args:
           file_path (str): Chemin vers le fichier JSON à charger.

       Returns:
           dict: Dictionnaire représentant le script avec les clés 'intro', 'parts' et 'outro'.

       Raises:
           FileNotFoundError: Si le fichier n'existe pas.
           ValueError: Si le contenu du JSON est incomplet ou mal formé.
       """

    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Fichier non trouvé : {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    expected_keys = {"intro", "parts", "outro"}
    if not expected_keys.issubset(data.keys()):
        raise ValueError("Script JSON invalide : doit contenir 'intro', 'parts' et 'outro'.")

    return data

#Dialogue Exploitation

def initvoicematch():
    """
    Initialise et retourne un dictionnaire vide pour l'association personnage-voix.

    Returns:
        dict: Dictionnaire vide.
    """
    return {}

def voicematching(voicmatch, nomdialogue, nomvoix):
    """
    Ajoute un mappage (nomdialogue → nomvoix) dans le dictionnaire fourni.

    Args:
        voicmatch (dict): Dictionnaire à compléter.
        nomdialogue (str): Nom du personnage (format '[# Nom]')(Prend en charge les espaces.).
        nomvoix (str): Voix associée.
    """
    if nomdialogue.startswith("[#") and nomdialogue.endswith("]"):
        nomdialogue = nomdialogue[2:-1].strip()

    # Ajoute l'entrée dans le dictionnaire : clé = nomdialogue, valeur = nomvoix
    voicmatch[nomdialogue] = nomvoix

def voicematchingfiller(voicematch: dict, *args):
    """
    Remplit le dictionnaire de correspondance voix/personnage avec une liste d'arguments alternés.

    Args:
        voicematch (dict): Dictionnaire de correspondance.
        *args (str): Alternance nom, voix (doit être pair).

     Exemple:
        voicematch = {}
        voicematchingfiller(voicematch, "Alice", "fr_1", "Bob", "en_2")
        print(voicematch)
        {'Alice': 'fr_1', 'Bob': 'en_2'}

    Raises:
        ValueError: Si le nombre d'arguments n'est pas pair.
    """
    if len(args) % 2 != 0:
        raise ValueError("Error: The number of arguments must be even (expected key/value pairs).")

    for i in range(0, len(args), 2):
        key = args[i]
        value = args[i + 1]
        voicematch[key] = value

def extract_character_names_from_dialogue_file(path: str) -> list[str]:
    """
    Analyse un fichier de dialogue (formaté) et retourne une liste unique des noms de personnages détectés.

    Args:
        path (str): Chemin vers le fichier .txt

    Returns:
        list[str]: Liste sans doublon des noms de personnages
    """
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    _, dialogues = parse_dialogue_file(content)
    names = {bloc["name"] for bloc in dialogues}
    return sorted(names)


def normalizestring(dialogue: str) -> list[str]:
    """
    Coupe un texte en blocs de dialogue à chaque nouvelle réplique détectée par un tag [# ...].

    Args:
        dialogue (str): Le texte brut contenant plusieurs blocs balisés (formaté avec des [# ...]).

    Returns:
        list[str]: Liste des blocs de texte, chacun commençant par un tag [# ...].

    Remarques :
        - Utilise une regex en lookahead pour conserver les délimiteurs ([# ...]) dans chaque bloc.
        - Le premier bloc vide est ignoré si le fichier commence par [# ...].

    Exemple :
        >> normalizestring("[# Alice : calme : 1] Bonjour. [# Bob : neutre : 2] Salut.")
        → ['[# Alice : calme : 1] Bonjour. ', '[# Bob : neutre : 2] Salut.']
    """
    pattern = r'(?=\[#\s*[^]]+\])'  # Lookahead pour ne pas consommer le tag
    return re.split(pattern, dialogue)[1:]  # [1:] enlève le bloc vide au début si le texte commence par [#


def remplacer_nom_dialogue(contenu: str, ancien_nom: str, nouveau_nom: str) -> str:
    """
    Remplace tous les noms de personnage dans les balises [# ...] d'un fichier de dialogue.

    Args:
        contenu (str): Contenu brut du fichier (incluant header JSON et dialogues).
        ancien_nom (str): Nom à remplacer.
        nouveau_nom (str): Nom de remplacement.

    Returns:
        str: Contenu avec les noms remplacés.
    """
    pattern = re.compile(rf'(\[#\s*){re.escape(ancien_nom)}(\s*:\s*[^:\]]+\s*:\s*\d+\s*\])')
    return pattern.sub(rf'\1{nouveau_nom}\2', contenu)

def remplacer_et_sauver_fichier(source_path: str, ancien_nom: str, nouveau_nom: str) -> str:
    """
    Remplace les noms dans un fichier de dialogue et sauvegarde le nouveau fichier.

    Le nom du fichier généré garde le même nom de base avec suffixe horodaté.

    Args:
        source_path (str): Chemin du fichier .txt d’origine.
        ancien_nom (str): Nom d’origine à remplacer.
        nouveau_nom (str): Nouveau nom à insérer.

    Returns:
        str: Chemin complet du fichier sauvegardé.
    """
    with open(source_path, "r", encoding="utf-8") as f:
        original_content = f.read()

    modified_content = remplacer_nom_dialogue(original_content, ancien_nom, nouveau_nom)

    base_name = os.path.basename(source_path).replace(".txt", "")
    horodatage = datetime.now().strftime("%Y%m%d-%H%M%S")
    nouveau_nom_fichier = f"{base_name}__renamed__{horodatage}.txt"

    output_dir = os.path.dirname(source_path)
    return save_text_to_file(output_dir, nouveau_nom_fichier, modified_content)


def assign_voices_by_gender(names: list[str]) -> dict:
    """
    Associe à chaque personnage une voix en fonction du genre détecté du prénom.

    Args:
        names (list[str]): Liste des noms des personnages.

    Returns:
        dict: Dictionnaire {nom_personnage: voix_choisie}
    """
    import random
    from Podcast_Generator.PodcastGeneratorAudio import list_custom_male_voices, list_custom_female_voices
    import gender_guesser.detector as gender
    d = gender.Detector()
    male_voices = list_custom_male_voices()
    female_voices = list_custom_female_voices()

    if not male_voices or not female_voices:
        raise ValueError("Pas assez de voix disponibles par genre.")

    result = {}
    for name in names:
        prenom = name.split()[0]  # Prend le premier mot comme prénom
        g = d.get_gender(prenom)
        if g in ['male', 'mostly_male']:
            voice = random.choice(male_voices)
        elif g in ['female', 'mostly_female']:
            voice = random.choice(female_voices)
        else:
            voice = random.choice(male_voices + female_voices)
        result[name] = voice
    return result


def parse_dialogue_file(content: str) -> tuple[dict, list[dict]]:
    """
    Prend le contenu brut d’un fichier de script de podcast,
    et retourne un tuple avec deux éléments :

    Un dictionnaire `meta` représentant les métadonnées du script, extraites du bloc JSON en début de fichier.
        ➤ Exemple : {
              "titre": "Retour de l'IA",
              "auteur": "Jean Bot",
              "date": "2025-04-02"
          }

    Une liste `dialogues` de blocs de dialogues (list[dict]), chaque élément étant une réplique avec :
        - name (str)    : nom du personnage
        - tone (str)    : ton choisi (doit exister dans les presets)
        - index (int)   : numéro du dialogue (pour l’ordre)
        - text (str)    : le texte parlé

        ➤ Exemple d'un élément :
            {
                "name": "Alice Thomas Anderson",
                "tone": "intrigué",
                "index": 3,
                "text": "Alors... on va devoir agir."
            }

    Notes: les blocs sont volontairement retournés en désordre si non triés,
               à toi de les classer ensuite selon l’index si besoin !

    Exemple d'utilisation :
    ---------------------------------
    meta, dialogues = parse_dialogue_file(contenu)
    print(meta["titre"])            # → "Retour de l'IA"
    print(dialogues[0]["text"])     # → "Tu es sûr que ce fichier est réel ?"
    ---------------------------------

    Args:
        content (str): Contenu complet du fichier dialogue (avec {meta} + blocs de texte)

    Returns:
        tuple: (meta_dict, list_of_dialogue_blocks)
    """

    content = content.strip()
    header = {}

    # 1. Extraire l’en-tête JSON s’il existe
    if content.startswith("{"):
        end = content.find("}")
        header_raw = content[:end + 1]
        try:
            header = json.loads(header_raw)
        except json.JSONDecodeError:
            raise ValueError("En-tête mal formé.")
        content = content[end + 1:].strip()

    # 2. Normaliser le dialogue
    blocks = normalizestring(content)  # ta fonction existante pour couper par [#...]

    # 3. Parser chaque bloc
    parsed = []
    for block in blocks:
        parsed.append(parse_dialogue_block(block))

    return header, parsed


def parse_dialogue_block(block: str) -> dict:
    """
    Parse un seul bloc de dialogue écrit sous la forme :
    [# Nom : Ton : ID] Texte...

    Extrait :
        - name (str)  → nom de la personne (espaces autorisés)
        - tone (str)  → ton vocal (ex. "calme", "sérieux", etc.)
        - index (int) → position dans la séquence
        - text (str)  → contenu de la réplique

    Exemple d'entrée :
        "[# Bob : sérieux : 2] Aussi réel que toi et moi."

    Résultat :
        {
            "name": "Bob",
            "tone": "sérieux",
            "index": 2,
            "text": "Aussi réel que toi et moi."
        }

    Note : Lève une erreur explicite si le bloc n’est pas bien formaté.
    """
    pattern = r'^\[#\s*(.+?)\s*:\s*(.+?)\s*:\s*(\d+)\s*\](.+)$'
    match = re.match(pattern, block.strip())
    if not match:
        raise ValueError(f"Bloc mal formé : {block}")

    name, tone, index, text = match.groups()
    return {
        "name": name.strip(),
        "tone": tone.strip(),
        "index": int(index.strip()),
        "text": text.strip()
    }

def generate_discussion_from_file(
    path: str,
    participants: int,
    *args: str,
    dry_run: bool = False
):
    """
    Charge un fichier de dialogue formaté et génère les fichiers audio.

    Args:
        path (str): Chemin vers le fichier .txt contenant le dialogue
        participants (int): Nombre de personnages
        *args (str): Alternance nom, voix (ex: "Alice", "fr_1", "Bob", "fr_2")
        dry_run (bool): Si True, ne génère pas les fichiers mais retourne le contenu traité

    Returns:
        list[dict]: La liste des blocs de dialogue formatés
    """
    with open(path, "r", encoding="utf-8") as f:
        contenu = f.read()

    meta, blocs = parse_dialogue_file(contenu)

    if len(args) != participants * 2:
        print("[ℹ] Assignation automatique des voix par genre...")
        names = extract_character_names_from_dialogue_file(path)
        noms_voix = assign_voices_by_gender(names)
    else:
        noms_voix = {args[i]: args[i + 1] for i in range(0, len(args), 2)}

    if dry_run:
        return blocs

    from Podcast_Generator.PodcastGeneratorAudio import create_discussion
    create_discussion(meta, noms_voix, blocs, presentateur=list(noms_voix.values())[0])

    return blocs
