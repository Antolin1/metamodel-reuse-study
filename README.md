# Analysis of EMF Meta-model Duplication on GitHub

## Requirements

To set up the Python environment using `conda`:

```shell
conda env create -f environment.yml
conda activate metamodel-reuse-study
```

For the Java environment, the project has been developed using Eclipse 2024-12, which requires Java 21. It is recommended to use the appropriate [Eclipse installer](https://www.eclipse.org/downloads/packages/release/2024-12/r), and install either the *Eclipse IDE for Java and DSL Developers* or the *Eclipse Modeling Tools* versions. Any dependencies of the executed code are managed through a target platform. Instructions on how to use it are provided below.

## Download and process data

The data used in the paper (metamodels and duplication network) can be found [here](https://zenodo.org/records/15487407).
As such, there is no need to execute the scripts in this section.

### Steps

Get list of Ecore files from the paper's website:
```shell
wget https://www.win.tue.nl/~obabur/publications/EMSE22/listOfEcoreFiles.csv
```

Generate SQLite database with the schema:
```shell
sqlite3 dup_network.db < schema.sql
```

Download meta-models from GitHub:
```shell
python download_data.py
```

Download metadata from GitHub:
```shell
python download_metadata.py
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
