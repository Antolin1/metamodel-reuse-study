#%%
import pandas as pd
import numpy as np
from collections import defaultdict

# %%
# Exploratory
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
df["original_name"] = df["original_path"].apply(lambda x: x.split("#")[-1])
df.head()

#%%

# some basic checks

assert (df["affected_elements"] >= 0).all(), "affected_elements should be non-negative"
assert (df["affected_annotations"] >= 0).all(), "affected_annotations should be non-negative"

assert (df["original_size"] >= 5).all(), "original_size should be greater than the minimum size"
assert (df["duplicate_size"] >= 5).all(), "duplicate_size should be greater than the minimum size"

assert (df["original_size_no_annotations"] >= 0).all(), "original_size without counting annotations should be non-negative"
assert (df["duplicate_size_no_annotations"] >= 0).all(), "duplicate_size without counting annotations should be non-negative"

assert (df["affected_elements"] >= df["affected_annotations"]).all(), "affected_elements should be greater than or equal to affected_annotations"

assert (df["original_size"] >= df["original_size_no_annotations"]).all(), "original_size should not be less than original_size_no_annotations"
assert (df["duplicate_size"] >= df["duplicate_size_no_annotations"]).all(), "duplicate_size should not be less than duplicate_size_no_annotations"

#%%

# the relative change metric ignoring annotations
df["relative_change"] = (df["affected_elements"] - df["affected_annotations"]) / df["original_size_no_annotations"]

#%%
df["relative_change"].isna().sum(), "NaN values in relative_change"

# %%
df_typeA = df[df["relative_change"] == 0].copy() # includes comparisons with only annotation changes
df_typesBC = df[df["relative_change"] > 0].copy()

print(f"Type A clones: {len(df_typeA)}")
print(f"Type B/C clones: {len(df_typesBC)}")

# %%
df_typesBC["affected_elements"].describe()

#%%
df_typesBC["relative_change"].describe()

#%%
# strange maximum value at 1.0000, it appears that in some metamodels all original elements were
# modified (plus some others were added), so the relative change is 1.0

df[df["relative_change"] >= 1].head(20)

# %%
df_typesBC["abs_size_change"] = abs(df_typesBC["original_size"] - df_typesBC["duplicate_size"])
df_typesBC["abs_size_change"].describe()

#%%
outliers = df_typesBC[df_typesBC["relative_change"] > 1].copy()
print(f"Len of type B/C clones: {len(df_typesBC)}")
print(f"Outliers (relative_change > 1): {len(outliers)}")

#%%
# remove outliers
df_typesBC = df_typesBC[df_typesBC["relative_change"] <= 1].copy()

#%%
# violin plot of relative_change
import seaborn as sns
import matplotlib.pyplot as plt

plt.figure(figsize=(10, 5))
sns.violinplot(x=df_typesBC["relative_change"],
                color='lightblue')
plt.xticks(np.arange(0, 1.1, 0.1))
plt.xlabel("Relative Change")
plt.grid(True)
plt.show()


#%%
# histogram of relative_change
num_bins = 10
df_typesBC["relative_change"].hist(bins=num_bins, figsize=(5, 5))

#%%
# get a sample for each bin and save it in a different csv file
df_typesBC["bin"] = pd.cut(df_typesBC["relative_change"], bins=num_bins)

#%%
# show bin sizes
bin_sizes = df_typesBC["bin"].value_counts().sort_index()
print(bin_sizes)

#%%
n_samples = 20
np.random.seed(42)
sampled_df = df_typesBC.groupby("bin").apply(
        lambda x: x.sample(n=min(n_samples, len(x)))).reset_index(drop=True)

# save each bin sample to a separate csv file
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

    for feature, count in sorted_features[:10]:
        print(f"{feature}: {count/len(group):.2f} ({count})")

    print("\n\n")

# %%
# study first bins
changes_threshold = 0.2
df_firstbins = df_typesBC[df_typesBC["relative_change"] < changes_threshold].copy()

#%%
# bin again
df_firstbins["relative_change"].hist(bins=8, figsize=(5, 5))

# %%
df_firstbins["bin2"] = pd.cut(df_firstbins["relative_change"], bins=8)

# sample again
sampled_df = df_firstbins.groupby("bin2").apply(
        lambda x: x.sample(n=min(n_samples, len(x)))).reset_index(drop=True)

# save each bin sample to a separate csv file
for bin_label, group in sampled_df.groupby("bin2"):
    bin_label = str(bin_label).replace("(", "").replace("]", "").replace(",", "-").replace(" ", "")
    csv_name = f"sample_bin2_relative_change_{bin_label}.csv"
    print(f'doAnalysis("{csv_name}", "all");')
    group.to_csv(csv_name, index=False)

#%%

# study of resource attachments issue
attachment_features = ["ADD-ResourceAttachment.EPackage",
                       "DELETE-ResourceAttachment.EPackage"]

movement_features = ["MOVE-EClass", "MOVE-EDataType", "MOVE-EEnum", "MOVE-EPackage"]

def has_root_change(row):
    has_attachment = any(row[feature] > 0 for feature in attachment_features)
    has_movement = any(row[feature] > 0 for feature in movement_features)
    return has_attachment and has_movement

df_typesBC["has_root_change"] = df_typesBC.apply(has_root_change, axis=1)


print(f"Total clones with root changes: {df_typesBC['has_root_change'].sum()} / {len(df_typesBC)}")
for bin_label, group in df_typesBC.groupby("bin"):
    bin_label = str(bin_label).replace("(", "").replace("]", "").replace(",", "-").replace(" ", "")
    root_changes_count = group["has_root_change"].sum()
    total_count = len(group)
    print(f"Bin {bin_label}: {root_changes_count}/{total_count} ({root_changes_count/total_count:.2f})")

# %%
