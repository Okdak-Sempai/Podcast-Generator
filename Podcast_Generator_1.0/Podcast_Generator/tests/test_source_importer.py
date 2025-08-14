import unittest
from pathlib import Path
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from Podcast_Generator import SourceImporter

class TestTextExtraction(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        #Initialisation du dossier Sample et des fichiers de test.
        cls.sample_dir = Path(__file__).parent / "Samples"
        cls.expected_dir = Path(__file__).parent / "Expected"

        # Définition des fichiers individuellement
        cls.txt_file1 = cls.sample_dir / "SampleFile1.txt"
        cls.txt_file2 = cls.sample_dir / "readme.txt"

        cls.pdf_file1 = cls.sample_dir / "Yu Wu Yu - Xi Wei Wei Xin.pdf"
        cls.pdf_file2 = cls.sample_dir / "Mocha AE Release Notes.pdf"
        cls.pdf_file3 = cls.sample_dir / "Cours (1).pdf"
        cls.pdf_file4 = cls.sample_dir / "Auteurs à connaître.pdf"
        cls.pdf_file5 = cls.sample_dir / "Andler, Charles - Nietzsche _ sa vie et sa pensée. Vol. 5. Nietzsche et le transformisme intellectualiste.pdf"

        cls.docx_file1 = cls.sample_dir / "GENUS-GNS2-Dossier-de-presse-2024-FRA.docx"
        cls.docx_file2 = cls.sample_dir / "FrameView SDK License (3Sept2020).docx"

        cls.md_file1 = cls.sample_dir / "zlib.md"
        cls.md_file2 = cls.sample_dir / "README.md"

        cls.tex_file1 = cls.sample_dir / "Cours.tex"

        cls.image_file1 = cls.sample_dir / "picture_pc_ff5052524b28cc92a2b36f41698eea41.webp"
        cls.image_file2 = cls.sample_dir / "panneau-de-direction-de-route-japon-56331672.webp"
        cls.image_file3 = cls.sample_dir / "subtitling-1-min.jpg"
        cls.image_file4 = cls.sample_dir / "images.jpg"
        cls.image_file5 = cls.sample_dir / "20201205202145000000_pre_223.jpg"
        cls.image_file6 = cls.sample_dir / "20250218_093655.jpg"


        cls.weblinks_file = cls.sample_dir / "weblinks.txt"

    def test_extract_text_from_txt(self):
        """Test extraction du texte depuis un fichier .txt"""

        #Actual
        text1 = SourceImporter.extract_text_from_txt(self.txt_file1)
        text2 = SourceImporter.extract_text_from_txt(self.txt_file2)
        #print("\n\nNB charaters:",len(text1))
        #save_text_to_file(str(self.expected_dir), "testtxt1",text1)
        #save_text_to_file(str(self.expected_dir), "testtxt2",text2)

        #Expected
        with open(self.txt_file1, "r", encoding="utf-8") as f1, open(self.txt_file2, "r", encoding="utf-8") as f2:
            content1 = f1.read()
            content2 = f2.read()

        #Assertions
        self.assertEqual(text1, content1, "Le contenu n'est pas le meme !")
        self.assertEqual(text2, content2, "Le contenu n'est pas le meme !")

    def test_extract_text_from_pdf_text(self):
        """Test extraction du texte depuis un fichier PDF"""

        #Actual
        extracted_pdf1 = SourceImporter.extract_text_from_pdf_text(self.pdf_file1)
        extracted_pdf2 = SourceImporter.extract_text_from_pdf_text(self.pdf_file2)
        extracted_pdf3 = SourceImporter.extract_text_from_pdf_text(self.pdf_file3)
        extracted_pdf5 = SourceImporter.extract_text_from_pdf_text(self.pdf_file5)

        #save_text_to_file(str(self.expected_dir), "testpdf1",extracted_pdf1)
        #save_text_to_file(str(self.expected_dir), "testpdf2",extracted_pdf2)
        #save_text_to_file(str(self.expected_dir), "testpdf3",extracted_pdf3)
        #save_text_to_file(str(self.expected_dir), "testpdf5",extracted_pdf5)

        #Expected
        with open(self.expected_dir / "testpdf1.txt", "r", encoding="utf-8") as f1, \
                open(self.expected_dir / "testpdf2.txt", "r", encoding="utf-8") as f2, \
                open(self.expected_dir / "testpdf3.txt", "r", encoding="utf-8") as f3, \
                open(self.expected_dir / "testpdf5.txt", "r", encoding="utf-8") as f5:
            saved_pdf1 = f1.read()
            saved_pdf2 = f2.read()
            saved_pdf3 = f3.read()
            saved_pdf5 = f5.read()

        #Assertions
        self.assertEqual(extracted_pdf1, saved_pdf1, "Le contenu n'est pas le meme !")
        self.assertEqual(extracted_pdf2, saved_pdf2, "Le contenu n'est pas le meme !")
        self.assertEqual(extracted_pdf3, saved_pdf3, "Le contenu n'est pas le meme !")
        self.assertEqual(extracted_pdf5, saved_pdf5, "Le contenu n'est pas le meme !")

    def test_extract_text_from_pdf_scanned(self):
        """Extraction du texte d'un PDF scanné avec OCR"""

        #Actual
        extracted_pdf4 = SourceImporter.extract_text_from_pdf_scanned(str(self.pdf_file4))
        #save_text_to_file(str(self.expected_dir), "testpdf4",extracted_pdf4)

        #Expected
        with open(self.expected_dir / "testpdf4.txt", "r", encoding="utf-8") as f4:
            saved_pdf4 = f4.read()

        #Assertions
        self.assertEqual(extracted_pdf4, saved_pdf4, "Le contenu n'est pas le meme !")

    def test_text_extract_text_from_docx(self):
        """Test extraction du texte de docx dans un fichier .txt"""
        #Actual
        extracted_docx1 = SourceImporter.extract_text_from_docx(self.docx_file1)
        extracted_docx2 = SourceImporter.extract_text_from_docx(self.docx_file2)

        #print(extracted_docx1)
        #print(extracted_docx2)
        #save_text_to_file(str(self.expected_dir), "testdocx1",extracted_docx1)
        #save_text_to_file(str(self.expected_dir), "testdocx2",extracted_docx2)

        #Expected
        with open(self.expected_dir / "testdocx1.txt", "r", encoding="utf-8") as f1, \
                open(self.expected_dir / "testdocx1.txt", "r", encoding="utf-8") as f2:
            saved_docx1 = f1.read()
            saved_docx2 = f2.read()

        #Assertions
        self.maxDiff = None
        self.assertEqual(extracted_docx1, saved_docx1, "Le contenu n'est pas le meme !")
        self.assertTrue(SourceImporter.are_texts_similar(extracted_docx2, saved_docx2), "Le contenu n'est pas le meme !")

    def test_extract_text_from_markdown(self):
        """Test extraction du texte de markdown dans un fichier .txt"""

        #ActuaL
        extracted_md_file1 = SourceImporter.extract_text_from_markdown(self.md_file1)
        extracted_md_file2 = SourceImporter.extract_text_from_markdown(self.md_file2)
        #save_text_to_file(str(self.expected_dir), "testmd1",extracted_md_file1)
        #save_text_to_file(str(self.expected_dir), "testmd2",extracted_md_file2)

        #Expected
        with open(self.expected_dir / "testmd1.txt", "r", encoding="utf-8") as f1, \
                open(self.expected_dir / "testmd2.txt", "r", encoding="utf-8") as f2:
            saved_md1 = f1.read()
            saved_md2 = f2.read()

        #Assertions
        self.assertEqual(extracted_md_file1, saved_md1, "Le contenu n'est pas le meme !")
        self.assertEqual(extracted_md_file2, saved_md2, "Le contenu n'est pas le meme !")

    def test_extract_text_from_latex(self):
        """Test extraction du texte de latex dans un fichier .txt"""

        #Actual
        extracted_tex_file1 = SourceImporter.extract_text_from_latex(self.tex_file1)
        #SystemEngine.save_text_to_file(str(self.expected_dir), "testtex1",extracted_tex_file1)

        #Expected
        with open(self.expected_dir / "testtex1.txt", "r", encoding="utf-8") as f1:
            saved_tex1 = f1.read()

        #Assertions
        self.assertEqual(extracted_tex_file1, saved_tex1, "Le contenu n'est pas le meme !")


    def test_extract_text_from_image(self):
        """Test extraction du texte d'image dans un fichier .txt"""

        #Actual
        extracted_image5 = SourceImporter.extract_text_from_image(str(self.image_file5))
        #extracted_image1 = SourceImporter.extract_text_from_image(str(self.image_file1))
        #extracted_image2 = SourceImporter.extract_text_from_image(str(self.image_file2))
        #extracted_image3 = SourceImporter.extract_text_from_image(str(self.image_file3))
        #extracted_image4 = SourceImporter.extract_text_from_image(str(self.image_file4))
        #extracted_image6 = SourceImporter.extract_text_from_image(str(self.image_file6))
        #print(extracted_image1)
        #print(extracted_image2)
        #print(extracted_image3)
        #print(extracted_image4)
        #print(extracted_image5)
        #print(extracted_image6)
        # save_text_to_file(str(self.expected_dir), "testimage1", extracted_image1)
        # save_text_to_file(str(self.expected_dir), "testimage2", extracted_image2)
        # save_text_to_file(str(self.expected_dir), "testimage3", extracted_image3)
        # save_text_to_file(str(self.expected_dir), "testimage4", extracted_image4)
        # save_text_to_file(str(self.expected_dir), "testimage5", extracted_image5)
        # save_text_to_file(str(self.expected_dir), "testimage6", extracted_image6)

        #Expected
        with open(self.expected_dir / "testimage5.txt", "r", encoding="utf-8") as f5:
            saved_image5 = f5.read()

        #Assertions
        self.assertTrue(SourceImporter.are_texts_similar(extracted_image5, saved_image5), "Le contenu n'est pas le meme !")

    def test_extract_text_from_web(self):
        """Test extraction du texte d'une page web dans fichier .txt"""

        #Actual
        with open(self.weblinks_file, "r") as f:
            lignes = f.readlines()
        lien1 = lignes[0].strip()
        lien2 = lignes[1].strip()
        #lien3 = lignes[2].strip()
        lien4 = lignes[3].strip()
        lien5 = lignes[4].strip()
        lien6 = lignes[5].strip()
        lien7 = lignes[6].strip()
        lien8 = lignes[7].strip()

        #Expected
        with open(self.expected_dir / "testweb1.txt", "r", encoding="utf-8") as f1, \
                open(self.expected_dir / "testweb2.txt", "r", encoding="utf-8") as f2, \
                open(self.expected_dir / "testweb3.txt", "r", encoding="utf-8") as f3, \
                open(self.expected_dir / "testweb4.txt", "r", encoding="utf-8") as f4, \
                open(self.expected_dir / "testweb5.txt", "r", encoding="utf-8") as f5, \
                open(self.expected_dir / "testweb6.txt", "r", encoding="utf-8") as f6, \
                open(self.expected_dir / "testweb7.txt", "r", encoding="utf-8") as f7, \
                open(self.expected_dir / "testweb8.txt", "r", encoding="utf-8") as f8:
            saved_web1 = f1.read()
            saved_web2 = f2.read()
            saved_web3 = f3.read()
            saved_web4 = f4.read()
            saved_web5 = f5.read()
            saved_web6 = f6.read()
            saved_web7 = f7.read()
            saved_web8 = f8.read()


        #Assertions
        extracted_weblink1 = SourceImporter.extract_text_from_web(lien1)
        #print("Weblink 1","is",SourceImporter.calculate_text_similarity(extracted_weblink1,saved_web1),"% accurate")
        self.assertTrue(SourceImporter.are_texts_similar(extracted_weblink1, saved_web1))

        extracted_weblink2 = SourceImporter.extract_text_from_web(lien2)
        #print("Weblink 2","is",SourceImporter.calculate_text_similarity(extracted_weblink2,saved_web2),"% accurate")
        self.assertTrue(SourceImporter.are_texts_similar(extracted_weblink2, saved_web2))

        #extracted_weblink3 = SourceImporter.extract_text_from_web(lien3)
        #print("Weblink 3","is",SourceImporter.calculate_text_similarity(extracted_weblink3,saved_web3),"% accurate")

        extracted_weblink5 = SourceImporter.extract_text_from_web(lien5)
        #print("Weblink 5","is",SourceImporter.calculate_text_similarity(extracted_weblink5,saved_web5),"% accurate")
        self.assertTrue(SourceImporter.are_texts_similar(extracted_weblink5, saved_web5))

        #extracted_weblink6 = SourceImporter.extract_text_from_web(lien6)
        #print("Weblink 6","is",SourceImporter.calculate_text_similarity(extracted_weblink6,saved_web6),"% accurate")
        #self.assertTrue(are_texts_similar(extracted_weblink6, saved_web6))

        # extracted_weblink7 = SourceImporter.extract_text_from_web(lien7)
        # print("Weblink 7","is",SourceImporter.calculate_text_similarity(extracted_weblink7,saved_web7),"% accurate")
        #
        # extracted_weblink8 = SourceImporter.extract_text_from_web(lien8)
        # print("Weblink 8","is",SourceImporter.calculate_text_similarity(extracted_weblink8,saved_web8),"% accurate")
        #
        # extracted_weblink4 = SourceImporter.extract_text_from_web(lien4)
        # print("Weblink 4","is",SourceImporter.calculate_text_similarity(extracted_weblink4,saved_web4),"% accurate")

    def test_detect_main_language(self):
        """Test de detection de langage"""

        #Actual
        anglais = "I like to read books."
        francais = "Il fait beau aujourd'hui."
        japonais = "今日は学校に行きません。"
        chinois_simplifie = "这个苹果很好吃。"
        chinois_traditionnel = "這裡的珍珠奶茶很好喝。"

        #Expected & Assertions
        self.assertEqual(SourceImporter.detect_main_language(anglais), 'eng')
        self.assertEqual(SourceImporter.detect_main_language(francais), 'fra')
        self.assertEqual(SourceImporter.detect_main_language(japonais), 'jpn')
        self.assertEqual(SourceImporter.detect_main_language(chinois_simplifie), 'chi_sim')
        self.assertEqual(SourceImporter.detect_main_language(chinois_traditionnel), 'chi_tra')

    def test_extract_file_handler_AND_extract_text_from_pdf(self):
        """Test du fileHandeler et extract_text_from_pdf"""

        #Actual
        with open(self.weblinks_file, "r") as f:
            lignes = f.readlines()
        lien1 = lignes[0].strip()

        #Expected
        with open(self.expected_dir / "testweb1.txt", "r", encoding="utf-8") as f1:
            saved_web1 = f1.read()
        with open(self.txt_file1, "r", encoding="utf-8") as f1, open(self.txt_file2, "r", encoding="utf-8") as f2:
            saved_txt = f1.read()
        with open(self.expected_dir / "testpdf1.txt", "r", encoding="utf-8") as f1:
            saved_pdf1 = f1.read()
        with open(self.expected_dir / "testpdf4.txt", "r", encoding="utf-8") as f4:
            saved_pdf_scan = f4.read()
        with open(self.expected_dir / "testdocx1.txt", "r", encoding="utf-8") as f1:
            saved_docx1 = f1.read()
        with open(self.expected_dir / "testmd1.txt", "r", encoding="utf-8") as f1:
            saved_md1 = f1.read()
        with open(self.expected_dir / "testtex1.txt", "r", encoding="utf-8") as f1:
            saved_tex1 = f1.read()
        with open(self.expected_dir / "testimage5.txt", "r", encoding="utf-8") as f5:
            saved_image5 = f5.read()

        self.assertTrue(SourceImporter.are_texts_similar(SourceImporter.extract_file_handler(str(lien1)), saved_web1))
        self.assertTrue(SourceImporter.are_texts_similar(SourceImporter.extract_file_handler(str(self.txt_file1)), saved_txt))
        self.assertTrue(SourceImporter.are_texts_similar(SourceImporter.extract_file_handler(str(self.docx_file1)), saved_docx1))
        self.assertTrue(SourceImporter.are_texts_similar(SourceImporter.extract_file_handler(str(self.md_file1)), saved_md1))
        self.assertTrue(SourceImporter.are_texts_similar(SourceImporter.extract_file_handler(str(self.tex_file1)), saved_tex1))
        self.assertTrue(SourceImporter.are_texts_similar(SourceImporter.extract_file_handler(str(self.image_file5)), saved_image5))

        #Test de extract_text_from_pdf() ; Ne peux retourner True que si la fonction appelle les bonnes sous fonctions.
        self.assertTrue(SourceImporter.are_texts_similar(SourceImporter.extract_file_handler(str(self.pdf_file1)), saved_pdf1))
        self.assertTrue(SourceImporter.are_texts_similar(SourceImporter.extract_file_handler(str(self.pdf_file4)), saved_pdf_scan))

    def test_calculate_text_similarity(self):
        """Test pour calculate_text_similarity"""
        self.assertEqual(SourceImporter.calculate_text_similarity("Hello world", "Hello world"), 100.0)
        self.assertEqual(SourceImporter.calculate_text_similarity("Hello world", "Goodbye moon"), 0.0)
        self.assertEqual(SourceImporter.calculate_text_similarity("", ""), 0.0)
        self.assertEqual(SourceImporter.calculate_text_similarity("Hello Hello world", "Hello world"), 100.0)

    def test_are_texts_similar(self):
        """Test pour are_texts_similar"""
        self.assertTrue(SourceImporter.are_texts_similar("Hello world", "Hello world", 50))
        self.assertFalse(SourceImporter.are_texts_similar("Hello world", "Goodbye world", 50))
        self.assertFalse(SourceImporter.are_texts_similar("Hello world", "Hello everyone", 80))
        self.assertTrue(SourceImporter.are_texts_similar("Hello world world", "Hello world", 50))


if __name__ == "__main__":
    unittest.main()
