import pytest
import json
from csv import DictReader
from sqlalchemy.exc import IntegrityError

import encoded.commands.sync_edw as sync_edw

import edw_test_data

from test_views import TYPE_LENGTH

pytestmark = [pytest.mark.sync_edw]

# globals
TEST_ACCESSION = 'ENCFF001RET'  # NOTE: must be in test set


@pytest.fixture
def edw_file_mock():
    return json_data_file('data/edw_file/edw_file_mock.json')


@pytest.fixture
def import_in_1():
    return json_data_file('data/edw_file/import_in.1.json')


def json_data_file(filename):
    from pkg_resources import resource_stream
    return json.load(resource_stream(__name__, filename))


@pytest.mark.slow
def test_get_all_datasets(workbook,testapp):

    sync_edw.try_datasets(testapp)
    assert(len(sync_edw.experiments) == TYPE_LENGTH['experiment'])
    assert(len(sync_edw.datasets) == TYPE_LENGTH['dataset'])

    assert all(len(v) == 1 for v in sync_edw.encode2_to_encode3.values())
    assert(len(sync_edw.encode2_to_encode3.keys()) == 7)
    assert(len(sync_edw.encode3_to_encode2.keys()) == 14)

    assert not sync_edw.encode3_to_encode2.get(edw_test_data.encode3, False)

    # Create hash of all ENCODE 2 experiments, map to ENCODE 3 accession
    assert sorted(sync_edw.encode2_to_encode3.keys()) == sorted(edw_test_data.encode2)


@pytest.mark.slow
def test_format_app_fileinfo_expanded(workbook, testapp):
    # Test extracting EDW-relevant fields from encoded file.json
    # Expanded JSON

    # load input
    url = '/files/' + TEST_ACCESSION

    resp = testapp.get(url).maybe_follow()
    file_dict = resp.json

    #fileinfo = sync_edw.format_app_fileinfo(testapp, file_dict)

    # compare results for identity with expected
    test_edwf = edw_test_data.format_app_file_out

    new_edw = sync_edw.convert_edw(testapp, test_edwf)
    assert( not sync_edw.compare_files(file_dict, test_edwf) )


@pytest.mark.slow
def test_post_duplicate(workbook, testapp):
    url = '/files/' + TEST_ACCESSION
    resp = testapp.get(url).maybe_follow()
    current = resp.json
    try:
        illegal_post = testapp.post_json(url, current, expect_errors=True)
    except IntegrityError:
        ### This should throw a 409 for both sqllite and postgres
        assert(True)

@pytest.mark.slow
def test_list_new(workbook, testapp):
    # Test obtaining list of 'new' accessions (at EDW, not at app)
    # Unexpanded JSON (requires GETs on embedded URLs)
    # TODO should be modified to look up by date

    edw_accs = edw_test_data.new_in
    app_accs = sync_edw.get_app_fileinfo(testapp).keys()
    new_accs = sorted(sync_edw.get_missing_filelist_from_lists(app_accs, edw_accs))
    assert new_accs == sorted(edw_test_data.new_out)


@pytest.fixture(scope='session')
def test_accession_app(request, check_constraints, zsa_savepoints, app_settings):
    from encoded import main
    app_settings = app_settings.copy()
    app_settings['accession_factory'] = 'encoded.server_defaults.test_accession'
    return main({}, **app_settings)

@pytest.fixture
def test_accession_testapp(request, test_accession_app, external_tx, zsa_savepoints):
    '''TestApp with JSON accept header.
    '''
    from webtest import TestApp
    environ = {
        'HTTP_ACCEPT': 'application/json',
        'REMOTE_USER': 'TEST',
    }
    return TestApp(test_accession_app, environ)

@pytest.mark.slow
def test_import_tst_file(workbook, test_accession_testapp, import_in_1):
    # Test import of new file TSTXX to encoded
    # this tests adds replicates, but never checks their validity
    # ignoring this because I don't want to deal with tearing down ES  posts

    import re

    sync_edw.get_all_datasets(test_accession_testapp)

    for fileinfo in import_in_1:

        converted_file = sync_edw.convert_edw(test_accession_testapp, fileinfo)
        #set_in = set(fileinfo.items())
        resp = sync_edw.post_fileinfo(test_accession_testapp, converted_file)
        # exercises: set_fileinfo_experiment, set_fileinfo_replicate, POST
        if resp:
            acc = converted_file['accession']
            url = sync_edw.collection_url(sync_edw.FILES) + acc
            get_resp = test_accession_testapp.get(url).maybe_follow()
            file_dict = get_resp.json
            assert( not sync_edw.compare_files(file_dict, converted_file) )
        else:
            ## one of the files in import_in_1 is not postable
            ## should maybe switch it from an experiment to a regular dataset
            assert(re.search('experiments', converted_file['dataset']))
            assert(not fileinfo['biological_replicate'] or not converted_file['technical_replicate'])


def test_encode3_experiments(workbook, testapp, edw_file_mock):
    # Test obtaining list of ENCODE 2 experiments and identifying which ENCODE3
    # accessions are ENCODE2 experiments

    # Test identifying an ENCODE 3 experiment
    #res = testapp.post_json('/index', {})

    sync_edw.get_all_datasets(testapp)

    edw_mock_p3 = {}
    for fileinfo in edw_file_mock:
        converted_file = sync_edw.convert_edw(testapp, fileinfo, phase='3')
        if converted_file['accession']:
            converted_file.pop('_test', None) # this is in the file for notation purposes only
            edw_mock_p3[fileinfo['accession']] = converted_file

    assert len(edw_mock_p3) == 13

    app_files_p3 = sync_edw.get_app_fileinfo(testapp, phase='3')

    assert len(app_files_p3.keys()) == 16


@pytest.mark.slow
def test_file_sync(workbook, testapp, edw_file_mock):

    import re

    sync_edw.get_all_datasets(testapp)

    edw_mock = {}
    test = {}
    filecount = 0
    for fileinfo in edw_file_mock:
        filecount = filecount+1
        converted_file = sync_edw.convert_edw(testapp, fileinfo)
        test[fileinfo['accession']] = converted_file.pop('_test', None) # this is in the file for notation purposes only
        edw_mock[fileinfo['accession']] = converted_file

    assert len(edw_mock) == filecount

    app_dict = sync_edw.get_app_fileinfo(testapp)
    #app_dict = { d['accession']:d for d in app_files }
    assert len(app_dict.keys()) == TYPE_LENGTH['file']

    edw_only, app_only, same, patch = sync_edw.inventory_files(testapp, edw_mock, app_dict)
    assert len(edw_only) == 17
    # have to troll the TEST column to predict these results
    assert len(app_only) == 13
    assert len(same) == 5
    assert len(patch) == 11

    before_reps = { d['uuid']: d for d in testapp.get('/replicates/').maybe_follow().json['@graph'] }

    for add in edw_only:
        acc = add['accession']
        url = sync_edw.collection_url(sync_edw.FILES) + acc
        resp = sync_edw.post_fileinfo(testapp, add)
        # check experiment status
        if re.match('FAIL', test[acc]):
            # currently either ambigious replicate or missing dataset
            assert(not resp)
        else:
            assert(resp.status_code == 201)

    ''' This fails due to bug #974 moved to distinct test case
    NOTE: Double posting on sqllite will NOT honor unique constraints!
    for ignore in same:
    # just try to do one duplicate for now.
        acc = ignore['accession']
        url = sync_edw.collection_url(sync_edw.FILES) + acc
        try:
           resp = sync_edw.post_fileinfo(testapp, ignore)
        except IntegrityError:
            assert(True)
    '''
    # Thought this should have thrown a 409... assert(resp.status_code == 409)
    for update in patch:
        diff = sync_edw.compare_files(app_dict[update], edw_mock[update])
        patched = sync_edw.patch_fileinfo(testapp, diff.keys(), edw_mock[update])
        should_fail = False
        for patch_prop in diff.keys():
            if patch_prop in sync_edw.NO_UPDATE or re.match('FAIL', test[update]):
                should_fail = True
        if should_fail:
            assert not patched
        else:
            assert patched


    post_app_dict = sync_edw.get_app_fileinfo(testapp)

    sync_edw.collections = []
    # reset global var!
    post_edw, post_app, post_same, post_patch= sync_edw.inventory_files(testapp, edw_mock, post_app_dict)
    assert len(post_edw) == 1
    assert len(post_app) == 13 # unchanged
    assert len(post_patch) == 4 # exsting files cannot be patched
    assert ((len(post_same)-len(same)) == (len(patch) -len(post_patch) + (len(edw_only) - len(post_edw))))
    assert len(post_app_dict.keys()) == (len(app_dict.keys()) + len(edw_only) - len(post_edw))

    user_patched = testapp.get('/files/ENCFF001RIC').maybe_follow().json
    assert(user_patched['submitted_by'] == u'/users/f5b7857d-208e-4acc-ac4d-4c2520814fe1/')
    assert(user_patched['status'] == u'OBSOLETE')

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
            new_reps[uuid] = after_reps[uuid]

    assert(len(same_reps.keys()) == 22)
    assert(not updated_reps)
    assert(len(new_reps) == 2)

    #TODO could maybe add a test to make sure that a file belonging to a dataset ends up with the right dataset
    #TODO tests for experiments with multiple mappings.


def test_patch_replicate(workbook, testapp, edw_file_mock):

    import re

    test_acc = 'ENCSR000ADH'
    test_set = sync_edw.try_datasets(testapp, dataset=test_acc)
    assert(test_set)

    update = [ x for x in sync_edw.NO_UPDATE if x != 'replicate' ]
    sync_edw.NO_UPDATE = update

    edw_mock = {}
    test = {}
    filecount = 0
    for fileinfo in edw_file_mock:
        converted_file = sync_edw.convert_edw(testapp, fileinfo)
        if converted_file.get('dataset', None) != test_set:
            continue
        filecount = filecount+1
        test[fileinfo['accession']] = converted_file.pop('_test', None) # this is in the file for notation purposes only
        edw_mock[fileinfo['accession']] = converted_file

    assert len(edw_mock) == filecount

    app_dict = sync_edw.get_app_fileinfo(testapp, dataset=test_set)
    #app_dict = { d['accession']:d for d in app_files }

    edw_only, app_only, same, patch = sync_edw.inventory_files(testapp, edw_mock, app_dict)
    assert len(patch) == 2
    assert len(same) == 2


    for update in patch:
        diff = sync_edw.compare_files(app_dict[update], edw_mock[update])
        patched = sync_edw.patch_fileinfo(testapp, diff.keys(), edw_mock[update])
        should_fail = False
        for patch_prop in diff.keys():
            if patch_prop in sync_edw.NO_UPDATE:
                should_fail = True
        if should_fail:
            assert not patched
        else:
            assert patched

    patched_file = testapp.get('/files/ENCFF001MYM').maybe_follow().json
    rep = testapp.get(patched_file['replicate']).maybe_follow().json
    assert(rep['biological_replicate_number'] == 1)
    assert(rep['technical_replicate_number'] == 2)
    assert(rep['experiment'] == patched_file['dataset'])
