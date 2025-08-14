import os
import tempfile
import pytest
from pathlib import Path
from Podcast_Generator.TTSWrapper import generate_audio, play_audio


class TestTTSWrapper:
    def setup_class(self):
        self.test_text = "Ceci est un test unitaire pour la voix."
        self.language = "fr"
        self.speed = 1.0
        self.emotion = "neutre"
        self.voice_config = {"speaker": "Damien Black"}
        self.output_path = Path(tempfile.gettempdir()) / "test_output_ttswrapper.wav"

    def test_generate_audio(self):
        generate_audio(
            text=self.test_text,
            file_path=str(self.output_path),
            language=self.language,
            speed=self.speed,
            emotion=self.emotion,
            voice_config=self.voice_config
        )
        assert self.output_path.exists(), "Le fichier audio n'a pas été créé."
        assert self.output_path.stat().st_size > 1000, "Le fichier audio est trop petit."

    def test_play_audio(self):
        if not self.output_path.exists():
            pytest.skip("Le fichier n'existe pas pour test_play_audio")

        try:
            play_audio(str(self.output_path))
        except PermissionError:
            pytest.skip("Permission refusée lors de la lecture audio sur ce système.")
        except Exception as e:
            pytest.fail(f"Erreur lors de la lecture du fichier : {e}")
