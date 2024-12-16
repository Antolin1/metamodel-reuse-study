#!/usr/bin/env python

'''
Tags copies with the presence or absence of the difference types detected by EMF Compare (ADD, CHANGE, MOVE, DELETE) plus annotations and package changes
'''

#%%
import pandas as pd
import numpy as np
np.random.seed(43)

data = pd.read_csv('stars-copies_with_changes.csv')
data

#%%
data.shape

# %%
diff_types = pd.read_csv("diff_types.csv")
diff_types

# %%
dt_names = diff_types["DiffType"].unique()

dt_features = {
    dt : diff_types[diff_types["DiffType"] == dt]["Feature"].unique() for dt in dt_names
}
dt_features

#%%
simple_diff_types = ["Annotations", "Add", "Delete", "Change", "ChangePackage"]

for dt in simple_diff_types:
    data[f"sum_{dt}"] = data[dt_features[dt]].sum(axis=1)
    data[f"type_{dt}"] = data[f"sum_{dt}"] > 0

data.head(5)

# %%

# tag package root changes
def has_root_package_change(row):
    mandatory_root_package_changes = dt_features["AddDeleteRootPackage"]
    extra_root_package_changes = dt_features["AddDeleteRootPackage-Extra"]

    # all mandatory changes need to be present
    has_mandatory_changes = True
    for f in mandatory_root_package_changes:
        if (row[f] == 0):
            has_mandatory_changes = False
            break

    # at least one extra change needs to be present
    has_extra_changes = False
    for f in extra_root_package_changes:
        if (row[f] > 0):
            has_extra_changes = True
            break

    return has_mandatory_changes and has_extra_changes

data["type_AddDeleteRootPackage"] = data.apply(has_root_package_change, axis=1)

#%%

# tag move changes, having into account if there are package root changes
def has_move_change(row):
    move_changes = dt_features["Move"]

    # if there are root package changes, consider the extra move changes
    if not row["type_AddDeleteRootPackage"]:
        move_changes = np.concatenate((move_changes, dt_features["AddDeleteRootPackage-Extra"]))

    return row[move_changes].sum() > 0

data["type_Move"] = data.apply(has_move_change, axis=1)

#%%

# extra type "package" that combines all package changes
data["type_Package"] = data["type_AddDeleteRootPackage"] | data["type_ChangePackage"]

#%%
data.to_csv("stars-copies_with_diff_types.csv", index=False)

#%%

# Generate sample for testing
sample = data.sample(30)
sample.to_csv("sample_diff_types.csv", index=False)
