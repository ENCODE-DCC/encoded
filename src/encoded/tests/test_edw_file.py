import pytest

import encoded.commands.read_edw_fileinfo
from edw_test_data import format_app_file_out
import json

# globals

EDW_FILE_TEST_DATA_DIR = 'src/encoded/tests/data/edw_file'

def test_app_file_show():
    assert(1 == 1)

def test_format_app_fileinfo():
    EDW_TEST_FILE = 'format_app_file_in.json'

    # load input
    f = open(EDW_FILE_TEST_DATA_DIR + '/' + EDW_TEST_FILE)
    file_dict = json.load(f)

    encoded.commands.read_edw_fileinfo.format_app_fileinfo(file_dict)

    # compare results for identity with expected
    set_app = set(file_dict.items())
    set_edw = set(format_app_file_out.items())
    assert len(set_edw ^ set_app) == 0


