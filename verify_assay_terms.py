import json
from importlib.machinery import SourceFileLoader

assay_data = SourceFileLoader('module.name', 'src/encoded/types/assay_data.py').load_module()
assay_terms = assay_data.assay_terms
ontology_file = json.load(open('ontology.json'))

verified_assays = []
incorrect_assays = []

for assay in assay_terms.keys():
    name_from_assay_data = assay
    id_from_assay_data = assay_terms[assay]
    name_from_ontology_json = ontology_file[id_from_assay_data]['name']
    preferred_name_from_ontology = ontology_file[id_from_assay_data]['preferred_name']
    synonyms_from_ontology = ontology_file[id_from_assay_data]['synonyms']

    if name_from_assay_data == name_from_ontology_json or name_from_assay_data == preferred_name_from_ontology or name_from_assay_data in synonyms_from_ontology:
        verified_assays.append(name_from_assay_data)
    else:
        incorrect_assays.append(name_from_assay_data)
        print("ERROR: " + name_from_assay_data + ' is paired with ' + id_from_assay_data + ' but ' + id_from_assay_data + '=[name:' + name_from_ontology_json + ',preferred_name:' + preferred_name_from_ontology + ',synonyms:' + str(synonyms_from_ontology) + ']')

total_assay_count = len(assay_terms.keys())
total_verified_assay_count = len(verified_assays)

print(str(total_verified_assay_count) + ' out of ' + str(total_assay_count) + ' assays verified')

if total_assay_count == total_verified_assay_count:
    print("GOOD TO GO")
else:
    print("NEED FIXES:" + str(incorrect_assays))
