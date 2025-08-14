import pytest
import os
import json
from pathlib import Path
from Podcast_Generator import PodcastScriptGenerator as psg, PodcastDialogueGenerator as pdg
from Podcast_Generator.LocalIAIManager import mistralQ4

# Dossiers de Samples
SAMPLES_DIR = Path(__file__).resolve().parent / "Samples" / "RSM-20250426-1019"
SCRIPT_EN = SAMPLES_DIR / "script_en.json"
DIALOGUE_RAW_EN = SAMPLES_DIR / "DialogueRaw__En__2025-04-26__10-38__en.txt"

class TestPodcastDialogueGenerator:

    def test_generate_participant_names_en(self):
        names = pdg.generate_participant_names(2, lang="en")
        assert isinstance(names, list)
        assert len(names) == 2
        assert len(set(names)) == 2  # Pas de doublons

    def test_generate_participant_names_fr(self):
        names = pdg.generate_participant_names(2, lang="fr")
        assert isinstance(names, list)
        assert len(names) == 2
        assert len(set(names)) == 2

    def test_resolve_best_tone(self):
        tone = pdg.resolve_best_tone("enthousiaste")
        assert isinstance(tone, str)
        assert tone in pdg.tone_list

    def test_format_to_bracketed_lines(self):
        raw_text = "Michelle(excited): We've made progress.\nMelissa(thoughtful): Let's build on that."
        formatted = pdg._format_to_bracketed_lines(raw_text)
        assert "[# Michelle : excited ]" in formatted
        assert "[# Melissa : thoughtful ]" in formatted

    def test_add_indices_to_bracketed(self):
        text = "[# Michelle : excited ] We've made progress.\n[# Melissa : thoughtful ] Let's build on that."
        indexed = pdg._add_indices_to_bracketed(text)
        assert "[# Michelle : excited : 1]" in indexed
        assert "[# Melissa : thoughtful : 2]" in indexed

    def test_generate_raw_dialogue_from_script_en(self, tmp_path):
        output_dir = tmp_path / "dialogue_output"
        output_dir.mkdir()
        path_script = SCRIPT_EN
        assert path_script.exists(), f"Script EN introuvable : {path_script}"

        generated = pdg.generate_raw_dialogue(
            script_path=str(path_script),
            participants=2,
            noms=["Alice", "Bob"],
            lang="en",
            backend="local",
            model_path=str(Path(__file__).resolve().parent.parent / mistralQ4),
            output_dir=str(output_dir)
        )
        assert os.path.exists(generated)
        with open(generated, "r", encoding="utf-8") as f:
            content = f.read()
        assert "[#" in content

    def test_generate_raw_dialogue_from_script_fr(self, tmp_path):
        output_dir = tmp_path / "dialogue_output_fr"
        output_dir.mkdir()
        path_script = SCRIPT_EN
        assert path_script.exists(), f"Script EN introuvable : {path_script}"

        generated = pdg.generate_raw_dialogue(
            script_path=str(path_script),
            participants=2,
            noms=["Claire", "Damien"],
            lang="fr",
            backend="local",
            model_path=str(Path(__file__).resolve().parent.parent / mistralQ4),
            output_dir=str(output_dir)
        )
        assert os.path.exists(generated)
        with open(generated, "r", encoding="utf-8") as f:
            content = f.read()
        assert "[#" in content
