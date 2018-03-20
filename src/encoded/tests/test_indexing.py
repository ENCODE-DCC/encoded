""" Test full indexing setup

The fixtures in this module setup a full system with postgresql and
elasticsearch running as subprocesses.
"""

import pytest

pytestmark = [pytest.mark.indexing]


@pytest.fixture(scope='session')
def app_settings(wsgi_server_host_port, elasticsearch_server, postgresql_server):
    from .conftest import _app_settings
    settings = _app_settings.copy()
    settings['create_tables'] = True
    settings['persona.audiences'] = 'http://%s:%s' % wsgi_server_host_port
    settings['elasticsearch.server'] = elasticsearch_server
    settings['snp_search.server'] = elasticsearch_server  # NOTE: tfrom snovault/serverfixtures.py  Need a region_es version?
    settings['sqlalchemy.url'] = postgresql_server
    settings['collection_datastore'] = 'elasticsearch'
    settings['item_datastore'] = 'elasticsearch'
    settings['indexer'] = True
    settings['indexer.processes'] = 2
    return settings


@pytest.yield_fixture(scope='session')
def app(app_settings):
    from encoded import main
    app = main({}, **app_settings)

    yield app

    # Shutdown multiprocessing pool to close db conns.
    from snovault.elasticsearch import INDEXER
    app.registry[INDEXER].shutdown()

    from snovault import DBSESSION
    DBSession = app.registry[DBSESSION]
    # Dispose connections so postgres can tear down.
    DBSession.bind.pool.dispose()


@pytest.fixture(scope='session')
def DBSession(app):
    from snovault import DBSESSION
    return app.registry[DBSESSION]


@pytest.fixture(autouse=True)
def teardown(app, dbapi_conn):
    from snovault.elasticsearch import create_mapping
    create_mapping.run(app)
    cursor = dbapi_conn.cursor()
    cursor.execute("""TRUNCATE resources, transactions CASCADE;""")
    cursor.close()


@pytest.fixture
def external_tx():
    pass


@pytest.yield_fixture
def dbapi_conn(DBSession):
    connection = DBSession.bind.pool.unique_connection()
    connection.detach()
    conn = connection.connection
    conn.autocommit = True
    yield conn
    conn.close()


@pytest.yield_fixture
def listening_conn(dbapi_conn):
    cursor = dbapi_conn.cursor()
    cursor.execute("""LISTEN "snovault.transaction";""")
    yield dbapi_conn
    cursor.close()


@pytest.mark.slow
def test_indexing_workbook(testapp, indexer_testapp):
    # First post a single item so that subsequent indexing is incremental
    testapp.post_json('/testing-post-put-patch/', {'required': ''})
    res = indexer_testapp.post_json('/index', {'record': True})
    assert res.json['indexed'] == 1

    import time
    from ..loadxl import load_all
    from pkg_resources import resource_filename
    inserts = resource_filename('encoded', 'tests/data/inserts/')
    docsdir = [resource_filename('encoded', 'tests/data/documents/')]
    load_all(testapp, inserts, docsdir)
    res = indexer_testapp.post_json('/index', {'record': True})
    assert res.json['updated']
    assert res.json['indexed']

    # NOTE: Both vis and region indexers are "followup" or secondary indexers
    #       and must be staged by the primary indexer
    res = indexer_testapp.post_json('/index_vis', {'record': True})
    assert res.json['cycle_took']
    assert res.json['title'] == 'vis_indexer'

    res = indexer_testapp.post_json('/index_region', {'record': True})
    assert res.json['cycle_took']
    assert res.json['title'] == 'region_indexer'
    assert res.json['indexed'] > 0

    # primary indexer contents
    res = testapp.get('/search/?type=Biosample')
    assert res.json['total'] > 5

    # vis indexer contents
    res = testapp.get('/batch_hub/type%3DExperiment/hg19/trackDb.json')
    # trackDb.json currently returns text/plain
    #import json
    #content = json.loads(res.text)
    #assert content['ChIP']['view']['groups']['aOIDR']['type'] == 'bigNarrowPeak'
    #assert content['tkRNA']['vis_id'] == 'ENCSR000AEN_hg19'
    assert res.json['ChIP']['view']['groups']['aOIDR']['type'] == 'bigNarrowPeak'
    assert res.json['tkRNA']['vis_id'] == 'ENCSR000AEN_hg19'

    # region indexer contents via region_search
    time.sleep(1)  # For some reason this fails without some winks
    res = testapp.get('/region-search/?region=chr13%3A61800000-78800000&genome=GRCh37')
    assert res.json['total'] == 1
    assert res.json['visualize_batch']['hg19']['UCSC']


def test_indexing_simple(testapp, indexer_testapp):
    import time
    # First post a single item so that subsequent indexing is incremental
    testapp.post_json('/testing-post-put-patch/', {'required': ''})
    res = indexer_testapp.post_json('/index', {'record': True})
    assert res.json['indexed'] == 1
    res = testapp.post_json('/testing-post-put-patch/', {'required': ''})
    uuid = res.json['@graph'][0]['uuid']
    res = indexer_testapp.post_json('/index', {'record': True})
    assert res.json['indexed'] == 1
    assert res.json['txn_count'] == 1
    assert res.json['updated'] == [uuid]
    res = testapp.get('/search/?type=TestingPostPutPatch')
    uuids = [indv_res['uuid'] for indv_res in res.json['@graph'] if 'uuid' in indv_res]
    count = 0
    while uuid not in uuids and count < 20:
        time.sleep(1)
        res = testapp.get('/search/?type=TestingPostPutPatch')
        uuids = [indv_res['uuid'] for indv_res in res.json['@graph'] if 'uuid' in indv_res]
        count += 1
    assert res.json['total'] == 3


def test_indexer_vis_state(dummy_request):
    from encoded.vis_indexer import VisIndexerState
    INDEX = dummy_request.registry.settings['snovault.elasticsearch.index']
    es = dummy_request.registry['elasticsearch']
    state = VisIndexerState(es,INDEX)
    result = state.get_initial_state()
    assert result['title'] == 'vis_indexer'
    result = state.start_cycle(['1','2','3'], result)
    assert result['cycle_count'] == 3
    assert result['status'] == 'indexing'
    cycles = result.get('cycles',0)
    result = state.finish_cycle(result, [])
    assert result['cycles'] == (cycles + 1)
    assert result['status'] == 'done'


def test_indexer_region_state(dummy_request):
    from encoded.region_indexer import RegionIndexerState
    INDEX = dummy_request.registry.settings['snovault.elasticsearch.index']
    es = dummy_request.registry['elasticsearch']
    state = RegionIndexerState(es,INDEX)
    result = state.get_initial_state()
    assert result['title'] == 'region_indexer'
    assert result['status'] == 'idle'
    display = state.display()
    assert 'files_added' in display
    assert 'files_dropped' in display


def test_listening(testapp, listening_conn):
    import time
    testapp.post_json('/testing-post-put-patch/', {'required': ''})
    time.sleep(1)
    listening_conn.poll()
    assert len(listening_conn.notifies) == 1
    notify = listening_conn.notifies.pop()
    assert notify.channel == 'snovault.transaction'
    assert int(notify.payload) > 0
