from pyramid import paster
from pyelasticsearch import ElasticSearch, IndexAlreadyExistsError
from collections import OrderedDict

ES_URL = 'http://localhost:9200'
DOCTYPE = 'basic'
es = ElasticSearch(ES_URL)

app = paster.get_app('production.ini')
root = app.root_factory(app)

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
        self.properties = dict()

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
        self['properties'][v] = {'type': 'multi_field', 'fields': {v: {'type': 'string'}, 'untouched': {'type': 'string', 'index': 'not_analyzed'}}}

    def __setobjprop__(self, k, v):
        self['properties'][k] = v


def create_mapping(collection_name, embedded):
    mapping = Mapper()
    ignore_properties = ['attachment', 'schema_version', 'uuid', 'tags', 'flowcell_details']
    properties = root[collection_name].schema['properties']
    for p in properties:
        if p not in mapping['properties'] and p not in ignore_properties and p not in embedded:
            mapping.__setprop__(p)
    return mapping


def main():
    for collection_name in COLLECTION_URL:
        collection = root[collection_name]
        schema = collection.schema
        embedded = collection.Item.embedded
        rev_links = dict()
        try:
            rev_links = collection.Item.rev
        except:
            pass

        try:
            es.create_index(collection_name)
        except IndexAlreadyExistsError:
            es.delete_index(collection_name)
            es.create_index(collection_name)
        
        mapping = create_mapping(collection_name, embedded)
        if 'calculated_props' in schema:
            calculated_props = schema['calculated_props']
            for calculated_prop in calculated_props:
                mapping.__setprop__(calculated_prop)

        for prop in embedded:
            if '.' in prop:
                new_mpping = mapping
                new_schema = schema
                for p in prop.split('.'):
                    if rev_links:
                        if p in rev_links:
                            name = rev_links[p][0]
                        else:
                            try:
                                name = new_schema['properties'][p]['linkTo']
                            except:
                                name = new_schema['properties'][p]['items']['linkTo']
                    else:
                        try:
                            name = new_schema['properties'][p]['linkTo']
                        except:
                            name = new_schema['properties'][p]['items']['linkTo']
                    if name == 'donor':
                        name = 'human_donor'
                    if p in new_mpping['properties']:
                        n = new_mpping['properties'][p]
                        if 'type' not in n:
                            new_mpping = new_mpping['properties'][p]
                            new_schema = root[name].schema
                            continue
                    new_mpping['properties'][p] = create_mapping(name, [])
                    new_mpping = new_mpping['properties'][p]
                    new_schema = root[name].schema
            else:
                if rev_links:
                    if prop in rev_links:
                        name = rev_links[prop][0]
                        mapping['properties'][prop] = create_mapping(name, [])
                        continue
                name = ''
                try:
                    name = schema['properties'][prop]['linkTo']
                except:
                    name = schema['properties'][prop]['items']['linkTo']
                if name == 'donor':
                    name = 'human_donor'
                mapping['properties'][prop] = create_mapping(name, [])
        es.put_mapping(collection_name, DOCTYPE, {'basic': mapping})
        es.refresh(collection_name)

if __name__ == '__main__':
    main()
