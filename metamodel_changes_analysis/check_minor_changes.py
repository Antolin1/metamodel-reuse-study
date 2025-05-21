#!/usr/bin/env python
# coding: utf-8

#%%
import pandas as pd

df = pd.read_csv("modified_metamodels.csv")
df.head()

# %%

print(f"Number of scenarios: {len(df)}")
print(df["scenario"].value_counts())

# %%
df.columns

# %% study metamodels by number of changed features

# focus on inter-duplication changes
df = df[df["scenario"] == "inter"]

print(len(df))

# %%
features = [c for c in df.columns if ('ADD' in c or 'CHANGE' in c or 'DELETE' in c or 'MOVE' in c)]

df["sum_changed_features"] = df[features].sum(axis=1)

df["sum_changed_features"].describe()

# %%
df.groupby("sum_changed_features").size()

# %%
num_changes = 1
few_changes = df[df["sum_changed_features"] <= num_changes]

# check which feature is greater than 1 for each case

few_changes[features].sum(axis=0).sort_values(ascending=False).head(30)

# %%
few_changes[features].sum(axis=0).sort_values(ascending=False).head(30) / len(df)
# %%
df[features].sum(axis=0).sort_values(ascending=False).head(30) / len(df)

# %%

# metamodels with super types

df_st = df[df["CHANGE-EClass.eSuperTypes"] == 1].copy()
len(df_st)

#%%
len(df_st["original_path"].unique())
# %%
len(df_st["duplicate_path"].unique())
# %%
df_st["original_mm_name"] = df_st["original_path"].apply(lambda x: x.split("#")[-1])

df_st["original_mm_name"].value_counts().head(40)

# %%
