# Evaluation of the clone detection tool

## Dataset

We used a labelled dataset of meta-models for this evaluation:

```shell
wget https://zenodo.org/records/2585432/files/manualDomains.zip
```

```shell
unzip manualDomains.zip
```

## Steps

From the meta-models labelled as state machines, generate the duplication clusters, and select a sample of positives and negative clusters (i.e. meta-models identified as clones or not):

```shell
python generate_clusters.py
```

The previous scripts generates the `positive.csv` and `negative.csv` datasets, which are used by the following programs in the Java project:

- `ToolEvaluationPositives.java`
- `ToolEvaluationNegatives.java`

The resulting `combined_results.csv` was completed by a manual inspection and labelling of the generated negatives and positives clusters of datasets.
