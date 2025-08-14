"""
PromptDialogueGenerator.py
===========================

Ce module regroupe tous les prompts utilisés pour transformer un texte brut en un dialogue réaliste
ainsi que pour générer un titre adapté, dans plusieurs langues (fr, en, ja, zh-cn, zh-tw).

Contenu :
- PROMPTS_DIALOGUE : Modèles de génération de dialogues entre participants.
- TITLE_PROMPTS : Modèles de génération de titres concis pour les dialogues.

Utilisation :
- Appelé dans `PodcastDialogueGenerator.py` pour générer les dialogues bruts à partir d'un script.
- Appelé pour générer dynamiquement un titre basé sur le contenu du dialogue.

Notes :
- Les formats exigés par les prompts sont stricts : (nom(tone): phrase).
- Les dialogues générés sont destinés à être transformés en audio via PodcastGeneratorAudio.py.

This module centralizes all multilingual prompts needed for dialogue and title generation
in the Podcast Generator project.
"""

PROMPTS_DIALOGUE = {
    "fr": (
        "Tu es un auteur de podcast.\n"
        "Tu dois transformer un texte en un **dialogue réaliste et cohérent**, exclusivement en français.\n"
        "⚠️ Tu dois écrire TOUT le dialogue uniquement en français, sauf pour les termes techniques ou citations exactes en anglais.\n\n"
        "Voici les participants : {participants}\n\n"
        "Suis **strictement** ce formalisme pour chaque intervention :\n"
        "nom(ton): discours\n\n"
        "Ne répond **rien d'autre que via ce formalisme**.\n\n"
        "Exemples valides :\n"
        "roger(content): salut.\n"
        "Marie(fâché): Quoi ?\n\n"
        "⚠️ Important :\n"
        "- Ne répète pas les définitions ou concepts déjà présentés dans les parties précédentes.\n"
        "- Si un concept a déjà été expliqué, développe-le, illustre-le ou applique-le à un nouveau contexte.\n\n"
        "Résumé des parties précédentes :\n{context}\n\n"
        "Texte actuel :\n{text}"
    ),
    "en": (
        "You are a podcast writer.\n"
        "You must transform a text into a **realistic and coherent dialogue**, strictly in English.\n"
        "⚠️ You must write the ENTIRE dialogue only in English, except for technical terms or exact quotes in other languages.\n\n"
        "Here are the participants: {participants}\n\n"
        "Strictly follow this format for each intervention:\n"
        "name(tone): speech\n\n"
        "Respond **only using this format**.\n\n"
        "Valid examples:\n"
        "roger(content): hi.\n"
        "Marie(angry): What?\n\n"
        "⚠️ Important:\n"
        "- Do not repeat definitions or concepts already presented in previous parts.\n"
        "- If a concept has already been explained, elaborate, illustrate or apply it in a new context.\n\n"
        "Summary of previous parts:\n{context}\n\n"
        "Current text:\n{text}"
    ),
    "ja": (
        "あなたはポッドキャストの作家です。\n"
        "テキストを**現実的で一貫性のある対話**に変換してください。\n"
        "⚠️ 対話全体を日本語のみで書いてください。技術用語や引用は例外です。\n\n"
        "参加者は次の通りです：{participants}\n\n"
        "各発言について、必ず次の形式を守ってください：\n"
        "名前(トーン): 発言\n\n"
        "**この形式以外の回答はしないでください**。\n\n"
        "有効な例：\n"
        "roger(content): こんにちは。\n"
        "Marie(怒り): 何？\n\n"
        "⚠️ 重要：\n"
        "- 前のパートですでに説明された定義や概念は繰り返さないでください。\n"
        "- 代わりに、それを発展させたり、例を挙げたり、新しい文脈で応用してください。\n\n"
        "前のパートの要約：\n{context}\n\n"
        "現在のテキスト：\n{text}"
    ),
    "zh-cn": (
        "你是一位播客编剧。\n"
        "你必须将文本转化为**真实且连贯的对话**，必须完全使用中文编写，除非是技术术语或引用。\n\n"
        "以下是参与者：{participants}\n\n"
        "请严格遵循以下格式来呈现每段发言：\n"
        "姓名(语气): 内容\n\n"
        "**只能使用这种格式回复**。\n\n"
        "有效示例：\n"
        "roger(content): 你好。\n"
        "Marie(生气): 什么？\n\n"
        "⚠️ 重要：\n"
        "- 不要重复已经在前面部分中解释过的定义或概念。\n"
        "- 如果某个概念已经讲过，请进一步扩展、举例或在新背景下应用它。\n\n"
        "前文摘要：\n{context}\n\n"
        "当前文本：\n{text}"
    ),
    "zh-tw": (
        "你是一位播客編劇。\n"
        "你必須將文字轉換為**真實且連貫的對話**，請全程使用繁體中文撰寫，除非是技術詞或精確引述。\n\n"
        "以下是參與者：{participants}\n\n"
        "請嚴格遵守以下格式來呈現每段發言：\n"
        "姓名(語氣): 內容\n\n"
        "**只能使用這種格式回覆**。\n\n"
        "有效範例：\n"
        "roger(content): 你好。\n"
        "Marie(生氣): 什麼？\n\n"
        "⚠️ 重要：\n"
        "- 不要重複前幾段已經說明過的定義或概念。\n"
        "- 若已說明過，請延伸、舉例或應用至不同情境。\n\n"
        "前文摘要：\n{context}\n\n"
        "目前內容：\n{text}"
    )
}
TITLE_PROMPTS = {
    "fr": "Voici un dialogue entre plusieurs participants. Génère un titre clair et court (max 10 mots), sans guillemets et Uniquement le titre :\n\n{text}",
    "en": "Here is a dialogue between several participants. Generate a clear and short title (max 10 words), without quotes. Output only the title:\n\n{text}",
    "ja": "これは複数の登場人物による対話です。短くて明確なタイトル（最大10語）を生成してください。引用符なしでタイトルのみを出力してください：\n\n{text}",
    "zh-cn": "以下是几位参与者之间的对话。生成一个清晰简短的标题（最多10个词），不要加引号，只输出标题：\n\n{text}",
    "zh-tw": "這是一段多位參與者的對話。請產生一個簡潔明確的標題（最多10個詞），不要加引號，只輸出標題：\n\n{text}"
}
