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
simple_diff_types = ["Annotations", "Change", "ChangePackage"]

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

# tag add-delete subpackage changes (not root ones)

def has_subpackage_change(row):
    mandatory_package_changes = dt_features["AddDeleteSubpackage"]
    extra_package_changes = dt_features["AddDeleteRootPackage-Extra"]

    # all mandatory changes need to be present
    has_mandatory_changes = True
    for f in mandatory_package_changes:
        if (row[f] == 0):
            has_mandatory_changes = False
            break

    # at least one extra change needs to be present
    has_extra_changes = False
    for f in extra_package_changes:
        if (row[f] > 0):
            has_extra_changes = True
            break

    return has_mandatory_changes and has_extra_changes

data["type_AddDeleteSubpackage"] = data.apply(has_subpackage_change, axis=1)

#%%

# extra type "package" that combines all package changes
data["type_Package"] = data["type_ChangePackage"] | data["type_AddDeleteRootPackage"] | data["type_AddDeleteSubpackage"]

#%%

# tag move changes, having into account if there are special package changes
def has_move_change(row):
    move_changes = dt_features["Move"]

    # if there are not package changes, consider the extra move changes
    if not row["type_AddDeleteRootPackage"] and not row["type_AddDeleteSubpackage"]:
        move_changes = np.concatenate((move_changes, dt_features["AddDeleteRootPackage-Extra"]))

    return row[move_changes].sum() > 0

data["type_Move"] = data.apply(has_move_change, axis=1)

#%%
# tag add and delete cases, having into account potential subpackage changes

def has_add_change(row):
    add_changes = dt_features["Add"]

    # if there are not subpackage changes, consider add package as well
    if not row["type_AddDeleteSubpackage"]:
        add_changes = np.concatenate((add_changes, ["ADD-EPackage"]))

    return row[add_changes].sum() > 0


def has_delete_change(row):
    delete_changes = dt_features["Delete"]

    # if there are not subpackage changes, consider delete package as well
    if not row["type_AddDeleteSubpackage"]:
        delete_changes = np.concatenate((delete_changes, ["DELETE-EPackage"]))

    return row[delete_changes].sum() > 0


data["type_Add"] = data.apply(has_add_change, axis=1)
data["type_Delete"] = data.apply(has_delete_change, axis=1)


#%%
data.to_csv("stars-copies_with_diff_types.csv", index=False)

#%%

# Generate sample for testing
sample = data.sample(30)
sample.to_csv("sample_diff_types.csv", index=False)


#%%

# Study "MOVE-EPackage" changes
data["has_MoveEPackage"] = data["MOVE-EPackage"] > 0
data[data["has_MoveEPackage"]].to_csv("has_move_epackage.csv", index=False)

print("Has MOVE-EPackage:", len(data[data["has_MoveEPackage"]]))

data_move_and_root_pkg = data[data["type_AddDeleteRootPackage"] & data["has_MoveEPackage"]]
data_move_and_root_pkg.to_csv("move_epackage_root_pkg.csv", index=False)

print("Has MOVE-EPackage + rootPkg change:", len(data_move_and_root_pkg))

#%%

data["has_AddEPackage"] = data["ADD-EPackage"] > 0
data["has_DeleteEPackage"] = data["DELETE-EPackage"] > 0

data_add_delete_pkg = data[data["has_AddEPackage"] & data["has_DeleteEPackage"]]
data_add_delete_pkg.to_csv("add_delete_epackage.csv", index=False)

print("Has add + delete EPackage:", len(data_add_delete_pkg))

print("Has add + delete + move EPackage:", len(data_add_delete_pkg[data_add_delete_pkg["has_MoveEPackage"]]))

print("Has add + delete + move EPackage + no root pkg:", len(data_add_delete_pkg[data_add_delete_pkg["has_MoveEPackage"] & ~data_add_delete_pkg["type_AddDeleteRootPackage"]]))

#%%
def has_extra_move_changes_without_pkg_ones(row):

    if row["type_Package"]:
        return False

    extra_package_changes = dt_features["AddDeleteRootPackage-Extra"]
    has_extra_changes = False
    for f in extra_package_changes:
        if (row[f] > 0):
            has_extra_changes = True
            break

    return has_extra_changes

data["type_MoveExtra"] = data.apply(has_extra_move_changes_without_pkg_ones, axis=1)
data["type_MoveExtra"].sum()

#%%
# has add package or delete package (but not both)
len(data[data["has_AddEPackage"] ^ data["has_DeleteEPackage"]])

#%%
# has add package and delete package
len(data[data["has_AddEPackage"] & data["has_DeleteEPackage"]])

#%%
# Possible combinations of column values

package_columns = ["ADD-EPackage", "DELETE-EPackage", "MOVE-EPackage", "ADD-ResourceAttachment.EPackage", "DELETE-ResourceAttachment.EPackage"]

data_pkg = data[package_columns].copy()

has_column = [f"has_{c}" for c in package_columns]

for hc, c in zip(has_column, package_columns):
    data_pkg[hc] = data_pkg[c] > 0

data_pkg[package_columns].value_counts().to_csv("package_columns_combinations.csv")

data_pkg[has_column].value_counts().to_csv("has_package_columns_combinations_binary.csv")


# %%
