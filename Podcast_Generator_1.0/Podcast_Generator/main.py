import SourceImporter
from Podcast_Generator.PodcastDialogueGenerator import generate_raw_dialogue
from Podcast_Generator.PodcastGeneratorAudio import GenerateAndMux
from Podcast_Generator.PodcastScriptGenerator import create_script_rag_modulaire, save_script_to_json
from Podcast_Generator.TextAnalyzer import summarize_with_meta_summary, extract_concepts, save_list_to_json
from pathlib import Path
from PyQt6.QtWidgets import QApplication
import sys
from MainWindow import MainWindow

if __name__ == "__main__":

    lang = "en"
    #path = input("Source to extract data from: ")
    path = "tests\Samples\Rapport_IA.pdf"
    # Extracttion du texte.
    text = SourceImporter.extract_file_handler(path)

    # Model path Sinon lancement Server
    # modelpath = "Models/Mistral-Nemo-Instruct-2407-Q8_0.gguf"
    # max_tokens = int

    # Création du resumé
    text_summaries = summarize_with_meta_summary(text,output_language=lang)
    text_keywords = extract_concepts(text_summaries[0],mode="keywords",output_language=lang)
    text_themes = extract_concepts(text_summaries[0],mode="themes",output_language=lang)

    summarypath = save_list_to_json(text_summaries,suffix="summary")
    save_list_to_json(text_keywords, suffix="keywords")
    save_list_to_json(text_themes, suffix="themes")

    folder = str(Path(summarypath).parent)

    # Création du Script
    script = create_script_rag_modulaire(folder_path=folder,output_language=lang)
    scriptpath = save_script_to_json(script,folder,lang=lang)

    # Création du Dialogue
    dialoguepath = generate_raw_dialogue(scriptpath, lang=lang, auteur="Le D")

    # Création des vocaux
    GenerateAndMux(dialoguepath)

    # その他 - Fonctions pour L'UI

                # add_tone_preset()
                # remove_tone_preset()
                # list_all_tones()
                # preview_tone()
                # resolve_best_tone()


                # call_model()

        # save_script_to_json()
        # load_script_from_json()

    # voicematching()
    # voicematchingfiller()
    # extract_character_names_from_dialogue_file()
    # remplacer_et_sauver_fichier()

    # generate_discussion_from_file()

                # convert_wav_to_mp3()
                # convert_mp3_to_wav()

                # get_available_speakers()
                # list_custom_male_voices()
                # list_custom_female_voices()
                # list_custom_all_mf_voices()
                # list_custom_raw_voices()
                # list_all_available_voices()

    # create_sentence()
    # create_discussion()
    # muxgenerateddiscussion()
