import pytest
from Podcast_Generator import PodcastScriptGenerator as psg
import pytest
import os
import json
from pathlib import Path

# Dossier Samples pour les fichiers RSM
SAMPLES_DIR = Path(__file__).resolve().parent / "Samples" / "RSM-20250426-1019"
DIALOGUE_SAMPLE = Path(__file__).resolve().parent / "Samples" / "Dialogues_MaladeImaginaire.txt"

class TestPodcastScriptGenerator:

    def test_initvoicematch(self):
        assert psg.initvoicematch() == {}

    def test_voicematching(self):
        vm = {}
        psg.voicematching(vm, "[# Alice]", "fr_1")
        assert vm == {"Alice": "fr_1"}

    def test_voicematchingfiller(self):
        vm = {}
        psg.voicematchingfiller(vm, "Bob", "fr_2", "Claire", "en_1")
        assert vm == {"Bob": "fr_2", "Claire": "en_1"}

        with pytest.raises(ValueError):
            psg.voicematchingfiller(vm, "Unpair")  # impaire → erreur

    def test_normalizestring(self):
        text = "[# Alice : calme : 1] Bonjour. [# Bob : neutre : 2] Salut."
        parts = psg.normalizestring(text)
        assert len(parts) == 2
        assert parts[0].startswith("[# Alice")
        assert parts[1].startswith("[# Bob")

    def test_parse_dialogue_block_valid(self):
        block = "[# Alice : joyeux : 3] C'est une belle journée !"
        parsed = psg.parse_dialogue_block(block)
        assert parsed == {
            "name": "Alice",
            "tone": "joyeux",
            "index": 3,
            "text": "C'est une belle journée !"
        }

    def test_parse_dialogue_block_invalid(self):
        with pytest.raises(ValueError):
            psg.parse_dialogue_block("Alice:joyeux:1 Pas de balise")

    def test_parse_dialogue_file_and_meta_extraction(self):
        content = '''{
                  "titre": "Test Podcast",
                  "auteur": "Auteur",
                  "date": "2025-04-02"
                }
                
                [# Alice : neutre : 1] Bonjour.
                [# Bob : calme : 2] Salut.'''
        meta, blocks = psg.parse_dialogue_file(content)
        assert meta["titre"] == "Test Podcast"
        assert len(blocks) == 2
        assert blocks[0]["name"] == "Alice"
        assert blocks[1]["tone"] == "calme"

    def test_generate_discussion_from_file_dry(self, tmp_path):
        file_path = tmp_path / "test_dialogue.txt"
        file_path.write_text('''{
                      "titre": "Essai",
                      "auteur": "Moi",
                      "date": "2025-04-04"
                    }
                    [# A : neutre : 1] Test phrase.''', encoding="utf-8")

        results = psg.generate_discussion_from_file(
            str(file_path),
            1,  # participants (non nommé)
            "A", "fr_1",
            dry_run=True
        )

        assert isinstance(results, list)
        assert results[0]["name"] == "A"

class TestPodcastScriptGeneratorExtended:

    def test_extract_character_names_from_dialogue_file(self):
        names = psg.extract_character_names_from_dialogue_file(str(DIALOGUE_SAMPLE))
        assert isinstance(names, list)
        assert len(names) > 0
        assert "Toinette" in names or "Argan" in names

    def test_remplacer_nom_dialogue(self, tmp_path):
        # Copie du fichier original
        source_copy = tmp_path / "dialogue_copy.txt"
        source_content = DIALOGUE_SAMPLE.read_text(encoding="utf-8")
        source_copy.write_text(source_content, encoding="utf-8")

        # Remplacer "Argan" par "Damien"
        output_path = psg.remplacer_et_sauver_fichier(str(source_copy), "Argan", "Damien")
        assert Path(output_path).exists()

        new_content = Path(output_path).read_text(encoding="utf-8")
        assert "[# Damien" in new_content

    def test_assign_voices_by_gender(self):
        names = ["Toinette", "Argan"]
        voices = psg.assign_voices_by_gender(names)
        assert isinstance(voices, dict)
        assert set(voices.keys()) == {"Toinette", "Argan"}

    def test_create_script_rag_modulaire(self):
        script = psg.create_script_rag_modulaire(
            folder_path=str(SAMPLES_DIR),
            backend="server"
        )
        assert isinstance(script, dict)
        assert "intro" in script and "parts" in script and "outro" in script
        assert isinstance(script["parts"], list)
        assert len(script["parts"]) == 4

    def test_save_and_load_script(self, tmp_path):
        dummy_script = {
            "intro": "Introduction de test.",
            "parts": [
                {"title": "Partie 1", "content": "Contenu 1."},
                {"title": "Partie 2", "content": "Contenu 2."},
                {"title": "Partie 3", "content": "Contenu 3."},
                {"title": "Partie 4", "content": "Contenu 4."}
            ],
            "outro": "Conclusion de test."
        }

        save_path = psg.save_script_to_json(dummy_script, str(tmp_path))
        assert os.path.exists(save_path)

        loaded_script = psg.load_script_from_json(save_path)
        assert dummy_script == loaded_script

if __name__ == "__main__":
    pytest.main(["-v"])
