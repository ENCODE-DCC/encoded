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


# Should be refactored a bit n remove lots of hard coded props
# TODO: For now ignores arrays. Should come up with a solution
def update_mapping(index):
    ''' Update the mapping for each index '''
    
    mapping = es.get_mapping(index)
    new_mapping = {'basic': {'properties': {}}}
    if mapping[index]:
        for prop in mapping[index]['basic']['properties']:
            # Default fields are ignored here
            if prop not in ['@id', '@type', 'uuid', 'accession', 'schema_version', 'actions', 'attachment', 'documents', 'possible_controls', 'tags', 'protocol_documents', 'flowcell_details']:
                if type(mapping[index]['basic']['properties'][prop]) is dict:
                    if 'type' in mapping[index]['basic']['properties'][prop]:
                        new_mapping['basic']['properties'][prop] = {'type': 'multi_field', 'fields': {prop: {'type': 'string'}, 'untouched': {'type': 'string', 'index': 'not_analyzed'}}}
                    else:
                        # edge cases
                        if prop == 'host_organism':
                            new_mapping['basic']['properties'][prop] = es.get_mapping('organism')['organism']['basic']
                        elif prop == 'submitted_by':
                            new_mapping['basic']['properties'][prop] = es.get_mapping('user')['user']['basic']
                        elif prop == 'characterizations':
                            new_mapping['basic']['properties'][prop] = es.get_mapping('antibody_characterization')['antibody_characterization']['basic']
                        elif prop == 'antibody':
                            new_mapping['basic']['properties'][prop] = es.get_mapping('antibody_lot')['antibody_lot']['basic']
                        elif prop == 'rnais':
                            new_mapping['basic']['properties'][prop] = es.get_mapping('rnai')['rnai']['basic']
                        elif prop == 'donor':
                            new_mapping['basic']['properties'][prop] = es.get_mapping('mouse_donor')['mouse_donor']['basic']
                            new_mapping['basic']['properties'][prop]['properties']['ethinicity'] = {'type': 'multi_field', 'fields': {'ethinicity': {'type': 'string'}, 'untouched': {'type': 'string', 'index': 'not_analyzed'}}}
                        elif prop == 'pooled_from' or prop == 'derived_from':
                            new_mapping['basic']['properties'][prop] = es.get_mapping('biosample')['biosample']['basic']
                        elif prop == 'constructs':
                            new_mapping['basic']['properties'][prop] = es.get_mapping('construct')['construct']['basic']
                        elif prop == 'treatments':
                            new_mapping['basic']['properties'][prop] = es.get_mapping('treatment')['treatment']['basic']
                        elif prop == 'replicates':
                            new_mapping['basic']['properties'][prop] = es.get_mapping('replicate')['replicate']['basic']
                        elif prop == 'files':
                            new_mapping['basic']['properties'][prop] = es.get_mapping('file')['file']['basic']
                        else:
                            new_mapping['basic']['properties'][prop] = es.get_mapping(prop)[prop]['basic']
    es.put_mapping(index, DOCTYPE, new_mapping)


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
        print "Indexing " + url + " collection!"
        res = testapp.get(COLLECTION_URL[url] + '?limit=all&collection_source=database', headers={'Accept': 'application/json'}, status=200)
        items = res.json['@graph']

        # try creating index, if it exists already delete it and create it
        index = url
        try:
            es.create_index(index)
        except IndexAlreadyExistsError:
            es.delete_index(index)
            es.create_index(index)

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
                if index == 'biosample' or index == 'experiment':
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
        print "Finished indexing " + str(count['count']) + " " + index
        print "Updating the mapping ..."
        update_mapping(index)
        print ""

if __name__ == '__main__':
    main()
