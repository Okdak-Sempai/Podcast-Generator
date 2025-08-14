"""
TTSWrapper.py
=============

Ce module encapsule l’utilisation du modèle XTTS-v2 (Coqui TTS) pour la synthèse vocale.

Rôle :
- Centraliser le chargement unique du modèle `TTS` via l’objet `tts`.
- Exposer une fonction `generate_audio(...)` pour générer un fichier audio à partir d’un texte.

Ce fichier existe aussi pour éviter les imports circulaires entre modules
qui utilisent à la fois `tts`, `create_sentence`, et `generate_audio`.
"""

import os
from TTS.api import TTS
from pydub import AudioSegment
from pydub.playback import play

# Initialisation du modèle XTTS
TTS_MODEL = "tts_models/multilingual/multi-dataset/xtts_v2"
tts = TTS(TTS_MODEL)

def play_audio(file_path: str):
    """
       Joue un fichier audio localement (debug/preview).

       Args:
           file_path (str): Chemin vers un fichier .wav

       Returns:
           None
       """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Fichier introuvable : {file_path}")
    sound = AudioSegment.from_file(file_path)
    play(sound)

def generate_audio(text: str, file_path: str, language: str, speed: float, emotion: str, voice_config: dict):
    """
     Génère un fichier audio à partir d'un texte via XTTS.

     Args:
         text (str): Le texte à synthétiser.
         file_path (str): Chemin de sauvegarde du fichier .wav.
         language (str): Code langue compatible XTTS :
                         - "fr" (français)
                         - "en" (anglais)
                         - "zh-cn" (chinois simplifié)
                         - "zh-tw" (chinois traditionnel)
                         - "ja" (japonais)
         speed (float): Vitesse de lecture (typiquement entre 0.5 et 2.0).
         emotion (str): Ton émotionnel à utiliser (doit exister dans `tone_presets.json`).
         voice_config (dict): Paramètres voix (par ex. {"speaker": "Nom"} ou {"speaker_wav": chemin_wav}).

     Returns:
         None
     """
    tts.tts_to_file(
        text=text,
        file_path=file_path,
        language=language,
        emotion=emotion,
        speed=speed,
        **voice_config
    )
