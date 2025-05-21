import argparse
from collections import defaultdict

import numpy as np
import pandas as pd
from plotnine import *
from scipy.stats import mannwhitneyu, spearmanr


def export_modified_metamodels(data_inter, data_intra):
    df_inter = data_inter[data_inter['affected_elements'] > 0].copy()
    df_intra = data_intra[data_intra['affected_elements'] > 0].copy()

    df_inter['scenario'] = 'inter'
    df_intra['scenario'] = 'intra'

    combined_df = pd.concat([df_inter, df_intra])
    combined_df.to_csv("metamodel_changes_analysis/modified_metamodels.csv", index=False)

def affected_elements(data_inter, data_intra):

    print(f'Proportion of affected elements = 0 inter: {len(data_inter[data_inter["affected_elements"]==0])/len(data_inter):.2f}')
    print(f'Affected elements = 0 inter: {len(data_inter[data_inter["affected_elements"]==0])}, Total inter: {len(data_inter)}')

    print(f'Proportion of affected elements = 0 intra: {len(data_intra[data_intra["affected_elements"]==0])/len(data_intra):.2f}')
    print(f'Affected elements = 0 intra: {len(data_intra[data_intra["affected_elements"]==0])}, Total intra: {len(data_intra)}')

    df1 = pd.DataFrame(
        {'Affected elements': list(data_inter[data_inter['affected_elements'] > 0]['affected_elements'])})
    df2 = pd.DataFrame(
        {'Affected elements': list(data_intra[data_intra['affected_elements'] > 0]['affected_elements'])})

    # Add a group column to distinguish the dataframes
    df1['scenario'] = 'inter'
    df2['scenario'] = 'intra'

    # Combine the dataframes
    combined_df = pd.concat([df1, df2])

    # Create the boxplot
    plot = (
            ggplot(combined_df, aes(x='scenario', y='Affected elements'))
            + geom_boxplot()
            + theme_minimal()
            + ggtitle("Affected elements at intra- and inter-level")
            + scale_y_log10()
    )

    plot.save("affected_elements_plot.pdf", format="pdf")

    stat, p_value = mannwhitneyu(df1['Affected elements'], df2['Affected elements'], alternative='two-sided')

    # Display the results
    print(f"Statistic: {stat}")
    print(f"P-value: {p_value}")

    print(f'Median affected elements inter: {df1["Affected elements"].median()}')
    print(f'Median affected elements intra: {df2["Affected elements"].median()}')

    # Step 1: Calculate the median of the data
    median = np.median(df1["Affected elements"])
    # Step 2: Calculate the absolute deviations from the median
    absolute_deviations = np.abs(np.array(df1["Affected elements"]) - median)
    # Step 3: Calculate the median of the absolute deviations (MAD)
    mad = np.median(absolute_deviations)
    print(f'Median absolute deviation affected elements inter: {mad}')

    # Step 1: Calculate the median of the data
    median = np.median(df2["Affected elements"])
    # Step 2: Calculate the absolute deviations from the median
    absolute_deviations = np.abs(np.array(df2["Affected elements"]) - median)
    # Step 3: Calculate the median of the absolute deviations (MAD)
    mad = np.median(absolute_deviations)
    print(f'Median absolute deviation affected elements intra: {mad}')

def feature_comparison(data_inter, data_intra):
    data_inter = data_inter[data_inter['affected_elements'] > 0]
    data_intra = data_intra[data_intra['affected_elements'] > 0]

    grouping = defaultdict(list)
    for c in data_inter.columns:
        if c.startswith('ADD-'):
            grouping[c.split('-')[1]].append(c)
        elif c.startswith('DELETE-'):
            grouping[c.split('-')[1]].append(c)

    for c, cs in grouping.items():
        # or of the columns in cs and store in c
        data_inter[f'ADD-OR-DELETE-{c}'] = data_inter[cs].any(axis=1)
        data_intra[f'ADD-OR-DELETE-{c}'] = data_intra[cs].any(axis=1)

        # remove data in cs
        data_inter = data_inter.drop(columns=cs)
        data_intra = data_intra.drop(columns=cs)

    features = [c for c in data_inter.columns if
                c.startswith('ADD-OR-DELETE-') or c.startswith('CHANGE-') or c.startswith('MOVE-')]
    feature_counts_inter = data_inter[features].sum(axis=0)
    feature_counts_inter.sort_values(ascending=False, inplace=True)

    feature_counts_inter = feature_counts_inter.reset_index()
    feature_counts_inter.columns = ['feature', 'count']

    # add proprortion
    feature_counts_inter['proportion'] = feature_counts_inter['count'] / len(data_inter)

    feature_counts_intra = data_intra[features].sum(axis=0)
    feature_counts_intra.sort_values(ascending=False, inplace=True)

    feature_counts_intra = feature_counts_intra.reset_index()
    feature_counts_intra.columns = ['feature', 'count']

    # add proprortion
    feature_counts_intra['proportion'] = feature_counts_intra['count'] / len(data_intra)


    # spearman correlation
    d = {}
    list1 = list(feature_counts_intra['feature'])
    list2 = list(feature_counts_inter['feature'])
    for i, j in enumerate(list1):
        d[j] = i + 1
    list1 = [d[j] for j in list1]
    list2 = [d[j] for j in list2]
    spearman_corr, p_value = spearmanr(list1, list2)
    # Display results
    print("Spearman correlation:", spearman_corr, p_value)

    print(feature_counts_inter[['feature', 'proportion']].round(2).head(10).to_latex(index=False, float_format="%.2f"))
    print(feature_counts_inter[feature_counts_inter['feature'].str.contains('ADD-OR-DELETE')][['feature', 'proportion']].round(2).head(10).to_latex(index=False, float_format="%.2f"))
    print(feature_counts_inter[feature_counts_inter['feature'].str.contains('MOVE')][['feature', 'proportion']].round(2).head(10).to_latex(index=False, float_format="%.2f"))
    print(feature_counts_inter[feature_counts_inter['feature'].str.contains('CHANGE')][['feature', 'proportion']].round(
        2).head(10).to_latex(index=False, float_format="%.2f"))


def main(args):
    data_inter = pd.read_csv(args.inter)
    data_intra = pd.read_csv(args.intra)

    for c in data_inter.columns:
        if c not in data_intra.columns:
            data_intra[c] = False

    for c in data_intra.columns:
        if c not in data_inter.columns:
            data_inter[c] = False

    export_modified_metamodels(data_inter, data_intra)
    affected_elements(data_inter, data_intra)
    feature_comparison(data_inter, data_intra)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--inter', type=str, default='metamodel_changes_analysis/cluster_stars_with_concrete_features-inter.csv')
    parser.add_argument('--intra', type=str, default='metamodel_changes_analysis/cluster_stars_with_concrete_features-intra.csv')
    args = parser.parse_args()
    main(args)
