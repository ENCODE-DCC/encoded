import json
from pyramid import paster
from pyelasticsearch import ElasticSearch, IndexAlreadyExistsError
from collections import OrderedDict

ES_URL = 'http://localhost:9200'
DOCTYPE = 'basic'
es = ElasticSearch(ES_URL)


# Part of this will be moved to schemas and other part should be in a proper dict
COLLECTION_URL = OrderedDict([
    ('user', '/users/'),
    ('access_key', '/access-keys/'),
    ('award', '/awards/'),
    ('lab', '/labs/'),
    ('organism', '/organisms/'),
    ('source', '/sources/'),
    ('target', '/targets/'),
    ('antibody_lot', '/antibody-lots/'),
    ('antibody_characterization', '/antibody-characterizations/'),
    ('antibody_approval', '/antibodies/'),
    ('mouse_donor', '/mouse-donors/'),
    ('human_donor', '/human-donors/'),
    ('treatment', '/treatments/'),
    ('construct', '/constructs/'),
    ('construct_characterization', '/construct-characterizations/'),
    ('rnai', '/rnais/'),
    ('rnai_characterization', '/rnai-characterizations/'),
    ('biosample', '/biosamples/'),
    ('biosample_characterization', '/biosample-characterizations/'),
    ('platform', '/platforms/'),
    ('library', '/libraries/'),
    ('replicate', '/replicates/'),
    ('file', '/files/'),
    ('experiment', '/experiments/')
])


class Mapper(dict):

    def __init__(self):
        self.basic = dict({'properties': {}})

    def __setattr__(self, k, v):
        if k in self.keys():
            self[k] = v
        elif not hasattr(self, k):
            self[k] = v
        else:
            raise AttributeError("Cannot set '%s', cls attribute already exists" % (k, ))

    def __getattr__(self, k):
        if k in self.keys():
            return self[k]
        raise AttributeError

    def __setprop__(self, v):
        self['basic']['properties'][v] = {'type': 'multi_field', 'fields': {v: {'type': 'string'}, 'untouched': {'type': 'string', 'index': 'not_analyzed'}}}

    def __setobjprop__(self, k, v):
        self['basic']['properties'][k] = v


def main():
    app = paster.get_app('production.ini')
    from webtest import TestApp
    environ = {
        'HTTP_ACCEPT': 'application/json',
        'REMOTE_USER': 'IMPORT',
    }
    testapp = TestApp(app, environ)

    for url in COLLECTION_URL:
        res = testapp.get('/profiles/' + url + '.json?format=json', headers={'Accept': 'application/json'}, status=200)
        schema = json.loads(res._app_iter[0])
        mapping = Mapper()
        for prop in schema['properties']:
            try:
                schema['properties'][prop]['linkTo']
            except:
                try:
                    schema['properties'][prop]['items']['linkTo']
                except:
                    mapping.__setprop__(prop)
                else:
                    try:
                        inner_mapping = es.get_mapping(schema['properties'][prop]['items']['linkTo'])
                    except:
                        pass
                    else:
                        mapping.__setobjprop__(prop, inner_mapping[schema['properties'][prop]['items']['linkTo']]['basic'])
            else:
                if prop != 'schema_version':
                    if type(schema['properties'][prop]['linkTo']) is list:
                        pass
                    else:
                        try:
                            inner_mapping = es.get_mapping(schema['properties'][prop]['linkTo'])
                        except:
                            
                        else:
                            mapping.__setobjprop__(prop, inner_mapping[schema['properties'][prop]['linkTo']]['basic'])
        try:
            es.create_index(url)
        except IndexAlreadyExistsError:
            es.delete_index(url)
            es.create_index(url)
        es.put_mapping(url, DOCTYPE, mapping)
        es.refresh(url)

if __name__ == '__main__':
    main()
