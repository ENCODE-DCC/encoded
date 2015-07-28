#! /users/bin/env Python

# Modified version of get_gene.py from ClinGen/LoadData. Creates JSON file with
# all 'active' HGNC Gene data for (initial) load into the server. Run this script
# before using this one:
#   obtain_external_data_files.py -s hgnc

import json
from uuid import uuid4

lineNum = 0
activeGene = 0
allData = []

# uuid mapping for previously existing entries to avoid validation errors
uuidMapping = {
    "FGFR3": "e7c51b8a-1c34-11e5-ab27-60f81dc5b05a",
    "RAD51C": "e265b19c-1c34-11e5-a27c-60f81dc5b05a",
    "DICER1": "da926a0a-1c34-11e5-b1eb-60f81dc5b05a",
    "SMAD3": "d474e1ab-1c34-11e5-b601-60f81dc5b05a",
    "AGTR2": "cade0ed4-1c34-11e5-b48e-60f81dc5b05a",
    "CD3E": "c46d1b4c-1c34-11e5-a0cc-60f81dc5b05a",
    "FANCM": "be87d21c-1c34-11e5-97f7-60f81dc5b05a",
    "NGLY1": "b728ee7a-1c34-11e5-9874-60f81dc5b05a",
    "BRCA1": "b0b8eae3-1c34-11e5-ac44-60f81dc5b05a",
    "EGFR": "a8ad0de1-1c34-11e5-8952-60f81dc5b05a",
    "MTBP": "a0221426-1c34-11e5-a98e-60f81dc5b05a",
    "PPM1D": "976c2251-1c34-11e5-aa54-60f81dc5b05a",
    "CUL9": "8fa4df11-1c34-11e5-8122-60f81dc5b05a",
    "TP63": "87abd005-1c34-11e5-ab22-60f81dc5b05a",
    "PIDD1": "7ee4bc4c-1c34-11e5-8550-60f81dc5b05a",
    "MDM4": "74064a68-1c34-11e5-b6ae-60f81dc5b05a",
    "CDIP1": "6dae8ba8-1c34-11e5-8d7f-60f81dc5b05a",
    "GSTM1": "65175499-1c34-11e5-a9ab-60f81dc5b05a",
    "JMY": "5f4c0c0c-1c34-11e5-9b11-60f81dc5b05a",
    "TP53": "59e9e6a6-1c34-11e5-bcda-60f81dc5b05a"
}


def safe_split(input):
    if input.startswith('"'):
        temp = input.strip('"')
    else:
        temp = input
    if temp.find('", "') != -1:
        output = temp.split('", "')
    else:
        if len(temp) > 0:
            output = [temp]
        else:
            output = []
    return output


def safe_split2(input):
    if input.find(',') != -1:
        output = input.split(', ')
    else:
        if len(input) > 0:
            output = [input]
        else:
            output = []
    return output

with open('rawData/gene.txt') as f:
    for line in f:
        if '\n' in line:
            line = line.strip('\n')
        colItem = line.split('\t')

        # only process if gene is approved
        if colItem[3] == "Approved":
            # previous symbol array
            presym = safe_split2(colItem[6])
            # previous name array
            prename = safe_split(colItem[7])
            #  synonym array (need '"' check??)
            syn = safe_split2(colItem[8])
            # name synonym array
            synname = safe_split(colItem[9])
            # pmid array
            pmids = safe_split2(colItem[13])
            # omim array
            omims = safe_split2(colItem[15])
            # locus type check
            if colItem[4] == 'unknown':
                locustype = ""
            else:
                locustype = colItem[4]
            # uuid check
            if colItem[1] in uuidMapping:
                uuid = uuidMapping[colItem[1]]
            else:
                uuid = str(uuid4())

            if lineNum > 0:
                newData = {
                    "symbol": colItem[1],
                    "hgncId": colItem[0],
                    "entrezId": colItem[14],
                    "name": colItem[2],
                    "hgncStatus": colItem[3],
                    "synonyms": syn,
                    "nameSynonyms": synname,
                    "previousSymbols": presym,
                    "previousNames": prename,
                    "chromosome": colItem[10],
                    "locusType": locustype,
                    "omimIds": omims,
                    "pmids": pmids,
                    "uuid": uuid
                }
                allData.append(newData)
                activeGene += 1
        lineNum += 1

fo = open('gene.json', 'w')
fo.write(json.dumps(allData))

print 'Approved genes: %d' % (activeGene)
print 'Total lines: %d' % (lineNum)
