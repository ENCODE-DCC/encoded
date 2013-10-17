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
experiments_mapping = {'basic': {'properties': {'system_slims': {'type': 'string', 'index': 'not_analyzed'}, 'organ_slims': {'type': 'string', 'index': 'not_analyzed'}, 'assay_term_name': {'type': 'string', 'index': 'not_analyzed'}, 'target': {'properties': {'organism': {'properties': {'name': {'type': 'string', 'index': 'not_analyzed'}}}}}, 'files': {'type': 'nested', 'properties': {'replicate': {'properties': {'library': {'properties': {'size_range': {'type': 'string'}}}}}}}, 'lab': {'properties': {'title': {'type': 'string', 'index': 'not_analyzed'}}}, 'replicates': {'type': 'nested', 'properties': {'library': {'properties': {'size_range': {'type': 'string'}}}, 'library id (sanity)': {'type': 'string'}}}}}}
antibodies_mapping = {'basic': {'properties': {'lab': {'properties': {'title': {'type': 'string', 'index': 'not_analyzed'}}}, 'target': {'properties': {'lab': {'properties': {'title': {'type': 'string', 'index': 'not_analyzed'}}}}}, 'antibody': {'properties': {'host_organism': {'properties': {'name': {'type': 'string', 'index': 'not_analyzed'}}}}}}}}

# Part of this will be moved to schemas and other part should be in a proper dict
COLLECTION_URL = OrderedDict([
    ('/users/', ['user', basic_mapping]),
    ('/access-keys/', ['access_key', basic_mapping]),
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
    ('/documents/', ['document', basic_mapping]),
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
    ('/replicates/', ['replicate', replicates_mapping]),
    ('/files/', ['file', basic_mapping]),
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
            pass
        else:
            es.put_mapping(index, DOCTYPE, COLLECTION_URL.get(url)[1])

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
                if COLLECTION_URL.get(url)[0] == 'biosample' or COLLECTION_URL.get(url)[0] == 'experiment':
                    try:
                        if document['biosample_term_id']:
                            document['organ_slims'] = (es.get('ontology', 'basic', document['biosample_term_id']))['_source']['organs']
                            document['system_slims'] = (es.get('ontology', 'basic', document['biosample_term_id']))['_source']['systems']
                            document['developmental_slims'] = (es.get('ontology', 'basic', document['biosample_term_id']))['_source']['developmental']
                        else:
                            document['organ_slims'] = []
                            document['system_slims'] = []
                            document['developmental_slims'] = []
                    except:
                        document['organ_slims'] = []
                        document['system_slims'] = []
                        document['developmental_slims'] = []

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
