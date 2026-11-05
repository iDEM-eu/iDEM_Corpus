"""
read_idem_corpus_it.py
======================

How to read the iDEM Italian corpus (idem_corpus_it_v1.4.json) correctly.

Run Italian corpus directly to see a short tour of the corpus:

    python read_idem_corpus_it.py idem_corpus_it_v1.4.json

Or import the helpers in your own code:

    from read_idem_corpus_it import load_corpus, iter_alignments, simplified_text, alignment_codes

Only the Python standard library is needed. pandas is optional and only used
by to_dataframe().

STRUCTURE IN ONE PICTURE
------------------------

    corpus        -> metadata about the whole corpus (version, counts, notes)
    criteria      -> the 31 lettura facile criteria codes used in this corpus
    documents     -> 16 source documents
      texts       -> 101 texts (a section of a document, one translator each)
        alignments  -> 325 original sentences
          simplified  -> 718 simplified entries, ordered by "position"

THREE THINGS TO GET RIGHT
-------------------------

1. One original sentence = one ALIGNMENT. Its simplification is spread over
   one or more entries in "simplified" (2.2 on average, up to 14), one entry
   per line of the easy-to-read text. An entry can hold several short
   sentences. Join all entries in "position" order to get the full version.
   Entries starting with "*" are bullet points.

2. The criteria codes belong to the WHOLE ALIGNMENT, not to the entry. They
   are repeated identically on every simplified entry of the alignment. Take
   them once per alignment (alignment_codes() does that). Counting them per
   entry inflates long simplifications; the "times_used" field in "criteria"
   is counted that way, so recount at alignment level for analyses.

3. Codes are strings ("2", "33", "0"), not integers. The JSON lists only the
   31 codes that are used (codes 1, 13 and 25 never occur). One alignment,
   IT_047-1, has no codes (the source cell read "x"; see "criteria_unparsed").
   Never compare codes with the Spanish or Catalan corpus: each language has
   its own catalogue.
"""

import json
import sys
from collections import Counter
from pathlib import Path


# ---------------------------------------------------------------------------
# 1. Loading
# ---------------------------------------------------------------------------

def load_corpus(path):
    """Load the JSON file. Always open Italian corpus as UTF-8 (accents, « », apostrophes)."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def criteria_lookup(corpus):
    """Return a dict: code (str) -> criterion entry.

    Each entry has: code, description (Italian), description_en, group
    (Parole, Ortotipografia, Testo, special), in_official_catalogue, times_used.
    """
    return {c["code"]: c for c in corpus["criteria"]}


# ---------------------------------------------------------------------------
# 2. Walking through the nested structure
# ---------------------------------------------------------------------------

def iter_alignments(corpus):
    """Yield (document, text, alignment) for every alignment, in corpus order."""
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
    """Full simplified version of one alignment: all entries in position order."""
    parts = sorted(alignment["simplified"], key=lambda s: s["position"])
    return sep.join((s["text"] or "").strip() for s in parts if (s["text"] or "").strip())


def alignment_codes(alignment):
    """The criteria codes of an alignment, taken ONCE (they repeat on every entry)."""
    entries = alignment["simplified"]
    return list(entries[0]["criteria_codes"]) if entries else []


# ---------------------------------------------------------------------------
# 3. Flat tables (easier for analysis, Excel, pandas)
# ---------------------------------------------------------------------------

def alignment_rows(corpus):
    """One row per ALIGNMENT: the unit the criteria codes describe."""
    rows = []
    for doc, text, al in iter_alignments(corpus):
        rows.append({
            "document_id": doc["document_id"],
            "text_id": text["text_id"],
            "translator_id": text["translator_id"],
            "alignment_id": al["alignment_id"],
            "original": al["original"],
            "simplified": simplified_text(al),
            "n_entries": len(al["simplified"]),
            "criteria_codes": sorted(alignment_codes(al), key=_code_sort_key),
            "quality_flags": al.get("quality_flags", []),
            "source_row": al["source_row"],
        })
    return rows


def entry_rows(corpus):
    """One row per SIMPLIFIED ENTRY (no criteria: they belong to the alignment)."""
    rows = []
    for doc, text, al, s in iter_simplified(corpus):
        rows.append({
            "document_id": doc["document_id"],
            "translator_id": text["translator_id"],
            "alignment_id": al["alignment_id"],
            "position": s["position"],
            "simplified": s["text"] or "",
            "is_bullet": (s["text"] or "").lstrip().startswith("*"),
            "complex_parts": s.get("complex_parts", []),
            "quality_flags": s.get("quality_flags", []),
            "source_row": s["source_row"],
        })
    return rows


def to_dataframe(rows):
    """Turn rows into a pandas DataFrame (needs: pip install pandas)."""
    import pandas as pd
    return pd.DataFrame(rows)


def _code_sort_key(code):
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

    alignments = list(iter_alignments(corpus))
    entries = list(iter_simplified(corpus))
    print(f"\nDocuments: {len(corpus['documents'])}")
    print(f"Texts:     {sum(len(d['texts']) for d in corpus['documents'])}")
    print(f"Alignments (original sentences): {len(alignments)}")
    print(f"Simplified entries:              {len(entries)}")

    # --- One example alignment -----------------------------------------
    doc, text, al = next(a for a in alignments if a[2]["alignment_id"] == "IT_023-2")
    print("\n--- Example alignment", al["alignment_id"], "---")
    print("Document:", doc["document_id"], "| Text:", text["text_id"],
          "| Translator:", text["translator_id"])
    print("Source:", doc["metadata"]["source_url"])
    print("\nORIGINAL:\n" + al["original"])
    print("\nSIMPLIFIED (entries in position order):")
    for s in sorted(al["simplified"], key=lambda s: s["position"]):
        print(f"  [{s['position']}] {s['text']}")
    print("\nCriteria codes for the whole alignment:")
    for c in alignment_codes(al):
        print(f"  {c:>3} = {crit[c]['description_en'][:70]}")
    if al.get("quality_flags"):
        print("\nQuality flags on this alignment:")
        for f in al["quality_flags"]:
            print("  -", f)

    # --- Criteria usage (counted once per alignment) --------------------
    usage = Counter(c for *_, al in alignments for c in alignment_codes(al))
    print("\nMost used criteria (counted once per alignment):")
    for code, n in usage.most_common(5):
        print(f"  {code:>3}  {n:4}x of {len(alignments)}  [{crit[code]['group']}] {crit[code]['description_en'][:55]}")

    # --- Quality flags -------------------------------------------------
    flagged = [al for *_, al in alignments if al.get("quality_flags")]
    print(f"\nAlignments with quality flags: {len(flagged)} of {len(alignments)}")

    try:
        df = to_dataframe(alignment_rows(corpus))
        print(f"\npandas DataFrame (one row per alignment): {df.shape[0]} rows x {df.shape[1]} columns")
        # df.to_excel("idem_it_alignments.xlsx", index=False)   # needs openpyxl
    except ImportError:
        print("\n(pandas not installed: skipping the DataFrame example)")


if __name__ == "__main__":
    default = Path(__file__).with_name("idem_corpus_it_v1.4.json")
    main(sys.argv[1] if len(sys.argv) > 1 else default)
