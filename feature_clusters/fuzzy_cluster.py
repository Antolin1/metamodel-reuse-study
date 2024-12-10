# -*- coding: utf-8 -*-
"""
Fuzzy tagging/clustering of metamodel changes (without pre-clustering)
"""

#%%
import pandas as pd
import numpy as np
np.random.seed(43)

data = pd.read_csv('stars-copies_with_changes.csv')

#%%
data.shape

# %%
# Study the changes in the EClass feature
change_class = data[data["CHANGE-EClass"] > 0]
change_class.shape

#%%
change_class.sample(40).to_csv("change_class_sample.csv", index=False)

# %%
feature_groups = pd.read_csv("feature_groups.csv")
feature_groups

#%%
all_features = feature_groups["Feature"].values
data["sum_all"] = data[all_features].sum(axis=1)

# %%
groups = feature_groups["MacroCluster"].unique()

group_features = {
    g : feature_groups[feature_groups["MacroCluster"] == g]["Feature"].unique() for g in groups
}
group_features

# %%
for g in groups:
    data[f"sum_{g}"] = data[group_features[g]].sum(axis=1)
    data[f"has_{g}"] = data[f"sum_{g}"] > 0
    data[f"ratio_{g}"] = data[f"sum_{g}"] / data["sum_all"]


#%%
sum_features = [f"sum_{g}" for g in groups]
ratio_features = [f"ratio_{g}" for g in groups]

data["ratio_all"] = data[ratio_features].sum(axis=1)
assert ((data["ratio_all"] - 1).abs().max() < 1e-10)

data[sum_features + ratio_features + ["ratio_all"]].head()

# %%
for g in groups:
    print(f"Group {g}")
    print(data[f"ratio_{g}"].describe())
    print()

#%%

# Get all combinations of elements in groups
from itertools import combinations

candidates = [g for g in groups if g not in []]

tuples = []
for n in range(1, len(groups) + 1):
    tuples.append(list(combinations(candidates, n)))

# flatten the list
tuples = [item for sublist in tuples for item in sublist]
print(tuples)


#%%

# sort the tuples by name

tuples = [sorted(t) for t in tuples]
tuples = sorted(tuples, key=lambda x: "_".join(x))
print(tuples)

#%%
for t in tuples:
    column = "all_in" + "_".join(t)
    negatives = [g for g in candidates if g not in t]

    data[column] = data[[f"has_{g}" for g in t]].all(axis=1) & ~data[[f"has_{g}" for g in negatives]].any(axis=1)

data.head()


#%%
all_in_features = data.columns[data.columns.str.startswith("all_in")]
all_in_features = sorted(all_in_features)

# pie chart of all_in features
import matplotlib.pyplot as plt

sizes = [data[f].sum() for f in all_in_features]
labels = [f[6:] for f in all_in_features]

fig1, ax1 = plt.subplots()
ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
ax1.axis('equal')

plt.show()

#%%

# bar chart the features
fig, ax = plt.subplots()
ax.barh(labels, sizes)
plt.suptitle("Counts for each exclusive group combination")
plt.show()

#%%
labels = groups
sizes = [data[f"has_{g}"].sum() for g in groups]

fig, ax = plt.subplots()
ax.barh(labels, sizes)
plt.suptitle("Changes from each group (non-exclusive)")
plt.show()

# %%
'''
Package group is assigned in the presence of either:
    - CHANGE-EPackage
    - ADD-ResourceAttachment.EPackage and DELETE-ResourceAttachment.EPackage and MOVE-EClass
'''
data["group_package"] = (
    (data["CHANGE-EPackage"] > 0) |
    ((data["ADD-ResourceAttachment.EPackage"] > 0) & (data["DELETE-ResourceAttachment.EPackage"] > 0) & (data["MOVE-EClass"] > 0)))

data["group_package"].value_counts()

# %%
data[data["group_package"]].sample(40).to_csv("group_package_sample.csv", index=False)
data[~data["group_package"]].sample(40).to_csv("no_group_package_sample.csv", index=False)

# %%
'''
Annotation group is assigned if any change to annotations is present
'''

data["group_annotation"] = (
    (data["ADD-EAnnotation"] > 0) |
    (data["CHANGE-EAnnotation"] > 0) |
    (data["DELETE-EAnnotation"] > 0))

data["group_annotation"].value_counts()

#%%

'''
Structural and non-structural are studied together

- If only changes of one type are present, the group is assigned
- If changes of both are present, we check how representative they are wrt the other group
'''
g_structural = "group_structural"
g_non_structural = "group_non_structural"

data[g_structural] = False
data[g_non_structural] = False

#%%

# Assign group for exclusive changes of each group (independent of the others)

print("Only structural:", len(data[(data["sum_Structural"] > 0) & (data["sum_Non-Structural"] == 0)]))
print("Only non-structural:", len(data[(data["sum_Non-Structural"] > 0) & (data["sum_Structural"] == 0)]))

data.loc[((data["sum_Structural"] > 0) & (data["sum_Non-Structural"] == 0)), g_structural] = True
data.loc[((data["sum_Non-Structural"] > 0) & (data["sum_Structural"] == 0)), g_non_structural] = True

#%%

mix = data[(data["sum_Structural"] > 0) & (data["sum_Non-Structural"] > 0)]
mix.shape

#%%

print("Structural")
print(mix["sum_Structural"].describe())
print(mix["ratio_Structural"].describe())
print()

print("Non-Structural")
print(mix["sum_Non-Structural"].describe())
print(mix["ratio_Non-Structural"].describe())

#%%

# Scatterplot structural vs non-structural

plt.scatter(mix["sum_Structural"], mix["sum_Non-Structural"], s=1)
plt.xlabel("Structural changes")
plt.ylabel("Non-structural changes")

# add a trendline with slope 1
x = np.linspace(0, 2500, 100)
plt.plot(x, x, color="red")

plt.xlim(0, 400)
plt.ylim(0, 400)


plt.tight_layout
plt.show()

#%%
more_structural = mix[mix["sum_Structural"] > mix["sum_Non-Structural"]]
less_structural = mix[mix["sum_Structural"] < mix["sum_Non-Structural"]]
on_line = mix[mix["sum_Structural"] == mix["sum_Non-Structural"]]

print("Copies below the trend line")
print(len(more_structural))

print("Copies above the trend line")
print(len(less_structural))

print("Copies on the trend line")
print(len(on_line))


#%%
on_line.sample(40).to_csv("structural-equal-non-structural.csv", index=False)

#%%

# Those with the same number of changes are assigned to both groups
data.loc[on_line.index, g_structural] = True
data.loc[on_line.index, g_non_structural] = True

# Those with more changes of one type are assigned to that group
# They can be assigned to the other group later if those other
# changes are considered representative
data.loc[more_structural.index, g_structural] = True
data.loc[less_structural.index, g_non_structural] = True

#%%
more_structural[["sum_Structural", "sum_Non-Structural"]].describe()

#%%
less_structural[["sum_Structural", "sum_Non-Structural"]].describe()

#%%

# Ratios of structural vs structural (ignoring the other groups)

more_structural = more_structural.copy()
more_structural["sum_both"] = more_structural["sum_Structural"] + more_structural["sum_Non-Structural"]
more_structural["proportion_structural"] = more_structural["sum_Structural"] / more_structural["sum_both"]
more_structural["proportion_non_structural"] = 1 - more_structural["proportion_structural"]

more_structural[["proportion_structural", "proportion_non_structural"]].describe()

more_structural.sample(100).to_csv("structural-above-non-structural.csv", index=False)

#%%
less_structural = less_structural.copy()
less_structural["sum_both"] = less_structural["sum_Structural"] + less_structural["sum_Non-Structural"]
less_structural["proportion_structural"] = less_structural["sum_Structural"] / less_structural["sum_both"]
less_structural["proportion_non_structural"] = 1 - less_structural["proportion_structural"]

less_structural[["proportion_structural", "proportion_non_structural"]].describe()

less_structural.sample(100).to_csv("structural-below-non-structural.csv", index=False)


#%%
non_structural_threshold = 0.22
tagged_non_structural = more_structural[more_structural["proportion_non_structural"] > non_structural_threshold]
print(f"Tagged non-structural: {len(tagged_non_structural)}/{len(more_structural)}")

structural_threshold = 0.25
tagged_structural = less_structural[less_structural["proportion_structural"] > structural_threshold]
print(f"Tagged structural: {len(tagged_structural)}/{len(less_structural)}")

print(f"Both taggged vs both having changes: {len(tagged_non_structural) + len(tagged_structural)}/{len(mix)}")

#%%

data.loc[tagged_non_structural.index, g_non_structural] = True
data.loc[tagged_structural.index, g_structural] = True

#%%
data.to_csv("stars-with-groups.csv", index=False)
