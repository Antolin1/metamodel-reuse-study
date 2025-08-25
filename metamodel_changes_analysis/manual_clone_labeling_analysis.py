#%%
import pandas as pd
from sklearn.metrics import roc_curve, auc
import matplotlib.pyplot as plt
import numpy as np

#%%
filename = "manual_clone_labeling.csv"
df = pd.read_csv(filename)
df.head()

#%%
num_samples = 10
df = df[df["sample_number"] < num_samples].copy()
df.shape

#%%
# retuirn final_label if it exists, otherwise return label
def get_final_label(row):
    if pd.notna(row["final_label"]):
        return row["final_label"]
    return row["label"]

#%%
df["combined_label"] = df.apply(get_final_label, axis=1)

#%%
# Convert labels to binary format: 'C' as positive class (1), 'B' as negative class (0)
df['binary_label'] = df['combined_label'].apply(lambda x: 1 if x == 'C' else 0)

# Compute ROC curve
fpr, tpr, thresholds = roc_curve(df['binary_label'], df['relative_change'])
roc_auc = auc(fpr, tpr)

# Plot ROC curve
plt.figure(figsize=(8, 6))
plt.plot(fpr, tpr, color='blue', lw=2, label=f'ROC curve (AUC = {roc_auc:.2f})')
plt.plot([0, 1], [0, 1], color='gray', lw=2, linestyle='--')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.legend(loc="lower right")
plt.grid(True)
plt.show()

# %%
# select optimal threshold (Youden’s J Statistic)
optimal_idx = np.argmax(tpr - fpr)
optimal_threshold = thresholds[optimal_idx]
print(f"Optimal threshold for classification: {optimal_threshold:.4f}")

#%%
# calculate precision, recall, f1-score for the optimal threshold
from sklearn.metrics import precision_score, recall_score, f1_score
df['predicted_label'] = df['relative_change'].apply(lambda x: 1 if x >= optimal_threshold else 0)
precision = precision_score(df['binary_label'], df['predicted_label'])
recall = recall_score(df['binary_label'], df['predicted_label'])
f1 = f1_score(df['binary_label'], df['predicted_label'])
print(f"Precision: {precision:.2f}, Recall: {recall:.2f}, F1-Score: {f1:.2f}")

#%%
df_typesBC = pd.read_csv("typeBC_clones.csv")
df_typesBC.head()
# %%

df_typesBC["relative_change_with_saturation"].describe()

# %%
df_typesBC["final_label"] = df_typesBC["relative_change_with_saturation"].apply(
    lambda x: "C" if x > optimal_threshold else "B"
)

#%%
df_typesBC["final_label"].value_counts()

#%%
df_typesA = pd.read_csv("typeA_clones.csv")
df_typesA["final_label"] = "A"


#%%
df_combined = pd.concat([df_typesA, df_typesBC], ignore_index=True)
df_combined.to_csv("labelled_clones.csv", index=False)

#%%
print(f"Type A: {len(df_combined[df_combined['final_label'] == 'A'])} ({len(df_combined[df_combined['final_label'] == 'A']) / len(df_combined) * 100:.2f}%)")
print(f"Type B: {len(df_combined[df_combined['final_label'] == 'B'])} ({len(df_combined[df_combined['final_label'] == 'B']) / len(df_combined) * 100:.2f}%)")
print(f"Type C: {len(df_combined[df_combined['final_label'] == 'C'])} ({len(df_combined[df_combined['final_label'] == 'C']) / len(df_combined) * 100:.2f}%)")

#%%
# get the clones of each type separated by scenario
scenarios = df_combined["scenario"].unique()
for scenario in scenarios:
    print(f"Scenario: {scenario}")
    df_scenario = df_combined[df_combined["scenario"] == scenario]
    print(f"  Type A: {len(df_scenario[df_scenario['final_label'] == 'A'])} ({len(df_scenario[df_scenario['final_label'] == 'A']) / len(df_scenario) * 100:.2f}%)")
    print(f"  Type B: {len(df_scenario[df_scenario['final_label'] == 'B'])} ({len(df_scenario[df_scenario['final_label'] == 'B']) / len(df_scenario) * 100:.2f}%)")
    print(f"  Type C: {len(df_scenario[df_scenario['final_label'] == 'C'])} ({len(df_scenario[df_scenario['final_label'] == 'C']) / len(df_scenario) * 100:.2f}%)")
