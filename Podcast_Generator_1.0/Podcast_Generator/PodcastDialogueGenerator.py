"""
PodcastDialogueGenerator.py
============================

Ce module gère la génération automatique de dialogues réalistes pour les podcasts,
à partir d'un script structuré.

Rôles :
- Générer un dialogue en plusieurs parties à partir d'un script
- Attribuer dynamiquement des prénoms aux participants
- Associer un ton réaliste à chaque réplique
- Générer un titre automatique pour le dialogue
- Sauvegarder le résultat au format texte balisé prêt pour la synthèse vocale
"""

import datetime

from Podcast_Generator.PodcastGeneratorAudio import GenerateAndMux, sanitize_filename
from Podcast_Generator.PodcastScriptGenerator import load_script_from_json, remplacer_et_sauver_fichier
from sentence_transformers import util, SentenceTransformer
import os
import re
import json
from pathlib import Path
from Podcast_Generator.LocalIAIManager import call_model
from Podcast_Generator.SystemEngine import save_text_to_file
from Podcast_Generator.TonePresetManager import load_tone_presets, list_all_tones
from faker import Faker
from Podcast_Generator.TextAnalyzer import summarize_with_meta_summary
from Podcast_Generator.PromptDialogueGenerator import PROMPTS_DIALOGUE, TITLE_PROMPTS
import time
from datetime import datetime

# === CONFIGURATION
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
model = SentenceTransformer(EMBEDDING_MODEL)
tone_presets = load_tone_presets()
tone_list = list(tone_presets.keys())
tone_embeddings = model.encode(tone_list, normalize_embeddings=True)

LANG_TO_LOCALE = {
    "fr": "fr_FR",
    "en": "en_US",
    "ja": "ja_JP",
    "zh-cn": "zh_CN",
    "zh-tw": "zh_TW"
}

def generate_participant_names(participants: int, lang: str = "fr", **kwargs) -> list[str]:
    """
    Génère une liste de prénoms uniques pour les participants, en respectant l'ordre d'insertion.

    Args:
        participants (int): Nombre de prénoms à générer.
        lang (str): Code langue pour Faker (ex: 'fr', 'en', 'ja', 'zh-cn', 'zh-tw').
        **kwargs: Arguments supplémentaires non utilisés directement ici.

    Returns:
        list[str]: Liste ordonnée de prénoms uniques.

    Remarques:
        - Si Faker ne peut pas générer suffisamment de prénoms uniques après 50 tentatives, la fonction renverra
          autant de prénoms uniques que possible.
    """
    locale = LANG_TO_LOCALE.get(lang.lower(), "fr_FR")
    fake = Faker(locale)

    noms = []
    tentatives = 0
    max_tentatives = 50

    while len(noms) < participants and tentatives < max_tentatives:
        prenom = fake.first_name()
        if prenom not in noms:
            noms.append(prenom)
        tentatives += 1

    if len(noms) < participants:
        print(f"Seuls {len(noms)} prénoms uniques ont pu être générés après {max_tentatives} tentatives.")

    return noms[:participants]

def resolve_best_tone(tone: str) -> str:
    """
    Trouve le ton le plus proche disponible en fonction d'un mot-clé fourni.

    Args:
        tone (str): Ton cible recherché (ex: "sérieux", "joyeux").

    Returns:
        str: Nom du ton existant le plus proche parmi les presets disponibles.
    """

    query = model.encode([tone], normalize_embeddings=True)
    scores = util.cos_sim(query, tone_embeddings)[0]
    return tone_list[int(scores.argmax())]

def _format_to_bracketed_lines(text: str) -> str:
    """
    Reformate un texte brut en blocs balisés au format [# Nom : Ton ] Texte.

    Args:
        text (str): Texte brut avec structure (Nom(Ton): Texte).

    Returns:
        str: Texte reformatté avec balises [# ...] pour chaque réplique.
    """

    lines = text.strip().splitlines()
    output = []
    for line in lines:
        match = re.match(r"^(\w+)(?:\(([^)]+)\))?\s*:\s*(.+)$", line)
        if match:
            name, tone, sentence = match.groups()
            name = name.strip()
            tone = tone.strip() if tone else "neutre"
            sentence = sentence.strip()
            output.append(f"[# {name} : {tone} ] {sentence}")
    return "\n".join(output)

def _add_indices_to_bracketed(text: str) -> str:
    """
    Ajoute un index numérique croissant à chaque bloc de dialogue balisé.

    Args:
        text (str): Texte contenant des balises [# Nom : Ton ].

    Returns:
        str: Texte enrichi où chaque bloc possède un index unique.
    """

    lines = text.strip().splitlines()
    count = 1
    output = []
    for line in lines:
        match = re.match(r"^(\[#\s*[^\]]+\])\s*(.+)$", line)
        if match:
            tag, sentence = match.groups()
            tag = tag.rstrip(' ]') + f" : {count}]"
            output.append(f"{tag} {sentence}")
            count += 1
    return "\n".join(output)

def generate_raw_dialogue(script_path: str, participants: int = 2, noms: list[str] = None, lang: str = "fr", backend: str = "server", model_path: str = None, output_dir: str = None, auteur: str = "PodcastGenerator") -> str:
    """
    Génère un fichier de dialogue brut à partir d'un script de podcast structuré.

    Args:
        script_path (str): Chemin vers le fichier de script JSON.
        participants (int, optional): Nombre de participants souhaités. Par défaut 2.
        noms (list[str], optional): Liste de noms à utiliser. Sinon génération automatique.
        lang (str): Code langue (ex: 'fr', 'en', 'ja', 'zh-cn', 'zh-tw').
        backend (str, optional): Mode d'appel du modèle ("server" ou "local"). Par défaut "server".
        model_path (str, optional): Chemin vers un modèle local si utilisé.
        output_dir (str, optional): Dossier de sauvegarde. Sinon utilise le dossier du script.
        auteur (str, optional): Auteur indiqué dans le header JSON. Par défaut "PodcastGenerator".

    Returns:
        str: Chemin absolu du fichier texte généré.

    Notes:
        - Génére une discussion complète en plusieurs parties basée sur le script.
        - Assigne des tons et des noms automatiquement aux répliques.
        - Génère un titre pour le dialogue final.
    """
    #Timers Start
    start_time = time.time()
    print(f"Début generate_raw_dialogue : {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    print("Chargement du script...")
    script = load_script_from_json(script_path)
    titre = Path(script_path).stem.replace("script_", "").replace("_", " ").strip().title()

    date_now = datetime.now().strftime("%Y-%m-%d")
    heure_now = datetime.now().strftime("%H-%M")
    filename = f"DialogueRaw__{titre.replace(' ', '_')}__{date_now}__{heure_now}__{lang}.txt"

    if output_dir is None:
        output_dir = os.path.dirname(script_path)
    os.makedirs(output_dir, exist_ok=True)

    if not noms or len(noms) < participants:
        print("Génération automatique des noms de personnages...")
        noms = noms or []
        noms_auto = generate_participant_names(participants, lang=lang)
        noms += [n for n in noms_auto if n not in noms][:participants - len(noms)]
    noms = noms[:participants] # To use the rightmost number of participants
    print(f"Personnages utilisés : {noms}")

    full_result = []
    context_resume = script.get("intro", "").strip()
    all_parts = script["parts"]
    total_parts = len(all_parts)

    for i, part in enumerate(all_parts):
        print("\n" + "="*40 + f" Partie {i+1} " + "="*40)
        title = part.get("title", f"Partie {i+1}")
        texte = part["content"].strip()
        print(f"Partie {i+1}/{total_parts} : {title}")

        # Timers Start
        start_time = time.time()
        print(f"Début Partie {title}: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

        resume_clean = summarize_with_meta_summary(context_resume, backend=backend, model_path=model_path)[0]

        prompt_template = PROMPTS_DIALOGUE.get(lang.lower(), PROMPTS_DIALOGUE["fr"])
        prompt = prompt_template.format(participants=", ".join(noms), context=resume_clean, text=texte)

        print("Envoi du prompt au modèle...")
        partie_result = call_model(prompt, backend=backend, model_path=model_path)
        print("Réponse du modèle :")
        print(partie_result[:500] + ("..." if len(partie_result) > 500 else ""))

        print("Dialogue généré pour cette partie :")
        print(partie_result.strip())
        full_result.append(partie_result.strip())
        context_resume += "\n" + partie_result.strip()
        if len(context_resume) > 3000:
            context_resume = context_resume[-3000:]
        # Timers End
        end_time = time.time()
        elapsed = end_time - start_time
        print(f"Fin Partie {title}: {datetime.now().strftime('%Y-%m-%d %H:%M')} — Temps écoulé : {elapsed:.2f} secondes")

    raw_text = "\n\n".join(full_result)
    step1 = _format_to_bracketed_lines(raw_text)
    final_text = _add_indices_to_bracketed(step1)

    titre_prompt_template = TITLE_PROMPTS.get(lang.lower(), TITLE_PROMPTS["fr"])
    titre_prompt = titre_prompt_template.format(text=final_text[:1500])
    titre = call_model(titre_prompt, backend=backend, model_path=model_path).splitlines()[0].strip().strip('"').strip()
    titre = re.sub(r'^(titre|title)\s*[:：-]*\s*', '', titre, flags=re.IGNORECASE)
    titre = sanitize_filename(titre).strip()

    header = {
        "titre": titre,
        "auteur": auteur,
        "date": date_now,
        "lang": lang
    }
    final_text = json.dumps(header, indent=2, ensure_ascii=False) + "\n\n" + final_text

    save_path = save_text_to_file(output_dir, filename, final_text)
    print(f"Dialogue généré et sauvegardé : {save_path}")

    # Timers End
    end_time = time.time()
    elapsed = end_time - start_time
    print(f"Fin generate_raw_dialogue: {datetime.now().strftime('%Y-%m-%d %H:%M')} — Temps écoulé : {elapsed:.2f} secondes")

    return save_path
