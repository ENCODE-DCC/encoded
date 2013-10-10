import pytest

import encoded.commands.read_edw_fileinfo
from edw_test_data import format_app_file_out
import json

# globals

# TEST_HASHES = {}
#pytest.mark.parametrize(('field1', 'field2'), TEST_HASHES.items())
# def test_fxn(field1, field2)

EDW_FILE_TEST_DATA_DIR = 'src/encoded/tests/data/edw_file'

def test_app_file_show():
    assert(1 == 1)

def test_format_app_fileinfo(testapp):
    # Test extracting EDW-relevant fields from encoded file.json
    EDW_TEST_FILE = 'format_app_file_in.json'

    # load input
    f = open(EDW_FILE_TEST_DATA_DIR + '/' + EDW_TEST_FILE)
    file_dict = json.load(f)

    encoded.commands.read_edw_fileinfo.format_app_fileinfo(testapp, file_dict)

    # compare results for identity with expected
    set_app = set(file_dict.items())
    set_edw = set(format_app_file_out.items())
    assert len(set_edw ^ set_app) == 0


#def test_get_app_fileinfo(workbook, testapp):
    #app_files = encoded.commands.read_edw_fileinfo.get_app_fileinfo(testapp)


#def test_new(workbook, app):
    # Test find of new files (accession at EDW but not encoded)


#def test_import(workbook, app)
    # Test import of new file to encoded



