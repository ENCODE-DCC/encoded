import pytest
import json
from csv import DictReader
from sqlalchemy.exc import IntegrityError

import encoded.commands.read_edw_fileinfo

import edw_test_data
import test_indexing

pytestmark = [pytest.mark.edw_sync]

# globals
EDW_FILE_TEST_DATA_DIR = 'src/encoded/tests/data/edw_file'

TEST_ACCESSION = 'ENCFF001RET'  # NOTE: must be in test set

@pytest.fixture(scope='session')
def app_settings(server_host_port, elasticsearch_server, connection):
    from .conftest import _app_settings
    settings = _app_settings.copy()
    settings['persona.audiences'] = 'http://%s:%s' % server_host_port
    settings['elasticsearch.server'] = elasticsearch_server
 #   settings['sqlalchemy.url'] = postgresql_server
    settings['collection_source'] = 'elasticsearch'
    return settings

#@pytest.fixture(scope='session')
#def app(request, app_settings):
    '''WSGI application level functional testing.
    '''
'''    from encoded.storage import DBSession

    DBSession.remove()
    DBSession.configure(bind=None)

    from encoded import main
    app = main({}, **app_settings)

    from encoded.commands import create_mapping
    create_mapping.run(app)
    res = app.post_json('/index', {})

    @request.addfinalizer
    def teardown_app():
        # Dispose connections so postgres can tear down
        DBSession.bind.pool.dispose()
        DBSession.remove()
        DBSession.configure(bind=None)

    return app
'''

@pytest.fixture
def testapp(app):
    from webtest import TestApp
    environ = {
        'HTTP_ACCEPT': 'application/json',
        'REMOTE_USER': 'TEST',
    }
    return TestApp(app, environ)


#@pytest.yield_fixture(scope='session')
@pytest.yield_fixture()
def workbook(connection, app, app_settings):
    from . import conftest
    from encoded.commands import es_index_data, create_mapping
    tx = connection.begin_nested()
    for fixture in conftest.workbook(connection, app, app_settings):
        print "SYNC: creating ES and indexing"
        create_mapping.run(app)
        es_index_data.run(app)
        yield fixture
    print 'SYNC: Rollback from sync workbook...'
    tx.rollback()

@pytest.yield_fixture()
def reset(connection, app):
    yield
    from encoded.commands import es_index_data, create_mapping
    print "SYNC: Resetting ES index"
    create_mapping.run(app)
    es_index_data.run(app)


def test_format_app_fileinfo_expanded(workbook, testapp):
    # Test extracting EDW-relevant fields from encoded file.json
    # Expanded JSON

    # load input
    url = '/files/' + TEST_ACCESSION

    resp = testapp.get(url).maybe_follow()
    file_dict = resp.json

    #fileinfo = encoded.commands.read_edw_fileinfo.format_app_fileinfo(testapp, file_dict)

    # compare results for identity with expected
    test_edwf = edw_test_data.format_app_file_out

    new_edw = encoded.commands.read_edw_fileinfo.convert_edw(testapp, test_edwf)
    assert( not encoded.commands.read_edw_fileinfo.compare_files(file_dict, test_edwf) )


def test_post_duplicate(workbook, testapp):
    url = '/files/' + TEST_ACCESSION
    resp = testapp.get(url).maybe_follow()
    current = resp.json
    try:
        illegal_post = testapp.post_json(url, current, expect_errors=True)
    except IntegrityError:
        ### This should throw a 409 for both sqllite and postgres
        assert(True)


def test_list_new(workbook, testapp):
    # Test obtaining list of 'new' accessions (at EDW, not at app)
    # Unexpanded JSON (requires GETs on embedded URLs)

    edw_accs = edw_test_data.new_in
    app_accs = encoded.commands.read_edw_fileinfo.get_app_fileinfo(testapp,
                                                                  full=False)
    new_accs = sorted(encoded.commands.read_edw_fileinfo.get_missing_filelist_from_lists(app_accs, edw_accs))
    assert new_accs == sorted(edw_test_data.new_out)


def test_import_file(workbook, testapp, reset):
    # Test import of new file to encoded
    # this tests adds replicates, but never checks their validity
    # ignoring this because I don't want to deal with tearing down ES  posts

    import re
    input_file = 'import_in.1.tsv'
    f = open(EDW_FILE_TEST_DATA_DIR + '/' + input_file)
    reader = DictReader(f, delimiter='\t')
    for fileinfo in reader:

        encoded.commands.read_edw_fileinfo.convert_edw(testapp, fileinfo)
        #set_in = set(fileinfo.items())
        resp = encoded.commands.read_edw_fileinfo.post_fileinfo(testapp, fileinfo)
        # exercises: set_fileinfo_experiment, set_fileinfo_replicate, POST
        if resp:
            acc = fileinfo['accession']
            url = encoded.commands.read_edw_fileinfo.collection_url(encoded.commands.read_edw_fileinfo.FILES) + acc
            get_resp = testapp.get(url).maybe_follow()
            file_dict = get_resp.json
            assert( not encoded.commands.read_edw_fileinfo.compare_files(file_dict, fileinfo) )
        else:
            ## one of the files in import_in.1.tsv is not postable
            ## should maybe switch it from an experiment to a regular dataset
            assert(re.search('experiments', fileinfo['dataset']))
            assert(not fileinfo['biological_replicate'] or not fileinfo['technical_replicate'])


def test_encode2_experiments(workbook, testapp):
    # Test obtaining list of ENCODE 2 experiments and identifying which ENCODE3
    # accessions are ENCODE2 experiments

    # Test identifying an ENCODE 3 experiment
    #res = testapp.post_json('/index', {})
    assert not encoded.commands.read_edw_fileinfo.is_encode2_experiment(testapp, edw_test_data.encode3)

    # Create hash of all ENCODE 2 experiments, map to ENCODE 3 accession
    encode2_hash = encoded.commands.read_edw_fileinfo.get_encode2_to_encode3(testapp)
    assert sorted(encode2_hash.keys()) == sorted(edw_test_data.encode2)

    # Test identifying an ENCODE 2 experiment
    assert encoded.commands.read_edw_fileinfo.is_encode2_experiment(testapp, encode2_hash.values()[0])

def test_file_sync(workbook, testapp, reset):

    mock_edw_file = 'edw_file_mock.tsv'
    f = open(EDW_FILE_TEST_DATA_DIR + '/' + mock_edw_file)
    reader = DictReader(f, delimiter='\t')

    edw_mock = {}
    for fileinfo in reader:
        encoded.commands.read_edw_fileinfo.convert_edw(testapp, fileinfo)
        del fileinfo['test']  # this is in the file for notation purposes only
        edw_mock[fileinfo['accession']] = fileinfo

    assert len(edw_mock) == 25

    app_files = encoded.commands.read_edw_fileinfo.get_app_fileinfo(testapp)
    app_dict = { d['accession']:d for d in app_files }
    assert len(app_files) == 24  ## just a place holder, could use TYPE_LENGTH from test_views.py
    # this is puzzling because it should not have the 2 from the previous test, should it?
    assert(len(app_files) == len(app_dict.keys())) # this should never duplicate

    edw_only, app_only, same, patch = encoded.commands.read_edw_fileinfo.inventory_files(testapp, edw_mock, app_dict)
    assert len(edw_only) == 12
    assert len(app_only) == 11
    assert len(same) == 6
    assert len(patch) == 7

    before_reps = { d['uuid']: d for d in testapp.get('/replicates/').maybe_follow().json['@graph'] }

    for add in edw_only:
        acc = add['accession']
        url = encoded.commands.read_edw_fileinfo.collection_url(encoded.commands.read_edw_fileinfo.FILES) + acc
        resp = encoded.commands.read_edw_fileinfo.post_fileinfo(testapp, add)
        # check experiment status
        if not resp:
            assert(add['dataset'] == 'ENCSR000AEO') # experiment does not exist in test database
        else:
            assert(resp.status_code == 201)

    ''' This fails due to bug #974 moved to distinct test case
    NOTE: Double posting on sqllite will NOT honor unique constraints!
    for ignore in same:
    # just try to do one duplicate for now.
        acc = ignore['accession']
        url = encoded.commands.read_edw_fileinfo.collection_url(encoded.commands.read_edw_fileinfo.FILES) + acc
        try:
           resp = encoded.commands.read_edw_fileinfo.post_fileinfo(testapp, ignore)
        except IntegrityError:
            assert(True)
    '''
    # Thought this should have thrown a 409... assert(resp.status_code == 409)

    for update in patch:
        diff = encoded.commands.read_edw_fileinfo.compare_files(app_dict[update], edw_mock[update])
        patched = encoded.commands.read_edw_fileinfo.patch_fileinfo(testapp, diff.keys(), edw_mock[update])
        should_fail = False
        for patch_prop in diff.keys():
            if patch_prop in encoded.commands.read_edw_fileinfo.NO_UPDATE:
                should_fail = True
        if should_fail:
            assert not patched
        else:
            assert patched

    # index new replicates
    from encoded.commands import es_index_data
    es_index_data.run(testapp.app, ['replicate', 'experiment', 'dataset'])

    post_app_files = encoded.commands.read_edw_fileinfo.get_app_fileinfo(testapp)
    post_app_dict = { d['accession']:d for d in post_app_files }
    assert(len(post_app_files) == len(post_app_dict.keys()))

    encoded.commands.read_edw_fileinfo.collections = []
    # reset global var!
    post_edw, post_app, post_same, post_patch= encoded.commands.read_edw_fileinfo.inventory_files(testapp, edw_mock, post_app_dict)
    assert len(post_edw) == 2 # new files cannot add
    assert len(post_app) == 11 # unchanged
    assert len(post_patch) == 4 # exsting files cannot be patched
    assert ((len(post_same)-len(same)) == (len(patch) -len(post_patch) + (len(edw_only) - len(post_edw))))
    assert len(post_app_files) == (len(app_files) + len(edw_only) - 2 )

    after_reps = { d['uuid']: d for d in testapp.get('/replicates/').maybe_follow().json['@graph'] }
    same_reps = {}
    updated_reps = {}
    new_reps = {}
    for uuid in after_reps.keys():
        if before_reps.has_key(uuid):
            bef = set([ x for x in before_reps[uuid].items() if type(x[1]) != list ])
            aft = set([ x for x in after_reps[uuid].items() if type(x[1]) != list ])
            rep_diff = aft - bef
            if(rep_diff):
                updated_reps[uuid] = rep_diff
            else:
                same_reps[uuid] = True
        else:
            new_reps['uuid'] = after_reps[uuid]

    assert(len(same_reps.keys()) == 17)
    assert(not updated_reps)
    assert(len(new_reps) == 1)











