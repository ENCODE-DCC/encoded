from pyramid import paster
from pyelasticsearch import ElasticSearch

ES_URL = 'http://localhost:9200'
DOCTYPE = 'basic'
es = ElasticSearch(ES_URL)

app = paster.get_app('production.ini')
root = app.root_factory(app)
collections = root.by_item_type.keys()


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

    for collection_name in collections:
        print "Indexing " + root.by_item_type[collection_name].__name__ + " collection!"
        res = testapp.get('/' + root.by_item_type[collection_name].__name__ + '/' + '?limit=all&collection_source=database', headers={'Accept': 'application/json'}, status=200)
        items = res.json['@graph']

        # try creating index, if it exists already delete it and create it
        counter = 0
        for item in items:
            try:
                item_json = testapp.get(str(item['@id']), headers={'Accept': 'application/json'}, status=200)
            except Exception as e:
                print e
            else:
                document_id = str(item_json.json['uuid'])
                document = item_json.json
                es.index(collection_name, DOCTYPE, document, document_id)
                counter = counter + 1
                if counter % 50 == 0:
                    es.flush(collection_name)

        es.refresh(collection_name)
        count = es.count('*:*', index=collection_name)
        print "Finished indexing " + str(count['count']) + " " + root.by_item_type[collection_name].__name__
        print

if __name__ == '__main__':
    main()
