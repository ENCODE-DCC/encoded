from pyramid import paster
from pyelasticsearch import ElasticSearch, IndexAlreadyExistsError
from collections import OrderedDict
from ..schema_utils import (
    load_schema,
)

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
    ('experiment', '/experiments/'),
    ('replicate', '/replicates/'),
    ('file', '/files/')
])


def generate_mapping(index):
    ''' Generates ElasticSearch mapping for each index '''

    schema = load_schema(index + '.json')
    mapping = dict({'basic': {}})
    try:
        facets = schema['facets']
    except:
        pass
    else:
        for facet in facets:
            print facet
    return mapping


def main():
    ''' Indexes app data loaded to th elasticsearch '''

    app = paster.get_app('dev-masterdata.ini')
    from webtest import TestApp
    environ = {
        'HTTP_ACCEPT': 'application/json',
        'REMOTE_USER': 'IMPORT',
    }
    testapp = TestApp(app, environ)

    print
    print "*******************************************************************"
    print
    print "Indexing ENCODE Data in Elastic Search"
    print

    for url in COLLECTION_URL:
        print "Indexing " + url + " ...."
        res = testapp.get(COLLECTION_URL[url] + '?limit=all&collection_source=database', headers={'Accept': 'application/json'}, status=200)
        items = res.json['@graph']

        # try creating index, if it exists already delete it and create it again and generate mapping
        index = url
        try:
            es.create_index(index)
        except IndexAlreadyExistsError:
            pass
        else:
            es.put_mapping(index, DOCTYPE, generate_mapping(index))
        
        counter = 0
        for item in items:
            try:
                item_json = testapp.get(str(item['@id']), headers={'Accept': 'application/json'}, status=200)
            except Exception as e:
                print e
            else:
                document_id = str(item_json.json['uuid'])
                document = item_json.json

                # For biosamples getting organ_slim and system_slim from ontology index
                if url == 'biosample':
                    if document['biosample_term_id']:
                        try:
                            document['organ_slims'] = (es.get('ontology', 'basic', document['biosample_term_id']))['_source']['organs']
                            document['system_slims'] = (es.get('ontology', 'basic', document['biosample_term_id']))['_source']['systems']
                            document['developmental_slims'] = (es.get('ontology', 'basic', document['biosample_term_id']))['_source']['developmental']
                        except:
                            document['organ_slims'] = []
                            document['system_slims'] = []
                            document['developmental_slims'] = []
                            print "ID not found - " + document['biosample_term_id']
                    else:
                        document['organ_slims'] = []
                        document['system_slims'] = []
                es.index(index, DOCTYPE, document, document_id)
                counter = counter + 1
                if counter % 50 == 0:
                    es.flush(index)

        es.refresh(index)
        count = es.count('*:*', index=index)
        print "Finished indexing " + str(count['count'])
        print ""

if __name__ == '__main__':
    main()
