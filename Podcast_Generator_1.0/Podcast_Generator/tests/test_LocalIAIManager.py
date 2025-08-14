import os
import unittest
from pathlib import Path

from Podcast_Generator import LocalIAIManager

class TestLocalIAIManagerFunctional(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        base_path = Path(__file__).resolve().parent.parent
        cls.model_path = mistralQ4 = "Models/Mistral-7B-Instruct-v0.1-GGUF/mistral-7b-instruct-v0.1.Q4_K_M.gguf"
        cls.model_path = base_path / LocalIAIManager.mistralQ4
        cls.model_path = str(cls.model_path)
        if not os.path.isfile(cls.model_path):
            raise FileNotFoundError(f"⚠️ Modèle non trouvé : {cls.model_path}")

        cls.prompt = "Explique en une phrase ce qu’est une étoile."

    def test_query_local_model(self):
        response = LocalIAIManager.query_local_model(
            prompt=self.prompt,
            model_path=self.model_path,
            max_tokens=100
        )
        print("\n[query_local_model] →", response)
        self.assertIsInstance(response, str)
        self.assertGreater(len(response.strip()), 0)

    def test_call_model_local(self):
        response = LocalIAIManager.call_model(
            prompt=self.prompt,
            backend="local",
            model_path=self.model_path,
            max_tokens=100
        )
        print("\n[call_model - local] →", response)
        self.assertIsInstance(response, str)
        self.assertGreater(len(response.strip()), 0)

    def test_get_context_limit_from_gguf(self):
        context_limit = LocalIAIManager.get_context_limit_from_gguf(self.model_path)
        print("\n[get_context_limit_from_gguf] →", context_limit)
        self.assertIsInstance(context_limit, int)
        self.assertGreater(context_limit, 0)

if __name__ == "__main__":
    unittest.main()
