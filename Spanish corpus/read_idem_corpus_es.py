"""
read_idem_corpus_es.py
======================

How to read the iDEM Spanish corpus (idem_corpus_es_v1.4.json) correctly.

Run Italian corpus directly to see a short tour of the corpus:

    python read_idem_corpus_es.py idem_corpus_es_v1.4.json

Or import the helpers in your own code:

    from read_idem_corpus_es import load_corpus, iter_alignments, simplified_text

Only the Python standard library is needed. pandas is optional and only used
by to_dataframe().

STRUCTURE IN ONE PICTURE
------------------------

    corpus        -> metadata about the whole corpus (version, counts, notes)
    criteria      -> list of the 35 Lectura Facil criteria (code -> description)
    documents     -> 17 source documents
      texts       -> 107 texts (a section of a document, one translator each)
        alignments  -> 356 original sentences
          simplified  -> 1294 simplified sentences, ordered by "position"

THREE THINGS TO GET RIGHT
-------------------------

1. One original sentence = one ALIGNMENT. Its simplification is spread over
   several entries in "simplified" (3.6 on average, up to 16). To get the full
   simplified version, join all entries of the alignment in "position" order.
   A single sentence is sometimes split across two consecutive entries, so do
   not treat one entry as one grammatical sentence.

2. "text" of a simplified entry can be an empty string or null (2 cases in
   v1.4). Always use  (s["text"] or "")  instead of  s["text"].

3. "criteria_codes" are strings ("2", "11", "0", "00"), not integers, and they
   describe the individual simplified entry they sit on. Look them up in
   "criteria". Never compare codes with the Italian or Catalan corpus: each
   language has its own catalogue.
"""

import json
import sys
from collections import Counter
from pathlib import Path


# ---------------------------------------------------------------------------
# 1. Loading
# ---------------------------------------------------------------------------

def load_corpus(path):
    """Load the JSON file. Always open Italian corpus as UTF-8 (accents, ñ, ¿, ¡)."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def criteria_lookup(corpus):
    """Return a dict: code (str) -> criterion entry.

    Each entry has: code, description (Spanish), description_en, group
    (Palabras, Frases, Ortotipografía, Texto, special), in_official_catalogue,
    times_used.
    """
    return {c["code"]: c for c in corpus["criteria"]}


# ---------------------------------------------------------------------------
# 2. Walking through the nested structure
# ---------------------------------------------------------------------------

def iter_alignments(corpus):
    """Yield (document, text, alignment) for every alignment, in corpus order.

    This is the main loop you need: an alignment is one original sentence
    together with all of its simplified sentences.
    """
    for document in corpus["documents"]:
        for text in document["texts"]:
            for alignment in text["alignments"]:
                yield document, text, alignment


def iter_simplified(corpus):
    """Yield (document, text, alignment, simplified_entry) for every entry."""
    for document, text, alignment in iter_alignments(corpus):
        for entry in sorted(alignment["simplified"], key=lambda s: s["position"]):
            yield document, text, alignment, entry


def simplified_text(alignment, sep="\n"):
    """Full simplified version of one alignment.

    Joins all entries in position order and skips empty/null ones. The
    default separator is a line break, because in Lectura Facil every entry
    is printed on its own line. Use sep=" " if you want running text.
    """
    parts = sorted(alignment["simplified"], key=lambda s: s["position"])
    return sep.join((s["text"] or "").strip() for s in parts if (s["text"] or "").strip())


def alignment_codes(alignment):
    """All criteria codes used anywhere in the alignment (with repetitions)."""
    return [c for s in alignment["simplified"] for c in s["criteria_codes"]]


# ---------------------------------------------------------------------------
# 3. Flat tables (easier for analysis, Excel, pandas)
# ---------------------------------------------------------------------------

def alignment_rows(corpus):
    """One row per ALIGNMENT: original next to the full simplification."""
    rows = []
    for doc, text, al in iter_alignments(corpus):
        rows.append({
            "document_id": doc["document_id"],
            "text_id": text["text_id"],
            "translator_id": text["translator_id"],
            "alignment_id": al["alignment_id"],
            "original": al["original"],
            "simplified": simplified_text(al),
            "n_simplified_entries": len(al["simplified"]),
            "criteria_codes": sorted(set(alignment_codes(al)), key=_code_sort_key),
            "quality_flags": al.get("quality_flags", []),
            "source_row": al["source_row"],
        })
    return rows


def sentence_rows(corpus):
    """One row per SIMPLIFIED ENTRY: the unit the criteria codes describe."""
    rows = []
    for doc, text, al, s in iter_simplified(corpus):
        rows.append({
            "document_id": doc["document_id"],
            "text_id": text["text_id"],
            "translator_id": text["translator_id"],
            "alignment_id": al["alignment_id"],
            "position": s["position"],
            "simplified": s["text"] or "",
            "criteria_codes": s["criteria_codes"],
            "complex_parts": s.get("complex_parts", []),
            "quality_flags": s.get("quality_flags", []),
            "notes": s.get("notes"),
            "source_row": s["source_row"],
        })
    return rows


def to_dataframe(rows):
    """Turn rows into a pandas DataFrame (needs: pip install pandas)."""
    import pandas as pd
    return pd.DataFrame(rows)


def _code_sort_key(code):
    # "0" and "00" first, then numeric order
    return (0, code) if not code.isdigit() or code.startswith("0") else (1, int(code))


# ---------------------------------------------------------------------------
# 4. Demo: run this file to see how everything fits together
# ---------------------------------------------------------------------------

def main(path):
    corpus = load_corpus(path)
    meta = corpus["corpus"]
    crit = criteria_lookup(corpus)

    print(f"iDEM corpus: {meta['language_name']} v{meta['version']} ({meta['generated']})")
    print(f"Declared counts: {meta['counts']}")

    # --- Counting -------------------------------------------------------
    alignments = list(iter_alignments(corpus))
    entries = list(iter_simplified(corpus))
    print(f"\nDocuments: {len(corpus['documents'])}")
    print(f"Texts:     {sum(len(d['texts']) for d in corpus['documents'])}")
    print(f"Alignments (original sentences): {len(alignments)}")
    print(f"Simplified entries:              {len(entries)}")
    print(f"  of which empty or null:        {sum(1 for *_, s in entries if not (s['text'] or '').strip())}")

    # --- One example alignment -----------------------------------------
    doc, text, al = next(a for a in alignments if a[2]["alignment_id"] == "ES_032-3")
    print("\n--- Example alignment", al["alignment_id"], "---")
    print("Document:", doc["document_id"], "| Text:", text["text_id"],
          "| Translator:", text["translator_id"])
    print("Source:", doc["metadata"]["source_url"])
    print("\nORIGINAL:\n" + al["original"])
    print("\nSIMPLIFIED (entries joined in position order):\n" + simplified_text(al))
    print("\nEntry by entry, with the criteria they apply:")
    for s in sorted(al["simplified"], key=lambda s: s["position"]):
        names = "; ".join(f"{c} = {crit[c]['description_en'][:45]}..." for c in s["criteria_codes"])
        print(f"  [{s['position']}] {s['text'] or ''}\n        codes: {names}")
    if al.get("quality_flags"):
        print("\nQuality flags on this alignment:")
        for f in al["quality_flags"]:
            print("  -", f)

    # --- Criteria usage -------------------------------------------------
    usage = Counter(c for *_, s in entries for c in s["criteria_codes"])
    print("\nMost used criteria (counted per simplified entry):")
    for code, n in usage.most_common(5):
        print(f"  {code:>3}  {n:4}x  [{crit[code]['group']}] {crit[code]['description_en'][:60]}")

    # --- Quality flags -------------------------------------------------
    flagged = [al for *_, al in alignments if al.get("quality_flags")]
    print(f"\nAlignments with quality flags: {len(flagged)} of {len(alignments)}")
    print(f"  of which spelling corrections from v1.4: "
          f"{sum(1 for al in flagged if any(f.startswith('[v1.4]') for f in al['quality_flags']))}")

    # --- Optional: export flat tables ----------------------------------
    try:
        df = to_dataframe(alignment_rows(corpus))
        print(f"\npandas DataFrame (one row per alignment): {df.shape[0]} rows x {df.shape[1]} columns")
        # df.to_excel("idem_es_alignments.xlsx", index=False)   # needs openpyxl
        # df.to_csv("idem_es_alignments.csv", index=False, encoding="utf-8")
    except ImportError:
        print("\n(pandas not installed: skipping the DataFrame example)")


if __name__ == "__main__":
    default = Path(__file__).with_name("idem_corpus_es_v1.4.json")
    main(sys.argv[1] if len(sys.argv) > 1 else default)
