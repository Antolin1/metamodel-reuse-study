# Analysis of EMF Meta-model Duplication on GitHub

## Requirements

TODO

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


## Analysis of the categories at intra-level

```shell
python categories_intra/analysis_intra_labels.py
```