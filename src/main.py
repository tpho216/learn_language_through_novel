from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Union, Dict, Any
from openai import OpenAI, OpenAIError
from json import JSONDecodeError
import json
import os
import logging
import re
from pathlib import Path
from dotenv import load_dotenv

from src.services.piper_tts import PiperTTSProvider
from src.services.openai_tts import OpenAITTSProvider

load_dotenv()

logger = logging.getLogger("learn_language_through_novel")
app = FastAPI(title="Chinese Learning Pipeline API")


SYSTEM_PROMPT = """
You are a linguistic analysis engine for a Chinese language learning application.

Your tasks:
1. Read the FULL Chinese chapter provided by the user from beginning to end.
2. Detect whether the chapter contains a chapter title.
3. Identify all characters appearing in the chapter.
4. Infer narrator presence if applicable.
5. Infer character gender ONLY when reasonably clear from name or context.
6. DO NOT invent facts.
7. DO NOT rewrite, paraphrase, or modify any original Chinese text.
8. Your output MUST be valid JSON.
9. Do NOT include explanations, markdown, or extra commentary.

CHAPTER TITLE INFERENCE RULES:
- The chapter title is usually located at the VERY BEGINNING of the Chinese text.
- It may include:
  - Words like: 章, 回, 卷, 节
  - Numbers (Arabic or Chinese): 1, 10, 一, 十, 百
  - Patterns such as:
    - 第九百八十九章 天象巨变
    - 第12章
    - 卷一 开端
- If the first line or first sentence clearly looks like a chapter title, extract it verbatim.
- If NO clear chapter title is present, set the title fields to null.
- DO NOT guess or fabricate a title.

VIETNAMESE TITLE TRANSLATION RULES:
- For the chapter title, you MUST provide THREE fields:
  1. title (Chinese original, exact text or null)
  2. title_vi_ref:
     - Use ONLY if a Vietnamese reference title is clearly provided and matches the Chinese title.
     - If no matching Vietnamese reference exists, set this field to null.
  3. title_vi_ai:
     - ALWAYS translate directly from the Chinese title using AI.
     - If the Chinese title is null, this must also be null.
     - The translation must be neutral, faithful, and literal.
- The merged Vietnamese title logic will be handled later; just output the fields correctly.

VOICE RULES:
- Narrator uses a neutral voice.
- Teaching explanations use a "teacher" voice.
- Character voices should be inferred later; for now, only provide hints.

Return JSON with the following structure ONLY:

{
  "chapter_meta": {
    "title": "... | null",
    "title_vi_ref": "... | null",
    "title_vi_ai": "... | null",
    "has_narrator": true,
    "language": "zh"
  },
  "characters": [
    {
      "name": "韩立",
      "role": "main_character",
      "gender_hint": "male | female | unknown",
      "notes": "short factual note if needed"
    }
  ]
}
"""


# =========================
# Request / Response Models
# =========================

class AnalyzeChapterRequest(BaseModel):
    chapter_id: str
    text_zh: str
    text_vi_ref: Optional[str] = None


class SentenceMeta(BaseModel):
    order: int
    text_zh: str
    character: str
    voice: str   # narrator | male | female


class SceneMeta(BaseModel):
    scene_id: str
    description: str
    sentences: List[SentenceMeta]


class AnalyzeChapterResponse(BaseModel):
    chapter_id: str
    scenes: List[SceneMeta]


# Enrichment models
class SentenceForEnrichment(BaseModel):
    order: int
    text_zh: str
    text_vi: Optional[str] = None
    text_vi_ref: Optional[str] = None


class EnrichSentenceRequest(BaseModel):
    chapter_id: str
    sentence: SentenceForEnrichment


class WordMeaning(BaseModel):
    word: str
    pinyin: str
    hanvi: Optional[str] = None
    meaning_vi: str
    used_as_vietnamese_loanword: bool = False


class PhraseExample(BaseModel):
    zh: str
    pinyin: str
    hanvi: Optional[str] = None
    vi: str
    new_words: Optional[List['WordMeaning']] = None


class Phrase(BaseModel):
  text: str
  pinyin: str
  hanvi: Optional[str] = None
  meaning_vi: Optional[str] = None
  hsk: Optional[Union[int, str]] = None
  use_in_modern_language: bool = False
  phrase_examples: Optional[List[PhraseExample]] = None


class Example(BaseModel):
    zh: str
    pinyin: str
    hanvi: Optional[str] = None
    vi: Optional[str] = None


class EnrichSentenceResponse(BaseModel):
  order: int
  text_zh: str
  pinyin: str
  phrases: List[Phrase]
  hsk_overall: Optional[Union[int, str]] = None
  examples: List[Example]
  hanzi_explanation: Optional[str] = None
  grammar_explanation: Optional[str] = None
  # Optional translations carried through from upstream sentence if available
  text_vi: Optional[str] = None
  text_vi_ref: Optional[str] = None
  text_vi_ai: Optional[str] = None


# ---------------------
# Deterministic TTS models
# ---------------------

class TTSSegment(BaseModel):
    order: int
    lang: str  # zh | vi | en
    voice: str  # narrator | teacher | character
    style: str  # neutral | slow | explanatory | natural
    text: str
    pause_after_ms: int
    meta: Optional[Dict[str, Any]] = None  # Optional metadata: pinyin, etc.


class PrepareTTSSegmentsRequest(BaseModel):
    enriched_sentence: EnrichSentenceResponse
    # Optional list of keys/paths to include; if None, defaults are used.
    selection: Optional[List[str]] = None
    # Optional chapter title metadata to speak before the sentence
    chapter_title_zh: Optional[str] = None
    chapter_title_vi: Optional[str] = None
    # Optional language cue overrides, e.g., {"zh": "中文", "vi": "Tiếng Việt"}
    lang_cues: Optional[Dict[str, str]] = None
    # Optional field cue overrides, e.g., {"title.zh": {"zh": "标题"}}
    field_cues: Optional[Dict[str, Dict[str, str]]] = None


class PrepareTTSSegmentsResponse(BaseModel):
    segments: List[TTSSegment]


class SynthesizeTTSRequest(BaseModel):
    segments: List[TTSSegment]
    output_dir: str = "audio"
    provider: str = "piper"  # "piper" or "openai"
    # Provider-specific settings
    piper_binary: Optional[str] = None
    openai_model: Optional[str] = "standard"  # "standard" or "hd"
    # Naming options
    filename_prefix: str = "segment"


class AudioSegmentResult(BaseModel):
    order: int
    success: bool
    output_path: Optional[str] = None
    duration_seconds: Optional[float] = None
    error: Optional[str] = None


class SynthesizeTTSResponse(BaseModel):
    total_segments: int
    successful: int
    failed: int
    results: List[AudioSegmentResult]
    output_dir: str




# =====================
# Routes
# =====================

@app.get("/")
async def root():
    return {
        "status": "ok",
        "message": "LLM + Piper pipeline server running"
    }


@app.post("/llm/analyze_chapter")
async def analyze_chapter(req: AnalyzeChapterRequest):

    prompt = f"""
You are analyzing a Chinese xianxia fiction chapter.

IMPORTANT RULES:
- The original and authoritative text is CHINESE.
- DO NOT modify, rewrite, paraphrase, or correct any Chinese text.
- Preserve Chinese sentences EXACTLY as written.
- Vietnamese text, if provided, is ONLY a reference.
- If Chinese and Vietnamese differ, ALWAYS trust Chinese.

CHAPTER TITLE DETECTION RULES:
- Carefully examine the VERY BEGINNING of the Chinese text.
- The chapter title is usually:
  - The first standalone line, OR
  - A header before the main narrative begins.
- Chapter titles often include:
  - Numbers (Arabic or Chinese): 1, 10, 一, 十, 百
  - Keywords such as: 第, 卷, 章, 回, 节
- Examples:
  - 第九百九十八章 不期而遇
  - 第六卷 通天灵宝
  - 卷一 初入修真界
- If such a title is present, extract it EXACTLY as written.
- If no clear chapter title exists, set chapter_meta.title = null.
- DO NOT invent or guess a chapter title.

CHAPTER TITLE VIETNAMESE RULES:
- If a Chinese chapter title exists:
  - title_vi_ai:
    - ALWAYS translate directly from the Chinese title.
    - The translation should be natural, neutral, and faithful.
  - title_vi_ref:
    - Use ONLY if the provided Vietnamese reference clearly contains a matching chapter title.
    - If the Vietnamese reference has a line starting with "Chương" followed by a number (e.g., "Chương 1000"), treat that line as the Vietnamese title reference and set title_vi_ref to it.
    - Otherwise set to null.
- If chapter_meta.title is null:
  - title_vi_ai = null
  - title_vi_ref = null

VIETNAMESE TRANSLATION RULES (SENTENCE LEVEL):
- For EACH Chinese sentence, you MUST output TWO Vietnamese fields:
  1. text_vi_ref:
     - Use ONLY if the provided Vietnamese reference clearly matches the Chinese sentence.
     - If no matching Vietnamese sentence exists, set this field to null.
  2. text_vi_ai:
     - ALWAYS translate directly from the Chinese sentence.
     - The translation should be natural, neutral, and faithful.
     - Do NOT add interpretation or explanation.

VOICE & DIALOGUE CLASSIFICATION RULES:
- Set is_dialogue = false AND voice = "narrator" when:
  - The sentence is narration, description, or action.
  - There is no explicit spoken dialogue.

- Set is_dialogue = true when:
  - The sentence is clearly spoken aloud, OR
  - Written as direct speech (quotation marks, colon), OR
  - Contains speech verbs such as:
    说, 道, 问, 喝道, 冷笑道, 喃喃道, 低声道, 开口说道

- Use a character voice (male | female | unknown) ONLY if is_dialogue = true.
- If the speaker is known from context, set "character" to that name.
- If the speaker is unknown, set character = "unknown".
- If gender is unclear, set voice = "unknown".

YOUR TASK:
1. Read the ENTIRE Chinese chapter first to understand context.
2. Detect and extract the chapter title if present.
3. Produce Vietnamese title translations as specified above.
4. Split the chapter into scenes based on narrative or logical changes.
5. For each sentence:
   - Preserve the original Chinese text exactly.
   - Identify narration vs dialogue.
   - Assign character, voice, and is_dialogue.
   - Produce Vietnamese translations as specified above.

Return ONLY valid JSON following this schema:

{{
  "chapter_id": "{req.chapter_id}",
  "chapter_meta": {{
    "title": "... | null",
    "title_vi_ref": "... | null",
    "title_vi_ai": "... | null",
    "has_narrator": true,
    "language": "zh"
  }},
  "scenes": [
    {{
      "scene_id": "...",
      "description": "...",
      "sentences": [
        {{
          "order": 1,
          "text_zh": "...",
          "text_vi_ref": null,
          "text_vi_ai": "...",
          "character": "...",
          "voice": "narrator | male | female | unknown",
          "is_dialogue": true | false
        }}
      ]
    }}
  ]
}}

Chinese chapter (authoritative):
<<<
{req.text_zh}
>>>

Vietnamese reference (optional):
<<<
{req.text_vi_ref or "N/A"}
>>>
"""

    try:
        access_token = os.getenv("OPENAI_API_KEY")
        if not access_token:
            raise HTTPException(
                status_code=500,
                detail="OPENAI_API_KEY is not set"
            )

        client = OpenAI(api_key=access_token)

        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=1,
        )

        raw = response.choices[0].message.content

        try:
          resp = json.loads(raw)
        except JSONDecodeError as e:
          # LLM trả text không phải JSON
          raise HTTPException(
            status_code=502,
            detail={
              "error": "LLM_RETURNED_INVALID_JSON",
              "message": str(e),
              "raw_output": raw
            }
          )

        # --- Minimal fallback if LLM returned no scenes ---
        if not resp.get("scenes"):
          resp["scenes"] = [
            {
              "scene_id": "scene-001",
              "description": "Auto-generated placeholder",
              "sentences": [
                {
                  "order": 1,
                  "text_zh": req.text_zh,
                  "text_vi_ai": "(placeholder translation)",
                  "text_vi": "(placeholder translation)",
                  "character": "narrator",
                  "voice": "narrator",
                  "is_dialogue": False,
                }
              ],
            }
          ]

        # --- Ensure chapter_meta title_vi_ref is populated from provided Vietnamese reference when missing ---
        chapter_meta = resp.setdefault("chapter_meta", {})
        if "title" not in chapter_meta:
          chapter_meta["title"] = None
        if "title_vi_ai" not in chapter_meta:
          chapter_meta["title_vi_ai"] = None
        chapter_meta.setdefault("title_vi_ref", None)

        # --- Normalize translation fields and enforce presence ---
        for scene in resp.get("scenes", []):
          if not scene.get("sentences"):
            scene["sentences"] = [
              {
                "order": 1,
                "text_zh": req.text_zh,
                "text_vi_ai": "(placeholder translation)",
                "text_vi": "(placeholder translation)",
                "character": "narrator",
                "voice": "narrator",
                "is_dialogue": False,
              }
            ]
          for s in scene.get("sentences", []):
            # Ensure AI translation field exists
            if "text_vi_ai" not in s and "text_vi" in s:
              s["text_vi_ai"] = s.get("text_vi")
            if "text_vi" not in s and "text_vi_ai" in s:
              s["text_vi"] = s.get("text_vi_ai")

            # attach chapter-level reference if missing
            if "text_vi_ref" not in s:
              s["text_vi_ref"] = req.text_vi_ref if getattr(req, "text_vi_ref", None) else None

            # if ref present prefer merged text
            if s.get("text_vi_ref") and not s.get("text_vi"):
              s["text_vi"] = s.get("text_vi_ref")

            # ensure text_vi present
            if "text_vi" not in s:
              s["text_vi"] = s.get("text_vi_ai") or s.get("text_vi_ref") or ""

            has_ref = bool(s.get("text_vi_ref"))
            has_ai = bool(s.get("text_vi_ai"))
            has_vi = bool(s.get("text_vi"))

            if not (has_ref or has_ai or has_vi):
              raise HTTPException(
                status_code=502,
                detail={
                  "error": "LLM_MISSING_VI",
                  "message": "LLM did not produce any Vietnamese translation for a sentence",
                  "chapter_id": req.chapter_id,
                  "scene_id": scene.get("scene_id"),
                  "sentence_order": s.get("order"),
                  "sentence": s.get("text_zh"),
                },
              )

            missing = [f for f in ("text_vi_ref", "text_vi_ai", "text_vi") if not s.get(f)]
            if missing:
              logger.warning(
                "Missing vi fields for chapter=%s scene=%s order=%s missing=%s",
                req.chapter_id,
                scene.get("scene_id"),
                s.get("order"),
                missing,
              )

        return resp

    except OpenAIError as e:
        # Lỗi từ OpenAI SDK (rate limit, auth, model, etc.)
        raise HTTPException(
            status_code=502,
            detail={
                "error": "OPENAI_API_ERROR",
                "message": str(e)
            }
        )

    except Exception as e:
      if isinstance(e, HTTPException):
        raise
      print("Unexpected error in /llm/analyze_chapter:", str(e))
      # Lỗi không lường trước
      raise HTTPException(
        status_code=500,
        detail={
          "error": "INTERNAL_SERVER_ERROR",
          "message": str(e)
        }
      )

@app.post("/llm/enrich_sentence", response_model=EnrichSentenceResponse)
async def enrich_sentence(req: EnrichSentenceRequest):
    """Enrich a single sentence with pinyin, phrases, HSK level, examples, and teacher explanation."""

    # Build context with text_vi_ref if available
    vi_context = f"Vietnamese reference translation: {req.sentence.text_vi_ref}" if req.sentence.text_vi_ref else ""
    vi_merged = f"Vietnamese (merged): {req.sentence.text_vi}" if req.sentence.text_vi else ""

    prompt = f"""
You are a master of Chinese–Hán Việt–Vietnamese linguistics,
a specialist in vocabulary, classical literature, and historical language transfer.

Your role:
- Act as: "Một chuyên gia từ vựng, văn học, ngôn ngữ tiếng Trung – Hán Việt – Việt"
- Teach clearly, precisely, and conservatively.

AUTHORITATIVE SOURCE RULES:
- The original Chinese sentence is authoritative.
- DO NOT modify or rewrite any Chinese text.
- Vietnamese reference text (text_vi_ref), if provided, is a learning aid ONLY.

EXPLANATION RULES:
When explaining vocabulary or phrases:
1. Start from the ORIGINAL Chinese word or phrase.
2. Provide the standard Hán Việt reading (if applicable).
  - Luôn kèm pinyin đối ứng với cách đọc Hán Việt (ví dụ: Hán Việt + pinyin).
3. Explain how that Hán Việt term is used or transformed in modern Vietnamese.
4. If text_vi_ref exists:
   - Use it to explain translation choices and word mapping.
   - Point out why certain Vietnamese words were chosen.
5. If there is a WELL-KNOWN historical, literary, or etymological reason:
   - Briefly mention it.
   - DO NOT speculate or invent obscure history.
   - If unsure, OMIT historical explanation.

PEDAGOGICAL STYLE:
- Use calm, teacher-like explanations.
- Explain like teaching a serious language learner.
- Avoid casual tone, jokes, or metaphors.

GRAMMAR TEACHING RULES:
- You MUST include a field named "grammar_explanation" in the output JSON.
- The grammar explanation must focus on HOW the Chinese sentence is formed.
- Explain:
  1. Sentence structure (word order and roles)
  2. Important grammar particles or constructions
  3. Literary or classical grammar if present
  4. How this structure is naturally rendered in Vietnamese

- DO NOT:
  - Rewrite the Chinese sentence
  - Paraphrase the Chinese sentence
  - Translate word-by-word mechanically
  - Invent grammar rules

- If the sentence uses standard modern grammar:
  - State that it follows a normal modern Chinese pattern.

- If the sentence uses xianxia / literary narration:
  - Briefly explain the stylistic grammar difference.

- Keep explanations concise, factual, and instructional.
- Write as a teacher explaining grammar to a learner.

CONTENT TO PRODUCE:
For the given Chinese sentence, provide:
- Pinyin with tone marks
- Key vocabulary and phrases with:
  - text: the Chinese phrase
  - pinyin: romanization
  - hanvi: direct Hán Việt reading (if applicable)
  - meaning_vi: Vietnamese meaning
  - hsk: HSK level (1–6 or "Above HSK")
  - use_in_modern_language: boolean indicating if phrase is used in modern Chinese
  - If use_in_modern_language = true:
    - Provide 1-2 example sentences (HSK 1-2 level) using that specific phrase
    - Each example must include: Chinese text, pinyin, Vietnamese translation
    - For any new words in examples, provide:
      - word: the Chinese word
      - pinyin: romanization
      - hanvi: direct Hán Việt reading (if applicable)
      - meaning_vi: Vietnamese meaning
      - used_as_vietnamese_loanword: true if this Hán Việt word is commonly used as a borrowed word in Vietnamese literature/language
- Hán Việt readings (where applicable)
- Vietnamese meaning and reasoning
- HSK level classification (1–6 or "Above HSK")
- 1–2 natural daily-life example sentences (Chinese + Vietnamese) for the entire sentence
- Explanations MUST be in Vietnamese

OUTPUT RULES:
- Output ONLY valid JSON.
- No markdown.
- No commentary outside JSON.
- All explanations must appear inside structured fields.

Return ONLY valid JSON matching this schema:

{{
  "order": {req.sentence.order},
  "text_zh": "{req.sentence.text_zh}",
  "pinyin": "...",
  "phrases": [
    {{
      "text": "...",
      "pinyin": "...",
      "hanvi": "...",
      "meaning_vi": "...",
      "hsk": "Above HSK",
      "use_in_modern_language": true,
      "phrase_examples": [
        {{
          "zh": "...",
          "pinyin": "...",
          "hanvi": "...",
          "vi": "...",
          "new_words": [
            {{
              "word": "...",
              "pinyin": "...",
              "hanvi": "...",
              "meaning_vi": "...",
              "used_as_vietnamese_loanword": true
            }}
          ]
        }}
      ]
    }}
  ],
  "hsk_overall": "Above HSK",
  "examples": [
    {{"zh": "...", "pinyin": "...", "hanvi": "...", "vi": "..."}}
  ],
  "hanzi_explanation": "...",
  "grammar_explanation": "..."
}}

Chinese sentence: {req.sentence.text_zh}
{vi_context}
{vi_merged}
"""

    try:
        access_token = os.getenv("OPENAI_API_KEY")
        if not access_token:
            raise HTTPException(status_code=500, detail="OPENAI_API_KEY is not set")

        client = OpenAI(api_key=access_token)
        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": "You are a master of Chinese-Vietnamese linguistics (Chuyên gia ngôn ngữ Trung - Hán Việt - Việt). Respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=1,
        )

        raw = response.choices[0].message.content
        try:
            data = json.loads(raw)
        except JSONDecodeError as e:
            raise HTTPException(
                status_code=502,
                detail={
                    "error": "ENRICH_INVALID_JSON",
                    "message": str(e),
                    "raw_output": raw
                }
            )

        return data

    except OpenAIError as e:
        raise HTTPException(
            status_code=502,
            detail={
                "error": "OPENAI_API_ERROR",
                "message": str(e)
            }
        )

    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        print("Unexpected error in /llm/enrich_sentence:", str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "error": "INTERNAL_SERVER_ERROR",
                "message": str(e)
            }
        )


def split_explanation_by_language(text: str) -> List[tuple[str, str]]:
  """
  Split explanation text by language, keeping Chinese and Vietnamese separate.
  
  For text like: "Các từ Hán như 诸位 (chư vị), 道友 (đạo hữu) đều là..."
  Returns: [('vi', 'Các từ Hán như '), ('zh', '诸位'), ('vi', ' (chư vị), '), ('zh', '道友'), ...]
  """
  import re
  
  if not text:
    return []
  
  # Pattern: match either Chinese characters or non-Chinese text
  # Chinese: [\u4E00-\u9FFF]+ (one or more CJK characters)
  # Non-Chinese: [^\u4E00-\u9FFF]+ (one or more non-CJK characters)
  pattern = r'([\u4E00-\u9FFF]+|[^\u4E00-\u9FFF]+)'
  matches = re.findall(pattern, text)
  
  result = []
  for match in matches:
    if re.match(r'^[\u4E00-\u9FFF]+$', match):
      # Pure Chinese
      result.append(('zh', match))
    else:
      # Vietnamese (with mixed Latin/spaces/punctuation)
      # Skip if it's just whitespace
      if match.strip():
        result.append(('vi', match))
  
  return result


@app.post("/llm/prepare_tts_segments", response_model=PrepareTTSSegmentsResponse)
async def prepare_tts_segments(req: PrepareTTSSegmentsRequest):
  """Deterministically convert an enriched sentence into TTS-ready segments (no LLM)."""

  def lang_cue(lang: str) -> str:
    defaults = {
      "zh": "中文",
      "vi": "Tiếng Việt",
      "en": "English",
    }
    if req.lang_cues and lang in req.lang_cues:
      return req.lang_cues[lang]
    return defaults.get(lang, "")

  def field_cue(field: str, lang: str) -> str:
    defaults = {
      "title.zh": {"zh": "标题"},
    "title.vi": {"vi": "Tựa đề"},
    "sentence.text_zh": {"zh": "原文句子"},
    "sentence.text_vi": {"vi": "Câu tiếng Việt"},
    "sentence.text_vi_ref": {"vi": "Câu tiếng Việt tham khảo"},
    "sentence.text_vi_ai": {"vi": "Câu tiếng Việt AI"},
    "phrases[].text": {"zh": "词汇"},
    "phrases[].meaning_vi": {"vi": "Nghĩa tiếng Việt"},
    "phrases[].phrase_examples[].zh": {"zh": "示例"},
    "phrases[].phrase_examples[].vi": {"vi": "Ví dụ tiếng Việt"},
    "phrases[].phrase_examples[].new_words[].word": {"zh": "新词汇"},
    "phrases[].phrase_examples[].new_words[].meaning_vi": {"vi": "Nghĩa từ mới"},
    "examples[].zh": {"zh": "示例"},
    "examples[].vi": {"vi": "Ví dụ tiếng Việt"},
    "hanzi_explanation": {"zh": "汉字解释", "vi": "Giải thích Hán tự"},
    "grammar_explanation": {"zh": "语法解释", "vi": "Giải thích ngữ pháp"}
    }
    merged = defaults.copy()
    if req.field_cues:
      for k, v in req.field_cues.items():
        merged[k] = {**merged.get(k, {}), **v}
    return merged.get(field, {}).get(lang, "")

  segments: List[TTSSegment] = []
  order_counter = 1
  last_lang: Optional[str] = None
  last_field: Optional[str] = None

  def add(lang: str, text: Optional[str], field: str, voice: str = "narrator", style: str = "neutral", pause_ms: int = 600, meta: Optional[Dict[str, Any]] = None):
    nonlocal order_counter, last_lang, last_field
    if not text:
      return
    
    # Only add prefix if field or language changed
    prefix_parts = []
    if field != last_field or lang != last_lang:
      cue = lang_cue(lang)
      if cue:
        prefix_parts.append(cue)
      field_label = field_cue(field, lang)
      if field_label:
        prefix_parts.append(field_label)
    
    if prefix_parts:
      text = f"{' '.join(prefix_parts)}, {text}"
    
    segments.append(
      TTSSegment(
        order=order_counter,
        lang=lang,
        voice=voice,
        style=style,
        text=text,
        pause_after_ms=pause_ms,
        meta=meta,
      )
    )
    last_lang = lang
    last_field = field
    order_counter += 1

  sel = req.selection or [
    "title.zh",
    "title.vi",
    "sentence.text_zh",
    "sentence.text_vi_ref",
    "sentence.text_vi_ai",
    "sentence.text_vi",
    "phrases[].text",
    "phrases[].meaning_vi",
    "phrases[].phrase_examples[].zh",
    "phrases[].phrase_examples[].vi",
    "examples[].zh",
    "examples[].vi",
    "hanzi_explanation",
    "grammar_explanation",
  ]

  s = req.enriched_sentence

  # titles (if provided)
  if "title.zh" in sel and req.chapter_title_zh:
    add("zh", req.chapter_title_zh, field="title.zh", voice="narrator", style="neutral", pause_ms=800)
  if "title.vi" in sel and req.chapter_title_vi:
    add("vi", req.chapter_title_vi, field="title.vi", voice="teacher", style="explanatory", pause_ms=700)

  # sentence-level fields
  if "sentence.text_zh" in sel:
    meta_zh = {}
    if s.pinyin:
      meta_zh["pinyin"] = s.pinyin
    add("zh", s.text_zh, field="sentence.text_zh", voice="narrator", style="neutral", pause_ms=600, meta=meta_zh if meta_zh else None)

  vi_text = None
  if "sentence.text_vi_ref" in sel and getattr(s, "text_vi_ref", None):
    vi_text = s.text_vi_ref
  elif "sentence.text_vi" in sel and getattr(s, "text_vi", None):
    vi_text = s.text_vi
  elif "sentence.text_vi_ai" in sel and getattr(s, "text_vi_ai", None):
    vi_text = s.text_vi_ai

  if vi_text:
    target_field = "sentence.text_vi_ref" if getattr(s, "text_vi_ref", None) else "sentence.text_vi" if getattr(s, "text_vi", None) else "sentence.text_vi_ai"
    add("vi", vi_text, field=target_field, voice="teacher", style="explanatory", pause_ms=600)

  # phrases
  if hasattr(s, "phrases") and s.phrases:
    for ph in s.phrases:
      if "phrases[].text" in sel:
        meta_phrase = {}
        if ph.pinyin:
          meta_phrase["pinyin"] = ph.pinyin
        if ph.hanvi:
          meta_phrase["hanvi"] = ph.hanvi
        add("zh", ph.text, field="phrases[].text", voice="teacher", style="neutral", pause_ms=400, meta=meta_phrase if meta_phrase else None)
      if "phrases[].meaning_vi" in sel and ph.meaning_vi:
        add("vi", ph.meaning_vi, field="phrases[].meaning_vi", voice="teacher", style="explanatory", pause_ms=500)
      if ph.phrase_examples:
        for ex in ph.phrase_examples:
          if "phrases[].phrase_examples[].zh" in sel:
            meta_ex = {}
            if ex.pinyin:
              meta_ex["pinyin"] = ex.pinyin
            if ex.hanvi:
              meta_ex["hanvi"] = ex.hanvi
            add("zh", ex.zh, field="phrases[].phrase_examples[].zh", voice="character", style="natural", pause_ms=400, meta=meta_ex if meta_ex else None)
          if "phrases[].phrase_examples[].vi" in sel and ex.vi:
            add("vi", ex.vi, field="phrases[].phrase_examples[].vi", voice="character", style="natural", pause_ms=400)
          # new words within phrase examples
          if ex.new_words:
            for nw in ex.new_words:
              if "phrases[].phrase_examples[].new_words[].word" in sel:
                meta_nw = {}
                if nw.pinyin:
                  meta_nw["pinyin"] = nw.pinyin
                if nw.hanvi:
                  meta_nw["hanvi"] = nw.hanvi
                add("zh", nw.word, field="phrases[].phrase_examples[].new_words[].word", voice="teacher", style="neutral", pause_ms=400, meta=meta_nw if meta_nw else None)
              if "phrases[].phrase_examples[].new_words[].meaning_vi" in sel and nw.meaning_vi:
                add("vi", nw.meaning_vi, field="phrases[].phrase_examples[].new_words[].meaning_vi", voice="teacher", style="explanatory", pause_ms=400)

  # examples
  if hasattr(s, "examples") and s.examples:
    for ex in s.examples:
      if "examples[].zh" in sel:
        meta_example = {}
        if ex.pinyin:
          meta_example["pinyin"] = ex.pinyin
        if ex.hanvi:
          meta_example["hanvi"] = ex.hanvi
        add("zh", ex.zh, field="examples[].zh", voice="character", style="natural", pause_ms=400, meta=meta_example if meta_example else None)
      if "examples[].vi" in sel and ex.vi:
        add("vi", ex.vi, field="examples[].vi", voice="character", style="natural", pause_ms=400)

  # hanzi explanation - split by language, keep Chinese and Vietnamese separate
  # Skip very short segments (whitespace/punctuation only)
  # Only add prefix for the first segment
  if "hanzi_explanation" in sel and s.hanzi_explanation:
    lang_segments = split_explanation_by_language(s.hanzi_explanation)
    first_segment = True
    for lang, text in lang_segments:
      # Skip if only whitespace or punctuation
      cleaned = text.strip()
      # Simple check: if it has at least one alphanumeric character or CJK
      if cleaned and re.search(r'[\w\u4E00-\u9FFF]', cleaned):
        voice = "narrator" if lang == "zh" else "teacher"
        if first_segment:
          # Add with prefix
          add(lang, text, field="hanzi_explanation", voice=voice, style="explanatory", pause_ms=800)
          first_segment = False
        else:
          # Manually add segment without prefix
          segments.append(
            TTSSegment(
              order=order_counter,
              lang=lang,
              voice=voice,
              style="explanatory",
              text=text,
              pause_after_ms=800,
              meta=None,
            )
          )
          order_counter += 1

  # grammar explanation - split by language, keep Chinese and Vietnamese separate
  # Skip very short segments (whitespace/punctuation only)
  # Only add prefix for the first segment
  if "grammar_explanation" in sel and s.grammar_explanation:
    lang_segments = split_explanation_by_language(s.grammar_explanation)
    first_segment = True
    for lang, text in lang_segments:
      # Skip if only whitespace or punctuation
      cleaned = text.strip()
      # Simple check: if it has at least one alphanumeric character or CJK
      if cleaned and re.search(r'[\w\u4E00-\u9FFF]', cleaned):
        voice = "narrator" if lang == "zh" else "teacher"
        if first_segment:
          # Add with prefix
          add(lang, text, field="grammar_explanation", voice=voice, style="explanatory", pause_ms=1000)
          first_segment = False
        else:
          # Manually add segment without prefix
          segments.append(
            TTSSegment(
              order=order_counter,
              lang=lang,
              voice=voice,
              style="explanatory",
              text=text,
              pause_after_ms=1000,
              meta=None,
            )
          )
          order_counter += 1

  return PrepareTTSSegmentsResponse(segments=segments)


@app.post("/tts/synthesize", response_model=SynthesizeTTSResponse)
async def synthesize_tts_segments(req: SynthesizeTTSRequest):
    """
    Synthesize audio files from TTS segments using configured provider.
    
    Supports:
    - Piper (local neural TTS)
    - OpenAI TTS API
    
    Each segment is synthesized to a separate audio file in the output directory.
    """
    
    # Initialize provider
    if req.provider == "piper":
        provider = PiperTTSProvider(piper_binary=req.piper_binary or "piper")
    elif req.provider == "openai":
        provider = OpenAITTSProvider(model=req.openai_model or "standard")
    else:
        raise HTTPException(status_code=400, detail=f"Unknown TTS provider: {req.provider}")
    
    # Ensure output directory exists
    output_dir = Path(req.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    results = []
    successful = 0
    failed = 0
    
    for segment in req.segments:
        # Generate output filename
        # Format: {prefix}_{order:04d}_{lang}_{voice}.{ext}
        ext = "mp3" if req.provider == "openai" else "wav"
        filename = f"{req.filename_prefix}_{segment.order:04d}_{segment.lang}_{segment.voice}.{ext}"
        output_path = output_dir / filename
        
        try:
            # Synthesize
            result = await provider.synthesize(
                text=segment.text,
                output_path=output_path,
                voice=segment.voice,
                lang=segment.lang,
                style=segment.style
            )
            
            if result.get("success"):
                results.append(AudioSegmentResult(
                    order=segment.order,
                    success=True,
                    output_path=str(output_path),
                    duration_seconds=result.get("duration_seconds") or result.get("estimated_duration_seconds")
                ))
                successful += 1
            else:
                results.append(AudioSegmentResult(
                    order=segment.order,
                    success=False,
                    error=result.get("error", "Unknown error")
                ))
                failed += 1
                
        except Exception as e:
            results.append(AudioSegmentResult(
                order=segment.order,
                success=False,
                error=str(e)
            ))
            failed += 1
    
    return SynthesizeTTSResponse(
        total_segments=len(req.segments),
        successful=successful,
        failed=failed,
        results=results,
        output_dir=str(output_dir)
    )