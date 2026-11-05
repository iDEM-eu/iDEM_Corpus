# iDEM Catalan Corpus (v1.4): structure and statistics

`idem_corpus_ca_v1.4.json` is a sentence-aligned corpus of Catalan source texts and their **Lectura Fàcil** (easy-to-read, A2) versions. All simplifications were made by humans at DINCAT. Each simplified entry is annotated with the DINCAT easy-to-read criteria that were applied.

> The Catalan, Spanish and Italian iDEM corpora are **not parallel**. Each language has its own criteria catalogue and conventions, so criterion codes must never be compared across languages. The Catalan file is also **structured differently** from the Spanish one (see "How to read it").

## Overview

| | |
|---|---|
| Documents | 14 |
| Texts | 105 (`CAT_001` – `CAT_105`) |
| Alignments (original sentences) | 383 |
| Simplified entries | 408 |
| Lines of simplified text | 1,379 |
| Words: original → simplified | 9,612 → 11,953 (124%) |
| Criteria codes used | 25 |
| Translators | 2 |

## Structure

The file has three top-level keys. The data lives in `documents`, nested four levels deep. Inside each simplified entry, the lines of the easy-to-read text are separated by line breaks:

```
idem_corpus_ca_v1.4.json
├── corpus                 metadata about the whole corpus
├── criteria               the 25 criteria codes used in this corpus
└── documents              14 source documents
      └── texts                 105 sections, one translator each
            └── alignments           383 original sentences
                  └── simplified          408 entries
                        └── text               1,379 lines, separated by "\n"
```

### `corpus`

Version, date, source file, change log (`changes_in_this_version`), notes on segmentation and annotation, a note on unofficial English translations of some criteria (`description_en_note`), and `counts`.

### `criteria`

```json
{
  "code": "18",
  "description": "Trieu paraules fàcilment comprensibles i familiars per al grup destinatari ...",
  "description_en": "Choose words that are easily understandable and familiar to the target group ...",
  "group": "linguistic",
  "in_official_catalogue": true,
  "times_used": 276
}
```

The full DINCAT catalogue has codes 1–38 for language, 39–60 for format and 61+ for accessibility, plus `0` (transcription: sentence kept unchanged) and `00` (explanation added by the translator). **The JSON lists only the 25 codes that are actually used**: 23 linguistic codes plus `0` and `00`. The English descriptions of codes 19, 20, 22, 23, 26, 28 and 29 are unofficial translations awaiting review by DINCAT.

### `documents` → `texts` → `alignments` → `simplified`

| Level | Fields |
|---|---|
| **document** | `document_id` (e.g. `CAT_002_006` = texts CAT_002 to CAT_006), `metadata`, `texts` |
| `metadata` | `source_url`, `creation_date`, `characters_without_spaces`, `corpus_category`, `text_type`, `topic`, `complexity_level`, `simplification_method`, `institution`, `tested_by_user_group`, `copyright_cleared` |
| **text** | `text_id`, `translator_id`, `alignments` |
| **alignment** | `alignment_id` (e.g. `CAT_001-1` = 1st sentence of text CAT_001), `original`, `simplified`, `source_row`, `quality_flags` *(optional)* |
| **simplified entry** | `position`, `text` (several lines separated by `\n`), `criteria_codes`, `complex_parts`, `source_row`, `quality_flags` *(optional)* |

`source_row` is the row in the source Excel file (`text_id_CAT_iDEM_corpus_split_simplfied.xlsx`).

## How to read it

**One alignment = one original sentence. Usually one simplified entry holds its whole easy-to-read version**, with one line per `\n`:

```
CAT_001-1  original:   Àpats a domicili. El servei d'àpats a domicili dona suport alimentari a
                       aquelles persones que, per la seva situació personal, no poden ...
           simplified: position 1, criteria 18, 14, 10, 26
                         Menjars a domicili
                         Hi ha un servei d'ajuda que porta el menjar a casa.
                         Aquest servei és per a persones que tenen problemes per cuinar.
                         Aquests problemes poden ser:
                         - per la seva situació personal no poden preparar el menjar.
                         - Necessiten ajuda per cuinar.
                         - La cuina de casa seva està en mal estat.
```

Points to watch:

- **Split `text` on `\n` to get lines.** 361 of 383 alignments have a single entry with on average 3.4 lines.
- **Some alignments have 2 or 3 entries.** In the 22 alignments with more than one entry, the extra entries usually add a gloss or explanation (codes `8` and `00`). Join all entries in `position` order.
- **Criteria are annotated per entry.** `criteria_codes` describe the whole entry, not a single line. Codes are strings (`"18"`, `"00"`), not integers.
- **Two apostrophe styles.** Both the typographic `’` and the straight `'` apostrophe occur (691 and 200 times). Normalise them before tokenising or comparing strings.
- **`creation_date`** is empty for 13 documents and free text (`"October 2024"`) for one.
- **The original also contains line breaks.** In 77 alignments it has a heading or list item on its own line.

`read_idem_corpus_ca.py` shows all of this in code and can export flat tables.

## Statistics

### Sentences

| | Value |
|---|---|
| Words per original sentence | mean 25.1, median 23 |
| Words per simplified line | mean 8.7, median 9 |
| Lines per alignment | mean 3.6, median 3, max 17 |
| Overall length (words) | 124% of the original |

Unlike the Spanish corpus, the Catalan simplifications are **longer** than the originals. The translators add explanations and glosses: the 24 alignments with code `8` or `00` grow to almost three times their original length (285% on average), the others to 119%.

### Documents

All 14 documents come from Barcelona institutions: ajuntament.barcelona.cat and its electronic office, barcelona.cat, sindicaturabarcelona.cat (the ombudsman) and decidim.barcelona.

| Category | Documents |
|---|---|
| Informative texts | 7 |
| Social justice & public policy analysis | 4 |
| Policy & administrative documents | 3 |

Topics include justice & governance, civic participation, social policy & disability accessibility, social justice (2 each), and tourism policy, digital governance, social services & taxation, data protection, sustainability, health (1 each).

Two documents make up half the corpus: `CAT_060_084` (social services & taxation, 96 alignments) and `CAT_024_047` (news on tourism policy, 89 alignments).

| Translator | Texts | Alignments | Documents |
|---|---|---|---|
| translator_4 | 52 | 185 | CAT_001 – CAT_052 |
| translator_5 | 53 | 198 | CAT_053 – CAT_105 |

All documents are copyright cleared. None were tested with a user group.

### Criteria

620 codes in total, 1.5 per simplified entry on average. Every entry has at least one code.

| Code | Uses | Criterion |
|---|---|---|
| 18 | 276 | Easily understandable, familiar words |
| 22 | 48 | Only common, frequent adverbs |
| 10 | 41 | Commas or lists for enumerations |
| 23 | 41 | Avoid abstract or technical words, or gloss them |
| 15 | 38 | Affirmative rather than negative sentences |
| 00 | 27 | Explanation added by the translator |
| 8 | 22 | Glossary or glosses for difficult terms |
| 0 | 20 | Transcription: sentence kept unchanged |

Code 18 appears on 68% of all entries. Consider analysing it separately so it does not dominate criteria statistics. Codes `8` and `00` almost always occur together.

### Annotations and quality flags

- **`complex_parts`:** 279 entries mark the difficult parts of the original.
- **`quality_flags`:** 89 alignments carry flags.
  - 69 alignments carry review flags, mostly about narrowed or shifted meaning and lost content.
  - The other flags start with `[v1.3]` or `[v1.4]`. They record corrections made in the JSON that are not yet in the source Excel, and they name the cells to fix there.

## Known issues not corrected

- **Website leftovers in 3 originals.** `CAT_054-2`, `CAT_054-4` and `CAT_055-2` start with `Tramit_Page.Description.dates`, `…price` or `…important_information`. These are template labels from the source website.
- **Typos in originals, left as published:** *altenativa* (CAT_004-6), *deducir* (CAT_071-3), *Se sollicita* (CAT_006-3), *l'organ* (CAT_005-1), *públic.Compra* (CAT_012-1), and *instal•lacions* / *col•laboració* written with a bullet instead of the middle dot (CAT_034-2, CAT_092-3).

## Versions

| Version | Date | Changes |
|---|---|---|
| 1.4 | 2026-11-05 | 28 clear orthography errors corrected in 27 simplified entries: 27 spaces after an elided article or pronoun removed (*l' Ajuntament* → *l'Ajuntament*), and *jutgats* → *jutjats* (CAT_091-2). Original texts, proper names and apostrophe styles unchanged. |
| 1.3 | 2026-09-25 | text_id corrections, criteria entries completed, counts recomputed. |
