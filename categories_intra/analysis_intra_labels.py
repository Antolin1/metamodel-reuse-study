import pandas as pd

FILE = 'categories_intra/samples_intra_labels.csv'

labels = pd.read_csv(FILE)

## Labels distribution

labels_reviewer_1 = []
labels_reviewer_2 = []
corrected_labels = []

for index, row in labels.iterrows():
    l1, l2 = row['label 1 reviewer 1'], row['label 2 reviewer 1']
    labels_reviewer_1.append(frozenset([str(l1), str(l2)]))

    l1, l2 = row['label 1 reviewer 2'], row['label 2 reviewer 2']
    labels_reviewer_2.append(frozenset([str(l1), str(l2)]))

    l1, l2 = row['Final label 1'], row['Final label 2']
    corrected_labels.append(frozenset([str(l1), str(l2)]))

final_labels = []
for lr1, lr2, cl in zip(labels_reviewer_1, labels_reviewer_2, corrected_labels):
    if lr1 == lr2:
        final_labels.append(lr1)
    else:
        final_labels.append(cl)

distinct_labels = []
for fl in final_labels:
    for l in fl:
      if l != 'nan':
        distinct_labels.append(l)

distinct_labels = list(set(distinct_labels))
total_prop = 0
props_dict = {}
for l in distinct_labels:
    cont = sum(l in fl for fl in final_labels)
    prop = 100 * cont/len(final_labels)
    total_prop += prop
    print(f"{l}: {cont}, {prop:.2f}")
    props_dict[l] = prop / 100

print(f"Total: {total_prop:.2f}")

from plotnine import *
import numpy as np

df = pd.DataFrame(list(props_dict.items()), columns=['Label', 'Proportion'])
df = df.sort_values(by=['Proportion'], ascending=False)

n = len(final_labels)
# Compute confidence intervals
z = 1.96  # Z-score for 95% confidence
df['Lower'] = df['Proportion'] - z * np.sqrt((df['Proportion'] / 100) * (1 - (df['Proportion'] / 100)) / n)
df['Upper'] = df['Proportion'] + z * np.sqrt((df['Proportion'] / 100) * (1 - (df['Proportion'] / 100)) / n)

plot = (ggplot(df, aes(x='reorder(Label, Proportion)', y='Proportion'))
 + geom_col()
 + coord_flip()  # Flip coordinates for horizontal bars
 # + geom_errorbar(aes(ymin='Lower', ymax='Upper'), width=0.4, color='black')
 + theme(axis_text_y=element_text(size=10))
 + labs(
        x='Categories',  # X-axis title
        y='Proportion',  # Y-axis title
    )  # Adjust y-axis text size if needed
 +
    scale_y_continuous(breaks=np.arange(0, 0.35, 0.05))
)

plot.save("intra_bar_plot.pdf", width=10, height=6, dpi=300)


## Kappa

def frozen_set_to_label(frozen_set):
    return ','.join(sorted(frozen_set))  # Convert frozenset to a sorted string representation

labels1 = [frozen_set_to_label(fs) for fs in labels_reviewer_1]
labels2 = [frozen_set_to_label(fs) for fs in labels_reviewer_2]

from sklearn.metrics import cohen_kappa_score

kappa_score = cohen_kappa_score(labels1, labels2)
print("Kappa Score:", kappa_score)