# Analysis on new data




### Steps

TODO
```shell
TODO
```

Generate SQLite database with the schema:
```shell
sqlite3 dup_network_new.db < major-new-mms/schema-major.sql
```

Download meta-models from GitHub:
```shell
python major-new-mms/download_data.py
```

Extract content of Ecore files and compute duplicates using Allamanis's approach:
```shell
python extract_concepts.py
python compute_duplicates.py
```

## Run EMF Compare comparisons

To run the EMF Compare scripts, you must first import the Eclipse project present in the `java` folder to your workspace. This project contains a target platform configuration in the `.target` file (open in Eclipse > Load Target Platform on top-right). Then, you can run any of the main programs of the project.

Again, if there is no desire to run these steps, the final datasets are already present in the [`metamodel_changes_analysis`](metamodel_changes_analysis) folder of the repository.

### Steps

Calculate the cluster stars that are used in the comparisons:

```shell
python calculate_cluster_stars.csv
```

In the java project, run the following main programs:

- `ClusterStarsAnalysisConcreteFeatures.java`
- `ClusterStarsAnalysisIntra.java`

These will generate their output datasets inside the [`feature_clusters`](feature_clusters) folder.


## Basic statistics

The following command computes basic statistics of the dataset, such as the number of meta-models, the number of repositories,
the users with the most meta-models, etc.
```shell
python dataset_statistics.py
```

## Duplication distribution

The following command computes the distribution of duplication in the dataset. Particularly, it shows
the ST1 and ST2 statistics of the duplication network, plots the distribution of the duplication cluster sizes, and prints
the top-10 most duplicated meta-models and most reused meta-models.

```shell
python analysis_duplication.py
```

## Intra-repository duplication

The following script computes the $Dup\mathcal{M}_r$ distribution over the repositories that show intra-repository duplication.
```shell
python analysis_intra.py
```

To display the label distribution, execute the following command:
```shell
python categories_intra_inter/analysis_labels.py --file categories_intra_inter/samples_intra_labels.csv --type intra
```

## Inter-repository duplication

The following script computes the $InterDup\mathcal{M}_r$ distribution over the repositories that show inter-repository duplication.
```shell
python analysis_inter.py
```

To display the label distribution, execute the following command:
```shell
python categories_intra_inter/analysis_labels.py --file categories_intra_inter/samples_inter_labels.csv --type inter
```

## Meta-model changes

To run the analysis of meta-model changes, execute the following command:

```shell
python metamodel_changes_analysis/analysis.py
```
