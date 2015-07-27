#! /Users/bin/env Python

# Modified version of get_disease.py from ClinGen/LoadData. Creates JSON file
# with all Orphanet data for (initial) load into the server. Run this script
# before using this one:
#   obtain_external_data_files.py -s orphanet

import json
from uuid import uuid4
from xml.etree import ElementTree as et

# uuid mapping for previously existing entries to avoid validation errors
uuidMapping = {
    "15": "78867c7a-16a6-11e5-8007-60f81dc5b05a",
    "654": "788ae1de-16a6-11e5-b341-60f81dc5b05a",
    "183660": "788aee73-16a6-11e5-8505-60f81dc5b05a",
    "777": "788c3bb0-16a6-11e5-8618-60f81dc5b05a",
    "370968": "788cd05e-16a6-11e5-97c0-60f81dc5b05a",
    "284984": "788d04b5-16a6-11e5-bc96-60f81dc5b05a",
    "891": "788d45ab-16a6-11e5-9042-60f81dc5b05a",
    "64742": "788d967d-16a6-11e5-acfb-60f81dc5b05a",
    "79452": "788e024f-16a6-11e5-a0b5-60f81dc5b05a"
}

tree = et.parse('rawData/disease.xml')
disorders = tree.findall('.//Disorder')
allData = []

omimNum = 0
omimMulti = 0
synonymNum = 0
synonymMulti = 0
for dis in disorders:
    synonym = []
    omim = []
    omimFound = False
    synFound = False

    # uuid check
    if dis.find('OrphaNumber').text in uuidMapping:
        uuid = uuidMapping[dis.find('OrphaNumber').text]
    else:
        uuid = str(uuid4())

    for child in dis.getchildren():
        syns = child.findall('.//Synonym')

        for syn in syns:
            synonym.append(syn.text)

        refs = child.findall('.//ExternalReference')
        for ref in refs:
            if ref.find('Source').text == 'OMIM':
                omim.append(ref.find('Reference').text)

    newData = {
        "orphaNumber": dis.find('OrphaNumber').text,
        "term": dis.find('Name').text,
        "type": dis.find('DisorderType/Name').text,
        "omimIds": omim,
        "synonyms": synonym,
        "active": True,
        "uuid": uuid
    }
    allData.append(newData)

    if len(omim) >0: omimNum += 1
    if len(omim) > 1: omimMulti += 1
    if len(synonym) > 0: synonymNum +=1
    if len(synonym) > 1: synonymMulti += 1

fo = open('orphaPhenotype.json', 'w')
fo.write(json.dumps(allData))

print len(disorders)
print omimNum
print synonymNum
print omimMulti
print synonymMulti
