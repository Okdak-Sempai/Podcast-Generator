import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import json

from PromptDialogueGenerator import PROMPTS_DIALOGUE
from pathlib import Path
from SourceImporter import extract_file_handler
from Podcast_Generator.TextAnalyzer import summarize_with_meta_summary, extract_concepts, save_list_to_json
from Podcast_Generator.PodcastScriptGenerator import create_script_rag_modulaire, save_script_to_json
from Podcast_Generator.PodcastDialogueGenerator import generate_raw_dialogue
from Podcast_Generator.PodcastGeneratorAudio import GenerateAndMux
from Podcast_Generator.TonePresetManager import list_all_tones


def choisir_langue() -> str:
    langues_disponibles = list(PROMPTS_DIALOGUE.keys())
    while True:
        print("Langues supportées :")
        for idx, code in enumerate(langues_disponibles, 1):
            print(f"{idx}. {code}")
        choix = input("Choisissez une langue (entrez le numéro) : ")
        try:
            idx = int(choix) - 1
            if 0 <= idx < len(langues_disponibles):
                return langues_disponibles[idx]
        except ValueError:
            pass
        print("Choix invalide. Veuillez réessayer.")


def choisir_mode_execution() -> str:
    while True:
        print("\nMode d'exécution :")
        print("1. Automatique (pipeline complet)")
        print("2. Manuel")
        choix = input("Choisissez un mode (1 ou 2) : ")
        if choix == "1":
            return "auto"
        elif choix == "2":
            return "manuel"
        print("Choix invalide. Veuillez entrer 1 ou 2.")

def demander_auteur() -> str:
    while True:
        auteur = input("Entrez le nom de l'auteur du podcast : ").strip()
        if auteur:
            return auteur
        print("Le nom de l'auteur ne peut pas être vide. Veuillez réessayer.")

def charger_resume_principal_depuis_json(path: str) -> str:
    """
    Charge le résumé principal depuis un fichier summary.json.

    Args:
        path (str): Chemin vers le fichier summary.json

    Returns:
        str: Le résumé principal (summary[0])

    Raises:
        Exception: Si le fichier est invalide ou mal formé
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list) or not data:
            raise ValueError("Le fichier ne contient pas de liste valide.")
        return data[0]
    except Exception as e:
        raise RuntimeError(f"Erreur lors du chargement du résumé : {e}")


def lancer_pipeline_complet(lang: str, auteur: str):
    print("\n--- Lancement du pipeline automatique [Temps éstimé: 1h40] ---\n")

    # 1. Source du texte
    path = input("Entrez le chemin de la source (.pdf, .docx, .txt, .md...) : ").strip()
    texte = extract_file_handler(path)

    if not texte:
        print("[ERREUR] Texte introuvable ou vide.")
        return

    # 2. Résumé + Concepts
    print("Résumé avec méta-analyse...")
    text_summaries = summarize_with_meta_summary(texte, output_language=lang)

    print("Extraction des mots-clés...")
    keywords = extract_concepts(text_summaries[0], mode="keywords", output_language=lang)

    print("Extraction des thèmes...")
    themes = extract_concepts(text_summaries[0], mode="themes", output_language=lang)

    # 3. Sauvegarde des fichiers
    summary_path = save_list_to_json(text_summaries, suffix="summary")
    save_list_to_json(keywords, suffix="keywords")
    save_list_to_json(themes, suffix="themes")

    folder = str(Path(summary_path).parent)
    print(f"Dossier de travail : {folder}")

    # 4. Génération du script
    print("Génération du script de podcast...")
    script = create_script_rag_modulaire(folder_path=folder, output_language=lang)
    script_path = save_script_to_json(script, folder, lang=lang)

    # 5. Génération du dialogue
    print("Génération des dialogues...")
    dialogue_path = generate_raw_dialogue(script_path, lang=lang, auteur=auteur)

    # 6. Synthèse audio
    print("Synthèse et assemblage final...")
    GenerateAndMux(dialogue_path)

    print("\nPipeline terminé avec succès.")


def menu_voix():
    from Podcast_Generator.PodcastGeneratorAudio import (
        get_available_speakers,
        list_custom_male_voices,
        list_custom_female_voices,
        list_custom_all_mf_voices,
        list_custom_raw_voices,
        list_all_available_voices
    )

    while True:
        print("\n--- Gestion des voix ---")
        print("1. Voix intégrées (XTTS)")
        print("2. Voix personnalisées masculines")
        print("3. Voix personnalisées féminines")
        print("4. Voix personnalisées toutes (Male + Female)")
        print("5. Voix brutes (racine Voices/)")
        print("6. Toutes les voix disponibles")
        print("7. Retour")

        choix = input("Choix : ").strip()

        if choix == "1":
            voix = get_available_speakers()
        elif choix == "2":
            voix = list_custom_male_voices()
        elif choix == "3":
            voix = list_custom_female_voices()
        elif choix == "4":
            voix = list_custom_all_mf_voices()
        elif choix == "5":
            voix = list_custom_raw_voices()
        elif choix == "6":
            voix = list_all_available_voices()
        elif choix == "7":
            break
        else:
            print("Choix invalide.")
            continue

        print("Voix disponibles :", ", ".join(voix) if voix else "[Aucune voix trouvée]")


def menu_etapes_pipeline(langue_globale: str):
    from Podcast_Generator.SourceImporter import extract_file_handler
    from Podcast_Generator.TextAnalyzer import summarize_with_meta_summary, extract_concepts, save_list_to_json
    from Podcast_Generator.PodcastScriptGenerator import create_script_rag_modulaire, save_script_to_json,generate_discussion_from_file
    from Podcast_Generator.PodcastDialogueGenerator import generate_raw_dialogue
    from Podcast_Generator.PodcastGeneratorAudio import GenerateAndMux, create_sentence, muxgenerateddiscussion
    from Podcast_Generator.PodcastScriptGenerator import (
        voicematching, voicematchingfiller, extract_character_names_from_dialogue_file, remplacer_et_sauver_fichier
    )

    current_lang = langue_globale
    voicematch = {}

    while True:
        print(f"\n--- Menu Génération par Étapes (Langue actuelle : {current_lang}) ---")
        print("1. Extraire du texte (fichier ou URL)")
        print("2. Générer un résumé à partir d’un fichier")
        print("3. Extraire les mots-clés à partir d’un fichier Resumé")
        print("4. Extraire les thèmes à partir d’un fichier Resumé")
        print("5. Effectuer Résumé + Mots-clés + Thèmes à la suite")
        print("6. Générer un script de podcast (depuis dossier JSON)(Necessite soit l'utilisation de l'option 5 soit un rassemblement manuel des 3 fichiers dans le même dossier)")
        print("7. Générer un dialogue à partir d’un script")
        print("8. Générer une discussion complète depuis un fichier dialogue")
        print("9. Générer une phrase simple (create_sentence)")
        print("10. Générer un podcast complet, en plusieurs fichiers vocaux (create_discussion)")
        print("11. Fusionner les fichiers vocaux en 1 (muxgenerateddiscussion)")
        print("12. Générer le podcast vocal (à partir d’un fichier dialogue)")
        print("13. Changer de langue")
        print("14. Retour")

        choix = input("Choix : ").strip()

        if choix == "1":
            path = input("Chemin vers la source : ").strip().strip('"')
            texte = extract_file_handler(path)
            if texte:
                print("[OK] Texte extrait :")
                print(texte)
            else:
                print("[ERREUR] Échec de l'extraction.")

        elif choix == "2":
            path = input("Chemin vers la source pour le résumé : ").strip().strip('"')
            texte = extract_file_handler(path)
            if not texte:
                print("[ERREUR] Impossible d'extraire le texte.")
                continue
            try:
                summaries = summarize_with_meta_summary(texte, output_language=current_lang)
                path_saved = save_list_to_json(summaries, suffix="summary")
                print(f"[OK] Résumé sauvegardé : {path_saved}")
            except Exception as e:
                print(f"[ERREUR] Échec du résumé : {e}")

        elif choix == "3":
            path = input("Chemin vers un fichier texte pour extraire les mots-clés : ").strip().strip('"')
            texte = charger_resume_principal_depuis_json(path)
            if not texte:
                print("[ERREUR] Impossible d'extraire le texte.")
                continue
            try:
                keywords = extract_concepts(texte, mode="keywords", output_language=current_lang)
                path_saved = save_list_to_json(keywords, suffix="keywords")
                print(f"[OK] Mots-clés sauvegardés : {path_saved}")
            except Exception as e:
                print(f"[ERREUR] Échec de l'extraction : {e}")

        elif choix == "4":
            path = input("Chemin vers un fichier texte pour extraire les thèmes : ").strip().strip('"')
            texte = charger_resume_principal_depuis_json(path)
            if not texte:
                print("[ERREUR] Impossible d'extraire le texte.")
                continue
            try:
                themes = extract_concepts(texte, mode="themes", output_language=current_lang)
                path_saved = save_list_to_json(themes, suffix="themes")
                print(f"[OK] Thèmes sauvegardés : {path_saved}")
            except Exception as e:
                print(f"[ERREUR] Échec de l'extraction : {e}")

        elif choix == "5":
            path = input("Chemin vers un fichier source à résumer : ").strip().strip('"')
            texte = extract_file_handler(path)
            if not texte:
                print("[ERREUR] Impossible d'extraire le texte.")
                continue
            try:
                summaries = summarize_with_meta_summary(texte, output_language=current_lang)
                path_summary = save_list_to_json(summaries, suffix="summary")
                keywords = extract_concepts(summaries[0], mode="keywords", output_language=current_lang)
                save_list_to_json(keywords, suffix="keywords", path=Path(path_summary).parent)
                themes = extract_concepts(summaries[0], mode="themes", output_language=current_lang)
                save_list_to_json(themes, suffix="themes", path=Path(path_summary).parent)
                print(f"[OK] Résumé, mots-clés et thèmes générés dans : {Path(path_summary).parent}")
            except Exception as e:
                print(f"[ERREUR] Une erreur est survenue : {e}")

        elif choix == "6":
            dossier = input("Chemin du dossier contenant les fichiers summary/keywords/themes : ").strip().strip('"')
            try:
                script = create_script_rag_modulaire(folder_path=dossier, output_language=current_lang)
                script_path = save_script_to_json(script, folder=dossier, lang=current_lang)
                print(f"[OK] Script sauvegardé dans : {script_path}")
            except Exception as e:
                print(f"[ERREUR] Échec de la génération du script : {e}")

        elif choix == "7":
            path_script = input("Chemin vers le fichier script JSON : ").strip().strip('"')
            auteur = input("Nom de l'auteur à inclure dans les métadonnées : ").strip()
            try:
                dialogue_path = generate_raw_dialogue(path_script, lang=current_lang, auteur=auteur)
                print(f"[OK] Dialogue généré dans : {dialogue_path}")
            except Exception as e:
                print(f"[ERREUR] Échec de la génération du dialogue : {e}")


        elif choix == "8":
            from Podcast_Generator.PodcastGeneratorAudio import list_all_available_voices
            from Podcast_Generator.PodcastScriptGenerator import extract_character_names_from_dialogue_file

            fichier = input("Fichier dialogue formaté à utiliser : ").strip().strip('"')
            names = extract_character_names_from_dialogue_file(fichier)
            nb_pers = len(names)

            print(f"[INFO] {nb_pers} personnages détectés :")
            for name in names:
                print(" -", name)

            print("\nVoix disponibles :", ", ".join(list_all_available_voices()))

            print("\nVeuillez entrer les voix pour chaque personnage dans ce format :")
            print("Nom1 Voix1 Nom2 Voix2 ...")
            print("Exemple : Joséphine fr_1 Louise Hanekawa.wav")

            args = input("Entrée : ").split()
            generate_discussion_from_file(fichier, nb_pers, *args)

        elif choix == "9":
            from Podcast_Generator.PodcastGeneratorAudio import list_all_available_voices
            from Podcast_Generator.TonePresetManager import list_all_tones
            voice = input(f"Voix ({', '.join(list_all_available_voices())}) : ").strip()
            ton = input(f"Ton ({', '.join(list_all_tones())}) : ").strip()
            texte = input("Texte à vocaliser : ").strip()
            result = create_sentence(voice, ton, texte, language=current_lang)
            print(f"[OK] Fichier audio généré : {result}")

        elif choix == "10":
            print("--- Dialogue Edit ---")
            while True:
                print("a. Associer une voix (voicematching)")
                print("b. Remplir plusieurs associations (voicematchingfiller)")
                print("c. Extraire les noms de personnages")
                print("d. Remplacer un nom dans un fichier de dialogue")
                print("e. Lancer create_discussion avec voix associées")
                print("f. Retour")
                sous_choix = input("Choix : ").strip().lower()
                if sous_choix == "a":
                    nom = input("Nom personnage : ").strip()
                    voix = input("Voix associée : ").strip()
                    voicematching(voicematch, nom, voix)
                elif sous_choix == "b":
                    args = input("Paires nom/voix séparées par espace : ").split()
                    voicematchingfiller(voicematch, *args)
                elif sous_choix == "c":
                    path = input("Chemin fichier dialogue : ").strip().strip('"')
                    noms = extract_character_names_from_dialogue_file(path)
                    print("Noms extraits :", ", ".join(noms))
                elif sous_choix == "d":
                    fichier = input("Fichier source : ").strip().strip('"')
                    old = input("Nom à remplacer : ").strip()
                    new = input("Nouveau nom : ").strip()
                    out = remplacer_et_sauver_fichier(fichier, old, new)
                    print(f"[OK] Fichier modifié sauvegardé : {out}")
                elif sous_choix == "e":
                    path = input("Chemin vers le fichier dialogue : ").strip().strip('"')
                    from Podcast_Generator.PodcastGeneratorAudio import create_discussion
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                    from Podcast_Generator.PodcastScriptGenerator import parse_dialogue_file
                    meta, dialogues = parse_dialogue_file(content)
                    create_discussion(meta, voicematch, dialogues)
                    print("[OK] Discussion générée avec create_discussion.")
                elif sous_choix == "f":
                    break
                else:
                    print("Choix invalide.")

        elif choix == "11":
            dossier = input("Dossier contenant les .wav : ").strip().strip('"')
            fichiers = sorted(str(f) for f in Path(dossier).glob("*.wav"))
            if not fichiers:
                print("[ERREUR] Aucun .wav trouvé.")
                continue
            result = muxgenerateddiscussion(fichiers, output_path=dossier)
            print(f"[OK] Fichier final : {result}")

        elif choix == "12":
            path_dialogue = input("Chemin vers le fichier .txt de dialogue : ").strip().strip('"')
            try:
                result = GenerateAndMux(path_dialogue)
                print(f"[OK] Fichier audio final généré : {result}")
            except Exception as e:
                print(f"[ERREUR] Échec de la génération audio : {e}")

        elif choix == "13":
            from PromptDialogueGenerator import PROMPTS_DIALOGUE
            langues_disponibles = list(PROMPTS_DIALOGUE.keys())
            print("Langues disponibles :")
            for idx, code in enumerate(langues_disponibles, 1):
                print(f"{idx}. {code}")
            choix_langue = input("Choisissez une nouvelle langue (numéro) : ")
            try:
                idx = int(choix_langue) - 1
                if 0 <= idx < len(langues_disponibles):
                    current_lang = langues_disponibles[idx]
                    print(f"[OK] Langue changée : {current_lang}")
                else:
                    print("Indice hors limites.")
            except ValueError:
                print("Entrée invalide.")

        elif choix == "14":
            break
        else:
            print("Choix invalide. Veuillez entrer un numéro valide.")


def menu_manuel(langue: str):
    while True:
        print("\n=== Menu Manuel ===")
        print("1. Tone Manager")
        print("2. Envoyer une requête au modèle")
        print("3. Convertir un fichier audio (wav/mp3)")
        print("4. Gestion des voix")
        print("5. Génération de podcast par étapes (menu avancé)")
        print("6. Quitter")

        choix = input("Choisissez une option (1 à 6) : ").strip()

        if choix == "1":
            menu_tone_manager()
        elif choix == "2":
            envoyer_requete_modele()
        elif choix == "3":
            menu_conversion_audio()
        elif choix == "4":
            menu_voix()
        elif choix == "5":
            menu_etapes_pipeline(langue_globale=langue)
        elif choix == "6":
            print("Fin du mode manuel.")
            break
        else:
            print("Choix invalide. Veuillez entrer un numéro entre 1 et 6.")



def menu_tone_manager():
    from Podcast_Generator.TonePresetManager import (
        add_tone_preset,
        remove_tone_preset,
        list_all_tones,
        preview_tone
    )
    from Podcast_Generator.PodcastDialogueGenerator import resolve_best_tone
    while True:
        print("\n--- Tone Manager ---")
        print("1. Lister tous les tons")
        print("2. Ajouter ou modifier un ton")
        print("3. Supprimer un ton")
        print("5. Trouver le ton le plus proche")
        print("6. Retour")

        choix = input("Choix : ").strip()

        if choix == "1":
            tons = list_all_tones()
            print("Tons disponibles :", ", ".join(tons))
        elif choix == "2":
            nom = input("Nom du ton : ").strip()
            speed = float(input("Vitesse (0.5 à 2.0) : "))
            emotion = input("Émotion (neutral, happy, sad, angry) : ").strip()
            add_tone_preset(nom, speed, emotion)
        elif choix == "3":
            nom = input("Nom du ton à supprimer : ").strip()
            if remove_tone_preset(nom):
                print(f"Ton '{nom}' supprimé.")
            else:
                print("Ton non trouvé.")
        elif choix == "4":
            ton = input("Nom recherché : ").strip()
            result = resolve_best_tone(ton)
            print(f"Ton le plus proche : {result}")
        elif choix == "5":
            break
        else:
            print("Choix invalide.")


def envoyer_requete_modele():
    from Podcast_Generator.LocalIAIManager import call_model
    prompt = input("Prompt à envoyer au modèle : ")
    print("Réponse du modèle :")
    print(call_model(prompt, backend="server"))


def menu_conversion_audio():
    from Podcast_Generator.PodcastGeneratorAudio import convert_wav_to_mp3, convert_mp3_to_wav
    print("\n--- Conversion audio ---")
    print("1. WAV → MP3")
    print("2. MP3 → WAV")
    choix = input("Choix : ").strip()

    try:
        if choix == "1":
            path = input("Chemin vers le fichier .wav : ").strip().strip('"')
            result = convert_wav_to_mp3(path)
            print(f"[OK] Fichier MP3 généré : {result}")
        elif choix == "2":
            path = input("Chemin vers le fichier .mp3 : ").strip().strip('"')
            result = convert_mp3_to_wav(path)
            print(f"[OK] Fichier WAV généré : {result}")
        else:
            print("Choix invalide.")
    except Exception as e:
        print(f"[ERREUR] La conversion a échoué : {e}")



# Modification dans main()
def main():
    auteur = demander_auteur()
    langue = choisir_langue()
    mode = choisir_mode_execution()

    if mode == "auto":
        lancer_pipeline_complet(langue, auteur)
    else:
        menu_manuel(langue)


if __name__ == "__main__":
    main()
