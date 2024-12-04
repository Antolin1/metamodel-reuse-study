#%%
import pandas as pd
import numpy as np
np.random.seed(43)

#%%
structural_features = [
    "ADD-EAttribute",
    "ADD-EClass",
    "ADD-EDataType",
    "ADD-EEnum",
    "ADD-EEnumLiteral",
    "ADD-EOperation",
    "ADD-EReference",
    "CHANGE-EClass",
    "DELETE-EAttribute",
    "DELETE-EClass",
    "DELETE-EDataType",
    "DELETE-EEnum",
    "DELETE-EEnumLiteral",
    "DELETE-EOperation",
    "DELETE-EReference",
    "MOVE-EAttribute",
    "MOVE-EEnumLiteral",
    "MOVE-EOperation",
    "MOVE-EReference",
    "ADD-EPackage",
    "DELETE-EPackage"
]

non_structural_features = [
    "CHANGE-EAttribute",
    "CHANGE-EDataType",
    "CHANGE-EEnum",
    "CHANGE-EOperation",
    "CHANGE-EReference",
    "CHANGE-EEnumLiteral"
]

package_features = [
    "ADD-ResourceAttachment.EPackage",
    "CHANGE-EPackage",
    "DELETE-ResourceAttachment.EPackage",
    "MOVE-EClass",
    "MOVE-EDataType",
    "MOVE-EEnum",
    "MOVE-EPackage"
]

annotation_features = [
    "ADD-EAnnotation",
    "CHANGE-EAnnotation",
    "DELETE-EAnnotation"
]

#%%
filenames = ["macro_cluster0-structural-major.csv",
             "macro_cluster1-nonstructural-minor.csv",
             "macro_cluster2-package.csv"]

selected = filenames[1]

data = pd.read_csv(selected)
data.head()

# %%
data["ratio_structural"] = data[structural_features].sum(axis=1) / data["sum_changes"]
data["ratio_non_structural"] = data[non_structural_features].sum(axis=1) / data["sum_changes"]
data["ratio_package"] = data[package_features].sum(axis=1) / data["sum_changes"]


#%%
data["ratio_sum"] = data["ratio_structural"] + data["ratio_non_structural"] + data["ratio_package"]
data["ratio_sum"].describe()

#%%

# draw a boxplot for each group
import matplotlib.pyplot as plt
import seaborn as sns

fig, ax = plt.subplots(3, 1, figsize=(10, 10))
sns.boxplot(x="ratio_structural", data=data, ax=ax[0])
sns.boxplot(x="ratio_non_structural", data=data, ax=ax[1])
sns.boxplot(x="ratio_package", data=data, ax=ax[2])

ax[0].set_xlim(-0.1, 1.1)
ax[1].set_xlim(-0.1, 1.1)
ax[2].set_xlim(-0.1, 1.1)

fig.suptitle(selected)

plt.show()
# %%

# %%
