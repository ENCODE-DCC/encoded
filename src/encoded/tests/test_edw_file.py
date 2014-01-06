import pytest
import json
from csv import DictReader

import encoded.commands.read_edw_fileinfo
import edw_test_data

pytestmark = [pytest.mark.edw_file]

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

    fileinfo = encoded.commands.read_edw_fileinfo.format_app_fileinfo(testapp, file_dict)

    # compare results for identity with expected
    set_app = set(fileinfo.items())
    set_edw = set(edw_test_data.format_app_file_out.items())
    assert set_app == set_edw


def test_list_new(workbook, testapp):
    # Test obtaining list of 'new' accessions (at EDW, not at app)
    # Unexpanded JSON (requires GETs on embedded URLs)

    edw_accs = edw_test_data.new_in
    app_accs = encoded.commands.read_edw_fileinfo.get_app_fileinfo(testapp,
                                                                  full=False)
    new_accs = sorted(encoded.commands.read_edw_fileinfo.get_missing_filelist_from_lists(app_accs, edw_accs))
    assert new_accs == sorted(edw_test_data.new_out)


def test_import_file(workbook, testapp):
    # Test import of new file to encoded

    test_num = 1    # for parameterization
    input_file = 'import_in.' + str(test_num) + '.tsv'
    f = open(EDW_FILE_TEST_DATA_DIR + '/' + input_file)
    reader = DictReader(f, delimiter='\t')
    for fileinfo in reader:
        # WARNING: type-unaware char conversion here, with field-specific
        # correction of mis-formatted int field
        unidict = {k.decode('utf8'): v.decode('utf8') for k, v in fileinfo.items()}
        unidict['replicate'] = int(unidict['replicate'])
        set_in = set(unidict.items())

        encoded.commands.read_edw_fileinfo.format_reader_fileinfo(fileinfo)
        resp = encoded.commands.read_edw_fileinfo.post_fileinfo(testapp, fileinfo)
        acc = fileinfo['accession']
        url = encoded.commands.read_edw_fileinfo.collection_url(encoded.commands.read_edw_fileinfo.FILES) + acc
        resp = testapp.get(url).maybe_follow()
        file_dict = resp.json
        fileinfo = encoded.commands.read_edw_fileinfo.format_app_fileinfo(testapp, file_dict)
        set_out = set(fileinfo.items())

        assert set_in == set_out


def test_encode2_experiments(workbook, testapp):
    # Test obtaining list of ENCODE 2 experiments and identifying which ENCODE3
    # accessions are ENCODE2 experiments

    # Test identifying an ENCODE 3 experiment
    assert not encoded.commands.read_edw_fileinfo.is_encode2_experiment(testapp, edw_test_data.encode3)

    # Create hash of all ENCODE 2 experiments, map to ENCODE 3 accession
    encode2_hash = encoded.commands.read_edw_fileinfo.get_encode2_to_encode3(testapp)
    assert sorted(encode2_hash.keys()) == sorted(edw_test_data.encode2)

    # Test identifying an ENCODE 2 experiment
    assert encoded.commands.read_edw_fileinfo.is_encode2_experiment(testapp, encode2_hash.values()[0])

