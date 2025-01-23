#%%
import pandas as pd

filename  = "metamodel_metrics.csv"

df = pd.read_csv(filename)
df.head()

#%%
df["RootPackages"].describe()

#%%
print("MMs with more than one root package:", len(df[df["RootPackages"] > 1]))

# %%
metrics = ["size_kb", "numelements", "EPackages", "EClasses", "EAttributes", "EReferences"]
df_selection = df[metrics].copy()

#%%
rename_dict = {
    "size_kb": "Size (KiB)",
    "numelements": "Size (Elements)"
}
df_selection.rename(columns=rename_dict, inplace=True)
df_selection.head()

#%%
df_metrics = df_selection.describe()
df_metrics = df_metrics.T

df_metrics['Metric'] = df_metrics.index

df_metrics.head()

#%%
df_metrics.drop(columns=["count", "min"], inplace=True)

# convert min, max, and quartiles to integers
# df_metrics["25%"] = df_metrics["25%"].astype(int)
# df_metrics["50%"] = df_metrics["50%"].astype(int)
# df_metrics["75%"] = df_metrics["75%"].astype(int)
# df_metrics["max"] = df_metrics["max"].astype(int)

rename_metrics = {
    "mean": "Mean",
    "std": "Std",
    "25%": "Q1",
    "50%": "Median",
    "75%": "Q3",
    "max": "Max"
}
df_metrics.rename(columns=rename_metrics, inplace=True)

df_metrics = df_metrics[["Metric", "Mean", "Std", "Q1", "Median", "Q3", "Max"]]

df_metrics.head()

# %%
# print dataframe as latex table
print(df_metrics.to_latex(index=False, float_format="%.2f"))

# %%
