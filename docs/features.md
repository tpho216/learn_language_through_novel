# Features

## Overview
**learn_language_through_novel** is a FastAPI-based service that converts Chinese novel chapters into rich learning materials with multi-language audio support.

---

## Core Features

### 🤖 LLM-Powered Analysis
- **Chapter Analysis** (`POST /llm/analyze_chapter`)
  - Automatically detects chapter titles from Chinese text
  - Splits chapters into logical scenes
  - Identifies characters and dialogue
  - Generates both reference and AI translations (Chinese → Vietnamese)
  - Tracks narrator vs. character speech

- **Sentence Enrichment** (`POST /llm/enrich_sentence`)
  - Extracts key vocabulary and phrases with Hán Việt readings
  - Provides HSK level classification (1-6 or Above HSK)
  - Generates natural example sentences for modern Chinese usage
  - Includes detailed grammar and vocabulary explanations
  - Identifies new words within phrase examples

### 🎙️ Text-to-Speech System

#### TTS Segment Preparation (`POST /llm/prepare_tts_segments`)
**Deterministic, non-LLM conversion of enriched sentences into TTS-ready segments**

Features:
- **Language-aware splitting**: Separates Chinese and Vietnamese text for appropriate voice assignment
- **Configurable field selection**: Choose which enrichment fields to include in audio
- **Smart prefix management**: Field labels appear only once, avoiding repetitive announcements
- **Punctuation filtering**: Removes segments that are only whitespace or punctuation marks
- **Metadata preservation**: Includes pinyin and Hán Việt readings in segment metadata

Supported fields:
- Chapter titles (Chinese + Vietnamese)
- Original sentence and reference translations
- Vocabulary phrases with meanings
- Example sentences with translations
- New words from examples
- Hán Việt explanations
- Grammar explanations

#### Audio Synthesis (`POST /tts/synthesize`)
**Multi-provider audio generation**

Providers:
- **Piper TTS** (local, neural TTS)
  - Downloaded voice models: `zh_CN-huayan-medium`, `vi_VN-vais1000-medium`, `en_US-lessac-medium`
  - 22050 Hz WAV output
  - Fast, offline processing
  
- **OpenAI TTS** (cloud-based)
  - Standard and HD quality options
  - MP3 output
  - Voice mapping: narrator→onyx, teacher→nova, character→alloy

Voice roles:
- **Narrator**: Neutral voice for original text and Chinese examples
- **Teacher**: Explanatory voice for Vietnamese translations and teaching content
- **Character**: Natural voice for example sentences

#### Audio Merging
- Concatenates multiple WAV segments with configurable silence (default: 500ms)
- Outputs single merged audio file for complete chapters
- Metadata tracking: duration, file paths, segment counts

### 🔄 Pipeline Orchestration

**`scripts/generate.py`** - Complete automation from text to audio

Pipeline stages:
1. **Analysis**: Parse chapter text, detect structure
2. **Enrichment**: Add vocabulary, grammar, examples (concurrent processing)
3. **TTS Preparation**: Generate audio segments deterministically
4. **Synthesis**: Create individual audio files per segment
5. **Merging**: Combine into single playable file

Configuration via `tasks/*.json`:
```json
{
  "chapter_id": "1000",
  "max_sentences": 2,
  "enable_enrichment": true,
  "prepare_tts_segments": true,
  "synthesize_audio": true,
  "synthesis_provider": "piper",
  "synthesis_merge_segments": true
}
```

### 🌏 Multi-Language Support

#### Language Detection
- Automatic Chinese/Vietnamese/English detection in explanations
- Character-level splitting using CJK Unicode ranges
- Vietnamese diacritic recognition
- Splits mixed-language content for correct voice assignment

#### Hán Việt (Han-Viet) Integration
- Provides Hán Việt readings for Chinese characters
- Identifies Vietnamese loanwords from Chinese
- Tracks usage in modern Vietnamese literature

#### Translation Handling
- **Reference translations** (`text_vi_ref`): Human-provided Vietnamese
- **AI translations** (`text_vi_ai`): LLM-generated Vietnamese
- **Merged translations** (`text_vi`): Prefers reference, falls back to AI

---

## Technical Architecture

### API Stack
- **Framework**: FastAPI with Pydantic v2
- **LLM**: OpenAI GPT-4.1
- **TTS**: Piper (local) + OpenAI (cloud)
- **Audio**: Python `wave` module for WAV processing

### Data Models
- `AnalyzeChapterRequest/Response`: Chapter structure with scenes and sentences
- `EnrichSentenceRequest/Response`: Vocabulary, phrases, grammar, examples
- `PrepareTTSSegmentsRequest/Response`: TTS segments with language/voice/style
- `SynthesizeTTSRequest/Response`: Audio generation with provider settings

### File Structure
```
.
├── src/
│   ├── main.py                    # FastAPI app + endpoints
│   ├── services/
│   │   ├── piper_tts.py          # Piper provider
│   │   └── openai_tts.py         # OpenAI provider
│   └── utils/
│       └── audio.py               # Audio merging utilities
├── scripts/
│   └── generate.py                # Pipeline orchestration
├── tasks/
│   └── task1.json                 # Task configuration
├── tests/
│   ├── test_e2e_tts.py           # End-to-end tests
│   └── test_tts_synthesis.py     # Synthesis tests
├── chapters/                      # Input text files
├── outputs/                       # JSON results + audio
└── audio/                         # Generated WAV/MP3 files
```

---

## Configuration Options

### TTS Selection
Choose which fields to include in audio output:
- `title.zh`, `title.vi` - Chapter titles
- `sentence.text_zh`, `sentence.text_vi_ref` - Sentence translations
- `phrases[].text`, `phrases[].meaning_vi` - Vocabulary
- `phrases[].phrase_examples[].*` - Example sentences
- `examples[].*` - Additional examples
- `hanzi_explanation`, `grammar_explanation` - Teaching content

### Language Cues
Customizable language announcements:
```json
{
  "zh": "中文",
  "vi": "Tiếng Việt",
  "en": "English"
}
```

### Field Cues
Customizable field labels per language:
```json
{
  "hanzi_explanation": {
    "zh": "汉字解释",
    "vi": "Giải thích Hán tự"
  }
}
```

---

## Output Examples

### Analysis Output
```json
{
  "chapter_id": "1000",
  "chapter_meta": {
    "title": "第六卷 通天灵宝 第一千章 石傀儡",
    "title_vi_ai": "Quyển Sáu Thông Thiên Linh Bảo Chương Một Ngàn: Thạch Khôi Lỗi"
  },
  "scenes": [...]
}
```

### TTS Segments
```json
{
  "order": 27,
  "lang": "vi",
  "voice": "teacher",
  "style": "explanatory",
  "text": "Tiếng Việt Giải thích Hán tự, Các từ như '",
  "pause_after_ms": 800,
  "meta": null
}
```

### Audio Output
- Individual segments: `segment_0001_zh_narrator.wav`
- Merged file: `1000_merged.wav` (e.g., 163.64s duration)

---

## Future Enhancements (Potential)
- [ ] Add more TTS providers (Azure, Google Cloud)
- [ ] Support for additional languages (English, Japanese)
- [ ] Web UI for pipeline management
- [ ] Real-time streaming TTS
- [ ] Background music and sound effects
- [ ] Vocabulary flashcard generation
- [ ] Progress tracking for learners
