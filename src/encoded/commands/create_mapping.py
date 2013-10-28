from pyramid import paster
from pyelasticsearch import ElasticSearch, IndexAlreadyExistsError

ES_URL = 'http://localhost:9200'
DOCTYPE = 'basic'
es = ElasticSearch(ES_URL)


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
    collections = root.by_item_type.keys()

    for collection_name in collections:
        print collection_name
        collection = root[collection_name]
        schema = collection.schema
        embedded = collection.Item.embedded

        mapping = Mapper()
        import pdb; pdb.set_trace();
        for prop in schema['properties']:
            if prop in embedded:
                try:
                    schema['properties'][prop]['items']['linkTo']
                except:
                    pass
                else:
                    pass
            else:
                mapping.__setprop__(prop)

        try:
            es.create_index(collection_name)
        except IndexAlreadyExistsError:
            es.delete_index(collection_name)
            es.create_index(collection_name)
        es.put_mapping(collection_name, DOCTYPE, mapping)
        es.refresh(collection_name)

if __name__ == '__main__':
    main()
