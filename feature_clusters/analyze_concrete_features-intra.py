# -*- coding: utf-8 -*-
"""
Study concrete features extracted from the changes of the stars clusters.

Add, delete and move features are the same as in the previous cases

Change features include the concrete type of the changed element, plus the changed feature

No feature filtering is done in this script.
"""

#%%
import pandas as pd

data = pd.read_csv('cluster_stars_with_concrete_features-intra.csv')
data

#%%
features = [c for c in data.columns if ('ADD' in c or 'CHANGE' in c or 'DELETE' in c or 'MOVE' in c)]

print(len(features))

#%%
data["sum_changed_features"] = data[features].sum(axis=1)

#%%

data_no_changes = data[data["sum_changed_features"] == 0]
print("No changes: ", data_no_changes.shape)

#%%

# rank features by frequency
feature_counts = data[features].sum(axis=0)
feature_counts.sort_values(ascending=False, inplace=True)

feature_counts = feature_counts.reset_index()
feature_counts.columns = ['feature', 'count']
feature_counts.to_csv('concrete_feature_counts-intra.csv', index=False)
