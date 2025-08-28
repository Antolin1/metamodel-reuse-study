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
df_annotation_changes = df[df["affected_annotations"] > 0]
print("Comparisons with affected annotations:", len(df_annotation_changes))

# by scenario
print(df_annotation_changes["scenario"].value_counts())
#%%

df_annotation_changes.to_csv("samples/comparisons_with_annotation_changes.csv", index=False)

# %%
df_only_annotation_changes = df[df["affected_elements"] == df["affected_annotations"]]
print("Comparisons with only annotation changes:", len(df_only_annotation_changes))

print(df_only_annotation_changes["scenario"].value_counts())

df_only_annotation_changes.to_csv("samples/comparisons_with_only_annotation_changes.csv", index=False)
