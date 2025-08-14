import unittest
from pathlib import Path
from Podcast_Generator import TextAnalyzer, LocalIAIManager, SourceImporter

class TestTextAnalyzerFunctional(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        base_path = Path(__file__).resolve().parent.parent
        cls.model_path = str(base_path / LocalIAIManager.mistralQ4)

        cls.text = (
            "L’intelligence artificielle transforme rapidement de nombreux domaines, "
            "de la médecine à l’éducation, en passant par les transports."
        )

    def test_clean_list(self):
        data = ["Le Chat", "la Maison", "les chiens", "des Oiseaux!", "du vent"]
        cleaned = TextAnalyzer.clean_list(data)
        self.assertIsInstance(cleaned, list)
        self.assertTrue(all(isinstance(item, str) for item in cleaned))
        self.assertTrue(all(len(item) > 2 for item in cleaned))

    def test_clean_raw_concepts(self):
        raw = ["- Mot-clé : IA", "Keyword: Artificial Intelligence", "* thème : Machine Learning"]
        cleaned = TextAnalyzer.clean_raw_concepts(raw)
        self.assertIsInstance(cleaned, list)
        self.assertGreater(len(cleaned), 0)

    def test_split_text_into_chunks(self):
        chunks = TextAnalyzer.split_text_into_chunks(self.text, max_chars=50)
        self.assertIsInstance(chunks, list)
        self.assertGreater(len(chunks), 0)

    def test_summarize_with_meta_summary(self):
        summary = TextAnalyzer.summarize_with_meta_summary(
            text=self.text,
            backend="local",
            model_path=self.model_path,
            max_tokens=100,
            chunk_token_limit=256
        )
        self.assertIsInstance(summary, list)
        self.assertGreater(len(summary), 1)  # global + au moins un chunk
        self.assertTrue(all(isinstance(x, str) for x in summary))
        self.assertGreater(len(summary[0].strip()), 0)  # Le résumé global

    def test_extract_concepts_keywords(self):
        keywords = TextAnalyzer.extract_concepts(
            text=self.text,
            mode="keywords",
            backend="local",
            model_path=self.model_path,
            max_tokens=100
        )
        self.assertIsInstance(keywords, list)
        self.assertGreater(len(keywords), 0)

    def test_extract_concepts_themes(self):
        themes = TextAnalyzer.extract_concepts(
            text=self.text,
            mode="themes",
            backend="local",
            model_path=self.model_path,
            max_tokens=100
        )
        self.assertIsInstance(themes, list)
        self.assertGreater(len(themes), 0)

    def test_group_semantic_concepts(self):
        grouped = TextAnalyzer.group_semantic_concepts(
            ["IA", "intelligence artificielle", "machine learning"],
            backend="local",
            model_path=self.model_path
        )
        self.assertIsInstance(grouped, list)
        self.assertGreater(len(grouped), 0)

if __name__ == "__main__":
    unittest.main()
