import pandas as pd

df_1 = pd.read_csv('ecore_metadata.csv')
df_2 = pd.read_csv('ecore_metadata_2.csv')

# merge into one and save it as csv

df_merged = pd.concat([df_1, df_2], ignore_index=True)
df_merged.to_csv('ecore_metadata_final.csv', index=False)
print("Dataframes merged and saved as 'ecore_metadata_merged.csv'.")