# Clause-Based Enrichment Structure - Example

## Overview

This document shows a complete example of the new clause-based enrichment structure.

## Sample Sentence

**Chinese:** "乾老魔诧异了起来，原本应经做攻击姿态的白影，一晃之下又重新回到了原处。"

**Breakdown:** This sentence has 2 main clauses.

## JSON Structure

```json
{
  "order": 1,
  "text_zh": "乾老魔诧异了起来，原本应经做攻击姿态的白影，一晃之下又重新回到了原处。",
  "pinyin": "qián lǎo mó chà yì le qǐ lái, yuán běn yīng jīng zuò gōng jī zī tài de bái yǐng, yī huǎng zhī xià yòu chóng xīn huí dào le yuán chù.",
  "clauses": [
    {
      "clause_id": "clause_1",
      "text": "乾老魔诧异了起来",
      "pinyin": "qián lǎo mó chà yì le qǐ lái",
      "hanvi": "Càn lão ma sủa dị liễu khởi lai",
      "meaning_vi": "Càn lão ma ngạc nhiên",
      "phrases": [
        {
          "text": "乾老魔",
          "pinyin": "qián lǎo mó",
          "hanvi": "Càn lão ma",
          "meaning_vi": "Càn lão ma (tên nhân vật)",
          "hsk": "Above HSK",
          "use_in_modern_language": true,
          "words": [
            {
              "word": "乾",
              "pinyin": "qián",
              "hanvi": "Càn",
              "meaning_vi": "Càn (bát quái)",
              "hsk": "Above HSK",
              "used_as_vietnamese_loanword": true
            },
            {
              "word": "老魔",
              "pinyin": "lǎo mó",
              "hanvi": "lão ma",
              "meaning_vi": "lão ma, lão quỷ",
              "hsk": "HSK 5",
              "used_as_vietnamese_loanword": false
            }
          ],
          "phrase_examples": []
        },
        {
          "text": "诧异了起来",
          "pinyin": "chà yì le qǐ lái",
          "hanvi": "sủa dị liễu khởi lai",
          "meaning_vi": "bắt đầu ngạc nhiên",
          "hsk": "HSK 5",
          "use_in_modern_language": true,
          "words": [
            {
              "word": "诧异",
              "pinyin": "chà yì",
              "hanvi": "sủa dị",
              "meaning_vi": "ngạc nhiên",
              "hsk": "HSK 5",
              "used_as_vietnamese_loanword": false
            },
            {
              "word": "了",
              "pinyin": "le",
              "hanvi": "liễu",
              "meaning_vi": "rồi (trợ từ)",
              "hsk": "HSK 1",
              "used_as_vietnamese_loanword": false
            },
            {
              "word": "起来",
              "pinyin": "qǐ lái",
              "hanvi": "khởi lai",
              "meaning_vi": "lên, bắt đầu (xu hướng)",
              "hsk": "HSK 2",
              "used_as_vietnamese_loanword": false
            }
          ],
          "phrase_examples": [
            {
              "zh": "他惊讶了起来",
              "pinyin": "tā jīng yà le qǐ lái",
              "hanvi": "Tha kinh nhã liễu khởi lai",
              "vi": "Anh ấy bắt đầu ngạc nhiên",
              "new_words": [
                {
                  "word": "惊讶",
                  "pinyin": "jīng yà",
                  "hanvi": "kinh nhã",
                  "meaning_vi": "ngạc nhiên, kinh ngạc",
                  "hsk": "HSK 4",
                  "used_as_vietnamese_loanword": false,
                  "already_explained": false
                },
                {
                  "word": "了",
                  "pinyin": "le",
                  "hanvi": "liễu",
                  "meaning_vi": "rồi (trợ từ)",
                  "hsk": "HSK 1",
                  "used_as_vietnamese_loanword": false,
                  "already_explained": true
                },
                {
                  "word": "起来",
                  "pinyin": "qǐ lái",
                  "hanvi": "khởi lai",
                  "meaning_vi": "lên, bắt đầu",
                  "hsk": "HSK 2",
                  "used_as_vietnamese_loanword": false,
                  "already_explained": true
                }
              ]
            }
          ]
        }
      ]
    },
    {
      "clause_id": "clause_2",
      "text": "原本应经做攻击姿态的白影，一晃之下又重新回到了原处",
      "pinyin": "yuán běn yīng jīng zuò gōng jī zī tài de bái yǐng, yī huǎng zhī xià yòu chóng xīn huí dào le yuán chù",
      "hanvi": "Nguyên bản ưng kinh tố công kích tư thái đích bạch ảnh, nhất hoảng chi hạ hựu trọng tân hồi đáo liễu nguyên xứ",
      "meaning_vi": "Bóng trắng vốn đã tạo tư thế tấn công, trong một thoáng lại quay về vị trí ban đầu",
      "phrases": [
        {
          "text": "原本",
          "pinyin": "yuán běn",
          "hanvi": "nguyên bản",
          "meaning_vi": "vốn, ban đầu",
          "hsk": "HSK 4",
          "use_in_modern_language": true,
          "words": [
            {
              "word": "原",
              "pinyin": "yuán",
              "hanvi": "nguyên",
              "meaning_vi": "gốc, nguyên",
              "hsk": "HSK 4",
              "used_as_vietnamese_loanword": true
            },
            {
              "word": "本",
              "pinyin": "běn",
              "hanvi": "bản",
              "meaning_vi": "gốc, bản",
              "hsk": "HSK 2",
              "used_as_vietnamese_loanword": true
            }
          ],
          "phrase_examples": [
            {
              "zh": "这里原本是森林",
              "pinyin": "zhè lǐ yuán běn shì sēn lín",
              "hanvi": "Giá lý nguyên bản thị sâm lâm",
              "vi": "Đây vốn là rừng",
              "new_words": [
                {
                  "word": "这里",
                  "pinyin": "zhè lǐ",
                  "hanvi": "giá lý",
                  "meaning_vi": "đây, nơi này",
                  "hsk": "HSK 1",
                  "used_as_vietnamese_loanword": false,
                  "already_explained": false
                },
                {
                  "word": "原本",
                  "pinyin": "yuán běn",
                  "hanvi": "nguyên bản",
                  "meaning_vi": "vốn, ban đầu",
                  "hsk": "HSK 4",
                  "used_as_vietnamese_loanword": true,
                  "already_explained": false
                },
                {
                  "word": "森林",
                  "pinyin": "sēn lín",
                  "hanvi": "sâm lâm",
                  "meaning_vi": "rừng",
                  "hsk": "HSK 4",
                  "used_as_vietnamese_loanword": true,
                  "already_explained": false
                }
              ]
            }
          ]
        },
        {
          "text": "应经做",
          "pinyin": "yīng jīng zuò",
          "hanvi": "ưng kinh tố",
          "meaning_vi": "đã nên làm, đáng lẽ đã làm",
          "hsk": "HSK 4",
          "use_in_modern_language": true,
          "words": [
            {
              "word": "应",
              "pinyin": "yīng",
              "hanvi": "ưng",
              "meaning_vi": "nên, phải",
              "hsk": "HSK 3",
              "used_as_vietnamese_loanword": true
            },
            {
              "word": "经",
              "pinyin": "jīng",
              "hanvi": "kinh",
              "meaning_vi": "đã, đã từng",
              "hsk": "HSK 4",
              "used_as_vietnamese_loanword": true
            },
            {
              "word": "做",
              "pinyin": "zuò",
              "hanvi": "tố",
              "meaning_vi": "làm",
              "hsk": "HSK 1",
              "used_as_vietnamese_loanword": false
            }
          ],
          "phrase_examples": [
            {
              "zh": "这件事应该做完了",
              "pinyin": "zhè jiàn shì yīng gāi zuò wán le",
              "hanvi": "Giá kiện sự ưng cai tố hoàn liễu",
              "vi": "Việc này đáng lẽ đã làm xong rồi",
              "new_words": [
                {
                  "word": "这件事",
                  "pinyin": "zhè jiàn shì",
                  "hanvi": "giá kiện sự",
                  "meaning_vi": "việc này",
                  "hsk": "HSK 2",
                  "used_as_vietnamese_loanword": false,
                  "already_explained": false
                },
                {
                  "word": "应该",
                  "pinyin": "yīng gāi",
                  "hanvi": "ưng cai",
                  "meaning_vi": "nên, đáng lẽ",
                  "hsk": "HSK 3",
                  "used_as_vietnamese_loanword": false,
                  "already_explained": false
                },
                {
                  "word": "做完",
                  "pinyin": "zuò wán",
                  "hanvi": "tố hoàn",
                  "meaning_vi": "làm xong",
                  "hsk": "HSK 2",
                  "used_as_vietnamese_loanword": false,
                  "already_explained": false
                }
              ]
            }
          ]
        },
        {
          "text": "攻击姿态",
          "pinyin": "gōng jī zī tài",
          "hanvi": "công kích tư thái",
          "meaning_vi": "tư thế tấn công",
          "hsk": "HSK 5",
          "use_in_modern_language": true,
          "words": [
            {
              "word": "攻击",
              "pinyin": "gōng jī",
              "hanvi": "công kích",
              "meaning_vi": "tấn công",
              "hsk": "HSK 4",
              "used_as_vietnamese_loanword": true
            },
            {
              "word": "姿态",
              "pinyin": "zī tài",
              "hanvi": "tư thái",
              "meaning_vi": "tư thế",
              "hsk": "HSK 6",
              "used_as_vietnamese_loanword": true
            }
          ],
          "phrase_examples": [
            {
              "zh": "他摆出攻击姿态",
              "pinyin": "tā bǎi chū gōng jī zī tài",
              "hanvi": "Tha bãi xuất công kích tư thái",
              "vi": "Anh ấy tạo tư thế tấn công",
              "new_words": [
                {
                  "word": "摆出",
                  "pinyin": "bǎi chū",
                  "hanvi": "bãi xuất",
                  "meaning_vi": "tạo ra, bày ra",
                  "hsk": "HSK 4",
                  "used_as_vietnamese_loanword": false,
                  "already_explained": false
                },
                {
                  "word": "攻击",
                  "pinyin": "gōng jī",
                  "hanvi": "công kích",
                  "meaning_vi": "tấn công",
                  "hsk": "HSK 4",
                  "used_as_vietnamese_loanword": true,
                  "already_explained": true
                },
                {
                  "word": "姿态",
                  "pinyin": "zī tài",
                  "hanvi": "tư thái",
                  "meaning_vi": "tư thế",
                  "hsk": "HSK 6",
                  "used_as_vietnamese_loanword": true,
                  "already_explained": true
                }
              ]
            }
          ]
        },
        {
          "text": "白影",
          "pinyin": "bái yǐng",
          "hanvi": "bạch ảnh",
          "meaning_vi": "bóng trắng",
          "hsk": "HSK 3",
          "use_in_modern_language": true,
          "words": [
            {
              "word": "白",
              "pinyin": "bái",
              "hanvi": "bạch",
              "meaning_vi": "trắng",
              "hsk": "HSK 1",
              "used_as_vietnamese_loanword": true
            },
            {
              "word": "影",
              "pinyin": "yǐng",
              "hanvi": "ảnh",
              "meaning_vi": "bóng, ảnh",
              "hsk": "HSK 3",
              "used_as_vietnamese_loanword": true
            }
          ],
          "phrase_examples": [
            {
              "zh": "树影在移动",
              "pinyin": "shù yǐng zài yí dòng",
              "hanvi": "Thụ ảnh tại di động",
              "vi": "Bóng cây đang di chuyển",
              "new_words": [
                {
                  "word": "树",
                  "pinyin": "shù",
                  "hanvi": "thụ",
                  "meaning_vi": "cây",
                  "hsk": "HSK 2",
                  "used_as_vietnamese_loanword": true,
                  "already_explained": false
                },
                {
                  "word": "影",
                  "pinyin": "yǐng",
                  "hanvi": "ảnh",
                  "meaning_vi": "bóng",
                  "hsk": "HSK 3",
                  "used_as_vietnamese_loanword": true,
                  "already_explained": true
                },
                {
                  "word": "在",
                  "pinyin": "zài",
                  "hanvi": "tại",
                  "meaning_vi": "đang",
                  "hsk": "HSK 1",
                  "used_as_vietnamese_loanword": true,
                  "already_explained": false
                },
                {
                  "word": "移动",
                  "pinyin": "yí dòng",
                  "hanvi": "di động",
                  "meaning_vi": "di chuyển",
                  "hsk": "HSK 4",
                  "used_as_vietnamese_loanword": true,
                  "already_explained": false
                }
              ]
            }
          ]
        },
        {
          "text": "一晃之下",
          "pinyin": "yī huǎng zhī xià",
          "hanvi": "nhất hoảng chi hạ",
          "meaning_vi": "trong một thoáng, trong chớp mắt",
          "hsk": "Above HSK",
          "use_in_modern_language": true,
          "words": [
            {
              "word": "一",
              "pinyin": "yī",
              "hanvi": "nhất",
              "meaning_vi": "một",
              "hsk": "HSK 1",
              "used_as_vietnamese_loanword": true
            },
            {
              "word": "晃",
              "pinyin": "huǎng",
              "hanvi": "hoảng",
              "meaning_vi": "lung lay, thoáng qua",
              "hsk": "HSK 5",
              "used_as_vietnamese_loanword": false
            },
            {
              "word": "之下",
              "pinyin": "zhī xià",
              "hanvi": "chi hạ",
              "meaning_vi": "dưới, trong lúc",
              "hsk": "HSK 4",
              "used_as_vietnamese_loanword": false
            }
          ],
          "phrase_examples": [
            {
              "zh": "一瞬之下就消失了",
              "pinyin": "yī shùn zhī xià jiù xiāo shī le",
              "hanvi": "Nhất thuấn chi hạ tựu tiêu thất liễu",
              "vi": "Trong chớp mắt đã biến mất rồi",
              "new_words": [
                {
                  "word": "瞬",
                  "pinyin": "shùn",
                  "hanvi": "thuấn",
                  "meaning_vi": "chớp mắt, giây lát",
                  "hsk": "HSK 5",
                  "used_as_vietnamese_loanword": true,
                  "already_explained": false
                },
                {
                  "word": "之下",
                  "pinyin": "zhī xià",
                  "hanvi": "chi hạ",
                  "meaning_vi": "dưới, trong",
                  "hsk": "HSK 4",
                  "used_as_vietnamese_loanword": false,
                  "already_explained": true
                },
                {
                  "word": "消失",
                  "pinyin": "xiāo shī",
                  "hanvi": "tiêu thất",
                  "meaning_vi": "biến mất",
                  "hsk": "HSK 4",
                  "used_as_vietnamese_loanword": true,
                  "already_explained": false
                }
              ]
            }
          ]
        },
        {
          "text": "又",
          "pinyin": "yòu",
          "hanvi": "hựu",
          "meaning_vi": "lại, lại nữa",
          "hsk": "HSK 2",
          "use_in_modern_language": true,
          "words": null,
          "phrase_examples": [
            {
              "zh": "他又来了",
              "pinyin": "tā yòu lái le",
              "hanvi": "Tha hựu lai liễu",
              "vi": "Anh ấy lại đến rồi",
              "new_words": [
                {
                  "word": "他",
                  "pinyin": "tā",
                  "hanvi": "tha",
                  "meaning_vi": "anh ấy",
                  "hsk": "HSK 1",
                  "used_as_vietnamese_loanword": false,
                  "already_explained": false
                },
                {
                  "word": "又",
                  "pinyin": "yòu",
                  "hanvi": "hựu",
                  "meaning_vi": "lại",
                  "hsk": "HSK 2",
                  "used_as_vietnamese_loanword": true,
                  "already_explained": false
                },
                {
                  "word": "来了",
                  "pinyin": "lái le",
                  "hanvi": "lai liễu",
                  "meaning_vi": "đến rồi",
                  "hsk": "HSK 1",
                  "used_as_vietnamese_loanword": false,
                  "already_explained": false
                }
              ]
            }
          ]
        },
        {
          "text": "重新回到原处",
          "pinyin": "chóng xīn huí dào yuán chù",
          "hanvi": "trọng tân hồi đáo nguyên xứ",
          "meaning_vi": "quay lại vị trí ban đầu",
          "hsk": "HSK 4",
          "use_in_modern_language": true,
          "words": [
            {
              "word": "重新",
              "pinyin": "chóng xīn",
              "hanvi": "trọng tân",
              "meaning_vi": "lại, một lần nữa",
              "hsk": "HSK 4",
              "used_as_vietnamese_loanword": true
            },
            {
              "word": "回到",
              "pinyin": "huí dào",
              "hanvi": "hồi đáo",
              "meaning_vi": "quay về",
              "hsk": "HSK 3",
              "used_as_vietnamese_loanword": false
            },
            {
              "word": "原处",
              "pinyin": "yuán chù",
              "hanvi": "nguyên xứ",
              "meaning_vi": "vị trí ban đầu",
              "hsk": "HSK 4",
              "used_as_vietnamese_loanword": true
            }
          ],
          "phrase_examples": [
            {
              "zh": "物品重新回到原位",
              "pinyin": "wù pǐn chóng xīn huí dào yuán wèi",
              "hanvi": "Vật phẩm trọng tân hồi đáo nguyên vị",
              "vi": "Đồ vật quay lại vị trí ban đầu",
              "new_words": [
                {
                  "word": "物品",
                  "pinyin": "wù pǐn",
                  "hanvi": "vật phẩm",
                  "meaning_vi": "đồ vật",
                  "hsk": "HSK 3",
                  "used_as_vietnamese_loanword": true,
                  "already_explained": false
                },
                {
                  "word": "重新",
                  "pinyin": "chóng xīn",
                  "hanvi": "trọng tân",
                  "meaning_vi": "lại, một lần nữa",
                  "hsk": "HSK 4",
                  "used_as_vietnamese_loanword": true,
                  "already_explained": true
                },
                {
                  "word": "回到",
                  "pinyin": "huí dào",
                  "hanvi": "hồi đáo",
                  "meaning_vi": "quay về",
                  "hsk": "HSK 3",
                  "used_as_vietnamese_loanword": false,
                  "already_explained": true
                },
                {
                  "word": "原位",
                  "pinyin": "yuán wèi",
                  "hanvi": "nguyên vị",
                  "meaning_vi": "vị trí ban đầu",
                  "hsk": "HSK 4",
                  "used_as_vietnamese_loanword": true,
                  "already_explained": false
                }
              ]
            }
          ]
        }
      ]
    }
  ],
  "hsk_overall": "Above HSK",
  "examples": [
    {
      "zh": "他突然诧异起来，然后又平静下去。",
      "pinyin": "tā tū rán chà yì qǐ lái, rán hòu yòu píng jìng xià qù",
      "hanvi": "Tha đột nhiên sủa dị khởi lai, nhiên hậu hựu bình tĩnh hạ khứ",
      "vi": "Anh ấy đột nhiên ngạc nhiên, sau đó lại bình tĩnh lại."
    }
  ],
  "hanzi_explanation": "诧异：表示惊讶、意外的情绪。",
  "grammar_explanation": "「一晃之下」是文言式的时间状语，表示「在一瞬间」的意思。"
}
```

## Key Points

### Clause Level
- Each clause is a **meaningful semantic unit**
- Has its own `clause_id`, text, pinyin, Hán Việt, and Vietnamese meaning
- Contains multiple phrases

### Phrase Level (within clause)
- Linguistic units smaller than clauses
- Each phrase has complete linguistic metadata
- Can be compound words broken down further in `words` field
- May have `phrase_examples` to show usage

### Word Level (within phrase examples)
- **Every word** in an example is broken down
- `already_explained` is set programmatically based on whether the word appeared earlier
- Tracks HSK level and Vietnamese loanword status

### TTS Segment Generation

With the new clause structure, TTS segments are generated as:

1. Full sentence (Chinese + Vietnamese)
2. **Clause 1** (Chinese + Vietnamese meaning)
3. Phrase 1a (Chinese + Vietnamese)
4. Phrase 1b (Chinese + Vietnamese)
5. **Clause 2** (Chinese + Vietnamese meaning)
6. Phrase 2a (Chinese + Vietnamese)
7. Phrase 2b (Chinese + Vietnamese)
8. etc.

This creates a natural learning flow: sentence → clauses → phrases → details
