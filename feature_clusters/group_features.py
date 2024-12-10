'''
Group features at the macro/cluster level, and analyse their distribution
'''

#%%
import pandas as pd
import numpy as np
np.random.seed(43)

import matplotlib.pyplot as plt
import seaborn as sns

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

selected = filenames[0]

data = pd.read_csv(selected)
data.head()

# %%
data["ratio_structural"] = data[structural_features].sum(axis=1) / data["sum_changes"]
data["ratio_non_structural"] = data[non_structural_features].sum(axis=1) / data["sum_changes"]
data["ratio_package"] = data[package_features].sum(axis=1) / data["sum_changes"]

#%%

x = data['ratio_structural']
y = data['ratio_non_structural']

# Create a 2D histogram
hist, xedges, yedges = np.histogram2d(x, y, bins=50)

hist = hist.T # convert for visualisation

# Create the scatter plot
fig, ax = plt.subplots(figsize=(6, 6))

# Plot each bin as a point
xpos, ypos = np.meshgrid(xedges[:-1] + 0.5 * (xedges[1] - xedges[0]),
                         yedges[:-1] + 0.5 * (yedges[1] - yedges[0]))
xpos = xpos.ravel()
ypos = ypos.ravel()
hist = hist.ravel()

# Only plot bins with counts > 0
mask = hist > 0
ax.scatter(xpos[mask], ypos[mask], s=hist[mask]*10, alpha=0.5)

ax.set_xlim(-0.1, 1.1)
ax.set_ylim(-0.1, 1.1)
ax.set_xlabel('Ratio Structural')
ax.set_ylabel('Ratio Nonstructural')
ax.set_title(f'{selected}')

plt.tight_layout()
plt.show()

#%%

fig, ax = plt.subplots(3, 1, figsize=(10, 10))
sns.violinplot(x="ratio_structural", data=data, ax=ax[0])
sns.violinplot(x="ratio_non_structural", data=data, ax=ax[1])
sns.violinplot(x="ratio_package", data=data, ax=ax[2])

ax[0].set_xlim(-0.1, 1.1)
ax[1].set_xlim(-0.1, 1.1)
ax[2].set_xlim(-0.1, 1.1)

fig.suptitle(selected)

plt.tight_layout()
plt.show()
# %%

# Now include annotations
data["ratio_structural"] = data[structural_features].sum(axis=1) / data["all_changes"]
data["ratio_non_structural"] = data[non_structural_features].sum(axis=1) / data["all_changes"]
data["ratio_package"] = data[package_features].sum(axis=1) / data["all_changes"]
data["ratio_annotation"] = data[annotation_features].sum(axis=1) / data["all_changes"]

#%%
fig, ax = plt.subplots(4, 1, figsize=(10, 10))
sns.violinplot(x="ratio_structural", data=data, ax=ax[0])
sns.violinplot(x="ratio_non_structural", data=data, ax=ax[1])
sns.violinplot(x="ratio_package", data=data, ax=ax[2])
sns.violinplot(x="ratio_annotation", data=data, ax=ax[3])

ax[0].set_xlim(-0.1, 1.1)
ax[1].set_xlim(-0.1, 1.1)
ax[2].set_xlim(-0.1, 1.1)
ax[3].set_xlim(-0.1, 1.1)

fig.suptitle(selected)

plt.tight_layout()
plt.show()

# %%
data["ratio_package"].describe()
# %%
