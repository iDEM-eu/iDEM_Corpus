"""
analyse_idem_corpus_it.py
Short exploratory analysis of the iDEM Italian corpus (v1.4).

    pip install pandas
    python analyse_idem_corpus_it.py idem_corpus_it_v1.4.json

Builds two tables (one row per alignment, one per simplified entry) and prints:
  1. descriptive statistics          5. criteria co-occurrence
  2. original vs simplified          6. criteria group profile per translator
  3. readability (LIX)               7. what drives the number of entries
  4. comparison between translators  8. flagged vs unflagged alignments

Criteria codes belong to the whole alignment in the Italian corpus, so they are
counted once per alignment throughout.
"""
import json, re, sys, warnings
from collections import Counter
from itertools import combinations
import pandas as pd

warnings.filterwarnings("ignore", category=RuntimeWarning)
pd.set_option("display.width", 120, "display.max_columns", 20, "display.precision", 2)
PATH = sys.argv[1] if len(sys.argv) > 1 else "idem_corpus_it_v1.4.json"
corpus = json.load(open(PATH, encoding="utf-8"))
CRIT = {c["code"]: c for c in corpus["criteria"]}

# ---------- text helpers -------------------------------------------------
WORD = re.compile(r"\w+")
words = lambda s: WORD.findall(s or "")
def sentences(s):  # sentence = text up to . ! ? (line breaks are layout, not sentence ends)
    return max(1, sum(1 for p in re.split(r"[.!?]+", s or "") if words(p)))
def lix(text):
    """LIX readability: words per sentence + % words longer than 6 letters.
    Language-independent; lower = easier (under 30 very easy, 40 average, over 50 hard)."""
    w = words(text)
    if not w: return None
    return len(w) / sentences(text) + 100 * sum(len(x) > 6 for x in w) / len(w)

# ---------- tables -------------------------------------------------------
A, E = [], []
for doc in corpus["documents"]:
    for text in doc["texts"]:
        for al in text["alignments"]:
            entries = sorted(al["simplified"], key=lambda s: s["position"])
            simp = "\n".join(s["text"] or "" for s in entries)
            wo, ws = words(al["original"]), words(simp)
            codes = list(entries[0]["criteria_codes"]) if entries else []   # once per alignment
            A.append(dict(alignment_id=al["alignment_id"], document_id=doc["document_id"],
                          translator=text["translator_id"], n_entries=len(entries),
                          n_bullets=sum((s["text"] or "").lstrip().startswith("*") for s in entries),
                          words_orig=len(wo), words_simp=len(ws),
                          wordlen_orig=sum(map(len, wo)) / max(1, len(wo)),
                          wordlen_simp=sum(map(len, ws)) / max(1, len(ws)),
                          lix_orig=lix(al["original"]), lix_simp=lix(simp),
                          vocab_overlap=len({x.lower() for x in wo} & {x.lower() for x in ws}) / max(1, len({x.lower() for x in wo})),
                          codes=codes, n_codes=len(codes), defines_terms="12" in codes,
                          unchanged=simp.strip() == al["original"].strip(),
                          flagged=any(not f.startswith("[v1.") for f in al.get("quality_flags", []))))  # review flags only
            for s in entries:
                E.append(dict(alignment_id=al["alignment_id"], translator=text["translator_id"], words=len(words(s["text"]))))
A, E = pd.DataFrame(A), pd.DataFrame(E)
A["growth"] = A.words_simp / A.words_orig.where(A.words_orig > 0)

def section(title): print(f"\n{'=' * 70}\n{title}\n{'=' * 70}")

# ---------- 1. descriptive statistics ------------------------------------
section("1. Descriptive statistics")
print(f"{A.document_id.nunique()} documents · {len(A)} alignments · {len(E)} simplified entries")
print(A[["n_entries", "words_orig", "words_simp", "growth", "n_codes"]].describe().T[["mean", "std", "min", "50%", "max"]])
print(f"\nWords per simplified entry: mean {E.words.mean():.1f}, median {E.words.median():.0f}")
print(f"Bullet-point entries: {A.n_bullets.sum()} of {len(E)}")

# ---------- 2. original vs simplified ------------------------------------
section("2. Original vs simplified")
print(pd.DataFrame({
    "original":   [A.words_orig.sum(), A.wordlen_orig.mean(), A.words_orig.mean()],
    "simplified": [A.words_simp.sum(), A.wordlen_simp.mean(), E.words.mean()],
}, index=["total words", "mean word length (chars)", "mean words per sentence/entry"]))
print(f"\nThe simplified text is {A.words_simp.sum() / A.words_orig.sum():.0%} as long as the original.")
print("  growth when terms are defined (code 12): {:.2f}   without: {:.2f}".format(
    A[A.defines_terms].growth.mean(), A[~A.defines_terms].growth.mean()))
print(f"Share of original vocabulary kept: {A.vocab_overlap.mean():.0%} (mean per alignment)")
print(f"Alignments returned unchanged: {A.unchanged.sum()}")

# ---------- 3. readability -----------------------------------------------
section("3. Readability: LIX (lower = easier)")
r = A[["lix_orig", "lix_simp"]].dropna()
print(r.describe().T[["mean", "std", "50%"]])
print(f"\nSimplified text is easier in {(r.lix_simp < r.lix_orig).mean():.0%} of alignments "
      f"(mean change {(r.lix_simp - r.lix_orig).mean():+.1f} points)")
print("Note: line breaks are not counted as sentence ends, so LIX reflects word length\n"
      "and punctuation-based sentence length, not the layout gain.")

# ---------- 4. translators -----------------------------------------------
section("4. Comparison between translators")
t = A.groupby("translator").agg(alignments=("alignment_id", "count"), entries_per_sent=("n_entries", "mean"),
                                growth=("growth", "mean"), lix_change=("lix_simp", "mean"),
                                codes_per_al=("n_codes", "mean"), bullets_per_al=("n_bullets", "mean"),
                                flagged=("flagged", "mean"))
t["lix_change"] -= A.groupby("translator").lix_orig.mean()
t = t.join(E.groupby("translator").agg(words_per_entry=("words", "mean")))
print(t)
print("Caution: each translator worked on different documents, so differences mix style and source text.")

# ---------- 5. criteria co-occurrence ------------------------------------
section("5. Criteria: most frequent pairs (excluding the near-universal codes 2, 5, 10, 11)")
common = {"2", "5", "10", "11"}
sets = [set(c) for c in A.codes]
pairs = Counter(p for s in sets for p in combinations(sorted(s - common), 2))
freq = Counter(c for s in sets for c in s)
for (a, b), n in pairs.most_common(8):
    lift = n * len(A) / (freq[a] * freq[b])
    print(f"  {a:>3} + {b:<3} {n:3}x  lift {lift:4.1f}   {CRIT[a]['description_en'][:28]} | {CRIT[b]['description_en'][:28]}")
print("Lift > 1: the two codes appear together more often than by chance.")

# ---------- 6. criteria group profile per translator ---------------------
section("6. Criteria group profile per translator (share of applied codes, %)")
long = A[["translator", "codes"]].explode("codes").dropna().reset_index(drop=True)
long["group"] = long.codes.map(lambda c: CRIT[c]["group"])
print(pd.crosstab(long.translator, long.group, normalize="index").mul(100).round(0))

# ---------- 7. what drives the number of entries -------------------------
section("7. What drives the number of simplified entries? (Spearman correlation)")
print(A[["n_entries", "words_orig", "wordlen_orig", "lix_orig", "n_codes"]].corr(method="spearman")["n_entries"].drop("n_entries").round(2))

# ---------- 8. flagged vs unflagged --------------------------------------
section("8. Alignments with review flags vs without")
print("(only review flags; the [v1.3]/[v1.4] correction notes are left out)")
print(A.groupby("flagged")[["words_orig", "n_entries", "growth", "vocab_overlap"]].mean())
print("\nFlag rate per document (top 5):")
print(A.groupby("document_id").flagged.mean().sort_values(ascending=False).head(5).map("{:.0%}".format))
