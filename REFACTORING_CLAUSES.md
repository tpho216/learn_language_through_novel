# Refactoring Summary: Phrases → Clauses + Phrases

## Date
January 6, 2026

## Overview
Major refactoring to restructure sentence enrichment from a flat phrase list to a hierarchical clause-phrase structure that better reflects Chinese linguistic structure.

## Changes Made

### 1. Data Model Updates ([src/main.py](../src/main.py))

#### Added `Clause` Model
```python
class Clause(BaseModel):
  """A clause within a sentence - a meaningful unit that may contain multiple phrases."""
  clause_id: str  # e.g., "clause_1", "clause_2"
  text: str  # The Chinese text of this clause
  pinyin: str
  hanvi: Optional[str] = None
  meaning_vi: str  # Vietnamese translation of this clause
  phrases: List[Phrase]  # Phrases within this clause
```

#### Updated `EnrichSentenceResponse`
- **Before:** `phrases: List[Phrase]`
- **After:** `clauses: List[Clause]`

Each clause now contains phrases, creating a two-level hierarchy.

### 2. LLM Prompt Updates ([src/main.py](../src/main.py))

Updated enrichment prompt to:
- First break sentences into **clauses** (meaningful units)
- Then extract **phrases within each clause**
- Updated JSON schema to reflect clause structure
- Added clause-level instructions to PHRASE EXTRACTION RULES

### 3. Post-Processing Logic ([src/main.py](../src/main.py))

Updated `already_explained` tracking to work with nested clause→phrase structure:
```python
if "clauses" in data:
    for clause in data["clauses"]:
        if "phrases" in clause and clause["phrases"]:
            for phrase in clause["phrases"]:
                # Track words across all clauses and phrases
```

### 4. TTS Segment Generation ([src/main.py](../src/main.py))

#### Updated Selection Fields
```python
sel = req.selection or [
    "sentence.text_zh",
    "sentence.text_vi",
    "clauses[].text",              # NEW: Clause Chinese text
    "clauses[].meaning_vi",        # NEW: Clause Vietnamese meaning
    "clauses[].phrases[].text",    # Updated path
    "clauses[].phrases[].meaning_vi",
    "clauses[].phrases[].phrase_examples[].zh",
    # ... etc
]
```

#### Updated Field Cues
Added Vietnamese/Chinese labels for clause-level fields:
- `"clauses[].text": {"zh": "分句"}` (sub-clause)
- `"clauses[].meaning_vi": {"vi": "Nghĩa phân câu"}` (clause meaning)

#### Updated TTS Generation Loop
Now generates audio in hierarchical order:
1. Full sentence (Chinese + Vietnamese)
2. **Clause 1** text + meaning
3. Phrases in Clause 1
4. **Clause 2** text + meaning
5. Phrases in Clause 2
6. etc.

### 5. Documentation Updates

#### [.github/copilot-instructions.md](../.github/copilot-instructions.md)
- Added "Enrichment Structure (Clauses → Phrases)" section
- Documented Clause and Phrase models with field descriptions

#### [docs/ENRICHMENT_DETAILS.md](../docs/ENRICHMENT_DETAILS.md)
- Complete rewrite to explain clause-based structure
- Added "Why Clauses?" section with example
- Updated from "Sentence → Phrases" to "Sentence → Clauses → Phrases"
- Added hierarchical diagram

#### [docs/CLAUSE_STRUCTURE_EXAMPLE.md](../docs/CLAUSE_STRUCTURE_EXAMPLE.md) (NEW)
- Complete JSON example showing clause structure
- Example sentence: "乾老魔诧异了起来，原本应经做攻击姿态的白影，一晃之下又重新回到了原处。"
- Shows 2 clauses with multiple phrases each
- Demonstrates `already_explained` tracking across clauses

## Benefits

### Linguistic Accuracy
- Better reflects how Chinese sentences are structured
- Clauses provide natural semantic boundaries (often at commas/conjunctions)
- Matches how complex literary Chinese is naturally parsed

### Learning Flow
- Clear hierarchy: sentence → clause → phrase → word
- Learners can understand clause-level meaning before diving into phrases
- More organized than flat phrase list

### TTS Experience
- Audio segments now follow natural sentence structure
- Clause-level pauses create better listening rhythm
- Teacher can explain clause meaning before phrases

## Migration Notes

### For API Consumers
- **Breaking change**: `EnrichSentenceResponse.phrases` → `EnrichSentenceResponse.clauses`
- Each clause now has `phrases` array
- TTS selection fields updated (e.g., `phrases[].text` → `clauses[].phrases[].text`)

### For Prompt Engineering
- LLM now receives instructions to:
  1. Break sentence into clauses first
  2. Then extract phrases within each clause
- Schema includes clause_id for tracking

### For Testing
- Existing enrichment outputs will not match new schema
- Need to regenerate enrichment data with new structure
- Test fixtures (response_1000.json) don't include enrichment, so unaffected

## Files Changed

1. [src/main.py](../src/main.py) - Models, prompt, post-processing, TTS generation
2. [.github/copilot-instructions.md](../.github/copilot-instructions.md) - Data model documentation
3. [docs/ENRICHMENT_DETAILS.md](../docs/ENRICHMENT_DETAILS.md) - Complete rewrite
4. [docs/CLAUSE_STRUCTURE_EXAMPLE.md](../docs/CLAUSE_STRUCTURE_EXAMPLE.md) - NEW example doc

## Next Steps

1. **Test the changes**: Run `python scripts/generate.py tasks/task1.json`
2. **Verify clause extraction**: Check that LLM properly segments sentences into clauses
3. **Check phrase completeness**: Ensure phrases like "一晃之下又" are captured within clauses
4. **Validate TTS flow**: Confirm audio segments follow clause→phrase hierarchy
5. **Update frontend** (if exists): Update to display clause structure in UI

## Example Output Structure

```
Sentence: "乾老魔诧异了起来，原本应经做攻击姿态的白影，一晃之下又重新回到了原处。"

└── Clause 1: "乾老魔诧异了起来"
    ├── Phrase: "乾老魔"
    └── Phrase: "诧异了起来"

└── Clause 2: "原本应经做攻击姿态的白影，一晃之下又重新回到了原处"
    ├── Phrase: "白影"
    ├── Phrase: "一晃之下" ← Previously missed, now captured!
    └── Phrase: "重新回到原处"
```
