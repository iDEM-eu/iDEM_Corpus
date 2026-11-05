# iDEM Italian Corpus (v1.4): structure and statistics

`idem_corpus_it_v1.4.json` is a sentence-aligned corpus of Italian source texts and their **lettura facile** (easy-to-read, A2) versions. All simplifications were made by humans at capito. Each alignment is annotated with the lettura facile criteria that were applied to it.

> The Italian, Spanish and Catalan iDEM corpora are **not parallel**. Each language has its own criteria catalogue and conventions, so criterion codes must never be compared across languages. In the Italian file the criteria describe the **whole alignment**, not single sentences (see "How to read it").

## Overview

| | |
|---|---|
| Documents | 16 |
| Texts | 101 (`IT_001` – `IT_101`) |
| Alignments (original sentences) | 325 |
| Simplified entries | 718 (234 of them bullet points) |
| Words: original → simplified | 9,051 → 10,524 (116%) |
| Criteria codes used | 31 |
| Translators | 2 |

## Structure

The file has three top-level keys. The data lives in `documents`, nested four levels deep:

```
idem_corpus_it_v1.4.json
├── corpus                 metadata about the whole corpus
├── criteria               the 31 criteria codes used in this corpus
└── documents              16 source documents
      └── texts                 101 sections, one translator each
            └── alignments           325 original sentences
                  └── simplified          718 entries, one per line of easy-to-read text
```

### `corpus`

Version, date, source file, change log (`changes_in_this_version`), notes on segmentation and annotation (`annotation_unit` is `"alignment"`), and `counts`.

### `criteria`

```json
{
  "code": "33",
  "description": "...",
  "description_en": "Use of bullet point formatting",
  "group": "Testo",
  "in_official_catalogue": true,
  "times_used": 352
}
```

The Italian catalogue has codes 1–33 plus `0` (transcription: sentence kept unchanged) and `00` (explanation). **The JSON lists only the 31 codes that are used.** Codes 1, 13, 25 and `00` never occur.

| Group | Codes in use |
|---|---|
| Ortotipografia | 2, 3, 4 |
| Parole | 5–12, 14–24, 26–30 |
| Testo | 31, 32, 33 |
| special | `0` (used once) |

**About `times_used`:** it counts codes per simplified entry. Because the codes are repeated on every entry of an alignment, these numbers are inflated for long simplifications. For example, code 33 has `times_used` 352 but is applied in only 77 alignments. Recount at alignment level for analyses.

### `documents` → `texts` → `alignments` → `simplified`

| Level | Fields |
|---|---|
| **document** | `document_id` (e.g. `IT_023_027` = texts IT_023 to IT_027), `metadata`, `texts` |
| `metadata` | `source_url`, `creation_date`, `characters_without_spaces`, `corpus_category`, `text_type`, `topic`, `complexity_level`, `simplification_method`, `institution`, `tested_by_user_group`, `copyright_cleared` |
| **text** | `text_id`, `translator_id`, `alignments` |
| **alignment** | `alignment_id` (e.g. `IT_023-2` = 2nd sentence of text IT_023), `original`, `simplified`, `source_row`, `quality_flags` *(optional)* |
| **simplified entry** | `position`, `text`, `criteria_codes` (the alignment's codes, repeated), `complex_parts`, `source_row`, `quality_flags` *(optional)*, `criteria_unparsed` *(once)* |

`source_row` is the row in the source Excel file (`text_id_IT_iDEM_corpus_split_simplified.xlsx`).

## How to read it

**One alignment = one original sentence.** Its simplification is spread over one or more entries, one per line of the easy-to-read text. Lines starting with `*` are bullet points. The criteria codes sit on every entry, but they describe the alignment as a whole:

```
IT_023-2  original:   Eppure milioni di bambini nel mondo continuano a vedersi negati diritti
                      fondamentali come la salute, l'istruzione, un'infanzia serena, un futuro sicuro.
          simplified: [1] Ma ancora oggi, milioni di bambini nel mondo non hanno i diritti più
                          importanti. Per esempio:
                      [2] * la salute
                      [3] * andare a scuola
                      [4] * un'infanzia felice
                      [5] * un futuro sicuro
          criteria (whole alignment): 2, 4, 5, 8, 10, 11, 33
```

Points to watch:

- **Take the codes once per alignment.** They are identical on all entries. Counting them per entry gives long simplifications more weight.
- **An entry can hold more than one sentence.** On average an entry has 14.7 words. Join all entries in `position` order to get the full text.
- **One alignment has no codes.** IT_047-1 has empty `criteria_codes`; its source cell read `x` (kept in `criteria_unparsed`).
- **`creation_date` is incomplete.** It is empty for 9 documents.
- **The original also contains line breaks.** In 66 alignments it has a heading or list item on its own line.

`read_idem_corpus_it.py` shows all of this in code and can export flat tables.

## Statistics

### Sentences

| | Value |
|---|---|
| Words per original sentence | mean 27.8, median 25 |
| Words per simplified entry | mean 14.7, median 12 |
| Entries per alignment | mean 2.2, median 1, max 14 |
| Overall length (words) | 116% of the original |

The Italian simplifications are slightly longer than the originals. Alignments where technical terms are defined (code 12) grow to about 1.4 times their length, the others hardly at all. 180 of 325 alignments are simplified as a single entry; the rest are split into a lead sentence and bullet points or several short lines.

### Documents

| Category | Documents |
|---|---|
| Informative texts | 7 |
| Political & legal analysis | 4 |
| Advocacy & social responsibility | 3 |
| Institutional & legal documents | 2 |

Sources include europarl.europa.eu (3), pagellapolitica.it (4), citizens.ec.europa.eu, actionaid.it, ilpost.it, universability.it, geopop.it, fishets.it and fishonlus.it (disability federation FISH), and inps.it. Topics range from EU elections and institutions to referendums, legislative reform, US tariffs, children's rights and disability policy.

| Translator | Texts | Alignments | Documents |
|---|---|---|---|
| translator_6 | 46 | 171 | IT_001 – IT_046 |
| translator_7 | 55 | 154 | IT_047 – IT_101 |

All documents are copyright cleared. None were tested with a user group.

### Criteria

Counted once per alignment: 2,255 codes, 6.9 per alignment on average.

| Code | Alignments | Share | Criterion |
|---|---|---|---|
| 5 | 297 | 91% | Commonly used verbs |
| 2 | 276 | 85% | Periods or commas to separate ideas |
| 11 | 269 | 83% | Replace abstract terms, foreign words, jargon |
| 10 | 260 | 80% | Short, simple, common nouns |
| 8 | 168 | 52% | Commonly used adjectives |
| 7 | 148 | 46% | Commonly used adverbs |
| 33 | 77 | 24% | Bullet points |
| 3 | 77 | 24% | Avoid unusual punctuation |
| 22 | 72 | 22% | Remove relative clauses |
| 12 | 72 | 22% | Define technical terms |

Codes 2, 5, 10 and 11 appear in more than 80% of alignments. They describe the basic simplification method rather than distinguishing between sentences.

By group: Parole 1,738 (77%), Ortotipografia 416 (18%), Testo 100 (4%), special 1.

### Annotations and quality flags

- **`complex_parts`:** filled on all 718 entries.
- **`quality_flags`:** 44 alignments carry flags; 41 of them have review flags.
  - **Language errors in the simplified text (14 alignments):** agreement, preposition and word-choice errors, see below.
  - **Content shifts:** a detail dropped or a meaning narrowed.
  - **Formatting:** unbalanced guillemets « » in 10 alignments, mostly where a quotation spans two alignments.
  - **Corrections:** flags starting with `[v1.3]` or `[v1.4]` record corrections made in the JSON that are not yet in the source Excel, and they name the cells to fix there.

## Known issues not corrected

These are grammar or word-choice errors, not spelling, and they are already recorded in `quality_flags`. Version 1.4 corrects spelling only, so they are left as they are:

- **Agreement errors:** *i più grandi elezioni* (IT_002-2), *Il Parlamento europea* (IT_012-1), IT_018-5, IT_025-2, *le leggi italiani* (IT_062-3), *questo è la cosa più importante* (IT_064-2), IT_087-3, IT_096-1
- **Wrong preposition:** *dipende di* instead of *dipende da* (IT_003-5, IT_004-1)
- **Wrong verb construction or tense:** *consentire qualcuno a fare* (IT_037-3), present instead of conditional (IT_007-1)
- **Wrong word:** *tassi* (rates) instead of *tasse/dazi* (IT_068-1, IT_070-1)
- **Duplicated sentence:** IT_057-2 and IT_057-3 have the same simplified sentence.

**Typos in originals, left as published:** *Perchè* (IT_001-4, IT_047-2) and *decretodel* (IT_081-2).

## Versions

| Version | Date | Changes |
|---|---|---|
| 1.4 | 2026-11-05 | 1 spelling error corrected: *realità* → *realtà* (IT_053-1). A full spell check found no other spelling errors in the simplified texts. |
| 1.3 | 2026-09-25 | text_id corrections, criteria entries completed, counts recomputed. |
