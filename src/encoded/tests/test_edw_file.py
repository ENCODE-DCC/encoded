import pytest
import json
from csv import DictReader

import encoded.commands.read_edw_fileinfo
import edw_test_data

# globals
EDW_FILE_TEST_DATA_DIR = 'src/encoded/tests/data/edw_file'

TEST_ACCESSION = 'ENCFF001RET'  # NOTE: must be in test set

# test_format_app

#@pytest.mark.parametrize('test_num', [1, 2])
# resisting parameterization, as test 1 will go much quicker 
# w/o loading workbook which isn't needed

def test_format_app_fileinfo_expanded(workbook, testapp):
    # Test extracting EDW-relevant fields from encoded file.json
    # Expanded JSON

    # load input
    url = '/files/' + TEST_ACCESSION

    resp = testapp.get(url).maybe_follow()
    file_dict = resp.json

    encoded.commands.read_edw_fileinfo.format_app_fileinfo(testapp, file_dict)

    # compare results for identity with expected
    set_app = set(file_dict.items())
    set_edw = set(edw_test_data.format_app_file_out.items())
    assert set_app == set_edw


def test_format_app_fileinfo_embedded(workbook, testapp):
    # Test extracting EDW-relevant fields from encoded file.json
    # Unexpanded JSON (requires GETs on embedded URLs)

    # load input
    url = '/files/' + TEST_ACCESSION + '/?embed=false/'
    resp = testapp.get(url).maybe_follow()
    file_dict = resp.json

    encoded.commands.read_edw_fileinfo.format_app_fileinfo(testapp, file_dict)

    # compare results for identity with expected
    set_app = set(file_dict.items())
    set_edw = set(edw_test_data.format_app_file_out.items())
    assert set_app == set_edw


def test_list_new(workbook, testapp):
    # Test obtaining list of 'new' accessions (at EDW, not at app)
    # Unexpanded JSON (requires GETs on embedded URLs)
    
    edw_accs = edw_test_data.new_in
    app_accs = encoded.commands.read_edw_fileinfo.get_app_fileinfo(testapp, 
                                                                  full=False)
    new_accs = sorted(encoded.commands.read_edw_fileinfo.get_new_filelist_from_lists(app_accs, edw_accs))
    assert new_accs == sorted(edw_test_data.new_out)


def test_import_file(workbook, testapp):
    # Test import of new file to encoded

    test_num = 1    # for parametrization
    input_file = 'import_in.' + str(test_num) + '.tsv'
    f = open(EDW_FILE_TEST_DATA_DIR + '/' + input_file)
    reader = DictReader(f, delimiter='\t')
    for fileinfo in reader:
        encoded.commands.read_edw_fileinfo.post_fileinfo(testapp, fileinfo)
        acc = fileinfo['accession']
        url = '/files/' + acc
        resp = testapp.get(url).maybe_follow()
        file_dict = resp.json
        encoded.commands.read_edw_fileinfo.format_app_fileinfo(testapp, file_dict)
        set_out = set(file_dict.items())

        # WARNING: type-unaware char conversion here, with field-specific
        # correction of mis-formatted int field
        unidict = {k.decode('utf8'): v.decode('utf8') for k, v in fileinfo.items()}
        unidict['replicate'] = int(unidict['replicate'])
        set_in = set(unidict.items())
        assert set_in == set_out


