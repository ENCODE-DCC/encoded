from pyramid import paster
from pyelasticsearch import ElasticSearch, IndexAlreadyExistsError
from collections import OrderedDict

ES_URL = 'http://localhost:9200'
DOCTYPE = 'basic'
es = ElasticSearch(ES_URL)

# Mapping will be moved to schemas eventually
basic_mapping = {'basic': {}}
libraries_mapping = {'basic': {'properties': {'size_range': {'type': 'string'}}}}
replicates_mapping = {'basic': {'properties': {'library': {'properties': {'size_range': {'type': 'string'}}}}}}
donors_mapping = {'basic': {'properties': {'age': {'type': 'string'}}}}

targets_mapping = {'basic': {'properties': {'lab': {'properties': {'title': {'type': 'string', 'index': 'not_analyzed'}}}, 'organism': {'properties': {'name': {'type': 'string', 'index': 'not_analyzed'}}}}}}
biosamples_mapping = {'basic': {'properties': {'source': {'properties': {'title': {'type': 'string', 'index': 'not_analyzed'}}}, 'lab': {'properties': {'title': {'type': 'string', 'index': 'not_analyzed'}}}, 'system_slims': {'type': 'string', 'index': 'not_analyzed'}, 'organ_slims': {'type': 'string', 'index': 'not_analyzed'}, 'biosample_type': {'type': 'string', 'index': 'not_analyzed'}, 'treatments': {'type': 'nested'}, 'constructs': {'type': 'nested'}}}}
experiments_mapping = {'basic': {'properties': {'assay_term_name': {'type': 'string', 'index': 'not_analyzed'}, 'target': {'properties': {'organism': {'properties': {'name': {'type': 'string', 'index': 'not_analyzed'}}}}}, 'files': {'type': 'nested', 'properties': {'replicate': {'properties': {'library': {'properties': {'size_range': {'type': 'string'}}}}}}}, 'lab': {'properties': {'title': {'type': 'string', 'index': 'not_analyzed'}}}, 'replicates': {'type': 'nested', 'properties': {'library': {'properties': {'size_range': {'type': 'string'}}}, 'library id (sanity)': {'type': 'string'}}}}}}
antibodies_mapping = {'basic': {'properties': {'target': {'properties': {'lab': {'properties': {'title': {'type': 'string', 'index': 'not_analyzed'}}}}}, 'antibody': {'properties': {'host_organism': {'properties': {'name': {'type': 'string', 'index': 'not_analyzed'}}}}}}}}

# Part of this will be moved to schemas and other part should be in a proper dict
COLLECTION_URL = OrderedDict([
    ('/users/', ['user', basic_mapping]),
    ('/awards/', ['award', basic_mapping]),
    ('/labs/', ['lab', basic_mapping]),
    ('/organisms/', ['organism', basic_mapping]),
    ('/sources/', ['source', basic_mapping]),
    ('/targets/', ['target', targets_mapping]),
    ('/antibody-lots/', ['antibody_lot', basic_mapping]),
    ('/antibody-characterizations/', ['antibody_characterization', basic_mapping]),
    ('/antibodies/', ['antibody_approval', antibodies_mapping]),
    ('/mouse-donors/', ['mouse_donor', donors_mapping]),
    ('/human-donors/', ['human_donor', donors_mapping]),
    ('/treatments/', ['treatment', basic_mapping]),
    ('/constructs/', ['construct', basic_mapping]),
    ('/construct-characterizations/', ['construct_characterization', basic_mapping]),
    ('/rnais/', ['rnai', basic_mapping]),
    ('/rnai-characterizations/', ['rnai_characterization', basic_mapping]),
    ('/biosamples/', ['biosample', biosamples_mapping]),
    ('/biosample-characterizations/', ['biosample_characterization', basic_mapping]),
    ('/platforms/', ['platform', basic_mapping]),
    ('/libraries/', ['library', basic_mapping]),
    ('/experiments/', ['experiment', experiments_mapping]),
    ('/replicates/', ['replicate', replicates_mapping])
])


def main():
    ''' Indexes app data loaded to th elasticsearch '''

    app = paster.get_app('production.ini')
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
        print "Indexing " + COLLECTION_URL.get(url)[0] + " ...."
        res = testapp.get(url + '?limit=all&collection_source=database', headers={'Accept': 'application/json'}, status=200)
        items = res.json['@graph']

        # try creating index, if it exists already delete it and create it again and generate mapping
        index = COLLECTION_URL.get(url)[0]
        try:
            es.create_index(index)
        except IndexAlreadyExistsError:
            es.delete_index(index)
            es.create_index(index)
        es.put_mapping(index, DOCTYPE, COLLECTION_URL.get(url)[1])

        counter = 0
        for item in items:
            item_json = testapp.get(str(item['@id']), headers={'Accept': 'application/json'}, status=200)
            document_id = str(item_json.json['@id'])[-37:-1]
            document = item_json.json

            # For biosamples getting organ_slim and system_slim from ontology index
            if COLLECTION_URL.get(url)[0] == 'biosample':
                if document['biosample_term_id']:
                    try:
                        document['organ_slims'] = (es.get('ontology', 'basic', document['biosample_term_id']))['_source']['organs']
                        document['system_slims'] = (es.get('ontology', 'basic', document['biosample_term_id']))['_source']['systems']
                    except:
                        document['organ_slims'] = []
                        document['system_slims'] = []
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
        print "Finished indexing " + str(count['count']) + " " + COLLECTION_URL.get(url)[0]
        print ""

if __name__ == '__main__':
    main()
