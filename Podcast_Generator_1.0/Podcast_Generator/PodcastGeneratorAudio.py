"""
PodcastGeneratorAudio.py
==========================

Module responsable de la génération vocale à partir des scripts de podcast.

Rôle :
- Convertir chaque réplique en audio à l’aide de XTTS (via `TTSWrapper`)
- Appliquer les paramètres de tonalité (vitesse, émotion) issus des presets
- Associer les voix aux personnages, lire le titre, et sauvegarder les fichiers
- Gérer la fusion finale des fichiers audio en un seul mix .wav

Structure :
- Fonctions internes (résolution de voix, découpage, etc.)
- Fonctions de génération (sentence, discussion complète)
- Outils audio (play, listage, fusion)
"""

import re
import warnings
from glob import glob

warnings.filterwarnings("ignore", category=FutureWarning)
import json
import string
import datetime
from datetime import datetime as dt

import os
from pathlib import Path

from Podcast_Generator.TTSWrapper import generate_audio
from pydub import AudioSegment
from pydub.playback import play

from Podcast_Generator.TTSWrapper import tts

from Podcast_Generator.TonePresetManager import load_tone_presets
from Podcast_Generator.PodcastScriptGenerator import parse_dialogue_file

from Podcast_Generator.PodcastScriptGenerator import extract_character_names_from_dialogue_file, assign_voices_by_gender
import random
import time
from datetime import datetime


# =========================
#   CONFIGURATION
# =========================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VOICE_DIR = os.path.join(BASE_DIR, "Voices")
PREVIEW_DIR = os.path.join(BASE_DIR, "VoicesPreview")
PRESET_FILE = os.path.join(os.path.dirname(__file__), "tone_presets.json")
MAX_LENGTH = 273
# Load tones
tone_presets = load_tone_presets()

def sanitize_filename(text):
    """
    Nettoie une chaîne de caractères pour l'utiliser comme nom de fichier.

    Args:
        text (str): Chaîne à nettoyer.

    Returns:
        str: Chaîne nettoyée sans caractères interdits.

    Remarque:
        Supprime les caractères incompatibles avec les systèmes de fichiers.
    """
    invalid_chars = '<>:"/\\|?*'
    return ''.join(c for c in text if c not in invalid_chars)


def _resolve_voice(voice: str, voice_dir: str = None) -> dict:
    """
    Résout dynamiquement une voix pour XTTS à partir de :
    - soit un nom de voix intégré au modèle XTTS (ex: "fr_1")
    - soit un fichier personnalisé .wav situé dans le dossier `voice_dir` (par défaut "Voices/")

    Args:
        voice (str): Nom logique (voix XTTS, ex: "fr_1") OU nom de fichier voix (ex: "Hanekawa.wav").
        voice_dir (str, optional): Dossier contenant les voix personnalisées (par défaut "Voices/").

    Returns:
        dict: Paramètre à passer dans XTTS :
              - {"speaker": <nom>} pour les voix intégrées
              - {"speaker_wav": <chemin>} pour un fichier personnalisé

    Raises:
        FileNotFoundError: Si un fichier .wav est précisé mais introuvable.
        ValueError: Si un nom XTTS inconnu est utilisé.

    Exemple:
        _resolve_voice("fr_1")
        >> {"speaker": "fr_1"}

        _resolve_voice("Hanekawa.wav")
        >> {"speaker_wav": "Voices/Hanekawa.wav"}

    Remarques:
        - Si l'argument se termine par .wav, on cherche un fichier.
        - Sinon, on vérifie s'il fait partie des voix intégrées du modèle.
        - La recherche du fichier est relative à `voice_dir`, ou au dossier par défaut "Voices/".
    """
    if voice_dir is None:
        voice_dir = VOICE_DIR

    voice_path = os.path.join(voice_dir, voice)

    if voice.lower().endswith(".wav"):
        if os.path.isfile(voice_path):
            return {"speaker_wav": voice_path}
        else:
            raise FileNotFoundError(f"Fichier voix introuvable : {voice_path}")

    available = get_available_speakers()
    if voice not in available:
        raise ValueError(f"Voix '{voice}' inconnue. Voix disponibles : {list(available)}")
    return {"speaker": voice}


def _split_text(text: str, max_len: int = MAX_LENGTH):
    """
    Découpe un texte trop long en segments courts compatibles XTTS.

    Args:
        text (str): Texte brut à découper.
        max_len (int): Longueur maximale par segment (limite XTTS).

    Returns:
        list[str]: Liste de segments courts prêts pour la synthèse.

    Remarque:
        Priorise la séparation par phrases, sinon coupe par mots.
        Essentiel, car XTTS couperait sinon de manière arbitraire.
    """
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    chunks = []
    for sentence in sentences:
        if len(sentence) <= max_len:
            chunks.append(sentence.strip())
        else:
            # Split par mots si la phrase est trop longue
            words = sentence.split()
            current = ""
            for word in words:
                if len(current) + len(word) + 1 <= max_len:
                    current += (" " + word) if current else word
                else:
                    chunks.append(current.strip())
                    current = word
            if current:
                chunks.append(current.strip())
    return chunks

def play_audio(file_path: str):
    """
    Lit un fichier audio localement (.wav) et affiche des messages de suivi.

    Args:
        file_path (str): Chemin vers le fichier à lire.

    Returns:
        None

    Raises:
        FileNotFoundError: Si le fichier n'existe pas.
        Exception: En cas d'erreur de lecture.

    Notes:
        - Affiche un message lors de la lecture et en cas d'erreur.
    """
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Le fichier n'existe pas : {file_path}")
        sound = AudioSegment.from_file(file_path)
        print(f"Lecture audio en cours : {file_path}")
        play(sound)
    except Exception as e:
        print(f"[ERREUR] Impossible de lire le fichier : {file_path}")
        print(f"[Exception] {e}")

def convert_wav_to_mp3(wav_path: str) -> str:
    """
    Convertit un fichier .wav en .mp3 dans le même dossier.

    Args:
        wav_path (str): Chemin vers le fichier .wav source.

    Returns:
        str: Chemin du fichier .mp3 généré.

    Raises:
        FileNotFoundError: Si le fichier d'entrée n'existe pas.
        ValueError: Si l'extension n'est pas .wav
    """
    source = Path(wav_path)
    if not source.exists():
        raise FileNotFoundError(f"Fichier introuvable : {wav_path}")
    if source.suffix.lower() != ".wav":
        raise ValueError("Le fichier doit être un .wav")

    mp3_path = source.with_suffix(".mp3")

    audio = AudioSegment.from_wav(source)
    audio.export(mp3_path, format="mp3")
    return str(mp3_path)

def convert_mp3_to_wav(mp3_path: str) -> str:
    """
    Convertit un fichier .mp3 en .wav dans le même dossier.

    Args:
        mp3_path (str): Chemin vers le fichier .mp3 source.

    Returns:
        str: Chemin du fichier .wav généré.

    Raises:
        FileNotFoundError: Si le fichier d'entrée n'existe pas.
        ValueError: Si l'extension n'est pas .mp3.
    """
    source = Path(mp3_path)
    if not source.exists():
        raise FileNotFoundError(f"Fichier introuvable : {mp3_path}")
    if source.suffix.lower() != ".mp3":
        raise ValueError("Le fichier doit être un .mp3")

    wav_path = source.with_suffix(".wav")

    audio = AudioSegment.from_mp3(source)
    audio.export(wav_path, format="wav")
    return str(wav_path)


# List of Voices
def get_available_speakers():
    """
    Liste les voix internes disponibles dans le modèle XTTS.

    Returns:
        list[str]: Noms des voix intégrées.
    """
    return list(tts.synthesizer.tts_model.speaker_manager.speakers.keys())

# Dossier contenant les voix personnalisées .wav

def list_custom_male_voices():
    """
    Liste les voix masculines personnalisées dans le dossier VoicesPreview/Male (sans extension .wav)

    Returns:
        list[str]: Noms de fichiers (sans extension).
    """
    male_dir = os.path.join(PREVIEW_DIR, "Male")
    return [os.path.splitext(f)[0] for f in os.listdir(male_dir) if f.lower().endswith(".wav")] if os.path.isdir(male_dir) else []

def list_custom_female_voices():
    """
    Liste les voix féminines personnalisées dans le dossier VoicesPreview/Female (sans extension .wav)

    Returns:
        list[str]: Noms de fichiers (sans extension).
    """
    female_dir = os.path.join(PREVIEW_DIR, "Female")
    return [os.path.splitext(f)[0] for f in os.listdir(female_dir) if f.lower().endswith(".wav")] if os.path.isdir(female_dir) else []


def list_custom_all_mf_voices():
    """
    Liste toutes les voix personnalisées dans Voices/Male + Voices/Female

    Returns:
        list[str]: Liste complète des voix personnalisées.
    """
    return list_custom_male_voices() + list_custom_female_voices()

def list_custom_raw_voices():
    """
    Liste les voix directement dans Voices/ (hors Male et Female)

    Returns:
        list[str]: Fichiers .wav présents à la racine de Voices/
    """
    raw_voices = []
    if os.path.isdir(VOICE_DIR):
        for f in os.listdir(VOICE_DIR):
            if f.lower().endswith(".wav") and not os.path.isdir(os.path.join(VOICE_DIR, f)):
                raw_voices.append(f)
    return raw_voices

def list_all_available_voices():
    """
    Retourne toutes les voix (customisées + intégrées).

    Returns:
        list[str]: Liste globale des voix disponibles.
    """

    all_custom = list_custom_all_mf_voices() + list_custom_raw_voices()
    builtin = list(get_available_speakers())
    return all_custom + builtin


#Sentence creations

def create_sentence(
    voice: str,
    ton: str,
    texte: str,
    language: str = "fr",
    output_path: str = "output",
    filename: str = "sentence.wav"
) -> str:
    """
    Génère un fichier audio (.wav) contenant une phrase vocalisée avec XTTS.

    Args:
        voice (str): Nom de la voix intégrée (ex: "fr_1") ou nom de fichier .wav personnalisé.
        ton (str): Nom du ton à utiliser (doit exister dans les presets sinon "neutre").
        texte (str): Texte à synthétiser.
        language (str, optional): Langue compatible XTTS. Par défaut : "fr".
            Langues supportées :
            - "fr" : français
            - "en" : anglais
            - "ja" : japonais
            - "zh-cn" : chinois simplifié
            - "zh-tw" : chinois traditionnel (Taïwan)
        output_path (str, optional): Dossier de sortie où sauvegarder l’audio.
        filename (str, optional): Nom du fichier à générer.

    Returns:
        str: Chemin complet vers le fichier audio généré.

    Remarques:
        - Si le texte dépasse la limite XTTS (273 caractères), il sera découpé automatiquement.
        - Tous les morceaux sont ensuite fusionnés en un seul fichier.

    Exemple:
        create_sentence("fr_1", "calme", "Bonjour, ceci est un test.")
    """
    os.makedirs(output_path, exist_ok=True)
    final_path = os.path.join(output_path, filename)

    # Utilise le preset du ton si reconnu, sinon neutre
    params = tone_presets.get(ton.lower(), {"speed": 1.0, "emotion": "neutral"})

    voice_resolved = _resolve_voice(voice)
    if "speaker_wav" in voice_resolved:
        voice_resolved.pop("speaker", None)
    else:
        voice_resolved.pop("speaker_wav", None)

    if len(texte) <= MAX_LENGTH:
        tts.tts_to_file(
            text=texte,
            file_path=final_path,
            language=language,
            emotion=params["emotion"],
            speed=params["speed"],
            **voice_resolved
        )
        return final_path

    # Si le texte est trop long → découpage et fusion
    parts = _split_text(texte)
    all_audio = AudioSegment.empty()

    for i, part in enumerate(parts):
        part_path = os.path.join(output_path, f"_part_{i}.wav")
        tts.tts_to_file(
            text=part,
            file_path=part_path,
            language=language,
            emotion=params["emotion"],
            speed=params["speed"],
            **voice_resolved
        )
        all_audio += AudioSegment.from_wav(part_path)
        os.remove(part_path)

    all_audio.export(final_path, format="wav")
    return final_path

def create_discussion(meta: dict, participants: dict, dialogues: list[dict], presentateur: str = None, output_base: str = None):
    """
    Génère tous les fichiers audio pour un script de podcast (titre + dialogues).

    Args:
        meta (dict): Métadonnées du podcast, avec au minimum 'titre', 'date' et 'lang'.
        participants (dict): Dictionnaire {nom_personnage: nom_voix}.
        dialogues (list[dict]): Liste de blocs avec : 'name', 'tone', 'index', 'text'.
        presentateur (str, optional): Voix utilisée pour lire le titre. Si None, voix aléatoire.
        output_base (str, optional): Dossier de destination. Si None, utilise le dossier du fichier source.

    Returns:
        str: Chemin absolu du dossier généré.
    """
    titre = meta.get("titre", "").strip() or "Podcast sans titre"
    date = meta.get("date", dt.today().date().isoformat())
    langue = meta.get("lang", "fr")

    titre_sanitized = sanitize_filename(titre).replace(" ", "_")
    heure_str = dt.now().strftime("%H%M%S")
    dossier_nom = f"{titre_sanitized}__{date}__{heure_str}"

    # Création du dossier cible (dans output_base si fourni, sinon à côté du fichier source)
    base_path = Path(output_base).resolve() if output_base else Path().resolve()
    folder_path = base_path / dossier_nom
    folder_path.mkdir(parents=True, exist_ok=True)

    # Choix du présentateur
    all_voices = list_all_available_voices()
    if not presentateur or presentateur not in all_voices:
        if not all_voices:
            raise ValueError("Aucune voix disponible pour le présentateur.")
        presentateur = random.choice(all_voices)
        print(f"Présentateur choisi aléatoirement : {presentateur}")

    # Intro : le titre
    titre_audio_path = folder_path / f"00__PRESENTATEUR__neutre__{date}.wav"
    print(f"Lecture du titre : « {titre} »")
    intro_path = create_sentence(presentateur, "neutre", titre, language=langue)
    os.rename(intro_path, titre_audio_path)

    max_index = len(dialogues)
    # Génération des répliques
    for bloc in dialogues:
        nom = bloc["name"]
        texte = bloc["text"]
        ton = bloc["tone"]
        index = bloc["index"]

        ton_final = ton if ton in tone_presets else "neutre"
        if nom not in participants:
            raise ValueError(f"[❌] Voix manquante pour le personnage : {nom}")
        voix = participants[nom]

        print(f"Génération [{index}/{max_index}:{nom}:{ton_final}]")

        nom_fichier = f"{str(index).zfill(2)}__{nom}__{ton_final}__{date}.wav"
        chemin_fichier = folder_path / nom_fichier

        audio_path = create_sentence(voix, ton_final, texte, language=langue)
        os.rename(audio_path, chemin_fichier)

    print(f"[✅] Discussion complète générée dans le dossier : {folder_path}")
    return str(folder_path)



def muxgenerateddiscussion(files: list[str], output_path: str, output_name: str = None) -> str:
    """
    Assemble les fichiers audio .wav dans l'ordre donné (alphabétique pré-trié) en un seul fichier .wav

    Args:
        files (list[str]): Liste des chemins de fichiers .wav à assembler
        output_path (str): Dossier contenant les fichiers à assembler (le mix final ira dans un sous-dossier 'Mix')
        output_name (str, optional): Nom du fichier final. Si None, utilise 'FINAL - <nom dossier>.wav'.

   Returns:
        str: Chemin absolu du fichier final généré.

    Raises:
        FileNotFoundError: Si un fichier listé est introuvable.

    Exemple:
        muxgenerateddiscussion(["01.wav", "02.wav"], "Episode_1")
    """
    if not files:
        raise ValueError("Aucun fichier à assembler fourni.")

        # Création du sous-dossier 'Mix' dans le dossier d'entrée
    mix_dir = os.path.join(output_path, "Mix")
    os.makedirs(mix_dir, exist_ok=True)

    # Nom de sortie par défaut : 'FINAL - <nom du dossier>.wav'
    if output_name is None:
        base_name = os.path.basename(os.path.normpath(output_path))
        output_name = f"FINAL - {base_name}.wav"

    # Chargement et assemblage
    combined = AudioSegment.silent(duration=0)
    for file in sorted(files):
        if not os.path.exists(file):
            raise FileNotFoundError(f"Fichier manquant : {file}")
        segment = AudioSegment.from_wav(file)
        combined += segment

    output_file = os.path.join(mix_dir, output_name)
    combined.export(output_file, format="wav")

    return output_file


def GenerateAndMux(full_dialogue_path: str, participants: dict = None, presentateur: str = None, output_base: str = None) -> str:
    """
    Génère un podcast audio complet depuis un fichier dialogue, puis assemble tous les fichiers audio.

    Args:
        full_dialogue_path (str): Fichier .txt contenant les dialogues formatés.
        participants (dict, optional): Dictionnaire {personnage: voix}. Si None, détection automatique.
        presentateur (str, optional): Voix du titre (présentateur). Si None, aléatoire.
        output_base (str, optional): Dossier de destination pour les fichiers générés.
                                     Si None, on utilise le dossier de full_dialogue_path.

    Returns:
        str: Chemin du fichier audio final mixé (.wav).
    """
    # Timers Start
    start_time = time.time()
    print(f"Début GenerateAndMux: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    with open(full_dialogue_path, "r", encoding="utf-8") as f:
        content = f.read()
    meta, dialogues = parse_dialogue_file(content)

    if participants is None:
        names = extract_character_names_from_dialogue_file(full_dialogue_path)
        participants = assign_voices_by_gender(names)

    # Si output_base est None → on prend le dossier du fichier de dialogue
    if output_base is None:
        output_base = str(Path(full_dialogue_path).resolve().parent)

    folder_path = create_discussion(meta, participants, dialogues, presentateur, output_base)
    folder_path = Path(folder_path)

    wavs = sorted(str(file) for file in folder_path.glob("*.wav"))
    if not wavs:
        raise ValueError("Aucun fichier à assembler fourni.")

    final_mix_path = muxgenerateddiscussion(
        files=wavs,
        output_path=str(folder_path)
    )

    # Timers End
    end_time = time.time()
    elapsed = end_time - start_time
    print(f"Fin GenerateAndMux: {datetime.now().strftime('%Y-%m-%d %H:%M')} — Temps écoulé : {elapsed:.2f} secondes")

    return final_mix_path
