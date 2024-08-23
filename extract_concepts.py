import glob
import json
import sqlite3
import xml.etree.ElementTree as ET

from tqdm import tqdm

CONN = sqlite3.connect('dup_network.db')
CURSOR = CONN.cursor()


# Function to get all attribute values by attribute name
def get_attribute_values(root, attribute_name):
    values = []
    for elem in root.iter():
        if attribute_name in elem.attrib:
            values.append(elem.attrib[attribute_name].lower())
    return values


def store_concepts(file, concepts):
    CURSOR.execute("UPDATE metamodels SET concepts=? WHERE local_path=?", (json.dumps(concepts), file))


for f in tqdm(glob.glob('metamodels/*.ecore')):
    try:
        # Parse the XML data
        tree = ET.parse(f)
        root = tree.getroot()
        attribute_values = get_attribute_values(root, 'name')
        store_concepts(f.split('/')[-1], attribute_values)
    except:
        print(f)
        continue

CONN.commit()
CONN.close()
