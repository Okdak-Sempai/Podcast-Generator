# Podcast Generator

Podcast Generator est un outil multiplateforme qui automatise la création de podcasts conversationnels à partir de textes, de documents, d’images ou de pages web. Il fonctionne entièrement hors‑ligne grâce à des modèles de langage locaux au format GGUF et à une synthèse vocale neurale (XTTS v2). Les voix, tons et langues sont personnalisables. L’outil exporte des fichiers audio au format MP3/WAV/MP4 et peut simuler une publication sur des plateformes de streaming.

---

## Sommaire

- [Fonctionnalités principales](#fonctionnalités-principales)
- [Modules et architecture](#modules-et-architecture)
- [Menus et usage indépendant des modules](#menus-et-usage-indépendant-des-modules)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Personnalisation](#personnalisation)
- [Conseils & Bonnes pratiques](#conseils--bonnes-pratiques)
- [Licence et contribution](#licence-et-contribution)

---

## Fonctionnalités principales

- **Importation et extraction de sources** : lit de nombreux formats de fichiers (.txt, .pdf, .docx, .md, .tex, images .jpg/.png/.webp) et pages web. L’OCR est appliqué si nécessaire. Détection automatique du type et de la langue du contenu.
- **Analyse de texte & RAG** : découpage contrôlable des textes, résumé de documents, extraction de mots clés, identification de thèmes. Utilisation de modèles locaux ou serveurs compatibles OpenAI.
- **Génération de script** : création d’un scénario narratif structuré (intro, 4 parties, conclusion), gestion des personnages, voix et langues, sauvegarde/chargement du script en JSON.
- **Génération de dialogues** : conversion automatique du script en dialogue réaliste multi-intervenants, attribution dynamique des noms et tons, gestion stricte de la syntaxe (nom(tone): phrase), prompts multilingues.
- **Synthèse vocale avancée** : chaque ligne du dialogue est transformée en audio XTTS, application des presets de ton (vitesse, émotion), attribution des voix, fusion audio en un unique fichier WAV.
- **Gestion centralisée des tons** : presets de ton (speed, emotion) définis dans un fichier JSON, ajout/suppression/preview.
- **Synthèse TTS unifiée** : encapsulation XTTS v2 (Coqui), fonction unique pour générer l’audio, évite les imports circulaires.
- **Gestion flexible des modèles** : interface unique pour interroger un modèle local GGUF via llama_cpp ou un serveur local compatible OpenAI, adaptation automatique aux limites de contexte, réglage des tokens et température.
- **Exportation** : sauvegarde du podcast au bon format/dossier, simulation de publication sur plateforme (ex : Deezer).

---

## Modules et architecture

L’application est organisée en modules spécialisés et indépendants :

| Module                  | Rôle                                                                                                                                                      |
|-------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **SourceImporter**      | Détection automatique du type de fichier/URL, extraction du texte de nombreux formats et application de l’OCR. Retourne le texte brut et la langue.         |
| **TextAnalyzer**        | Analyse du texte : détection de la langue, découpage pour le RAG, résumés, extraction de mots clés et thèmes. Permet de forcer la langue de sortie.        |
| **PodcastScriptGenerator** | Génère un scénario structuré (intro, 4 parties, conclusion), sauvegarde/charge des scripts JSON, assigne des personnages/voix, normalise le dialogue.    |
| **PodcastDialogueGenerator** | Transforme le script en dialogue réaliste, attribue noms/tons, génère un titre, sauvegarde au format balisé prêt pour la TTS.                        |
| **PromptDialogueGenerator** | Centralise les prompts multilingues pour la génération de dialogue et de titres, impose une syntaxe stricte (nom(tone): phrase).                      |
| **TonePresetManager**   | Gère les presets de ton (vitesse, émotion), ajout/suppression/preview via tone_presets.json.                                                               |
| **PodcastGeneratorAudio** | Convertit chaque ligne du dialogue en audio XTTS, applique les presets de ton, attribue les voix, fusionne en un fichier audio unique.                   |
| **TTSWrapper**          | Encapsule XTTS v2 (Coqui), expose generate_audio() pour produire l’audio.                                                                                  |
| **LocalAIManager**      | Interface unique pour interroger un modèle local GGUF ou serveur OpenAI, réglage du contexte et des paramètres de génération.                              |
| **PodcastExporter**     | Sauvegarde le podcast hors ligne (MP3/WAV/MP4) et simule la publication sur une plateforme de streaming.                                                    |

---

## Menus et usage indépendant des modules

Chaque module expose des fonctions utilisables indépendamment du pipeline complet. Vous pouvez ainsi automatiser, tester ou intégrer Podcast Generator à d’autres outils :

| Module / menu             | Fonctions indépendantes                                          | Usage typique                                                                                   |
|---------------------------|------------------------------------------------------------------|-------------------------------------------------------------------------------------------------|
| **LocalAIManager**        | `call_llm(prompt, max_tokens, temperature)`                      | Interroger directement un modèle GGUF ou serveur OpenAI local pour des réponses personnalisées.  |
| **SourceImporter**        | `detect_file_type(path)`, `extract_text(path)`, `extract_text_from_url(url)` | Déterminer le type d’un fichier/URL, extraire le texte brut, appliquer l’OCR.                   |
| **TextAnalyzer**          | `detect_language(text)`, `split_text(text, max_tokens)`, `summarize_chunks(chunks, language)`, `extract_keywords(text, language)`, `find_themes(text, language)` | Décomposer, détecter la langue, résumer, extraire mots clés ou thèmes.                          |
| **PodcastScriptGenerator**| `generate_script_from_summary(summary, language)`, `save_script(script, path)`, `load_script(path)`, `associate_characters(script, voices)` | Créer un scénario à partir d’un résumé, gérer les scripts JSON, associer voix/personnages.      |
| **PodcastDialogueGenerator** | `generate_dialogue(script)`, `generate_title(dialogue)`        | Transformer un script en dialogue réaliste, générer un titre.                                   |
| **TonePresetManager**     | `list_presets()`, `add_preset(name, speed, emotion)`, `remove_preset(name)`, `preview_tone(text, preset)` | Gérer les presets de ton : consultation, ajout, suppression, pré‑écoute.                       |
| **PodcastGeneratorAudio** | `voice_for_character(character)`, `generate_line_audio(line, preset)`, `merge_audio(lines)`, `play_audio(path)` | Convertir une ligne en audio, choisir la voix, fusionner, écouter le résultat.                 |
| **PodcastExporter**       | `save_podcast_offline(file_path)`, `publish_to_Deezer(platform, file_path)` | Copier le fichier audio vers un emplacement ou simuler la publication sur une plateforme.        |

> Consultez les docstrings des modules pour plus de détails sur les paramètres et valeurs de retour.

---

## Installation

### Prérequis

- **Système d’exploitation** : Windows 10/11 (64 bits) testé et fonctionnel. macOS (≥ Monterey) supporté en théorie. Linux possible mais non garanti.
- **Python 3.11** : à installer avant le projet (`python --version` pour vérifier).
- **Matériel recommandé** : Intel Core i5 (10ᵉ génération) ou AMD Ryzen 5 (série 3000), 16 Go RAM (32 Go recommandé pour grands modèles), SSD avec ~10 Go libres. Un GPU NVIDIA (CUDA) accélère les performances.

### Étapes

1. **Téléchargez et extrayez le projet** :  
   Récupérez l’archive Podcast_Generator_1.0.zip sur GitHub et décompressez-la dans le dossier de travail.

   ```
   Podcast_Generator_1.0/
   ├── Podcast_Generator/      # Code source
   ├── Models/                 # Emplacement des modèles LLM (vide par défaut)
   ├── requirements.txt        # Dépendances Python
   ├── launcher_windows.bat    # Lanceur Windows
   ├── install_mac.command     # Prépare les scripts macOS
   ├── launcher_mac.command    # Lanceur macOS
   ```

2. **Installer llama-cpp-python** :  
   Clonez et compilez [llama-cpp-python](https://github.com/abetlen/llama-cpp-python) en suivant les instructions du dépôt (compilation spécifique à l’OS). Placez le dossier à la racine du projet.

3. **Créer un environnement virtuel et installer les dépendances** :
   ```bash
   python -m venv .venv
   source .venv/bin/activate              # Sous Windows : .venv\Scripts\activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Télécharger des modèles GGUF** :  
   Récupérez des modèles adaptés sur [Hugging Face](https://huggingface.co/) et placez-les dans le dossier Models/.  
   - `Mistral-Nemo-Instruct-2407-Q8_0` : français/anglais
   - `Qwen 1.5 – 7B – Chat Q8_0` : japonais/chinois

5. **Lancer l’application** :
   - **Windows** : double-cliquez sur `launcher_windows.bat`.
   - **macOS** : exécutez `install_mac.command` puis lancez avec `launcher_mac.command`.
   - **Linux** : activez l’environnement virtuel et lancez `python Podcast_Generator/mainTerminalUI.py`.

---

## Utilisation

Flux général :

1. **Importation des sources** : sélectionnez un fichier ou une URL. SourceImporter détecte le type, applique l’OCR si nécessaire, récupère le texte brut.
2. **Analyse du texte** : TextAnalyzer détecte la langue, segmente pour le RAG, extrait mots clés et thèmes, résume via modèle local ou serveur.
3. **Création du script** : PodcastScriptGenerator produit le scénario narratif structuré (intro, 4 parties, conclusion), personnalisation des personnages, voix et langues.
4. **Génération du dialogue** : PodcastDialogueGenerator transforme le script en dialogue entre intervenants, adapte les tons, génère un titre.
5. **Synthèse vocale** : PodcastGeneratorAudio convertit chaque réplique en audio, applique les presets, fusionne en un fichier unique. TTSWrapper fournit la synthèse XTTS.
6. **Exportation** : PodcastExporter sauvegarde le résultat au format MP3/WAV/MP4 et propose la publication simulée sur une plateforme.

---

## Personnalisation

- **Presets de ton** : caractéristiques vocales (vitesse, émotion) dans `tone_presets.json`. Gérez-les via TonePresetManager (ajout, suppression, preview).
- **Choix des voix** : chaque personnage est associé à une voix (ex : fr_male_1, en_female_1). Utilisez les voix XTTS incluses ou ajoutez les vôtres.
- **Langues** : support du français, anglais, japonais, chinois. La langue des prompts et du TTS est choisie automatiquement, mais peut être forcée.

---

## Conseils & bonnes pratiques

- **Sélection du modèle** : privilégiez un modèle GGUF adapté à votre langue et matériel. Les modèles compacts (Q4/Q5) consomment moins de RAM.
- **Gestion de la mémoire** : pour les grands modèles (7B+), 16–32 Go RAM sont recommandés. Un GPU NVIDIA compatible CUDA accélère le calcul.
- **Déconnexion d’internet** : le programme fonctionne hors-ligne avec les modèles locaux. Internet requis pour l’installation et le téléchargement des modèles.
- **Mise à jour des modèles** : remplacez ou ajoutez des modèles dans Models/ à tout moment, en vérifiant leur compatibilité.

---

## Licence et contribution

Ce projet est publié sous la licence **Public Read‑Only License (Permission Required for Reuse)** (voir [LICENSE](LICENSE)).  
Vous avez le droit de consulter et lire le code pour un usage personnel non commercial.  
Toute copie, modification, redistribution, intégration dans d’autres projets ou utilisation au-delà de la lecture nécessite une **autorisation écrite** du titulaire des droits.

Les suggestions et retours (issues, discussions) sont les bienvenus, mais toute contribution de code ou modification doit être explicitement validée et autorisée par le propriétaire du projet.

---

## À propos

Podcast Generator est destiné à la création de podcasts conversationnels multilingues, entièrement local et personnalisable. Les modules peuvent être utilisés indépendamment pour automatiser des tâches, tester des modèles, ou intégrer l’outil dans vos propres scripts.

Pour plus de détails sur chaque module, fonctions et intégration, consultez les commentaires et docstrings dans le code source.

---
