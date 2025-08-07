#%%
import pandas as pd
import numpy as np

# %%
# Exploratory
data_inter = pd.read_csv("cluster_stars_with_concrete_features-inter.csv")
data_intra = pd.read_csv("cluster_stars_with_concrete_features-intra.csv")

for c in data_inter.columns:
    if c not in data_intra.columns:
        data_intra[c] = 0

for c in data_intra.columns:
    if c not in data_inter.columns:
        data_inter[c] = 0

df = pd.concat([data_inter, data_intra], ignore_index=True)

#%%
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
outliers[["original_name", "original_size", "duplicate_size", "affected_elements",
          "relative_change"]].sort_values("relative_change", ascending=False).head(40)

#%%
# remove outliers
df_typesBC = df_typesBC[df_typesBC["relative_change"] <= 1].copy()

#%%
# histogram of relative_change
df_typesBC["relative_change"].hist(bins=10, figsize=(5, 5))

#%%

# get a sample for each bin and save it in a different csv file
df_typesBC["bin"] = pd.cut(df_typesBC["relative_change"], bins=10)
sampled_df = df_typesBC.groupby("bin").apply(lambda x: x.sample(n=min(n_samples, len(x)))).reset_index(drop=True)

n_samples = 5
np.random.seed(42)

# seave each bin sample to a separate csv file
for bin_label, group in sampled_df.groupby("bin"):
    bin_label = str(bin_label).replace("(", "").replace("]", "").replace(",", "-")
    bin_label = bin_label.replace(" ", "")
    group.to_csv(f"sampled_relative_change_{bin_label}.csv", index=False)
# %%
# sample outliers as well
outliers_sampled = outliers.sample(n=min(n_samples, len(outliers)))
outliers_sampled.to_csv("sampled_relative_change_outliers.csv", index=False)
