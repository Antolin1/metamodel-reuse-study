#%%
import os

import pandas as pd
import numpy as np
from collections import defaultdict

import matplotlib.pyplot as plt
import seaborn as sns


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

assert (df["affected_elements"] - df["affected_annotations"] - df["package_content_movements"] >= 0).all(), "affected_elements minus affected_annotations and package_content_movements should be non-negative"

#%%
df_typeA = df[(df["affected_elements"] - df["affected_annotations"]) == 0].copy()
df_typesBC = df[(df["affected_elements"] - df["affected_annotations"]) > 0].copy()

print(f"Type A clones: {len(df_typeA)}")
print(f"Type B/C clones: {len(df_typesBC)}")

#%%
# the relative change metric ignoring annotations
df_typesBC["relative_change"] = ((df_typesBC["affected_elements"] - df_typesBC["affected_annotations"])
                                 / df_typesBC["original_size_no_annotations"])


#%%
# study of package changes with element movements issue
pkg_content_move_features = ["MOVE-EClass", "MOVE-EDataType", "MOVE-EEnum", "MOVE-EPackage"]

def has_pkg_content_moves(row):
    return any(row[feature] > 0 for feature in pkg_content_move_features)

df_typesBC["has_pkg_content_moves"] = df_typesBC.apply(has_pkg_content_moves, axis=1)

print(f"Clones with pkg content moves: {df_typesBC['has_pkg_content_moves'].sum()} / {len(df_typesBC)}")

#%%
df_pkg_content_moves = df_typesBC[df_typesBC["has_pkg_content_moves"]].copy()

assert (df_typesBC["package_content_movements"] > 0).sum() == len(df_pkg_content_moves), "pkg_content_moves should match the filtered DataFrame"

#%%
features = [c for c in df_pkg_content_moves.columns if
            c.startswith('ADD-') or
            c.startswith('DELETE-') or
            c.startswith('CHANGE-') or
            c.startswith('MOVE-')]

len(features)

#%%
features_ratio = {f : df_pkg_content_moves[f].sum() / len(df_pkg_content_moves) for f in features}

# sort and print the top features
sorted_features = sorted(features_ratio.items(), key=lambda x: x[1], reverse=True)
print("Top features with their ratios:")
for feature, ratio in sorted_features[:10]:
    print(f"{feature}: {ratio:.2f}")

#%%
print("total:", len(df_pkg_content_moves))

print("Add and remove resource attachment package:",
      ((df_pkg_content_moves["ADD-ResourceAttachment.EPackage"] > 0) &
       (df_pkg_content_moves["DELETE-ResourceAttachment.EPackage"] > 0)).sum())

print("Add or remove resource attachment package:",
      ((df_pkg_content_moves["ADD-ResourceAttachment.EPackage"] > 0) |
       (df_pkg_content_moves["DELETE-ResourceAttachment.EPackage"] > 0)).sum())

print("only add resource attachment package:",
      ((df_pkg_content_moves["ADD-ResourceAttachment.EPackage"] > 0) &
       (df_pkg_content_moves["DELETE-ResourceAttachment.EPackage"] == 0)).sum())

print("only delete resource attachment package:",
      ((df_pkg_content_moves["ADD-ResourceAttachment.EPackage"] == 0) &
       (df_pkg_content_moves["DELETE-ResourceAttachment.EPackage"] > 0)).sum())

print("add XOR delete resource attachment package:",
      (df_pkg_content_moves["ADD-ResourceAttachment.EPackage"] !=
       df_pkg_content_moves["DELETE-ResourceAttachment.EPackage"]).sum())

#%%
def save_dataframe(df, filename):
    # check if samples directory exists

    if not os.path.exists("samples"):
        os.makedirs("samples")

    output_path = os.path.join("samples", filename)
    df.to_csv(output_path, index=False)
    print(f'doAnalysis("{output_path}", "all");')


save_dataframe(df_pkg_content_moves[df_pkg_content_moves["ADD-ResourceAttachment.EPackage"] !=
       df_pkg_content_moves["DELETE-ResourceAttachment.EPackage"]], "sample_pkg_content_xor_add_delete_resourceattachment.csv")

#%%
# sample those with add and remove resource attachment package
df_add_remove_resource_attachment = df_pkg_content_moves[
        (df_pkg_content_moves["ADD-ResourceAttachment.EPackage"] > 0) &
        (df_pkg_content_moves["DELETE-ResourceAttachment.EPackage"] > 0)].copy()

n_samples = 40
np.random.seed(42)
df_sample = df_add_remove_resource_attachment.sample(n=min(n_samples, len(df_add_remove_resource_attachment)))

save_dataframe(df_sample, "sample_pkg_content_add_remove_resourceattachment.csv")

#%%
resource_attachment_features = ["ADD-ResourceAttachment.EPackage", "DELETE-ResourceAttachment.EPackage"]
def has_resource_attachment(row):
    return any(row[feature] > 0 for feature in resource_attachment_features)

df_pkg_content_moves["has_resource_attachment"] = df_pkg_content_moves.apply(has_resource_attachment, axis=1)

df_no_resource_attachment = df_pkg_content_moves[~df_pkg_content_moves["has_resource_attachment"]].copy()
print(f"Pkg moves without resource attachment: {len(df_no_resource_attachment)} / {len(df_pkg_content_moves)}")

#%%
features_ratio = {f : df_no_resource_attachment[f].sum() / len(df_no_resource_attachment) for f in features}

# sort and print the top features
sorted_features = sorted(features_ratio.items(), key=lambda x: x[1], reverse=True)
print("Top features with their ratios:")
for feature, ratio in sorted_features[:10]:
    print(f"{feature}: {ratio:.2f}")

#%%
df_no_resource_attachment["add_and_delete_package"] = (
        (df_no_resource_attachment["ADD-EPackage"] > 0) &
        (df_no_resource_attachment["DELETE-EPackage"] > 0))

add_and_delete = df_no_resource_attachment["add_and_delete_package"].sum()

print(f"rows with delete and add package changes: {add_and_delete} ({add_and_delete / len(df_no_resource_attachment)}")

save_dataframe(df_no_resource_attachment[df_no_resource_attachment["add_and_delete_package"]], "sample_pkg_content_moves_add_and_delete_package.csv")

#%%

# Summary: for those comparisons with either:
# - add and delete resource attachment packages
# - add and delete internal packages
# do not consider package movement changes when calculating the relative change metric

# the "does" is there to avoid feature filtering issues
df_typesBC["does_add_and_remove_attachment_package"] = (
        (df_typesBC["has_pkg_content_moves"]) &
        (df_typesBC["ADD-ResourceAttachment.EPackage"] > 0) &
        (df_typesBC["DELETE-ResourceAttachment.EPackage"] > 0))

df_typesBC["does_add_and_remove_internal_package"] = (
        (df_typesBC["has_pkg_content_moves"]) &
        (df_typesBC["ADD-EPackage"] > 0) &
        (df_typesBC["DELETE-EPackage"] > 0))

print("Adds and removes resource attachment package:",
      df_typesBC["does_add_and_remove_attachment_package"].sum())
print("Adds and removes internal package:",
        df_typesBC["does_add_and_remove_internal_package"].sum())

either_of_both = (df_typesBC["does_add_and_remove_attachment_package"] |
                           df_typesBC["does_add_and_remove_internal_package"])
print("Either of both: ", either_of_both.sum())

#%%
def update_relative_change(row):
    if row["does_add_and_remove_attachment_package"] or row["does_add_and_remove_internal_package"]:
        return (row["affected_elements"] - row["affected_annotations"] - row["package_content_movements"]) / row["original_size_no_annotations"]

    # else: leave it as is
    return row["relative_change"]

df_typesBC["old_relative_change"] = df_typesBC["relative_change"]
df_typesBC["relative_change"] = df_typesBC.apply(update_relative_change, axis=1)

#%%
assert df_typesBC[~either_of_both]["relative_change"].equals(df_typesBC[~either_of_both]["old_relative_change"]), "Relative change should not change for those without either of both conditions"

assert (df_typesBC[either_of_both]["relative_change"] < df_typesBC[either_of_both]["old_relative_change"]).all(), "Relative change should decrease for those with either of both conditions"

#%%
# boxplot of new relative change and old relative change 
plt.figure(figsize=(10, 5))
sns.boxplot(data=df_typesBC[either_of_both][["relative_change", "old_relative_change"]],
            palette=["lightgreen", "lightcoral"])
plt.xticks([0, 1], ["Relative Change", "Old Relative Change"])
plt.xlabel("Metric")
plt.ylabel("Value")
plt.title("Relative Change Metrics of elements with movements issue")
plt.grid(True)
plt.show()


#%%
df_typesBC["original_size_no_annotations"].describe()

#%%
[(q, df_typesBC["duplicate_size_no_annotations"].quantile(q))
 for q in [0.01, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.45, 0.5, 0.55]]

#%%

# saturating factor for the relative change metric
k = df_typesBC["original_size_no_annotations"].quantile(0.20)
print(f"Saturating factor k: {k}")

def saturating_factor(size):
    return size / (size + k)

#%%
# study the saturating factor for the first elements (except the really big ones)

cutoff = df_typesBC["original_size_no_annotations"].quantile(0.7)
df_aux = df_typesBC[df_typesBC["original_size_no_annotations"] <= cutoff].copy()

df_aux["original_size_no_annotations"].hist(bins=20, figsize=(10, 5))

#%%

# plot the saturating factor for each original size value
plt.figure(figsize=(10, 5))
sns.lineplot(x=df_aux["original_size_no_annotations"],
             y=df_aux["original_size_no_annotations"].apply(saturating_factor),
             color='blue')

plt.xlabel("Original Size (without annotations)")
plt.ylabel("Saturating Factor")
plt.title("Saturating Factor vs Original Size (without annotations)")
plt.grid(True)
plt.show()


#%%
df_typesBC["saturating_factor"] = df_typesBC["original_size_no_annotations"].apply(saturating_factor)
df_typesBC["saturating_factor"].describe()

#%%
df_typesBC["relative_change"].describe()
#%%

# apply the saturating factor to the relative change metric
df_typesBC["relative_change_with_saturation"] = df_typesBC["relative_change"] * df_typesBC["saturating_factor"]

#%%
df_typesBC["relative_change_with_saturation"].describe()

assert (df_typesBC["relative_change_with_saturation"] >= 0).all(), "Relative change with saturation should be non-negative"

assert (df_typesBC["relative_change_with_saturation"] < df_typesBC["relative_change"]).all(), "Relative change with saturation should be less than the original relative change"

#%%
df_aux = df_typesBC.copy()

plt.figure(figsize=(10, 5))

sns.scatterplot(x=df_aux["relative_change"],
                y=df_aux["relative_change_with_saturation"])
plt.xlabel("Relative Change (without saturation)")
plt.ylabel("Relative Change (with saturation)")
plt.title("Relative Change vs Relative Change with Saturation")
plt.grid(True)
plt.xlim(0, 1)
plt.ylim(0, 1)
plt.axline((0, 0), slope=1, color='red', linestyle='--')
plt.show()

#%%
# plot the difference between the relative change metrics against the original size
plt.figure(figsize=(10, 5))
sns.scatterplot(x=df_aux["original_size_no_annotations"],
                y=df_aux["relative_change"] - df_aux["relative_change_with_saturation"],
                color='blue')
plt.xlabel("Original Size (without annotations)")
plt.ylabel("Relative Change Difference")
plt.xscale('log')
plt.title("Relative Change Difference vs Original Size (without annotations)")
plt.grid(True)
plt.axhline(0, color='red', linestyle='--')
plt.show()

# %%
df_typesBC["abs_size_change"] = abs(df_typesBC["original_size"] - df_typesBC["duplicate_size"])
df_typesBC["abs_size_change"].describe()

#%%
outliers = df_typesBC[df_typesBC["relative_change_with_saturation"] > 1].copy()
print(f"Len of type B/C clones: {len(df_typesBC)}")
print(f"Outliers (relative_change > 1): {len(outliers)}")

#%%
# remove outliers
df_typesBC = df_typesBC[df_typesBC["relative_change_with_saturation"] <= 1].copy()

#%%
# violin plot of relative_change
import seaborn as sns
import matplotlib.pyplot as plt

plt.figure(figsize=(10, 5))
sns.violinplot(x=df_typesBC["relative_change_with_saturation"],
               color='lightblue')
plt.xticks(np.arange(0, 1.1, 0.1))
plt.xlabel("Relative Change")
plt.grid(True)
plt.show()

#%%
df_typesBC["relative_change_with_saturation"].describe()

#%%
# histogram of relative_change
num_bins = 10
df_typesBC["relative_change_with_saturation"].hist(bins=num_bins, figsize=(5, 5))

#%%
# get a sample for each bin and save it in a different csv file
df_typesBC["bin"] = pd.cut(df_typesBC["relative_change_with_saturation"], bins=num_bins)

#%%
# show bin sizes
bin_sizes = df_typesBC["bin"].value_counts().sort_index()
print(bin_sizes)

#%%
n_samples = 20
np.random.seed(42)
sampled_df = df_typesBC.groupby("bin").apply(
        lambda x: x.sample(n=min(n_samples, len(x)))).reset_index(drop=True)

sample_files = []
sample_number = []
relative_change = []

# save each bin sample to a separate csv file
for bin_label, group in sampled_df.groupby("bin"):
    bin_label = (str(bin_label)
                 .replace("(", "")
                 .replace("]", "")
                 .replace(",", "-")
                 .replace(" ", "")
                 .strip())

    csv_name = f"sampled_relative_change_{bin_label}.csv"
    save_dataframe(group, csv_name)

    for index, (ids, row) in enumerate(group.iterrows()):
        sample_files.append(csv_name)
        sample_number.append(index)
        relative_change.append(row["relative_change_with_saturation"])

# sample outliers as well
outliers_sampled = outliers.sample(n=min(n_samples, len(outliers)))
outliers_csv_name = "sampled_relative_change_outliers.csv"
save_dataframe(outliers_sampled, outliers_csv_name)

for index, (ids, row) in enumerate(outliers_sampled.iterrows()):
        sample_files.append(outliers_csv_name)
        sample_number.append(index)
        relative_change.append(row["relative_change_with_saturation"])

#%%
assert len(sample_files) == len(sample_number) == len(relative_change), "Sample files, numbers and relative changes should have the same length"

#%%
# create a DataFrame with the samples
labelling_df = pd.DataFrame({
    "sample_file": sample_files,
    "sample_number": sample_number,
    "relative_change": relative_change,
    "label" : ["" for _ in sample_files],
    "notes" : ["" for _ in sample_files]
})
labelling_df.to_csv("samples/template_for_labelling_BC_clones.csv", index=False)

#%%
assert len(df_typeA) + len(df_typesBC) + len(outliers) == len(df), "Type A and Type B/C clones should sum up to the original DataFrame length"

# %%
relevant_columns = ["cluster", "original", "original_path", "duplicate", "duplicate_path",
       "affected_elements", "original_size", "duplicate_size",
       "affected_annotations", "original_size_no_annotations",
       "duplicate_size_no_annotations", "package_content_movements", "relative_change_with_saturation", "scenario"]

#%%
df_typeA["relative_change_with_saturation"] = 0.0
df_typeA[relevant_columns].to_csv("typeA_clones.csv", index=False)

# %%
df_typesBC = pd.concat([df_typesBC, outliers])
print(df_typesBC.shape)

#%%
df_typesBC[relevant_columns].to_csv("typeBC_clones.csv", index=False)
