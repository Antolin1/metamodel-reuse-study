#!/usr/bin/env python

'''Check for the use of XMI IDs in the metamodels'''

import xml.etree.ElementTree as ET
import sys

def count_xmi_id_attributes(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    count = 0

    for elem in root.iter():
        if '{http://www.omg.org/XMI}id' in elem.attrib:
            count += 1
    return count

if __name__ == "__main__":
    xml_file = sys.argv[1]
    count = count_xmi_id_attributes(xml_file)
    print(count)
