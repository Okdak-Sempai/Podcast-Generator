"""
TonePresetManager.py
=====================

Ce module gère la manipulation des presets de tons utilisés pour la synthèse vocale dans le projet Podcast Generator.
Il a été séparé de `PodcastGeneratorAudio.py` pour :
- éviter les dépendances circulaires entre modules,
- permettre une gestion autonome, simple et modulaire des tons vocaux.

Il permet de :
- Charger, sauvegarder et lister les presets définis dans un fichier JSON (`tone_presets.json`)
- Ajouter, supprimer et prévisualiser dynamiquement un ton
- Faciliter les tests et ajustements des paramètres vocaux via la fonction `preview_tone`

Les presets sont utilisés pour définir la vitesse (`speed`) et l’émotion (`emotion`) dans les appels au modèle XTTS v2 (Coqui).
"""

import json
import os
from pathlib import Path

TONE_PRESET_PATH = Path(__file__).resolve().parent / "tone_presets.json"

def load_tone_presets(path: Path = TONE_PRESET_PATH) -> dict:
    """
    Charge les presets de tons à partir du fichier JSON spécifié.

    Args:
        path (Path): Chemin vers le fichier JSON (optionnel). Par défaut : tone_presets.json dans le dossier courant.

    Returns:
        dict: Dictionnaire contenant les presets de tons au format {nom: {"speed": float, "emotion": str}}

    Exemple :
        load_tone_presets()["calme"]
        {'speed': 0.95, 'emotion': 'neutral'}
    """
    if not os.path.exists(TONE_PRESET_PATH):
        return {}
    with open(TONE_PRESET_PATH, "r", encoding="utf-8") as f:
        return json.load(f)
tone_presets = load_tone_presets()


def save_tone_presets(presets: dict):
    """
    Sauvegarde les presets de tons dans le fichier JSON.

    Args:
        presets (dict): Dictionnaire contenant tous les presets à écrire.

    Returns:
        None
    """
    with open(TONE_PRESET_PATH, "w", encoding="utf-8") as f:
        json.dump(presets, f, indent=4, ensure_ascii=False)

def add_tone_preset(name: str, speed: float, emotion: str):
    """
    Ajoute un nouveau ton ou modifie un ton existant.

    Si le ton existe déjà, il est mis à jour avec les nouvelles valeurs.
    Un message affiche l'ancien et le nouveau preset pour vérification.

    Args:
        name (str): Nom du ton à ajouter ou modifier (ex: "sérieux")
        speed (float): Vitesse de lecture (ex: 1.0). Doit être entre 0.5 et 2.0.
        emotion (str): Émotion vocale (ex: "happy", "sad", "neutral", "angry").
                       Doit correspondre aux valeurs supportées par XTTS.

    Returns:
        None

    Exemple :
        add_tone_preset("intense", 1.2, "angry")

    Remarques :
        - Si le ton est nouveau, il sera ajouté sans message particulier.
        - Si le ton existe déjà, un message affichera sa modification :
            [Remplacement] 'intense' : {'speed': 1.0, 'emotion': 'angry'} → {'speed': 1.2, 'emotion': 'angry'}
    """
    presets = load_tone_presets()
    new_values = {"speed": speed, "emotion": emotion}
    if name in presets:
        old_values = presets[name]
        print(f"[Remplacement] '{name}' : {old_values} → {new_values}")
    else:
        print(f"[Ajout] Nouveau preset ajouté : '{name}' → {new_values}")
    presets[name] = new_values
    save_tone_presets(presets)


def remove_tone_preset(name: str) -> bool:
    """
    Supprime un ton existant du fichier de presets.

    Args:
        name (str): Nom du ton à supprimer.

    Returns:
        bool: True si suppression réussie, False si le ton n'existait pas.

    Exemple :
        remove_tone_preset("intense")
        True
    """
    presets = load_tone_presets()
    if name in presets:
        del presets[name]
        save_tone_presets(presets)
        return True
    return False

def list_all_tones() -> list[str]:
    """
    Retourne tous les noms de tons disponibles.

    Returns:
        list[str]: Liste des clés définies dans le fichier tone_presets.json

    Exemple :
        list_all_tones()
        ['neutre', 'calme', 'posé', ...]
    """
    return list(load_tone_presets().keys())

def preview_tone(ton: str, voice: str = "fr_1", text: str = "Voici un exemple de test."):
    """
    Génère une preview audio d’un ton spécifique avec une voix donnée.

    Args:
        ton (str): Nom du ton à tester (doit exister dans les presets, sinon fallback 'neutre')
        voice (str): Nom de la voix ou fichier .wav (par défaut: "fr_1")
        text (str): Texte à vocaliser (par défaut : phrase de test en français)

    Notes:
        - Crée un fichier `preview_<ton>.wav` dans VoicesPreview/
        - Joue l’audio automatiquement

    Exemple :
        preview_tone("dramatique", "Hanekawa.wav", "Je suis fatigué.")
    """
    output_path = "VoicesPreview"
    filename = f"preview_{ton}.wav"
    os.makedirs(output_path, exist_ok=True)

    voice_config = _resolve_voice(voice)
    params = tone_presets.get(ton.lower(), {"speed": 1.0, "emotion": "neutral"})

    filepath = os.path.join(output_path, filename)
    generate_audio(
        text=text,
        file_path=filepath,
        language="fr",
        speed=params["speed"],
        emotion=params["emotion"],
        voice_config=voice_config
    )
    play_audio(filepath)