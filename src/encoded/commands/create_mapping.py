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
    ('document', '/documents/'),
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
    root = app.root_factory(app)
    ignore_properties = ['attachment', 'schema_version', 'uuid', 'tags', 'flowcell_details']

    for collection_name in COLLECTION_URL:
        collection = root[collection_name]
        schema = collection.schema
        embedded = collection.Item.embedded

        try:
            es.create_index(collection_name)
        except IndexAlreadyExistsError:
            es.delete_index(collection_name)
            es.create_index(collection_name)
        
        mapping = Mapper()
        if 'calculated_props' in schema:
            calculated_props = schema['calculated_props']
            for calculated_prop in calculated_props:
                mapping.__setprop__(calculated_prop)

        for prop in schema['properties']:
            if prop not in ignore_properties:
                if prop in embedded:
                    try:
                        inner_object = schema['properties'][prop]['linkTo']
                    except:
                        inner_object = schema['properties'][prop]['items']['linkTo']
                    # Handling donors edge case here
                    if inner_object == 'donor':
                        inner_object = 'human_donor'
                    # If they are embedding same object
                    if inner_object != collection_name:
                        mapping.__setobjprop__(prop, es.get_mapping(inner_object)[inner_object]['basic'])
                else:
                    mapping.__setprop__(prop)
        es.put_mapping(collection_name, DOCTYPE, mapping)
        es.refresh(collection_name)

if __name__ == '__main__':
    main()
