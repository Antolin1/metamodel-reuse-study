#%%
import pandas as pd

df = pd.read_csv("combined_results.csv")
df.head()

# %%

predicted = "duplicate_detector"
real = "manual_label"

df["TP"] = (df[predicted] == 1) & (df[real] == 1)
df["FP"] = (df[predicted] == 1) & (df[real] == 0)
df["TN"] = (df[predicted] == 0) & (df[real] == 0)
df["FN"] = (df[predicted] == 0) & (df[real] == 1)

df.head(50)

#%%

precision = df["TP"].sum() / (df["TP"].sum() + df["FP"].sum())
recall = df["TP"].sum() / (df["TP"].sum() + df["FN"].sum())
f1 = 2 * (precision * recall) / (precision + recall)

print(f"Precision: {precision}")
print(f"Recall: {recall}")
print(f"F1: {f1}")
