"""
PromptTextAnalyzer.py
======================

Ce module regroupe tous les prompts textuels utilisés par TextAnalyzer.py
et PodcastScriptGenerator.py pour interagir avec les modèles LLM (locaux ou serveurs).

Contenu :
- PROMPTS_RAG : Ensemble multilingue de prompts pour la génération de résumés, mots-clés, thèmes,
  regroupement de concepts et création de scripts de podcast.
- TITLE_PROMPTS : Prompts spécifiques à la génération automatique de titres de dialogues.

Notes :
- Tous les prompts sont préformatés avec des espaces réservés pour l'injection dynamique de contenu.
- Le module est indépendant et ne contient pas de logique exécutable.

This module centralizes all RAG and podcast generation prompts in a multilingual fashion
for consistency and easy maintenance.
"""

PROMPTS_RAG = {
    "fr": {
        "summary_rag": (
            "Génère un résumé structuré et informatif du texte suivant,"
            "Chaque phrase doit exprimer une idée claire ou un fait important,"
            "Évite les paraphrases, privilégie un style factuel et concis.:```"
        ),
        "keywords": (
            "Voici un texte. Extrait les mots-clés pertinents et informatifs,"
            "Évite les mots vides. Retourne une liste à puces synthétique.:```"
        ),
        "themes": (
            "Identifie les grands thèmes de ce résumé,"
            "Donne entre 5 et 8 titres clairs et thématiques, sans phrases.:```"
        ),
        "grouping": (
            "Voici une liste de concepts extraits d’un texte,"
            "Regroupe les termes qui désignent la même idée ou un concept proche,"
            "Retourne une liste nettoyée, avec un seul terme par groupe.:```"
        ),
        "podcast_script": (
            "Tu es un scénariste expert en podcasts.\n\n"
            "Ta mission :\nCréer un script structuré en 4 parties thématiques (avec titres et contenu),\n"
            "comprenant aussi une introduction engageante et une conclusion fluide.\n\n"
            "Style narratif : {style}\n\n"
            "Résumé global : {summary}\n"
            "Extraits importants : {top_chunks}\n"
            "Thèmes : {themes}\n"
            "Mots-clés : {keywords}\n\n"
            "Structure attendue :\nINTRO:\n...\nPARTIE 1: <Titre>\n...\nPARTIE 2: <Titre>\n...\nPARTIE 3: <Titre>\n...\nPARTIE 4: <Titre>\n...\nOUTRO:\n..."
        )
    },
    "en": {
        "summary_rag": (
            "Generate a clear and structured summary of the following text,"
            "Each sentence should convey a distinct idea or relevant fact,"
            "Avoid paraphrasing, keep the style dense and informative.:```"
        ),
        "keywords": (
            "Extract the most relevant and informative keywords from the text,"
            "Avoid stopwords. Return a concise bullet-point list.:```"
        ),
        "themes": (
            "Identify the main themes covered in this summary,"
            "Return 5 to 8 explicit and concise section titles only.:```"
        ),
        "grouping": (
            "Here is a list of concepts extracted from a text,"
            "Group together those that refer to the same or similar ideas,"
            "Return a cleaned list with one representative term per group.:```"
        ),
        "podcast_script": (
            "You are an experienced podcast writer.\n\n"
            "Your task:\nCreate a script structured into 4 thematic sections, each with a clear title and meaningful content.\n"
            "Start with an engaging introduction and finish with a thoughtful conclusion.\n\n"
            "Narrative style: {style}\n\n"
            "Global summary: {summary}\n"
            "Key supporting excerpts: {top_chunks}\n"
            "Main themes: {themes}\n"
            "Keywords to include: {keywords}\n\n"
            "Expected structure:\nINTRO:\n...\nPART 1: <Title>\n...\nPART 2: <Title>\n...\nPART 3: <Title>\n...\nPART 4: <Title>\n...\nOUTRO:\n..."
        )
    },
    "ja": {
        "summary_rag": (
            "以下のテキストから、明確かつ構造的な要約を作成してください,"
            "各文は、重要な事実や明確なアイデアを伝える必要があります,"
            "言い換えを避け、情報量の多い簡潔な文体でまとめてください。:```"
        ),
        "keywords": (
            "以下のテキストから重要なキーワードを抽出してください,"
            "助詞や一般的な単語は避けてください。箇条書きで返してください。:```"
        ),
        "themes": (
            "この要約から主なテーマを特定してください,"
            "5～8個の簡潔で明確なセクションタイトルを返してください。:```"
        ),
        "grouping": (
            "以下はテキストから抽出された概念のリストです,"
            "同じ意味や関連する意味を持つ項目をグループ化してください,"
            "各グループにつき1つの代表語のみを返してください。:```"
        ),
        "podcast_script": (
            "あなたは経験豊富なポッドキャストの脚本家です。\n\n"
            "タスク：\n4つのテーマに沿ったセクションに分けて、各セクションにわかりやすいタイトルと内容をつけて構成してください。\n"
            "魅力的な導入文（イントロ）と、締めくくりのアウトロを含めてください。\n\n"
            "ナレーションスタイル：{style}\n\n"
            "全体の要約：{summary}\n"
            "重要な補足内容：{top_chunks}\n"
            "カバーすべきテーマ：{themes}\n"
            "含めるべきキーワード：{keywords}\n\n"
            "構成例：\nINTRO:\n...\nパート1: <タイトル>\n...\nパート2: <タイトル>\n...\nパート3: <タイトル>\n...\nパート4: <タイトル>\n...\nOUTRO:\n..."
        )
    },
    "zh-cn": {
        "summary_rag": (
            "请根据以下文本生成结构清晰、信息丰富的摘要,"
            "每句话应传达一个明确的事实或核心观点,"
            "避免重复和同义改写，保持表达紧凑。:```"
        ),
        "keywords": (
            "请提取此文本中最关键的关键词，避免停用词,"
            "返回精炼的项目符号列表。:```"
        ),
        "themes": (
            "请根据该摘要列出主要主题,"
            "仅返回5至8个简明扼要的主题标题。:```"
        ),
        "grouping": (
            "以下是从文本中提取的概念列表,"
            "请将具有相似或相同含义的词语归为一组，并仅返回每组中的一个代表词。:```"
        ),
        "podcast_script": (
            "你是一位经验丰富的播客脚本编写者。\n\n"
            "任务：\n撰写一个结构清晰的播客剧本，包括四个主题部分，每部分需有明确标题和实质内容。\n"
            "剧本应以吸引人的开头（INTRO）开始，并以总结性结尾（OUTRO）结束。\n\n"
            "风格类型：{style}\n\n"
            "整体摘要：{summary}\n"
            "关键内容片段：{top_chunks}\n"
            "需要覆盖的主题：{themes}\n"
            "关键词：{keywords}\n\n"
            "结构示例：\nINTRO:\n...\n部分1：<标题>\n...\n部分2：<标题>\n...\n部分3：<标题>\n...\n部分4：<标题>\n...\nOUTRO:\n..."
        )

    },
    "zh-tw": {
        "summary_rag": (
            "請根據以下內容生成清晰、結構化的摘要,"
            "每句話應該表達一個明確的想法或重要事實,"
            "避免冗詞或重複敘述，風格應簡潔而有資訊量。:```"
        ),
        "keywords": (
            "以下のテキストから重要なキーワードを日本語で抽出してください。:```"
            "技術用語も含め、簡潔に記述し、箇条書きで返してください。:```"
        ),
        "themes": (
            "この要約から主なテーマを日本語で特定してください。:```"
            "5～8個の簡潔で明確なタイトルのみ返してください。:```"
        ),
        "grouping": (
            "以下是從文本中提取的概念清單,"
            "請將意思相近或相同的項目歸為一組，並為每組選擇一個代表詞返回。:```"
        ),
        "podcast_script": (
            "你是一位資深的 Podcast 腳本撰寫者。\n\n"
            "任務：\n撰寫一份包含四個主題段落的腳本，每段需有明確的標題與內容，\n"
            "開頭請設計為引人入勝的 INTRO，結尾為具總結性的 OUTRO。\n\n"
            "敘述風格：{style}\n\n"
            "整體摘要：{summary}\n"
            "重要內容摘錄：{top_chunks}\n"
            "核心主題：{themes}\n"
            "應納入的關鍵字：{keywords}\n\n"
            "預期結構：\nINTRO:\n...\n第1段：<標題>\n...\n第2段：<標題>\n...\n第3段：<標題>\n...\n第4段：<標題>\n...\nOUTRO:\n..."
        )
    }
}
