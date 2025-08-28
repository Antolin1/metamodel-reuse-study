#%%
import os

import pandas as pd
import numpy as np
from collections import defaultdict

import matplotlib.pyplot as plt
import seaborn as sns


# %%
data_inter = pd.read_csv("cluster_stars_with_concrete_features-inter.csv")
data_intra = pd.read_csv("cluster_stars_with_concrete_features-intra.csv")

data_inter["scenario"] = "inter"
data_intra["scenario"] = "intra"

for c in data_inter.columns:
    if c not in data_intra.columns:
        data_intra[c] = 0

for c in data_intra.columns:
    if c not in data_inter.columns:
        data_inter[c] = 0

df = pd.concat([data_inter, data_intra], ignore_index=True).copy()
df.shape

#%%
print("Total comparisons:", len(df))

#%%
df = df[df["affected_elements"] > 0].copy()
print("Comparisons with changes:", len(df))

# %%
df_nsuri_changes = df[df["CHANGE-EPackage.nsURI"] > 0].copy()
print("Comparisons with affected nsURI:", len(df_nsuri_changes))

# %%
import re

pattern = "nsURI\s*=\s*['\"](.*?)['\"]"
def get_nsuris_from_metamodel(metamodel_path):
    metamodels_folder = "../metamodels"
    full_path = os.path.join(metamodels_folder, metamodel_path)
    nsuris = []
    if os.path.exists(full_path):
        with open(full_path, "r") as f:
            for line in f:
                line = line.strip()
                if 'nsURI' in line:
                    uri = re.findall(pattern, line)
                    if uri:
                        nsuris.append(uri[0].strip())
    return list(nsuris)

def get_nsuris(row):
    original_nsuris = get_nsuris_from_metamodel(row["original_path"])
    duplicate_nsuris = get_nsuris_from_metamodel(row["duplicate_path"])
    return original_nsuris, duplicate_nsuris

df_nsuri_changes[["original_nsuris", "duplicate_nsuris"]] = df_nsuri_changes.apply(get_nsuris, axis=1, result_type="expand")

df_nsuri_changes.to_csv("samples/nsuri_changes.csv", index=False)

# %%
df_nsuri_changes["original_nsuri_counts"] = df_nsuri_changes["original_nsuris"].apply(len)
df_nsuri_changes["duplicate_nsuri_counts"] = df_nsuri_changes["duplicate_nsuris"].apply(len)

# %%
print("No nsuri in original or duplicate:", len(df_nsuri_changes[(df_nsuri_changes["original_nsuri_counts"] == 0) | (df_nsuri_changes["duplicate_nsuri_counts"] == 0)]),"/", len(df_nsuri_changes))

# %%
df_nsuri_changes[["original_nsuri_counts", "duplicate_nsuri_counts"]].value_counts()

#%%

# leave only those with one nsuri in both
df_nsuri_changes_one_nsuri = df_nsuri_changes[(df_nsuri_changes["original_nsuri_counts"] == 1) & (df_nsuri_changes["duplicate_nsuri_counts"] == 1)].copy()
print("Comparisons with one nsuri in both:", len(df_nsuri_changes_one_nsuri), "/", len(df_nsuri_changes))

# %%
df_nsuri_changes_one_nsuri["original_nsuri"] = df_nsuri_changes_one_nsuri["original_nsuris"].apply(lambda x: x[0] if x else None)
df_nsuri_changes_one_nsuri["duplicate_nsuri"] = df_nsuri_changes_one_nsuri["duplicate_nsuris"].apply(lambda x: x[0] if x else None)
# %%
# levenshtein distance between original_nsuri and duplicate_nsuri
import Levenshtein
df_nsuri_changes_one_nsuri["nsuri_levenshtein"] = df_nsuri_changes_one_nsuri.apply(lambda row: Levenshtein.distance(row["original_nsuri"], row["duplicate_nsuri"]), axis=1)
df_nsuri_changes_one_nsuri["nsuri_levenshtein_ratio"] = df_nsuri_changes_one_nsuri.apply(lambda row: Levenshtein.ratio(row["original_nsuri"], row["duplicate_nsuri"]), axis=1)
df_nsuri_changes_one_nsuri["nsuri_levenshtein_jaro"] = df_nsuri_changes_one_nsuri.apply(lambda row: Levenshtein.jaro(row["original_nsuri"], row["duplicate_nsuri"]), axis=1)
df_nsuri_changes_one_nsuri["nsuri_levenshtein_jaro_winkler"] = df_nsuri_changes_one_nsuri.apply(lambda row: Levenshtein.jaro_winkler(row["original_nsuri"], row["duplicate_nsuri"]), axis=1)

df_nsuri_changes_one_nsuri[["original_nsuri", "duplicate_nsuri", "nsuri_levenshtein", "nsuri_levenshtein_ratio", "nsuri_levenshtein_jaro", "nsuri_levenshtein_jaro_winkler"]]

# %%
df_nsuri_changes_one_nsuri["nsuri_levenshtein"].value_counts().head(30)
# %%
df_nsuri_changes_one_nsuri.sort_values(by=["nsuri_levenshtein", "scenario"])[["scenario", "original_nsuri", "duplicate_nsuri", "nsuri_levenshtein", "nsuri_levenshtein_ratio", "nsuri_levenshtein_jaro", "nsuri_levenshtein_jaro_winkler"]].to_csv("samples/nsuri_changes_with_similarities.csv", index=False)

# %%
df_nsuri_changes_one_nsuri["nsuri_levenshtein_jaro_winkler"].describe()
