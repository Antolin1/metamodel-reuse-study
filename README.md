# Analysis of EMF Meta-model Duplication on GitHub

## Requirements

Set-up conda environment:
```shell
conda env create -f environment.yml
conda activate metamodel-reuse-study
```
Java and so on, TODO.

## Download and process data

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
python extract_conteps.py
python compute_duplicates.py
```


## Run EMF Compare

Finally run the EMF compare of `java` folder. To do this, you must load the target configuration present in the `.target` file (open in Ecilpse > Load Target Platform on top-right).

## Basic statistics

The following command compute basic statistics of the dataset, such as the number of meta-models, the number of repositories,
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

To display the label distribution, execute the following command:
```shell
python categories_intra_inter/analysis_labels.py --file categories_intra_inter/samples_inter_labels.csv --type inter
```

## Meta-model changes

To run the analysis of meta-model changes, execute the following command:

```shell
python metamodel_changes_analysis/analysis.py
```
