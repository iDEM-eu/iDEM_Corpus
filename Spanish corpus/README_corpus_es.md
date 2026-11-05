# iDEM Spanish Corpus (v1.4): structure and statistics

`idem_corpus_es_v1.4.json` is a sentence-aligned corpus of Spanish source texts and their **Lectura Fácil** (easy-to-read, A2) versions. All simplifications were made by humans at PIM. Each simplified sentence is annotated with the Lectura Fácil criteria that were applied.

> The Spanish, Italian and Catalan iDEM corpora are **not parallel**. Each language has its own criteria catalogue and conventions, so criterion codes must never be compared across languages.

## Overview

| | |
|---|---|
| Documents | 17 |
| Texts | 107 (`ES_001` – `ES_107`) |
| Alignments (original sentences) | 356 |
| Simplified entries | 1,294 (2 empty) |
| Words: original → simplified | 10,542 → 10,111 |
| Criteria in catalogue | 35 |
| Translators | 3 |

## Structure

The file has three top-level keys. The data lives in `documents`, nested four levels deep:

```
idem_corpus_es_v1.4.json
├── corpus                 metadata about the whole corpus
├── criteria               the criteria catalogue (35 entries)
└── documents              17 source documents
      └── texts                 107 sections, one translator each
            └── alignments           356 original sentences
                  └── simplified          1,294 simplified entries
```

### `corpus`

Version, date, source file, change log (`changes_in_this_version`), notes on segmentation and annotation, and `counts`.

### `criteria`

```json
{
  "code": "3",
  "description": "No usar punto y coma (;), puntos suspensivos (...) ...",
  "description_en": "Avoid use of semicolons (;), ellipses (...), etc., parentheses, ...",
  "group": "Ortotipografía",
  "in_official_catalogue": true,
  "times_used": 47
}
```

| Group | Codes |
|---|---|
| Ortotipografía | 1–4 |
| Palabras | 5–9, 11–18 |
| Frases | 19–31 |
| Texto | 32–34 |
| special | `0` (transcription: sentence kept unchanged), `00` (explanation) |

Code 10 does not exist in the Spanish catalogue.

### `documents` → `texts` → `alignments` → `simplified`

| Level | Fields |
|---|---|
| **document** | `document_id` (e.g. `ES_001_005` = texts ES_001 to ES_005), `metadata`, `texts` |
| `metadata` | `source_url`, `creation_date`, `characters_without_spaces`, `corpus_category`, `text_type`, `topic`, `complexity_level`, `simplification_method`, `institution`, `tested_by_user_group`, `copyright_cleared` |
| **text** | `text_id`, `translator_id`, `alignments` |
| **alignment** | `alignment_id` (e.g. `ES_032-3` = 3rd sentence of text ES_032), `original`, `simplified`, `source_row`, `quality_flags` *(optional)* |
| **simplified entry** | `position`, `text`, `criteria_codes`, `complex_parts`, `source_row`, `quality_flags` *(optional)*, `notes` *(optional)* |

`source_row` is the row in the source Excel file (`text_id_ES_iDEM_corpus_split_simplified.xlsm`).

## How to read it

**One alignment = one original sentence.** Its simplification is split into several entries in `simplified`, one per line of the easy-to-read text. To get the full simplified version, join all entries of an alignment in `position` order:

```
ES_032-3  original:   Despliegue del euro digital. El pleno señala que la confianza del público
                      es imprescindible para que el euro digital tenga éxito e insiste en que ...
          simplified: [1] Comienzo del euro digital
                      [2] El parlamento dice que la confianza de los ciudadanos es importante
                      [3] para que el euro digital tenga éxito
                      [4] e insiste que el Banco Central europeo
                      [5] tiene que mostrar sus beneficios antes de que los diputados,
                      [6] además del Consejo de Gobierno del Banco Central Europeo,
                      [7] decidan introducir el euro digital.
```

Points to watch:

- **An entry is a line, not always a sentence.** One sentence can run over several entries (positions 4–7 above).
- **Criteria are annotated per entry.** `criteria_codes` describe the entry they sit on. Codes are strings (`"2"`, `"00"`), not integers.
- **`text` can be empty or `null`** (ES_023-2 position 5, ES_097-3 position 1). Use `s["text"] or ""`.
- **Optional fields.** `quality_flags` and `notes` are only present where needed.
- **`counts.simplified_sentences`** (1,292) excludes the 2 empty entries; the file contains 1,294.

`read_idem_corpus_es.py` shows all of this in code and can export flat tables.

## Statistics

### Sentences

| | Value |
|---|---|
| Words per original sentence | mean 29.6, median 27 |
| Words per simplified entry | mean 7.8 |
| Simplified entries per alignment | mean 3.6, median 3, max 16 |
| Overall length (words) | 96% of the original |

The simplified texts are about as long as the originals but split into much shorter lines.

### Documents

| Category | Documents |
|---|---|
| Informative texts | 11 |
| Political & ideological articles | 2 |
| News articles | 2 |
| Policy & legislative documents | 2 |

Topics include civic participation (4), social policy (3), justice & legal affairs (2), and EU elections, economic policy, institutions and legislation (1 each). Sources include comunidad.madrid, europarl.europa.eu, citizens.ec.europa.eu, ajuntament.barcelona.cat, eldiario.es and es.wikipedia.org.

The largest document, `ES_083_107` (eldiario.es), holds 80 alignments and 323 simplified entries, about a quarter of the corpus.

| Translator | Texts | Alignments |
|---|---|---|
| translator_1 | 29 | 86 |
| translator_2 | 40 | 134 |
| translator_3 | 38 | 136 |

All documents are copyright cleared. None were tested with a user group. `creation_date` is missing for 10 documents.

### Criteria

1,930 codes in total, 1.5 per simplified entry on average. Every entry has at least one code.

| Group | Uses |
|---|---|
| Ortotipografía | 880 |
| Palabras | 692 |
| Frases | 294 |
| Texto | 57 |
| special | 7 |

| Code | Uses | Criterion |
|---|---|---|
| 2 | 823 | Paragraph or line breaks to separate ideas |
| 11 | 173 | Short, simple, common nouns |
| 5 | 142 | Frequent/common verbs |
| 12 | 139 | Replace abstract terms, foreign words, technical terms |
| 23 | 101 | Logical order: subject + verb + predicate |
| 13 | 76 | Define necessary technical terms |
| 19 | 56 | Indicative mood and simple tenses |
| 25 | 53 | Add the subject to avoid ellipsis |

Code 2 appears on 64% of all entries. Consider analysing it separately so it does not dominate criteria statistics.

### Annotations and quality flags

- **`complex_parts`:** 565 entries mark the difficult parts of the original.
- **`quality_flags`:** 64 alignments carry flags.
  - Most describe content changes, such as lost or shifted meaning.
  - A few describe formatting, such as unbalanced quotes or website leftovers.
  - Flags starting with `[v1.3]` or `[v1.4]` record corrections made in the JSON that are not yet in the source Excel. They also name the cells to fix there.
- **`notes`:** 10 entries carry notes.

## Versions

| Version | Date | Changes |
|---|---|---|
| 1.4 | 2026-11-05 | 23 clear spelling errors corrected in 21 simplified entries (mostly missing accents; `auro` → `euro` in ES_032-3). Original texts and proper names unchanged. |
| 1.3 | 2026-09-25 | text_id corrections, 4 duplicate sentences removed, criteria catalogue completed, counts recomputed. |
