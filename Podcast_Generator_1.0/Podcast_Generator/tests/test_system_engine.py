import unittest
from pathlib import Path
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from Podcast_Generator import SystemEngine

class TestSystemEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """
        Initialisation des dossiers contenant les fichiers de test.
        Initializes the directories containing test files.
        """

        cls.sample_dir = Path(__file__).parent / "Samples" #Samples folder
        cls.expected_dir = Path(__file__).parent / "Expected" # Expected folder

    def test_save_text_to_file(self):
        """
        Teste la création et la suppression d'un fichier texte.
        Tests the creation and deletion of a text file.
        """
        # Création et sauvegarde d'un fichier de test
        # Creating and saving a test file
        savefiletestpath = SystemEngine.save_text_to_file(str(self.expected_dir),"savefiletest","Mama mia")

        #Assertion
        # Vérification que la fonction retourne bien un chemin sous forme de string
        # Verifies that the function returns a path as a string
        self.assertIsInstance(savefiletestpath, str)

        # Suppression du fichier après test pour éviter les fichiers temporaires inutiles
        # Deletes the file after the test to avoid unnecessary temporary files
        try:
            Path(savefiletestpath).unlink()
        except Exception as e:
            self.fail(e)