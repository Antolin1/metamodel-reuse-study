#%%
import pandas as pd
import numpy as np

np.random.seed(43)

#%%
data = pd.read_csv('macro_cluster1-annotations.csv')
data

#%%
data.shape

#%%
features = [c for c in data.columns if ('ADD' in c or 'CHANGE' in c or 'DELETE' in c or 'MOVE' in c) and 'EAnnotation' not in c]
print(features)
len(features)

#%%
data["sum_changes"] = data[features].sum(axis=1)
data["sum_changes"].describe()

#%%

# Separate rows with no changes appart from in annotations
# Kmeans does not detect these as separate as we would prefer

data_no_changes = data[data["sum_changes"] == 0]
data = data[data["sum_changes"] > 0].copy()

data_no_changes.shape
#%%
len(data[data["sum_changes"] == 0])

#%%

from sklearn.decomposition import PCA
from sklearn.preprocessing import normalize

X = data[features]
X = normalize(X, norm='l2')

pca = PCA(n_components=13)
X_transformed = pca.fit_transform(X)
np.sum(pca.explained_variance_ratio_)

# %%
#%%
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

# List to store the WCSS values
wcss = []
ks_considered = [2, 5, 7, 10, 13, 15, 20, 25, 30]

# Loop through different values of k (number of clusters)
for k in ks_considered:
    kmeans = KMeans(n_clusters=k, init='k-means++',
                    max_iter=300, n_init=10, random_state=0)
    kmeans.fit(X_transformed)
    wcss.append(kmeans.inertia_)  # Inertia is another term for WCSS

# Plotting the elbow plot
plt.figure(figsize=(8,5))
plt.plot(ks_considered, wcss, marker='o', linestyle='--')
plt.title('Elbow Method for Optimal k')
plt.xlabel('Number of clusters (k)')
plt.ylabel('WCSS')
plt.show()

#%%
from kneed import KneeLocator

kneedle = KneeLocator([2, 5, 7, 10, 13, 15, 20, 25, 30],
                      wcss, curve='convex', direction='decreasing')

elbow_point = kneedle.elbow
print(f"Elbow point: {elbow_point}")

# %%
kmeans = KMeans(n_clusters=kneedle.elbow, init='k-means++',
                    max_iter=300, n_init=10, random_state=0)
kmeans.fit(X_transformed)

cluster_sizes = np.bincount(kmeans.labels_)
cluster_sizes

for cluster in range(10):
    print(f"Cluster {cluster}: {cluster_sizes[cluster]}")
    data_cluster = data[kmeans.labels_ == cluster]
    data_cluster = pd.DataFrame(normalize(data_cluster[features], norm='l1'), columns=data_cluster[features].columns).mean()
    # top 10 features
    top_features = 100 * data_cluster.sort_values(ascending=False).head(10)
    print(top_features)
    print()

data['cluster_kmeans'] = kmeans.labels_

# %%
sample_size = 20
for cluster in range(10):
    data_cluster = data[kmeans.labels_ == cluster]
    data_cluster.sample(sample_size).to_csv(f"annotations-cluster{cluster}-sample.csv", index=False)
