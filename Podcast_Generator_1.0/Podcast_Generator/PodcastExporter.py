import os
import shutil
import platform

def save_podcast_offline(podcast_path: str) -> int:

    """
    sauvegarde d'un podcast hors ligne selon le système d'exploitation.

    Args:
        podcast_path (str): Chemin du fichier podcast

    Returns:
        int: Code d'exécution
            0 = Succès
            1 = Fichier introuvable
            2 = OS non supporté
            3 = Erreur inattendue
    """

    try:
        if not os.path.isfile(podcast_path):
            print(f" Fichier introuvable : {podcast_path}")
            return 1
	    
        #list des systemes d'exploitation acceptes
        valid_os = ["windows", "linux", "mac"]
        
        current_os = platform.system().lower()
        filename = os.path.basename(podcast_path) #extraire le nom du fichier
        
        if (current_os =="darwin") : current_os ="mac"

        if current_os == "windows":
            dest_dir = os.path.expanduser("~/PodcastsOfflineWindows") #convertir le chemin relatif en un chemin absolu complet
        elif current_os == "linux":
            dest_dir = os.path.expanduser("~/PodcastsOfflineLinux")
        elif current_os == "mac":
            dest_dir = os.path.expanduser("~/PodcastsOfflineMac")
        else:
            print(f" OS non supporté : {current_os} ")
            return 2

        os.makedirs(dest_dir, exist_ok=True)
        dest_path = os.path.join(dest_dir, filename) # Chemin de destination final

        shutil.copy2(podcast_path, dest_path)  # Copier le fichier dans le répertoire de destination

        print(f" Podcast sauvegardé dans : {dest_path} ")
        return 0

    except Exception as e:
        print(f" Erreur inattendue : {e} ")
        return 3



def publish_to_Deezer(platform: str, file_path: str) -> int:
    """
    Simule la publication d'un fichier audio sur Deezer.
    
    Args:
        platform: Le nom de la plateforme dans ce cas  'Deezer'
        file_path : Le chemin vers le fichier audio à publier

    Returns:
        int: Code d'exécution (0: succès, 1: fichier introuvable, 2: mauvaise plateforme, 3: erreur)
    """

    try:
        if platform.lower() != "deezer":
            print("Plateforme non supportée.")
            return 2

        if not os.path.isfile(file_path):
            print("Fichier introuvable :", file_path)
            return 1

        # Simuler la publication (dans la réalité, il faudrait passer par un partenaire Deezer)
        print(f"Publication du fichier '{file_path}' sur {platform}...")
        
        #ici ajout de la logique de publication
        
        print("Publication réussie !")
        return 0

    except Exception as e:
        print("Erreur inattendue :", e)
        return 3


def publish_to_Spotify(platform: str, file_path: str) -> int:

    try:
        if platform.lower() != "spotify":
            print("Plateforme non supportée.")
            return 2

        if not os.path.isfile(file_path):
            print("Fichier introuvable :", file_path)
            return 1

        print(f"Publication du fichier '{file_path}' sur {platform}...")
        
        #ici ajout de la logique de publication
        
        print("Publication réussie !")
        return 0

    except Exception as e:
        print("Erreur inattendue :", e)
        return 3
