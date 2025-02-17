import argparse

import numpy as np
import pandas as pd
from plotnine import *
from sklearn.metrics import cohen_kappa_score


def main(args):
    labels = pd.read_csv(args.file, sep=';')
    print(labels.columns)
    ## Labels distribution

    labels_reviewer_1 = []
    labels_reviewer_2 = []
    corrected_labels = []

    for index, row in labels.iterrows():
        if 'label 3 reviewer 1' in row:
            l1, l2, l3 = row['label 1 reviewer 1'], row['label 2 reviewer 1'], row['label 3 reviewer 1']
            labels_reviewer_1.append(frozenset([str(l1), str(l2), str(l3)]))
        else:
            l1, l2 = row['label 1 reviewer 1'], row['label 2 reviewer 1']
            labels_reviewer_1.append(frozenset([str(l1), str(l2)]))

        if 'label 3 reviewer 2' in row:
            l1, l2, l3 = row['label 1 reviewer 2'], row['label 2 reviewer 2'], row['label 3 reviewer 2']
            labels_reviewer_2.append(frozenset([str(l1), str(l2), str(l3)]))
        else:
            l1, l2 = row['label 1 reviewer 2'], row['label 2 reviewer 2']
            labels_reviewer_2.append(frozenset([str(l1), str(l2)]))

        if 'Final label 3' in row:
            l1, l2, l3 = row['Final label 1'], row['Final label 2'], row['Final label 3']
            corrected_labels.append(frozenset([str(l1), str(l2), str(l3)]))
        else:
            l1, l2 = row['Final label 1'], row['Final label 2']
            corrected_labels.append(frozenset([str(l1), str(l2)]))

    final_labels = []
    for lr1, lr2, cl in zip(labels_reviewer_1, labels_reviewer_2, corrected_labels):
        if lr1 == lr2:
            final_labels.append(lr1)
        else:
            final_labels.append(cl)

        print(lr1, lr2, final_labels[-1])
        assert frozenset(['nan', 'nan', 'nan']) != final_labels[-1]
        assert frozenset(['nan', 'nan']) != final_labels[-1]
        assert frozenset(['nan']) != final_labels[-1]


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
     + geom_text(aes(label=df['Proportion'].round(2)), nudge_y=0.02, size=12)
     + theme(axis_text=element_text(size=15),
             axis_title=element_text(size=20))
     + labs(
            x='Categories',  # X-axis title
            y='Proportion',  # Y-axis title
        )  # Adjust y-axis text size if needed
     +
        scale_y_continuous(breaks=np.arange(0, 0.35, 0.05))
    )

    plot.save(f"{args.type}_bar_plot.pdf", width=10, height=6, dpi=300)


    ## Kappa

    def frozen_set_to_label(frozen_set):
        return ','.join(sorted(frozen_set))  # Convert frozenset to a sorted string representation

    labels1 = [frozen_set_to_label(fs) for fs in labels_reviewer_1]
    labels2 = [frozen_set_to_label(fs) for fs in labels_reviewer_2]


    kappa_score = cohen_kappa_score(labels1, labels2)
    print("Kappa Score:", kappa_score)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', type=str)
    parser.add_argument('--type', type=str, choices=['inter', 'intra'])
    args = parser.parse_args()
    main(args)