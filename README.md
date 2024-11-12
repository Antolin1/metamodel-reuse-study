# metamodel-reuse-study

```shell
wget https://www.win.tue.nl/~obabur/publications/EMSE22/listOfEcoreFiles.csv
```

```shell
sqlite3 dup_network.db < schema.sql
```

```shell
python download_data.py
```

```shell
python download_metadata.py
```

```shell
python extract_conteps.py
```

```shell
python compute_duplicates.py
```

Finally run the EMF compare of `java` folder. To do this, you must load the target configuration present in the `.target` file (open in Ecilpse > Load Target Platform on top-right).
