import pytest
import json
from pathlib import Path
from Podcast_Generator import TonePresetManager as tpm

class TestTonePresetManager:
    def setup_method(self):
        self.preset_path = Path(__file__).resolve().parent.parent / "tone_presets.json"
        self.backup = self.preset_path.read_text(encoding="utf-8")
        self.original_presets = tpm.load_tone_presets()

    def teardown_method(self):
        self.preset_path.write_text(self.backup, encoding="utf-8")

    def test_load_tone_presets(self):
        presets = tpm.load_tone_presets()
        assert isinstance(presets, dict)
        assert "neutre" in presets
        assert "speed" in presets["neutre"]
        assert "emotion" in presets["neutre"]

    def test_add_tone_preset(self):
        tpm.add_tone_preset("joyeux_test", 1.3, "happy")
        assert "joyeux_test" in tpm.load_tone_presets()

    def test_remove_tone_preset(self):
        name = "to_remove_test"
        tpm.add_tone_preset(name, 0.9, "sad")
        tpm.remove_tone_preset(name)
        assert name not in tpm.load_tone_presets()

    def test_get_preset_existing(self):
        presets = tpm.load_tone_presets()
        preset = presets.get("neutre", {})
        assert "speed" in preset and "emotion" in preset

    def test_get_preset_non_existing(self):
        presets = tpm.load_tone_presets()
        preset = presets.get("inexistant_xyz", {"speed": 1.0, "emotion": "neutral"})
        assert preset == {"speed": 1.0, "emotion": "neutral"}

    def test_list_all_tones(self):
        """Test que list_all_tones retourne bien une liste et contient au moins 'neutre'"""
        tones = tpm.list_all_tones()
        assert isinstance(tones, list)
        assert "neutre" in tones

    def test_preview_tone(self):
        """Test que preview_tone génère un fichier preview_<ton>.wav"""
        ton = "calme"  # Ton qui existe dans tone_presets.json
        voice = "fr_1"  # -> Voix interne XTTS ! PAS fichier wav
        text = "Ceci est un test de prévisualisation audio."

        # Appel de la fonction pour générer
        tpm.preview_tone(ton=ton, voice=voice, text=text)

        preview_dir = Path(__file__).resolve().parent.parent / "VoicesPreview"
        generated_file = preview_dir / f"preview_{ton}.wav"

        # Assertions
        assert generated_file.exists(), f"Le fichier {generated_file} n'a pas été généré."
        assert generated_file.stat().st_size > 1000, "Le fichier audio semble vide ou corrompu."

        # Nettoyage
        generated_file.unlink()