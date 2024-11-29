import pandas as pd
import numpy as np

'''Sample grouped clusters for manual inspection'''

clusters =  [
    "macro_cluster0-structural-major",
    "macro_cluster1-annotations",
    "macro_cluster2-nonstructural-minor",
    "macro_cluster3-package"]

sample_size = 40
np.random.seed(43)

for cluster in clusters:
    df = pd.read_csv(f"{cluster}.csv")
    sample = df.sample(sample_size)
    sample.to_csv(f"{cluster}-sample.csv", index=False)
