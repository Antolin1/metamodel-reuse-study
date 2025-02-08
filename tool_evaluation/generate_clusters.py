#!/usr/bin/env python
# -*- coding: utf-8 -*-

#%%

import csv
import glob
import random
import xml.etree.ElementTree as ET
from pprint import pprint

from dpu_utils.codeutils.deduplication import DuplicateDetector

TARGET_LABEL = '008'
FOLDER = 'manualDomains'
SEED = 123

random.seed(SEED)

#%%
def get_attribute_values(root, attribute_name):
    values = []
    for elem in root.iter():
        if attribute_name in elem.attrib:
            values.append(elem.attrib[attribute_name].lower())
    return values


#%%
detector = DuplicateDetector(min_num_tokens_per_document=5)

num_files = 0
for file in glob.glob(f"{FOLDER}/*.ecore"):
    domain = file.split('_')[1]
    if domain == TARGET_LABEL:
        tree = ET.parse(file)
        root = tree.getroot()
        attribute_values = get_attribute_values(root, 'name')
        detector.add_file(file, attribute_values, language=None)
        num_files += 1

print(f"Added {num_files} files to the detector")

duplicates = detector.compute_duplicates()
detector.print_clone_set_stats(duplicates)

#%%
positive_samples = []
negative_representatives = []

for group in duplicates:
    # for positives, all elements in the cluster are needed, the first of the
    #     random suffle is used as representative
    positives = list(group)
    random.shuffle(positives)
    positive_samples.append(positives)

    # for negatives, a representative is randomly selected
    negative_representatives.append(random.sample(list(group), 1)[0])

print("Positive")
pprint(positive_samples)
with open('positive.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    cont = 0
    for item in positive_samples:
        for i in item:
            writer.writerow([i, cont])
        cont += 1

print("Negative")
pprint(negative_representatives)
with open('negative.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    for item in negative_representatives:
        writer.writerow([item])
