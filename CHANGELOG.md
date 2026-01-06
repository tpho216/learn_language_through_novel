# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2026-01-07

### Changed
- **BREAKING**: Refactored enrichment data model from flat phrase structure to hierarchical clause→phrase model
  - `EnrichSentenceResponse.phrases` → `EnrichSentenceResponse.clauses: List[Clause]`
  - Each clause now contains `clause_id`, `text`, `pinyin`, `hanvi`, `meaning_vi`, and `phrases[]`
  - Better reflects Chinese linguistic structure where sentences contain multiple semantic clauses
  - Updated LLM prompt to break sentences into clauses first, then extract phrases within each clause
  - See `docs/ENRICHMENT_DETAILS.md` and `docs/CLAUSE_STRUCTURE_EXAMPLE.md` for details

- **BREAKING**: Updated task configuration paths from `phrases[]` to `clauses[].phrases[]`
  - TTS selection fields updated in `task1.json`
  - Field cues added: "分句"/"Nghĩa phân câu" for clause-level content

### Added
- TTS generation for compound word breakdowns (`clauses[].phrases[].words[]`)
  - Speaks individual components of compound phrases (e.g., "一晃之下" → "一晃" + "之下")
  - Field cues: "组成词"/"Nghĩa tổ thành"
- Clause-level TTS segments with separate Chinese text and Vietnamese meaning
- Documentation files:
  - `docs/ENRICHMENT_DETAILS.md` - Explains clause→phrase hierarchy
  - `docs/CLAUSE_STRUCTURE_EXAMPLE.md` - Complete JSON example with 5 clauses
  - `REFACTORING_CLAUSES.md` - Summary of all refactoring changes

### Fixed
- TTS segment order duplication causing repeated audio in merged files
  - Added `start_order` parameter to `PrepareTTSSegmentsRequest`
  - `scripts/generate.py` now tracks `next_order` across all sentences
  - Prevents sentence 1 (orders 1-32) and sentence 2 (orders 1-24) from overlapping
- Vietnamese character voice model configuration
  - Changed `vi_character` from `vi_VN-vivos-x_low` to `vi_VN-vais1000-medium`
  - Matches available voice models in user environment

## [0.1.0] - 2026-01-04

### Added
- **LLM Integration**: FastAPI endpoints for chapter analysis with GPT-4 integration
  - `/llm/analyze_chapter` - Splits chapters into scenes and sentences with character detection
  - `/llm/enrich_sentence` - Enriches sentences with vocabulary, grammar, HSK levels, and examples
  
- **TTS System**: Complete text-to-speech pipeline with multi-language support
  - `/llm/prepare_tts_segments` - Deterministic TTS segment generation
  - `/tts/synthesize` - Audio synthesis with provider abstraction
  - Language-aware segmentation for mixed Chinese/Vietnamese content
  - Intelligent prefix management (only shows once per field)
  - Punctuation filtering to remove non-content segments
  
- **TTS Providers**: Flexible provider architecture
  - Piper TTS (local neural TTS with downloaded voice models)
  - OpenAI TTS (cloud-based synthesis)
  - Voice mapping: narrator, teacher, character roles
  
- **Audio Processing**: 
  - WAV file concatenation with configurable silence between segments
  - Audio merging utility for complete chapters
  
- **Pipeline Orchestration**: 
  - `scripts/generate.py` - Complete end-to-end pipeline execution
  - Task configuration system via JSON files
  - Support for chapter analysis → enrichment → TTS preparation → synthesis → merging
  
- **Language Features**:
  - Mixed-language explanation handling (Chinese/Vietnamese)
  - Han-Viet (Hán Việt) readings for Chinese characters
  - Pinyin metadata support
  - HSK level classification
  
- **Configuration**:
  - Task-based configuration (e.g., `tasks/task1.json`)
  - Configurable TTS selection, language cues, and field labels
  - Provider-specific settings (Piper binary path, OpenAI model selection)
  
- **Testing**:
  - End-to-end TTS pipeline tests
  - Provider-specific synthesis tests

### Infrastructure
- FastAPI application with Pydantic v2 models
- Python virtual environment setup
- Environment variable management via `.env`
- Comprehensive `.gitignore` configuration
