#!/usr/bin/env python

'''Check for the use of Generics in the metamodels'''

import xml.etree.ElementTree as ET

def count_specific_elements(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    eGenericType_count = 0
    eBounds_count = 0
    eTypeParameters_count = 0

    for elem in root.iter():
        if elem.tag == 'eGenericType':
            eGenericType_count += 1
        elif elem.tag == 'eBounds':
            eBounds_count += 1
        elif elem.tag == 'eTypeParameters':
            eTypeParameters_count += 1

    return eGenericType_count, eBounds_count, eTypeParameters_count

if __name__ == "__main__":
    print('mm,eGenericType,eBounds,eTypeParameters')
    with open("metamodels.txt", "r") as f:
        for line in f:
            xml_file = line.strip()
            eGenericType_count, eBounds_count, eTypeParameters_count = count_specific_elements(f"../metamodels/{xml_file}")
            print(f'{xml_file},{eGenericType_count},{eBounds_count},{eTypeParameters_count}')
