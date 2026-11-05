"""
analyse_idem_corpus_es.py
Short exploratory analysis of the iDEM Spanish corpus (v1.4).

    pip install pandas
    python analyse_idem_corpus_es.py idem_corpus_es_v1.4.json

Builds two tables (one row per alignment, one per simplified line) and prints:
  1. descriptive statistics          5. criteria co-occurrence
  2. original vs simplified          6. criteria profile per translator
  3. readability (Fernández Huerta)  7. what predicts the number of lines
  4. comparison between translators  8. flagged vs unflagged alignments
"""
import json, re, sys
from collections import Counter
from itertools import combinations
import pandas as pd

pd.set_option("display.width", 120, "display.max_columns", 20, "display.precision", 2)
import warnings; warnings.filterwarnings("ignore", category=RuntimeWarning)
PATH = sys.argv[1] if len(sys.argv) > 1 else "idem_corpus_es_v1.4.json"
corpus = json.load(open(PATH, encoding="utf-8"))
CRIT = {c["code"]: c for c in corpus["criteria"]}

# ---------- text helpers -------------------------------------------------
WORD = re.compile(r"\w+")  # words and numbers
words = lambda s: WORD.findall(s or "")
def syllables(w):  # heuristic: one syllable per vowel group (good enough for Spanish)
    return max(1, len(re.findall(r"[aeiouáéíóúüy]+", w.lower())))
def sentences(s):  # sentence = text up to . ! ? (line breaks are layout, not sentence ends)
    return max(1, sum(1 for p in re.split(r"[.!?]+", s or "") if words(p)))
def fernandez_huerta(text):
    """Spanish readability, 0-100, higher = easier (60-70 ~ 'normal', 80+ ~ 'easy')."""
    w = words(text)
    if not w: return None
    return 206.84 - 0.60 * (100 * sum(map(syllables, w)) / len(w)) - 1.02 * (100 * sentences(text) / len(w))

# ---------- tables -------------------------------------------------------
A, S = [], []
for doc in corpus["documents"]:
    for text in doc["texts"]:
        for al in text["alignments"]:
            lines = sorted(al["simplified"], key=lambda s: s["position"])
            simp = "\n".join(s["text"] or "" for s in lines)
            wo, ws = words(al["original"]), words(simp)
            A.append(dict(alignment_id=al["alignment_id"], document_id=doc["document_id"],
                          translator=text["translator_id"], topic=doc["metadata"]["topic"],
                          n_lines=len(lines), words_orig=len(wo), words_simp=len(ws),
                          wordlen_orig=sum(map(len, wo)) / max(1, len(wo)),
                          wordlen_simp=sum(map(len, ws)) / max(1, len(ws)),
                          fh_orig=fernandez_huerta(al["original"]),
                          fh_simp=fernandez_huerta(simp),
                          vocab_overlap=len({x.lower() for x in wo} & {x.lower() for x in ws}) / max(1, len({x.lower() for x in wo})),
                          unchanged=simp.strip() == al["original"].strip(),
                          flagged=bool(al.get("quality_flags"))))
            for s in lines:
                S.append(dict(alignment_id=al["alignment_id"], translator=text["translator_id"],
                              position=s["position"], words=len(words(s["text"])),
                              codes=s["criteria_codes"], n_codes=len(s["criteria_codes"])))
A, S = pd.DataFrame(A), pd.DataFrame(S)
A["compression"] = A.words_simp / A.words_orig.where(A.words_orig > 0)

def section(title): print(f"\n{'=' * 70}\n{title}\n{'=' * 70}")

# ---------- 1. descriptive statistics ------------------------------------
section("1. Descriptive statistics")
print(f"{A.document_id.nunique()} documents · {len(A)} alignments · {len(S)} simplified lines")
print(A[["n_lines", "words_orig", "words_simp", "compression"]].describe().T[["mean", "std", "min", "50%", "max"]])
print(f"\nWords per simplified line: mean {S.words.mean():.1f}, median {S.words.median():.0f}")

# ---------- 2. original vs simplified ------------------------------------
section("2. Original vs simplified")
print(pd.DataFrame({
    "original":   [A.words_orig.sum(), A.wordlen_orig.mean(), A.words_orig.mean()],
    "simplified": [A.words_simp.sum(), A.wordlen_simp.mean(), S.words.mean()],
}, index=["total words", "mean word length (chars)", "mean words per sentence/line"]))
print(f"\nShare of original vocabulary kept: {A.vocab_overlap.mean():.0%} (mean per alignment)")
print(f"Alignments returned unchanged: {A.unchanged.sum()}")

# ---------- 3. readability -----------------------------------------------
section("3. Readability: Fernández Huerta index (higher = easier)")
r = A[["fh_orig", "fh_simp"]].dropna()
print(r.describe().T[["mean", "std", "50%"]])
print(f"\nSimplified text is easier in {(r.fh_simp > r.fh_orig).mean():.0%} of alignments "
      f"(mean gain {(r.fh_simp - r.fh_orig).mean():+.1f} points)")
print("Note: syllables are estimated heuristically. Line breaks are not counted as sentence ends,\n"
      "so the index captures word difficulty and punctuation-based sentence length, not the layout gain.")

# ---------- 4. translators -----------------------------------------------
section("4. Comparison between translators")
t = A.groupby("translator").agg(alignments=("alignment_id", "count"), lines_per_sent=("n_lines", "mean"),
                                compression=("compression", "mean"), fh_gain=("fh_simp", "mean"),
                                flagged=("flagged", "mean"))
t["fh_gain"] -= A.groupby("translator").fh_orig.mean()
t = t.join(S.groupby("translator").agg(words_per_line=("words", "mean"), codes_per_line=("n_codes", "mean")))
print(t)
print("Caution: each translator worked on different documents, so differences mix style and source text.")

# ---------- 5. criteria co-occurrence ------------------------------------
section("5. Criteria: most frequent pairs on the same line (excluding code 2)")
pairs = Counter(p for codes in S.codes for p in combinations(sorted(set(codes) - {"2"}), 2))
freq = Counter(c for codes in S.codes for c in codes)
for (a, b), n in pairs.most_common(8):
    lift = n * len(S) / (freq[a] * freq[b])
    print(f"  {a:>3} + {b:<3} {n:3}x  lift {lift:4.1f}   {CRIT[a]['description_en'][:28]} | {CRIT[b]['description_en'][:28]}")
print("Lift > 1: the two codes appear together more often than by chance.")

# ---------- 6. criteria profile per translator ---------------------------
section("6. Criteria group profile per translator (share of applied codes)")
long = S.explode("codes").dropna(subset=["codes"]).reset_index(drop=True)
long["group"] = long.codes.map(lambda c: CRIT[c]["group"])
print(pd.crosstab(long.translator, long.group, normalize="index").mul(100).round(0))

# ---------- 7. what drives the number of lines ---------------------------
section("7. What drives the number of simplified lines? (Spearman correlation)")
print(A[["n_lines", "words_orig", "wordlen_orig", "fh_orig"]].corr(method="spearman")["n_lines"].drop("n_lines").round(2))

# ---------- 8. flagged vs unflagged --------------------------------------
section("8. Alignments with quality flags vs without")
print(A.groupby("flagged")[["words_orig", "n_lines", "compression", "vocab_overlap"]].mean())
print("\nFlag rate per document (top 5):")
print(A.groupby("document_id").flagged.mean().sort_values(ascending=False).head(5).map("{:.0%}".format))
