import csv
import glob
import random
import xml.etree.ElementTree as ET
from itertools import combinations
from pprint import pprint

from dpu_utils.codeutils.deduplication import DuplicateDetector

TARGET_LABEL = '008'
FOLDER = 'manualDomains'
SAMPLES_PER_CLUSTER = 3
SEED = 123

random.seed(SEED)

detector = DuplicateDetector(min_num_tokens_per_document=5)


def get_attribute_values(root, attribute_name):
    values = []
    for elem in root.iter():
        if attribute_name in elem.attrib:
            values.append(elem.attrib[attribute_name].lower())
    return values


for file in glob.glob(f"{FOLDER}/*.ecore"):
    domain = file.split('_')[1]
    if domain == TARGET_LABEL:
        tree = ET.parse(file)
        root = tree.getroot()
        attribute_values = get_attribute_values(root, 'name')
        detector.add_file(file, attribute_values, language=None)


duplicates = detector.compute_duplicates()
detector.print_clone_set_stats(duplicates)


positive_samples = []
negative_samples = []
for group in duplicates:
    if len(group) > SAMPLES_PER_CLUSTER:
        positive_samples.append(random.sample(list(group), SAMPLES_PER_CLUSTER))
    else:
        positive_samples.append(list(group))

    negative_samples.append(random.sample(list(group), 1)[0])

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
pprint(negative_samples)
with open('negative.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    for item in negative_samples:
        writer.writerow([item])
