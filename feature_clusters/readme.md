# Description of the scripts regarding clusters analysis

- `analyze_clusters.py`: copy of colab's exploration notebook up to the generation and exporting of clusters. It also includes a bit of cluster analysis, and the sampling of kmeans clusters.

- `annotations.py`: exploration of annotations use of intra vs. inter metamodel copies.

- `count_generics.py`: study of generics usage in the dataset.

- `count_xmi_ids.py`: study of the presence of xmi IDs in the dataset metamodels.

- `diff_types.py`: tags copies with the presence or absence of the difference types detected by EMF Compare (ADD, CHANGE, MOVE, DELETE) plus annotations and package changes.

- `fuzzy_cluster.py`: manually assigns macro-clusters hinted by kmeans analysis (can assign multiple clusters to same copy). Superseded by `diff_types.py`.

- `group_features`: groups features by macro-cluster type. Superseded by `fuzzy_cluster.py`.

- `sample_clusters.py`: sampling of grouped/macro clusters (later we decided to sample and review pre-grouped kmeans clusters)

- `study_root_changes.py`: a study of causes for root- changing differences in metamodels, that led to discovering how XMI ids were preventing some duplicate comparisons.

- `sub_cluster_without_annotations.py`: analysis of the annotations macro-cluster, that contained copies belonging to the other clusters (but with annotations clusters as well)
