# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
