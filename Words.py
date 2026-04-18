# pip install nltk wordfreq
import nltk
nltk.download("wordnet")
nltk.download("omw-1.4")
import nltk
from nltk.corpus import wordnet as wn
from wordfreq import zipf_frequency
import random

nltk.download("wordnet")

# ----------------------------
# 1. Extract REAL nouns only
# ----------------------------
nouns = set()

for syn in wn.all_synsets(pos="n"):  # nouns only
    for lemma in syn.lemma_names():
        w = lemma.lower()

        # clean filters
        if "_" in w:          # removes multi-word combos
            continue
        if not w.isalpha():   # remove weird tokens
            continue
        if len(w) < 3:
            continue

        nouns.add(w)

nouns = list(nouns)

# ----------------------------
# 2. Score by word frequency
# ----------------------------
def score(word):
    return zipf_frequency(word, "en")

# ----------------------------
# 3. Split into difficulty tiers
# ----------------------------

easy = []
medium = []
hard = []

for w in nouns:
    s = score(w)

    if s >= 4.0:
        easy.append(w)
    elif s >= 3.0:
        medium.append(w)
    else:
        hard.append(w)

# ----------------------------
# 4. Balance sizes (5000 total)
# ----------------------------

random.shuffle(easy)
random.shuffle(medium)
random.shuffle(hard)

easy = easy[:1700]
medium = medium[:1700]
hard = hard[:1600]

all_words = easy + medium + hard

# ----------------------------
# 5. Save file
# ----------------------------

with open("werewords_nouns_clean_5000.txt", "w") as f:
    f.write("[EASY]\n")
    f.write("\n".join(easy))

    f.write("\n\n[MEDIUM]\n")
    f.write("\n".join(medium))

    f.write("\n\n[HARD]\n")
    f.write("\n".join(hard))

print("Saved: werewords_nouns_clean_5000.txt")
print("Total words:", len(all_words))


