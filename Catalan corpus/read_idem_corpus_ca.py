"""
read_idem_corpus_ca.py
======================

How to read the iDEM Catalan corpus (idem_corpus_ca_v1.4.json) correctly.

Run Italian corpus directly to see a short tour of the corpus:

    python read_idem_corpus_ca.py idem_corpus_ca_v1.4.json

Or import the helpers in your own code:

    from read_idem_corpus_ca import load_corpus, iter_alignments, simplified_text, split_lines

Only the Python standard library is needed. pandas is optional and only used
by to_dataframe().

STRUCTURE IN ONE PICTURE
------------------------

    corpus        -> metadata about the whole corpus (version, counts, notes)
    criteria      -> the 25 DINCAT criteria codes used in this corpus
    documents     -> 14 source documents
      texts       -> 105 texts (a section of a document, one translator each)
        alignments  -> 383 original sentences
          simplified  -> 408 simplified entries, ordered by "position"
            (text)    -> 1,379 lines, separated by "\\n" inside each entry

THREE THINGS TO GET RIGHT
-------------------------

1. The Catalan corpus is organised differently from the Spanish one. Almost
   every alignment (361 of 383) has ONE simplified entry, and that entry holds
   the whole easy-to-read version: its lines are separated by line breaks
   ("\\n") inside "text". To work with lines, split the text on "\\n".

2. A few alignments (22) have 2 or 3 entries. The extra entries usually add a
   gloss or explanation (codes 8 and 00). Join all entries in "position"
   order to get the full simplification.

3. "criteria_codes" are strings ("18", "0", "00"), not integers, and they
   describe the whole simplified entry they sit on (all of its lines). Look
   them up in "criteria". The JSON lists only the 25 codes that are used, not
   the full DINCAT catalogue. Never compare codes with the Spanish or Italian
   corpus: each language has its own catalogue.
"""

import json
import sys
from collections import Counter
from pathlib import Path


# ---------------------------------------------------------------------------
# 1. Loading
# ---------------------------------------------------------------------------

def load_corpus(path):
    """Load the JSON file. Always open Italian corpus as UTF-8 (accents, l·l, apostrophes)."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def criteria_lookup(corpus):
    """Return a dict: code (str) -> criterion entry.

    Each entry has: code, description (Catalan), description_en, group
    (linguistic or special), in_official_catalogue, times_used.
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


def split_lines(entry_or_text):
    """The lines of one simplified entry (or of any text), without empty lines."""
    text = entry_or_text["text"] if isinstance(entry_or_text, dict) else entry_or_text
    return [line.strip() for line in (text or "").split("\n") if line.strip()]


def simplified_text(alignment, sep="\n"):
    """Full simplified version of one alignment: all entries in position order."""
    parts = sorted(alignment["simplified"], key=lambda s: s["position"])
    return sep.join(line for s in parts for line in split_lines(s))


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
            "n_entries": len(al["simplified"]),
            "n_lines": len(simplified_text(al).split("\n")),
            "criteria_codes": sorted(set(alignment_codes(al)), key=_code_sort_key),
            "quality_flags": al.get("quality_flags", []),
            "source_row": al["source_row"],
        })
    return rows


def entry_rows(corpus):
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
            "n_lines": len(split_lines(s)),
            "criteria_codes": s["criteria_codes"],
            "complex_parts": s.get("complex_parts", []),
            "quality_flags": s.get("quality_flags", []),
            "source_row": s["source_row"],
        })
    return rows


def line_rows(corpus):
    """One row per LINE of simplified text (no criteria: codes sit on entries)."""
    rows = []
    for doc, text, al, s in iter_simplified(corpus):
        for i, line in enumerate(split_lines(s), start=1):
            rows.append({"alignment_id": al["alignment_id"], "position": s["position"],
                         "line_no": i, "line": line, "translator_id": text["translator_id"]})
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
    lines = line_rows(corpus)
    print(f"\nDocuments: {len(corpus['documents'])}")
    print(f"Texts:     {sum(len(d['texts']) for d in corpus['documents'])}")
    print(f"Alignments (original sentences): {len(alignments)}")
    print(f"Simplified entries:              {len(entries)}")
    print(f"Lines inside those entries:      {len(lines)}")
    print(f"Alignments with more than one entry: "
          f"{sum(1 for *_, al in alignments if len(al['simplified']) > 1)}")

    # --- One example alignment -----------------------------------------
    doc, text, al = next(a for a in alignments if a[2]["alignment_id"] == "CAT_001-1")
    print("\n--- Example alignment", al["alignment_id"], "---")
    print("Document:", doc["document_id"], "| Text:", text["text_id"],
          "| Translator:", text["translator_id"])
    print("Source:", doc["metadata"]["source_url"])
    print("\nORIGINAL:\n" + al["original"])
    for s in al["simplified"]:
        print(f"\nSIMPLIFIED ENTRY, position {s['position']} ({len(split_lines(s))} lines):")
        for i, line in enumerate(split_lines(s), 1):
            print(f"  {i}. {line}")
        print("  criteria codes for the whole entry:")
        for c in s["criteria_codes"]:
            print(f"    {c:>3} = {crit[c]['description_en'][:70]}...")
    if al.get("quality_flags"):
        print("\nQuality flags on this alignment:")
        for f in al["quality_flags"]:
            print("  -", f)

    # --- Criteria usage -------------------------------------------------
    usage = Counter(c for *_, s in entries for c in s["criteria_codes"])
    print("\nMost used criteria (counted per simplified entry):")
    for code, n in usage.most_common(5):
        print(f"  {code:>3}  {n:4}x  {crit[code]['description_en'][:65]}")

    # --- Quality flags -------------------------------------------------
    flagged = [al for *_, al in alignments if al.get("quality_flags")]
    print(f"\nAlignments with quality flags: {len(flagged)} of {len(alignments)}")
    print(f"  of which corrections from v1.4: "
          f"{sum(1 for al in flagged if any(f.startswith('[v1.4]') for f in al['quality_flags']))}")

    try:
        df = to_dataframe(alignment_rows(corpus))
        print(f"\npandas DataFrame (one row per alignment): {df.shape[0]} rows x {df.shape[1]} columns")
        # df.to_excel("idem_ca_alignments.xlsx", index=False)   # needs openpyxl
    except ImportError:
        print("\n(pandas not installed: skipping the DataFrame example)")


if __name__ == "__main__":
    default = Path(__file__).with_name("idem_corpus_ca_v1.4.json")
    main(sys.argv[1] if len(sys.argv) > 1 else default)
