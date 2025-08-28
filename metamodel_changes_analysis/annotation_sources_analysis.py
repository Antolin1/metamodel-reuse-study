#%%
from collections import defaultdict
import pandas as pd

#%%
filename = "samples/comparisons_with_annotation_changes.csv.analysis.txt"

source_lines = open(filename).readlines()
sources_by_comparison = [line.strip().split(",") for line in source_lines]

frequencies = defaultdict(int)
for sources in sources_by_comparison:
    for s in sources:
        frequencies[s.replace("\"", "")] += 1

# %%
# sorted by frequency
sorted_frequencies = sorted(frequencies.items(), key=lambda x: x[1], reverse=True)
for s, f in sorted_frequencies:
    print(f"{s}: {f}")

#%%
# create a dataframe with key and value columns
df = pd.DataFrame(sorted_frequencies, columns=["source", "frequency"])
print("number of unique sources:", len(df))
df.head(30)

#%%
for s in df["source"].unique():
   print(s)

# %%
# counts without repetition (e.g. two OCL sources appearing in the same comparison)

def contains_fragment(sources, fragment):
    for s in sources:
        if fragment in s:
            return True
    return False

fragments = ["OCL", "gmf", "capella", "opengis", "GenModel"]
for fragment in fragments:
    count = sum(1 for sources in sources_by_comparison
                if contains_fragment(sources, fragment))
    print(f"Contains '{fragment}': {count}")

# %%
