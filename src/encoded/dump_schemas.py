from collections import OrderedDict
import json
import requests
import sys


BASE_URL = "http://localhost:6543"
TYPE_URL = {
    'organism': '/organisms/',
    'source': '/sources/',
    'target': '/targets/',
    'antibody_lot': '/antibody-lots/',
    'validation': '/validations/',
    'antibody_approval': '/antibodies/',
#    'user': '/users/',
    'lab': '/labs/',
    'award': '/awards/',
    'donor': '/donors/',
    'document': '/documents/',
    'treatment': '/treatments/',
    'construct': '/constructs/',
    'biosample': '/biosamples/',
    'platform': '/platforms/',
    'library': '/libraries/',
    'replicate': '/replicates/',
    'file': '/files/',
    'assay': '/assays/',
    'experiment': '/experiments/',
}

SKIP = ['_embedded', '_links', 'accession', '_uuid']

outdir = 'src/encoded/schemas/'
json_heads = {'Accept': 'application/json'}

json_format = {
    'sort_keys': True,
    'indent': 4,
    'separators': (',', ': '),
}


def basic_schema(value, null_type='string', template=None, nullable=all,
                 _key=None):

    # recursing paramaters
    params = locals().copy()
    del params['value']
    del params['_key']

    if template is None:
        template = OrderedDict([
            ('title', ''),
            ('description', ''),
            ('default', None),
        ])

    def templated(data):
        out = template.copy()
        out.update(data)
        if nullable is all or _key in nullable:
            if isinstance(out['type'], basestring):
                out['type'] = [out['type']]
            if 'null' not in out['type']:
                out['type'].append('null')
        return out

    if value is None:
        return templated({'type': null_type})
    elif isinstance(value, basestring):
        return templated({'type': 'string'})
    elif isinstance(value, bool):
        return templated({'type': 'boolean'})
    elif isinstance(value, int):
        return templated({'type': 'integer'})
    elif isinstance(value, float):
        return templated({'type': 'number'})
    elif isinstance(value, dict):
        key_prefix = _key + '.' if _key else ''
        properties = OrderedDict(
            (k, basic_schema(v, _key=(key_prefix + k), **params))
            for k, v in sorted(value.items()))
        return templated({
            'type': 'object',
            'properties': properties,
        })
    elif isinstance(value, list):
        _key = _key + '[]' if _key else '[]'
        if value:
            item = value[0]
        else:
            item = None
        return templated({
            'type': 'array',
            'items': basic_schema(item, _key=_key, **params),
        })
    else:
        raise ValueError(value)



for item in TYPE_URL.keys():
    fn = outdir + item + ".json"
    collection_r = requests.get(BASE_URL + TYPE_URL[item], headers=json_heads)
    try:
        assert collection_r.ok
    except:
        import pdb;pdb.set_trace()
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
