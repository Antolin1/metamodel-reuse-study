#%%
import pandas as pd
import numpy as np
from collections import defaultdict

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
num_bins = 10

# get a sample for each bin and save it in a different csv file
df_typesBC["bin"] = pd.cut(df_typesBC["relative_change"], bins=num_bins)


#%%

n_samples = 10
np.random.seed(42)
sampled_df = df_typesBC.groupby("bin").apply(
        lambda x: x.sample(n=min(n_samples, len(x)))).reset_index(drop=True)

# seave each bin sample to a separate csv file
for bin_label, group in sampled_df.groupby("bin"):
    bin_label = str(bin_label).replace("(", "").replace("]", "").replace(",", "-").replace(" ", "")
    csv_name = f"sampled_relative_change_{bin_label}.csv"
    print(f'doAnalysis("{csv_name}", "all");')
    group.to_csv(csv_name, index=False)

# %%
# sample outliers as well
outliers_sampled = outliers.sample(n=min(n_samples, len(outliers)))
outliers_csv_name = "sampled_relative_change_outliers.csv"
print(f'doAnalysis("{outliers_csv_name}", "all");')
outliers_sampled.to_csv(outliers_csv_name, index=False)

# %%
df_aux = df_typesBC.copy()

# group add or delete features in the same column
grouping = defaultdict(list)
for c in df_aux.columns:
    if c.startswith('ADD-'):
        grouping[c.split('-')[1]].append(c)
    elif c.startswith('DELETE-'):
        grouping[c.split('-')[1]].append(c)

for c, cs in grouping.items():
    # or of the columns in cs and store in c
    df_aux[f'ADD-OR-DELETE-{c}'] = data_inter[cs].any(axis=1)

    # remove data in cs
    df_aux.drop(columns=cs, inplace=True)

features = [c for c in df_aux.columns
            if ('ADD' in c or 'CHANGE' in c or 'DELETE' in c or 'MOVE' in c)]


for bin_label, group in df_aux.groupby("bin"):
    bin_label = str(bin_label).replace("(", "").replace("]", "").replace(",", "-").replace(" ", "")

    feature_counts = defaultdict(int)

    for idx, row in group.iterrows():
        for feature in features:
            if row[feature] > 0:
                feature_counts[feature] += 1

    # sort features by count and print the top ones
    sorted_features = sorted(feature_counts.items(), key=lambda x: x[1], reverse=True)
    print(f"Features in bin {bin_label}:")

    for feature, count in sorted_features[:20]:
        print(f"{feature}: {count/len(group):.2f} ({count})")

    print("\n\n")

# %%
