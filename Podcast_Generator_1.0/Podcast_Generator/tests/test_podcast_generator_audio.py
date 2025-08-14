import datetime
import warnings

from Podcast_Generator.PodcastGeneratorAudio import GenerateAndMux, convert_wav_to_mp3, convert_mp3_to_wav
import Podcast_Generator.PodcastScriptGenerator
from Podcast_Generator.PodcastScriptGenerator import initvoicematch, voicematchingfiller

warnings.filterwarnings("ignore", category=FutureWarning)
import shutil
import os
import sys
import pytest
from pydub import AudioSegment
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from Podcast_Generator import PodcastGeneratorAudio

# Dossier dédié aux sorties de test
TEST_OUTPUT_DIR = Path("tests/test_directory")
TEST_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# === TESTS GENERATION DE PHRASES ===

def test_create_sentence_tts_builtin_voice():
    voice = "Claribel Dervla"
    tone = "calme"
    texte = "Ceci est une phrase de test pour vérifier la génération vocale automatique."
    output_path = "test_output"
    filename = "test_sentence.wav"

    output_file = PodcastGeneratorAudio.create_sentence(
        voice=voice,
        ton=tone,
        texte=texte,
        output_path=output_path,
        filename=filename,
        language="fr"  # ou "en", "zh", ou "ja".
    )

    assert os.path.exists(output_file), "Le fichier audio n'a pas été généré."

    audio = AudioSegment.from_file(output_file)
    assert len(audio) > 1000, "Le fichier audio est vide ou trop court."

    os.remove(output_file)
    os.rmdir(output_path)

def test_create_sentence_with_invalid_tone():
    voice = "Claribel Dervla"
    texte = "Test avec un ton invalide, doit retomber sur 'neutre'."
    output_path = "test_output"
    filename = "test_invalid_tone.wav"
    output_file = PodcastGeneratorAudio.create_sentence(
        voice=voice,
        ton="pas_un_ton",
        texte=texte,
        output_path=output_path,
        filename=filename,
        language="fr"
    )
    assert os.path.exists(output_file)
    os.remove(output_file)
    os.rmdir(output_path)

def test_create_sentence_with_custom_wav_voice():
    voice_name = "Chirac Pommes.wav"  # doit exister dans Voices/
    tone = "dramatique"
    texte = "Je crois que les filles m'aiment bien parceque je suis un peu mystérieux comme Light Yagami, je suis toujours tout seul, aux récrées je m’assoie sur un banc avec ma capuche et la tête baissé et quand quelque passe à coté de moi je chuchote des truc genre okamari no suzoki, ça ne veut rien dire mais ça fait mystique, les gens sont intrigués."

    output_path = "output"
    filename = "Chirac2_Test.wav"

    output_file = PodcastGeneratorAudio.create_sentence(
        voice=voice_name,
        ton=tone,
        texte=texte,
        output_path=output_path,
        filename=filename,
        language="fr"  # ou "en", "zh", ou "ja".
    )

    assert os.path.exists(output_file), "Le fichier audio personnalisé n'a pas été généré."

    audio = AudioSegment.from_file(output_file)
    assert len(audio) > 1000, "Le fichier audio est vide ou trop court."

    os.remove(output_file)

def test_create_sentence_with_custom_wav_voice2():
    voice_name = "Hanekawa.wav"  # doit exister dans Voices/
    tone = "solennel"
    texte = "老兵はただ去るのみ。"

    output_path = "output"
    filename = "Hanekawa.wav"

    output_file = PodcastGeneratorAudio.create_sentence(
        voice=voice_name,
        ton=tone,
        texte=texte,
        output_path=output_path,
        filename=filename,
        language="ja"  # ou "en", "zh", "ja".
    )

    assert os.path.exists(output_file), "Le fichier audio personnalisé n'a pas été généré."

    audio = AudioSegment.from_file(output_file)
    assert len(audio) > 1000, "Le fichier audio est vide ou trop court."

# === TESTS RESOLUTION DE VOIX ===

def test_resolve_voice_builtin():
    resolved = PodcastGeneratorAudio._resolve_voice("Claribel Dervla")
    assert "speaker" in resolved or "speaker_wav" in resolved

def test_resolve_voice_invalid():
    with pytest.raises(ValueError):
        PodcastGeneratorAudio._resolve_voice("VoixInconnue123")

def test_resolve_voice_missing_wav():
    with pytest.raises(FileNotFoundError):
        PodcastGeneratorAudio._resolve_voice("missing_voice.wav")

def test_get_available_speakers():
    speakers = PodcastGeneratorAudio.get_available_speakers()
    assert isinstance(speakers, (list, dict, set)), "La liste des voix doit être un itérable."
    assert len(speakers) > 0, "Aucune voix disponible n'a été détectée."

# === TESTS SPLIT TEXTE ===

def test_split_text_chunks():
    long_text = (
        "Voici une première phrase complète. Ensuite une deuxième phrase très très longue qui dépasse les 273 caractères, ce qui signifie qu'elle doit être découpée correctement par la fonction split, même si elle ne contient pas de ponctuation facilement exploitable, pour éviter tout dépassement." * 2
    )
    parts = PodcastGeneratorAudio._split_text(long_text)
    assert all(len(p) <= 273 for p in parts), "Certains morceaux dépassent la limite de 273 caractères."
    assert sum(len(p) for p in parts) >= len(long_text) * 0.9, "Le texte a été trop raccourci lors du découpage."



def test_create_discussion_from_dialogue_file():
    from pathlib import Path
    import os

    original_cwd = Path.cwd()
    test_dir = Path("tests/test_directory")
    test_dir.mkdir(parents=True, exist_ok=True)
    os.chdir(test_dir)

    try:
        path = Path(original_cwd / "Samples/Dialogue1test.txt")
        assert path.exists(), f"Fichier non trouvé : {path}"

        from Podcast_Generator.PodcastScriptGenerator import generate_discussion_from_file

        dialogues = generate_discussion_from_file(
            str(path),
            2,
            "Major", "Claribel Dervla",
            "Batou", "Craig Gutsy",
            dry_run=False
        )

        assert len(dialogues) > 0

        meta = {
            "titre": "Sommes-nous encore humains ?",
            "auteur": "Masamune Shirow",
            "date": "2025-04-02"
        }
        date_str = datetime.datetime.strptime(meta["date"], "%Y-%m-%d").strftime("%Y-%m-%d")
        output_dirs = [d for d in Path(".").iterdir() if d.is_dir() and d.name.startswith("Sommes-nous_encore_humains_")]
        assert output_dirs, "Le dossier de sortie n’a pas été créé."
    finally:
        os.chdir(original_cwd)


def test_generate_and_mux_dialogue2():
    from pathlib import Path
    import os

    original_cwd = Path.cwd()
    test_dir = Path("tests/test_directory")
    test_dir.mkdir(parents=True, exist_ok=True)
    os.chdir(test_dir)

    try:
        path = Path(original_cwd / "Samples/Dialogue2test.txt")
        assert path.exists(), f"Le fichier Dialogue2test.txt est introuvable à {path}"

        from Podcast_Generator.PodcastGeneratorAudio import GenerateAndMux

        final_output = GenerateAndMux(
            full_dialogue_path=str(path),
            participants={
                "Light": "Damien Black",
                "L": "Zacharie Aimilios"
            },
            presentateur="Rosemary Okafor"
        )

        assert final_output.endswith(".wav"), "Le fichier de sortie doit être un .wav"
        assert Path(final_output).exists(), "Le fichier audio final n'a pas été créé"
    finally:
        os.chdir(original_cwd)

def test_mux_generated_discussion_mock():
    from Podcast_Generator.PodcastGeneratorAudio import muxgenerateddiscussion
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        file1 = tmpdir_path / "01.wav"
        file2 = tmpdir_path / "02.wav"
        silence = AudioSegment.silent(duration=1000)
        silence.export(file1, format="wav")
        silence.export(file2, format="wav")

        result_path = muxgenerateddiscussion([
            str(file1), str(file2)
        ], output_path=tmpdir)

        assert result_path.endswith(".wav")
        assert Path(result_path).exists()
        audio = AudioSegment.from_file(result_path)
        expected_duration = 2000  # 2 × 1000 ms
        tolerance = 800  # autorise jusqu’à 800 ms de perte
        assert len(audio) >= expected_duration - tolerance, f"Durée insuffisante : {len(audio)} ms"


# === TESTS VOIX DISPONIBLES ===

class TestVoiceListing:

    def test_list_custom_male_voices(self):
        male_voices = PodcastGeneratorAudio.list_custom_male_voices()
        assert isinstance(male_voices, list), "Le retour doit être une liste."
        for voice in male_voices:
            assert isinstance(voice, str), "Chaque nom de voix doit être une chaîne de caractères."
            assert not voice.endswith(".wav"), "Les noms de voix ne doivent pas contenir l’extension '.wav'"

    def test_list_custom_female_voices(self):
        female_voices = PodcastGeneratorAudio.list_custom_female_voices()
        assert isinstance(female_voices, list), "Le retour doit être une liste."
        for voice in female_voices:
            assert isinstance(voice, str), "Chaque nom de voix doit être une chaîne de caractères."
            assert not voice.endswith(".wav"), "Les noms de voix ne doivent pas contenir l’extension '.wav'"

    def test_list_custom_all_mf_voices(self):
        all_mf = PodcastGeneratorAudio.list_custom_all_mf_voices()
        # print("Voix Male + Female :", all_mf)
        assert isinstance(all_mf, list), "Le retour doit être une liste."
        assert set(all_mf) >= set(PodcastGeneratorAudio.list_custom_male_voices()), "Les voix Male doivent être incluses"
        assert set(all_mf) >= set(PodcastGeneratorAudio.list_custom_female_voices()), "Les voix Female doivent être incluses"

    def test_list_custom_raw_voices(self):
        raw = PodcastGeneratorAudio.list_custom_raw_voices()
        # print("Voix dans Voices/ racine :", raw)
        assert isinstance(raw, list), "Le retour doit être une liste."
        for voice in raw:
            assert voice.endswith(".wav"), "Les voix doivent être des fichiers .wav"

    def test_list_all_available_voices(self):
        all_voices = PodcastGeneratorAudio.list_all_available_voices()
        # print("Toutes les voix disponibles :", all_voices)
        assert isinstance(all_voices, list), "Le retour doit être une liste."
        builtin = list(PodcastGeneratorAudio.get_available_speakers())
        assert any(v in all_voices for v in builtin), "Les voix intégrées doivent être présentes dans la liste totale"

def test_convert_wav_to_mp3():
    # Arrange
    wav_file = Path(__file__).resolve().parent.parent / "Voices" / "Chirac Pommes.wav"
    assert wav_file.exists(), f"Le fichier source n'existe pas : {wav_file}"

    # Act
    mp3_path = convert_wav_to_mp3(str(wav_file))

    # Assert
    assert os.path.exists(mp3_path), "Le fichier .mp3 n'a pas été généré."
    audio = AudioSegment.from_file(mp3_path)
    assert len(audio) > 1000, "Le fichier MP3 est vide ou trop court."

    # Clean up
    os.remove(mp3_path)

def test_convert_mp3_to_wav_from_samples():


    # On est déjà dans tests/, donc Samples/ est directement là
    mp3_sample_path = Path("Samples/MegaMan Star Force 3 Warning Battle Sound Effect.mp3")
    assert mp3_sample_path.exists(), f"Fichier MP3 introuvable : {mp3_sample_path}"

    wav_path = convert_mp3_to_wav(str(mp3_sample_path))
    assert os.path.exists(wav_path), "WAV non créé."

    audio = AudioSegment.from_file(wav_path)
    assert len(audio) > 500, "WAV généré trop court."

    if os.path.exists(wav_path):
        os.remove(wav_path)


# Creation des Samples de voix
# def test_preview_all_builtin_voices():
#     output_path = "VoicesPreview"
#     os.makedirs(output_path, exist_ok=True)
#     voix = list(PodcastGeneratorAudio.get_available_speakers())
#     assert len(voix) > 0, "Aucune voix intégrée trouvée."
#
#     for speaker in voix:
#         path = PodcastGeneratorAudio.create_sentence(
#             voice=speaker,
#             ton="neutre",
#             texte="A calm voice in a restless world.",
#             output_path=output_path,
#             filename=f"{speaker}.wav"
#         )
#         assert os.path.exists(path), f"Le fichier {speaker}.wav n'a pas été généré."
#         audio = AudioSegment.from_file(path)
#         assert len(audio) > 500, f"Le fichier généré pour {speaker} est vide ou trop court."

def test_presidents():
    voices = initvoicematch()
    voicematchingfiller(voices,"Argan","Emmanuel Macron.wav","Toinette","Chirac Pommes.wav")
    original_cwd = Path.cwd()
    test_dir = Path("tests/test_directory")
    test_dir.mkdir(parents=True, exist_ok=True)
    os.chdir(test_dir)
    path = Path(original_cwd / "Samples/Dialogues_MaladeImaginaire.txt")
    GenerateAndMux(path,voices,"Alison Dietlinde")


if __name__ == "__main__":
    pytest.main(["-v"])
