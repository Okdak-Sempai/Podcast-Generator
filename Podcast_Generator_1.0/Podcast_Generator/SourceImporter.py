"""
SourceImporter.py
==================

Module responsable de l'importation et de l'extraction de texte depuis diverses sources
pour le projet Podcast Generator.

Rôles :
- Détecter le type de fichier ou d'URL fourni et appliquer l'extraction adaptée.
- Gérer l'extraction de texte pour : .txt, .pdf, .docx, .md, .tex, images (.jpg, .png, .webp), et pages web.
- Appliquer de l'OCR automatique si nécessaire (PDF scannés, images).
- Détecter automatiquement la langue dominante du texte extrait.
- Fournir des outils de comparaison textuelle basique (similarité).

Principales bibliothèques utilisées :
- PyPDF2, fitz (PyMuPDF), Tesseract OCR, BeautifulSoup, Selenium, langdetect, markdown.

Notes :
- Tous les textes extraits sont retournés sous forme brute (str), sans enrichissement.
- Ce module est conçu pour être multiplateforme (Windows/Linux/Mac).

This module extracts raw text content from various sources (files or URLs) for further processing
in the Podcast Generator project.
"""

import re
import PyPDF2
import fitz
from PIL import Image
from pytesseract import pytesseract
from pathlib import Path
import io
from langdetect import detect
import markdown
import docx2txt
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import time
from datetime import datetime

def extract_file_handler(path):
    """
    Description:
        Sélectionne la fonction d'extraction adaptée en fonction du type de fichier ou de l'URL et retourne le texte extrait.
        Selects the appropriate extraction function based on the file type or URL and returns the extracted text.

    Args:
        path (str): Chemin vers le fichier ou URL.
                    Path to the file or URL.

    Returns:
        str or None: Texte extrait si l'extraction aboutit, sinon None.
                     Extracted text if successful, otherwise None.
    """
    #Timers Start
    start_time = time.time()
    print(f"Début extract_file_handler : {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    url_pattern = re.compile(r'^https?://')
    if url_pattern.match(path):
        #Timers End
        end_time = time.time()
        elapsed = end_time - start_time
        print(f"Fin extract_file_handler: {datetime.now().strftime('%Y-%m-%d %H:%M')} — Temps écoulé : {elapsed:.2f} secondes")
        return extract_text_from_web(path)
    else:
        extension = Path(path).suffix.lower()
        if extension == '.txt':
            # Timers End
            end_time = time.time()
            elapsed = end_time - start_time
            print(f"Fin extract_file_handler: {datetime.now().strftime('%Y-%m-%d %H:%M')} — Temps écoulé : {elapsed:.2f} secondes")
            return extract_text_from_txt(path)
        elif extension == '.pdf':
            # Timers End
            end_time = time.time()
            elapsed = end_time - start_time
            print(f"Fin extract_file_handler: {datetime.now().strftime('%Y-%m-%d %H:%M')} — Temps écoulé : {elapsed:.2f} secondes")
            return extract_text_from_pdf(path)
        elif extension == '.docx':
            # Timers End
            end_time = time.time()
            elapsed = end_time - start_time
            print(
                f"Fin extract_file_handler: {datetime.now().strftime('%Y-%m-%d %H:%M')} — Temps écoulé : {elapsed:.2f} secondes")
            return extract_text_from_docx(path)
        elif extension == '.md':
            # Timers End
            end_time = time.time()
            elapsed = end_time - start_time
            print(
                f"Fin extract_file_handler: {datetime.now().strftime('%Y-%m-%d %H:%M')} — Temps écoulé : {elapsed:.2f} secondes")
            return extract_text_from_markdown(path)
        elif extension == '.tex':
            # Timers End
            end_time = time.time()
            elapsed = end_time - start_time
            print(
                f"Fin extract_file_handler: {datetime.now().strftime('%Y-%m-%d %H:%M')} — Temps écoulé : {elapsed:.2f} secondes")
            return extract_text_from_latex(path)
        elif extension in ['.jpeg', '.jpg','.png', '.webp']:
            # Timers End
            end_time = time.time()
            elapsed = end_time - start_time
            print(
                f"Fin extract_file_handler: {datetime.now().strftime('%Y-%m-%d %H:%M')} — Temps écoulé : {elapsed:.2f} secondes")
            return extract_text_from_image(path)
    print(path,"n'est pas valide.")
    # Timers End
    end_time = time.time()
    elapsed = end_time - start_time
    print(
        f"Fin extract_file_handler: {datetime.now().strftime('%Y-%m-%d %H:%M')} — Temps écoulé : {elapsed:.2f} secondes")
    return None

def extract_text_from_web(url):
    """
    Description:
        Extraction du texte à partir d'une URL en gérant les pop-ups de cookies.
        Extracts text from a URL handling dynamic cookies pop-ups.

    Notes:
        S'il n'y a pas de résultat après l'extraction, il est préférable de générer un PDF de la page (Ctrl + P) et d'effectuer l'extraction sur le fichier PDF.
        If the extraction does not return any results, it is better to generate a PDF of the page (Ctrl + P) and perform the extraction on the PDF file.

    Args:
        url (str): L'URL à traiter.
                   The URL to process.

    Returns:
        str: Texte extrait de la page web.
             The extracted text from the web page.
    """
    # Configuration du navigateur en mode headless pour ne pas afficher d'interface graphique.
    # Configure the browser in headless mode to avoid GUI display.
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=options)

    try:
        # Chargement de la page
        # Load the page.
        driver.get(url)

        # Attendre que le document soit complètement chargé
        # Wait until the document is fully loaded.
        WebDriverWait(driver, 10).until(lambda d: d.execute_script('return document.readyState') == 'complete')

        # Tenter de trouver et cliquer sur le bouton d'acceptation des cookies si présent.
        # Attempt to find and click the cookie acceptance button if present.
        try:
            accept_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accepter')]"))
            )
            accept_button.click()
            # Attendre que le pop-up disparaisse
            # Wait for the pop-up to disappear.
            WebDriverWait(driver, 5).until(
                EC.invisibility_of_element((By.XPATH, "//button[contains(text(), 'Accepter')]"))
            )
        except TimeoutException:
            # Si le bouton n'est pas trouvé ou non interactif, continuer sans interruption.
            # If the button is not found or clickable, continue without interruption.
            pass

        # Attendre que le corps de la page soit visible (contenu principal chargé).
        # Wait until the page body is visible (main content loaded).
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.TAG_NAME, 'body'))
        )

        # Récupérer le contenu rendu par le navigateur.
        # Retrieve the rendered content from the browser.
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        # Supprimer le bandeau de cookies s'il existe (exemple avec OneTrust).
        # Remove the cookie banner if it exists (e.g., OneTrust).
        cookie_banner = soup.find('div', id='onetrust-banner-sdk')
        if cookie_banner:
            cookie_banner.decompose()

        # Retourne le texte brut extrait.
        # Return the extracted plain text.
        return soup.get_text(separator=' ', strip=True)
    finally:
        # Fermer le navigateur pour libérer les ressources.
        # Quit the browser to free resources.
        driver.quit()

#TXT
def extract_text_from_txt(file_path):
    """
    Description:
        Extraction du texte à partir d'un fichier .txt.
        Extracts text from a .txt file.

    Args:
        file_path (str): Chemin du fichier texte.
                         Path to the text file.

    Returns:
        str: Texte contenu dans le fichier.
             Text content from the file.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()


#PDF
def extract_text_from_pdf_text(file_path):
    """
    Description:
        Extraction du texte d'un PDF contenant du texte sélectionnable.
        Extracts text from a PDF with selectable text.

    Args:
        file_path (str): Chemin du fichier PDF.
                         Path to the PDF file.

    Returns:
        str: Texte extrait du PDF.
             Text extracted from the PDF.
    """
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        return "".join([page.extract_text() for page in reader.pages])


def extract_text_from_pdf_scanned(file_path, languages='eng+fra+jpn+chi_sim+chi_tra'):
    """
    Description:
        Extrait le texte d'un PDF scanné en utilisant l'OCR et ajuste la reconnaissance selon la langue détectée.
        Extracts text from a scanned PDF using OCR and adjusts recognition based on the detected language.

    Args:
        file_path (str): Chemin du PDF.
                         Path to the PDF file.
        languages (str): Langues initiales pour Tesseract (ex: 'eng+fra+jpn+chi_sim+chi_tra').
                         Initial languages for Tesseract (e.g., 'eng+fra+jpn+chi_sim+chi_tra').

    Returns:
        str: Texte extrait du PDF.
             Text extracted from the PDF.
    """
    text = ""
    pdf_document = fitz.open(file_path)

    for page_num in range(pdf_document.page_count):
        page = pdf_document.load_page(page_num)
        pix = page.get_pixmap()

        # Convertir en image PIL.
        # Convert to a PIL image.
        image_bytes = pix.tobytes("png")
        image = Image.open(io.BytesIO(image_bytes))
        image = image.convert('L')

        # Premier OCR avec toutes les langues.
        # First OCR with all specified languages.
        page_text = pytesseract.image_to_string(image, lang=languages).strip()
        text += page_text + "\n"

        # Détection de la langue dominante.
        # Detect the dominant language.
        main_lang = detect_main_language(page_text)

        # Si la langue détectée est différente, refaire un OCR plus précis.
        # If the detected language differs, perform a more precise OCR.
        if main_lang != languages:
            page_text = pytesseract.image_to_string(image, lang=main_lang).strip()
            text += page_text + "\n"

    pdf_document.close()
    return text.strip()


def extract_text_from_pdf(file_path):
    """"
    Description:
        Extraction générale du texte d'un PDF.
        Utilise la fonction d'extraction de texte sélectionnable[extract_text_from_pdf_text(file_path)], si c'est un echec, utilisation de extract_text_from_pdf_scanned(file_path, languages='eng+fra+jpn+chi_sim+chi_tra').
        General extraction of text from a PDF.
        Attempts to extract selectable text using extract_text_from_pdf_text(file_path). If this fails, it falls back to OCR processing with extract_text_from_pdf_scanned(file_path, languages='eng+fra+jpn+chi_sim+chi_tra').        Uses standard extraction if possible, otherwise falls back to OCR.

    Args:
        file_path (str): Chemin du PDF.
                         Path to the PDF file.

    Returns:
        str: Texte extrait du PDF.
             Text extracted from the PDF.
    """
    extracted_text = extract_text_from_pdf_text(file_path)
    if not extracted_text.strip():
        extracted_text = extract_text_from_pdf_scanned(file_path)
    return extracted_text

#DOCX
def extract_text_from_docx(file_path):
    """
    Description:
        Extrait le texte d'un fichier DOCX.
        Extracts text from a DOCX file.

    Args:
        file_path (str): Chemin du fichier DOCX.
                         Path to the DOCX file.

    Returns:
        str: Texte extrait du DOCX.
             Text extracted from the DOCX.
    """
    return docx2txt.process(file_path)

#Markdown/MD
def extract_text_from_markdown(file_path):
    """
    Description:
        Extraction du texte à partir d'un fichier Markdown.
        Convertit le Markdown en HTML puis en texte brut.
        Extracts text from a Markdown file.
        Converts Markdown to HTML and then extracts plain text.

    Args:
        file_path (str): Chemin du fichier Markdown.
                         Path to the Markdown file.

    Returns:
        str: Texte extrait du Markdown.
             Text extracted from the Markdown.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        markdown_content = file.read()

    # Convertir le markdown en HTML.
    # Convert Markdown to HTML.
    html = markdown.markdown(markdown_content)

    # Utiliser BeautifulSoup pour retirer les balises HTML.
    # Use BeautifulSoup to remove HTML tags.
    soup = BeautifulSoup(html, 'html.parser')
    return soup.get_text()


#Latex/TEX
def extract_text_from_latex(file_path):
    """
    Description:
        Extraction du texte à partir d'un fichier LaTeX.
        Tente d'utiliser pylatexenc pour une conversion précise, sinon applique un nettoyage basique.
        Extracts text from a LaTeX file.
        Tries to use pylatexenc for precise conversion, otherwise applies basic cleanup.

    Args:
        file_path (str): Chemin du fichier LaTeX.
                         Path to the LaTeX file.

    Returns:
        str: Texte extrait du LaTeX.
             Text extracted from the LaTeX.
    """
    # Lecture du fichier.
    # Read the file.
    with open(file_path, 'r', encoding='utf-8') as file:
        latex_content = file.read()

    try:
        from pylatexenc.latex2text import LatexNodes2Text
        text = LatexNodes2Text().latex_to_text(latex_content)
    except ImportError:
        # Si pylatexenc n'est pas installé, appliquer un nettoyage basique.
        # If pylatexenc is not installed, perform basic cleanup.
        text = re.sub(r'\\[a-zA-Z]+\*?(?:\[[^\]]*\])?(?:\{[^\}]*\})?', '', latex_content)

    return text


#Image
def extract_text_from_image(file_path, languages='eng+fra+jpn+chi_sim+chi_tra'):
    """
    Description:
        Extrait le texte d'une image en utilisant l'OCR avec optimisation linguistique.
        Extracts text from an image using OCR with language optimization.

    Notes:
        Il faut des images propres et sans trop de bruit et avec une seule langue.
        For good text extraction from images, you need clean images with minimal noise and a single language.

    Args:
        file_path (str): Chemin vers l'image.
                         Path to the image file.
        languages (str): Langues initiales pour Tesseract (ex: 'eng+fra+jpn+chi_sim+chi_tra').
                         Initial languages for Tesseract (e.g., 'eng+fra+jpn+chi_sim+chi_tra').

    Returns:
        str: Texte extrait de l'image.
             Text extracted from the image.
    """
    try:
        image = Image.open(file_path)
        # Améliorer la reconnaissance en convertissant en niveaux de gris.
        # Enhance recognition by converting the image to grayscale.
        image = image.convert('L')

        # Premier OCR avec toutes les langues spécifiées.
        # First OCR using all specified languages.
        text = pytesseract.image_to_string(image, lang=languages).strip()

        # Détection de la langue dominante.
        # Detect the dominant language.
        main_lang = detect_main_language(text)

        # Si la langue détectée diffère, refaire l'OCR avec la langue détectée.
        # If the detected language differs, redo OCR using the detected language.
        if main_lang != languages:
            text = pytesseract.image_to_string(image, lang=main_lang).strip()

        return text

    except Exception as e:
        print(f"Erreur lors du traitement de l'image : {e}")
        return ""

def detect_main_language(text):
    """
       Description:
           Détecte la langue principale du texte fourni et retourne le code de langue pour Tesseract.
           Detects the main language of the provided text and returns the language code for Tesseract.
       
       Notes:
           Retourne anglais par défaut.
           Returns english by default.

       Args:
           text (str): Texte à analyser.
                       Text to analyze.

       Returns:
           str: Code de langue (ex: 'eng', 'fra', etc.). Par défaut 'eng' si la détection échoue.
                Language code (e.g., 'eng', 'fra', etc.). Defaults to 'eng' if detection fails.
       """
    try:
        lang = detect(text)
        lang_map = {
            'en': 'eng',
            'fr': 'fra',
            'ja': 'jpn',
            'zh-cn': 'chi_sim',
            'zh-tw': 'chi_tra'
        }
        return lang_map.get(lang, 'eng')
    except:
        return 'eng'

#Comparators
def are_texts_similar(text1, text2, threshold=0.69):
    """
    Description:
        Compare deux textes et retourne True si leur similarité dépasse un seuil donné.
        Compares two texts and returns True if their similarity exceeds a given threshold.

    Args:
        text1 (str): Premier texte.
                     First text.
        text2 (str): Deuxième texte.
                     Second text.
        threshold (float, optional): Seuil minimal de similarité (attendu en pourcentage de 0 à 100). Par défaut : 0.69.
                                     Minimum similarity threshold (expected as a percentage between 0 and 100). Default: 0.69.
                                     # Note: Vérifiez que le seuil correspond bien à l'échelle de pourcentage.

    Returns:
        bool: True si la similarité est supérieure ou égale au seuil, sinon False.
              True if similarity is greater than or equal to the threshold, otherwise False.
    """
    # Formalisation des textes en ensembles de mots.
    # Convert texts to sets of words.
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())

    # Calcul de la similarité via l'intersection et l'union des ensembles de mots.
    # Calculate similarity using the intersection and union of the word sets.
    intersection = len(words1 & words2)
    union = len(words1 | words2)

    similarity = (intersection / union) * 100 if union > 0 else 0
    return similarity >= threshold


def calculate_text_similarity(text1, text2):
    """
    Description:
        Compare deux textes et retourne leur pourcentage de similarité.
        Compares two texts and returns the percentage of similarity between them.

    Args:
        text1 (str): Premier texte.
                     First text.
        text2 (str): Deuxième texte.
                     Second text.

    Returns:
        float: Pourcentage de similarité entre les deux textes (de 0 à 100).
               Similarity percentage between the two texts (from 0 to 100).
    """
    # Formalisation des textes en ensembles de mots.
    # Convert texts to sets of words.
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())

    # Calcul de la similarité via l'intersection et l'union des ensembles de mots.
    # Calculate similarity using the intersection and union of the word sets.
    intersection = len(words1 & words2)
    union = len(words1 | words2)

    similarity = (intersection / union) * 100 if union > 0 else 0
    return similarity