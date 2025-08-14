"""
SystemEngine.py
===============

Module utilitaire pour la gestion de fichiers dans le projet Podcast Generator.

Rôles :
- Sauvegarder du texte dans des fichiers `.txt`.


Notes :
- Le module n'assure plus la compatibilité directe entre OS (Windows/Linux/Mac) comme rôle principal.

This module centralizes file operations management for the Podcast Generator project.
"""

from pathlib import Path

def save_text_to_file(directory: str, filename: str, text: str) -> str:
    """
       Description:
           Sauvegarde un texte dans un fichier .txt à l'intérieur d'un dossier existant.
           Saves text into a .txt file inside an existing directory.

       Notes:
           - Le dossier doit exister avant l'exécution de la fonction.
           - The directory must exist before executing the function.

       Libraries:
           pathlib.Path

       Args:
           directory (str): Chemin du dossier où sauvegarder le fichier.
                            Path of the directory where the file should be saved.
           filename (str): Nom du fichier à créer (avec ou sans extension).
                           Name of the file to create (with or without an extension).
           text (str): Contenu à écrire dans le fichier.
                       Content to write into the file.

       Returns:
           str: Le chemin complet du fichier sauvegardé.
                The full path of the saved file.
    """
    # Vérifier si l'extension .txt est présente, sinon l'ajouter.
    # Ensure the .txt extension is present, otherwise add it.
    if not filename.lower().endswith(".txt"):
        filename += ".txt"

    # Création du chemin complet du fichier.
    # Create the full file path.
    file_path = Path(directory) / filename

    # Ouverture du fichier en mode écriture avec encodage UTF-8.
    # Open the file in write mode with UTF-8 encoding.
    with file_path.open("w", encoding="utf-8") as file:
        file.write(text)

    # Retourner le chemin du fichier sauvegardé.
    # Return the path of the saved file.
    return str(file_path)