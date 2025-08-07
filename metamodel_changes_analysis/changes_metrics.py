#%%
import pandas as pd

# %%
# Exploratory
data_inter = pd.read_csv("cluster_stars_with_concrete_features-inter.csv")

print(len(data_inter))
#%%
data_inter["inter"].value_counts()

#%%
data_intra = pd.read_csv("cluster_stars_with_concrete_features-intra.csv")

print(len(data_intra))

#%%

for c in data_inter.columns:
    if c not in data_intra.columns:
        data_intra[c] = False

for c in data_intra.columns:
    if c not in data_inter.columns:
        data_inter[c] = False


#%%
df = None
df["original_name"] = df["original_path"].apply(lambda x: x.split("#")[-1])
df.head()

# %%
df_typeA = df[df["affected_elements"] == 0]
df_typesBC = df[df["affected_elements"] > 0].copy()

print(f"Type A clones: {len(df_typeA)}")
print(f"Type B/C clones: {len(df_typesBC)}")

# %%
df_typesBC["affected_elements"].describe()

# %%
df_typesBC["abs_size_change"] = abs(df_typesBC["original_size"] - df_typesBC["duplicate_size"])
df_typesBC["abs_size_change"].describe()

#%%
df_typesBC["relative_change"] = df_typesBC["affected_elements"] / df_typesBC["original_size"]

df_typesBC["relative_change"].describe()

# %%
outliers = df_typesBC[df_typesBC["relative_change"] > 1].copy()
print(f"Len of type B/C clones: {len(df_typesBC)}")
print(f"Outliers (relative_change > 1): {len(outliers)}")

#%%
outliers[["original_name", "original_size", "duplicate_size", "affected_elements", "relative_change"]].sort_values("relative_change", ascending=False).head(40)

#%%
# remove outliers
df_typesBC = df_typesBC[df_typesBC["relative_change"] <= 1].copy()

#%%
# histogram of relative_change
df_typesBC["relative_change"].hist(bins=50, figsize=(5, 5))

#%%
threshold = 0.2
df_typeB = df_typesBC[df_typesBC["relative_change"] <= threshold].copy()
df_typeC = df_typesBC[df_typesBC["relative_change"] > threshold].copy()

print(f"Type B clones: {len(df_typeB)}")
print(f"Type C clones: {len(df_typeC)}")
