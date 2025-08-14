import os
import sys

# le chemin parent pour accéder à PodcastExporter.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from PodcastExporter import save_podcast_offline


PODCAST_PATH = "Podcast_Generator/Voices/Hanekawa.wav"
PODCAST_PATH = "Podcast_Generator/VoicesPreview/Female/AlexandraHisakawa.wav"

def test_save_podcast_offline() :

    print("Debut de sauvegard")

    i=save_podcast_offline(PODCAST_PATH)

    if (i==1) :
        print("reussi")

if __name__ == "__main__":
    test_save_podcast_offline()