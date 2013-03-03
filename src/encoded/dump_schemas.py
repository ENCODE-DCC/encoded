import json
import requests
import sys
from encoded.schema_utils import basic_schema


BASE_URL = "http://localhost:6543"
'''TYPE_URL = {
    'organism': '/organisms/',
    'source': '/sources/',
    'target': '/targets/',
    'antibody_lot': '/antibody-lots/',
    'validation': '/validations/',
    'antibody_approval': '/antibodies/',
}'''
TYPE_URL = {
    'colleague': '/users/',
    'lab': '/labs/',
    'award': '/awards/',
    ##{ 'institute': '/institutes/'),
}

SKIP = ['_embedded', '_links']

outdir = 'src/encoded/schemas/'
json_heads = {'Accept': 'application/json'}

json_format = {
    'sort_keys': True,
    'indent': 4,
    'separators': (',', ': '),
}

for item in TYPE_URL.keys():
    fn = outdir + item + ".json"
    collection_r = requests.get(BASE_URL + TYPE_URL[item], headers=json_heads)
    assert collection_r.ok
    i_url = collection_r.json()['_embedded']['resources'].keys()[0]
    individual_r = requests.get(BASE_URL + i_url, headers=json_heads)
    assert individual_r.ok
    individual = individual_r.json()

    for key in SKIP:
        try:
            del individual[key]
        except KeyError:
            pass

    try:
        fh = open(fn, "w")
    except:
        sys.stdout.write("Could not open %s\n" % fn)
        continue

    fh.write(json.dumps(basic_schema(individual),
                        sort_keys=json_format['sort_keys'],
                        indent=json_format['indent'],
                        separators=json_format['separators'],
                        )
    )
    fh.close()
