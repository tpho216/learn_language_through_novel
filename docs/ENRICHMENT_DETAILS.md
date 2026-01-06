# Sentence Enrichment - Clauses and Phrase Breakdown

## Overview

The sentence enrichment feature provides a **hierarchical breakdown** of Chinese sentences using linguistic clauses and phrases. Each sentence is broken into **clauses** (meaningful units often separated by commas or conjunctions), and each clause contains **phrases** (linguistic units) with complete word-by-word analysis. The `already_explained` field is set **programmatically** after enrichment to track repeated words.

## Structure

### Linguistic Hierarchy

```
Sentence
├── Clause 1
│   ├── Phrase 1
│   │   ├── Word breakdown
│   │   └── Phrase examples
│   └── Phrase 2
│       ├── Word breakdown
│       └── Phrase examples
└── Clause 2
    ├── Phrase 3
    └── Phrase 4
```

### Why Clauses?

Chinese sentences, especially in literary texts, often contain multiple clauses that express distinct ideas:

Example: "乾老魔诧异了起来，原本应经做攻击姿态的白影，一晃之下又重新回到了原处。"

Can be broken into clauses:
1. "乾老魔诧异了起来" (Qián lǎo mó was surprised)
2. "原本应经做攻击姿态的白影，一晃之下又重新回到了原处" (The white shadow... returned to original position)

Each clause has a coherent meaning and contains multiple phrases.

## Changes from Previous Design

### Previous Structure
- Sentence → Phrases → Phrase Examples → New Words

### New Structure
- Sentence → **Clauses** → Phrases → Phrase Examples → New Words

### Benefits
- Better reflects Chinese sentence structure
- Clearer semantic units for comprehension
- More organized learning flow
- Matches how complex sentences are naturally parsed

## Data Structure

### Clause Model

```json
{
  "clause_id": "clause_1",
  "text": "乾老魔诧异了起来",
  "pinyin": "qián lǎo mó chà yì le qǐ lái",
  "hanvi": "Càn lão ma sủa dị liễu khởi lai",
  "meaning_vi": "Càn lão ma ngạc nhiên",
  "phrases": [...]
}
```

### Phrase Model (within Clause)

```json
{
  "text": "诧异",
  "pinyin": "chà yì",
  "hanvi": "sủa dị",
  "meaning_vi": "ngạc nhiên",
  "hsk": "HSK 5",
  "use_in_modern_language": true,
  "words": [...],
  "phrase_examples": [...]
}
```

### WordMeaning Model

```json
{
  "word": "出了",
  "pinyin": "chū le",
  "hanvi": "xuất liễu",
  "meaning_vi": "đã xảy ra, đã xuất hiện",
  "hsk": "HSK 2",
  "used_as_vietnamese_loanword": false,
  "already_explained": false
}
```

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `word` | string | The Chinese word/phrase |
| `pinyin` | string | Romanization with tone marks |
| `hanvi` | string | Hán Việt reading (if applicable) |
| `meaning_vi` | string | Vietnamese meaning |
| `hsk` | string | HSK level: "HSK 1" through "HSK 6" or "Above HSK" |
| `used_as_vietnamese_loanword` | boolean | True if this Hán Việt word is commonly used in Vietnamese |
| `already_explained` | boolean | True if this word was explained earlier in the enrichment |

## Example: Complete Breakdown

For the phrase "出了什么事情" (What happened?):

```json
{
  "text": "出了什么事情",
  "pinyin": "chū le shénme shìqíng",
  "hanvi": "xuất liễu thậm ma sự tình",
  "meaning_vi": "Đã xảy ra chuyện gì",
  "hsk": "HSK 3",
  "use_in_modern_language": true,
  "phrase_examples": [
    {
      "zh": "出了什么事情？",
      "pinyin": "Chūle shénme shìqíng?",
      "hanvi": "Xuất liễu thậm ma sự tình?",
      "vi": "Đã xảy ra chuyện gì vậy?",
      "new_words": [
        {
          "word": "出了",
          "pinyin": "chū le",
          "hanvi": "xuất liễu",
          "meaning_vi": "đã xảy ra, đã xuất hiện",
          "hsk": "HSK 2",
          "used_as_vietnamese_loanword": false,
          "already_explained": false
        },
        {
          "word": "什么",
          "pinyin": "shénme",
          "hanvi": "thậm ma",
          "meaning_vi": "gì, cái gì",
          "hsk": "HSK 1",
          "used_as_vietnamese_loanword": false,
          "already_explained": false
        },
        {
          "word": "事情",
          "pinyin": "shìqíng",
          "hanvi": "sự tình",
          "meaning_vi": "sự việc, chuyện",
          "hsk": "HSK 3",
          "used_as_vietnamese_loanword": true,
          "already_explained": false
        }
      ]
    }
  ]
}
```

## Handling Repeated Words

If a word appears again in a later example, it's still listed but flagged:

```json
{
  "zh": "你知道出了什么事情吗？",
  "vi": "Bạn có biết có chuyện gì xảy ra không?",
  "new_words": [
    {
      "word": "你",
      "pinyin": "nǐ",
      "hanvi": "nhĩ",
      "meaning_vi": "bạn, ngươi",
      "hsk": "HSK 1",
      "already_explained": false
    },
    {
      "word": "知道",
      "pinyin": "zhīdào",
      "hanvi": "tri đạo",
      "meaning_vi": "biết",
      "hsk": "HSK 2",
      "already_explained": false
    },
    {
      "word": "出了",
      "pinyin": "chū le",
      "hanvi": "xuất liễu",
      "meaning_vi": "đã xảy ra",
      "hsk": "HSK 2",
      "already_explained": true  ← Marked as already explained
    },
    {
      "word": "什么",
      "pinyin": "shénme",
      "hanvi": "thậm ma",
      "meaning_vi": "gì",
      "hsk": "HSK 1",
      "already_explained": true  ← Marked as already explained
    },
    {
      "word": "事情",
      "pinyin": "shìqíng",
      "hanvi": "sự tình",
      "meaning_vi": "sự việc",
      "hsk": "HSK 3",
      "already_explained": true  ← Marked as already explained
    },
    {
      "word": "吗",
      "pinyin": "ma",
      "hanvi": "ma",
      "meaning_vi": "hư từ nghi vấn (chỉ câu hỏi)",
      "hsk": "HSK 1",
      "already_explained": false
    }
  ]
}
```

## Classical/Literary Phrases (No Examples)

When a phrase is **not used in modern language** (classical/literary Chinese), no examples are provided:

```json
{
  "text": "诸位道友",
  "pinyin": "zhū wèi dàoyǒu",
  "hanvi": "Chư vị đạo hữu",
  "meaning_vi": "các vị đạo hữu",
  "hsk": "Above HSK",
  "use_in_modern_language": false,
  "phrase_examples": []  ← Empty because it's classical/literary
}
```

**Why empty?**
- Phrases like "诸位道友" (honorable dao friends) are from classical Chinese or xianxia novels
- They don't appear in modern daily conversation
- Creating "modern examples" would be artificial and misleading
- Students learn these from context in the source material

**Which phrases get examples?**
- ✅ `use_in_modern_language: true` → Gets 1-2 modern example sentences
- ❌ `use_in_modern_language: false` → Empty array (classical/literary only)

## Benefits for Learning

1. **Complete Coverage**: No vocabulary is skipped or assumed
2. **HSK Progression**: Each word shows its difficulty level
3. **Loanword Awareness**: Identifies which Hán Việt words are used in Vietnamese
4. **Smart Repetition**: Flags repeated words to avoid redundant teaching
5. **Systematic Learning**: Students can track every component of a sentence

## Usage in TTS Generation

With the detailed breakdown, the TTS pipeline can:
- Generate audio for **every** word
- Skip repeated words if `already_explained: true`
- Provide comprehensive vocabulary drills
- Create word-by-word pronunciation practice

## Implementation Notes

The LLM is instructed to:
1. Break down each example sentence into ALL constituent words
2. Never skip words, even simple ones like "什么" or "了"
3. Provide complete linguistic information for each word
4. NOT set "already_explained" (handled programmatically)
5. Maintain consistency in Hán Việt readings and translations
6. Leave phrase_examples empty for classical/literary phrases (use_in_modern_language: false)

After the LLM response, the system:
- Tracks all words that have been explained
- Sets `already_explained: true` for any word that appears again
- Preserves all word entries even if repeated (for reference)

## Testing

To test the new enrichment format:

```bash
# Start server
uvicorn src.main:app --reload --port 8000

# Run task with enrichment enabled
python scripts/generate.py tasks/task1.json

# Check output JSON for complete word breakdown
cat outputs/task1_*.json | jq '.scenes[0].sentences[0].enrichment.phrases[0].phrase_examples[0].new_words'
```

You should see ALL words in the example, not just "new" vocabulary.
