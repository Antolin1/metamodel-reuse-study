#%%
import pandas as pd

#%%
cluster = 1
clusters =  [
    "macro_cluster0-structural-major", "macro_cluster1-annotations", "macro_cluster2-nonstructural-minor",
    "macro_cluster3-package"]

filename = f"{clusters[cluster]}.csv"
df = pd.read_csv(filename)
df.head()

#%%
df.shape

# %%
df_inter = df[df["inter"] == 1]
df_intra = df[df["inter"] == 0]

df_inter.shape, df_intra.shape
# %%
counts_inter = df_inter.groupby(["original_path"])["original"].count().sort_values(ascending=False)

counts_inter.to_csv(f"cluster{cluster}-inter_counts.csv")

# %%
counts_intra = df_intra.groupby(["original_path"])["original"].count().sort_values(ascending=False)

counts_intra.to_csv(f"cluster{cluster}-intra_counts.csv")

# %%
for name, data in zip(["inter", "intra"], [counts_inter, counts_intra]):
    print(name)
    print("cluster size:", data.sum())
    print("distinct original mms:", len(data))
    print("proportion:", len(data) / data.sum())
    print("duplications stats:")
    print(data.agg(["median", "mean", "std", "min", "max"]))
    print()
