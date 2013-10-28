from pyramid import paster
from pyelasticsearch import ElasticSearch
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
        counter = 0
        for item in items:
            try:
                item_json = testapp.get(str(item['@id']), headers={'Accept': 'application/json'}, status=200)
            except Exception as e:
                print e
            else:
                document_id = str(item_json.json['uuid'])
                document = item_json.json
                es.index(index, DOCTYPE, document, document_id)
                counter = counter + 1
                if counter % 50 == 0:
                    es.flush(index)

        es.refresh(index)
        count = es.count('*:*', index=index)
        print "Finished indexing " + str(count['count']) + " " + url
        print

if __name__ == '__main__':
    main()
