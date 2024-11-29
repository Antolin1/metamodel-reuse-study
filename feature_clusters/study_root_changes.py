#%%
import pandas as pd
from count_xmi_ids import count_xmi_id_attributes

'''Study root changes in metamodels, leading to the discovery of differing XMI IDs'''

#%%
clusters =  [
    "macro_cluster0-structural-major",
    "macro_cluster1-annotations",
    "macro_cluster2-nonstructural-minor",
    "macro_cluster3-package"]

#%% Extract a sample of cluster 0
df = pd.read_csv(clusters[0] + ".csv")
df_root_changes = df[(df["ADD-ResourceAttachment.EPackage"] > 0) &
                         (df["DELETE-ResourceAttachment.EPackage"] > 0)]
sample = df_root_changes.sample(40)
sample.to_csv(f"{clusters[0]}-onlyRootChanges-sample.csv", index=False)

#%%
def has_differing_ids(row):
    original_ids = count_xmi_id_attributes(f"../metamodels/{row['original_path']}")
    duplicate_ids = count_xmi_id_attributes(f"../metamodels/{row['duplicate_path']}")

    return original_ids != duplicate_ids and (original_ids == 0 or duplicate_ids == 0)

for index, cluster in enumerate(clusters):
    df = pd.read_csv(f"{cluster}.csv")
    df_root_changes = df[(df["ADD-ResourceAttachment.EPackage"] > 0) &
                         (df["DELETE-ResourceAttachment.EPackage"] > 0)]
    print("Cluster:", index)
    print("Cluster size:", len(df))
    print("Elems with root changes:", len(df_root_changes))
    print("Root changes ratio:", len(df_root_changes) / len(df))

    differing_ids = 0
    for index, row in df_root_changes.iterrows():
        if has_differing_ids(row):
            differing_ids += 1

    print(f"Cluster {index} roots size: ", len(df_root_changes))
    print("Differing id counts:", differing_ids)
    print()
