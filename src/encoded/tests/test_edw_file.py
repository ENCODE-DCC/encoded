import pytest
import json
from sqlalchemy.engine.base import Engine

import encoded.edw_file
import edw_test_data

pytestmark = [pytest.mark.edw_file]

## edw_file
# def format_edw_fileinfo(file_dict, exclude=None):
# def make_edw(data_host=None):
# def dump_filelist(fileaccs, header=True, typeField=None):
# def dump_fileinfo(fileinfos, header=True, typeField=None, exclude=None):
# def get_edw_filelist(edw, limit=None, experiment=True, phase=ENCODE_PHASE_ALL):
# def get_edw_max_id(edw):
# def get_edw_fileinfo(edw, limit=None, experiment=True, start_id=0,

def test_make_edw():

    edw = encoded.edw_file.make_edw()
    assert(type(edw)==Engine)

def test_get_edw_files():

    ''' test connectivity schema integrity basic query not all options '''
    edw = encoded.edw_file.make_edw()
    files = encoded.edw_file.get_edw_fileinfo(edw,limit=50)
    assert(len(files)==50)
    for f in files:
        ## quasi validate required fields
        assert(f['accession'])
        assert(f.has_key('biological_replicate'))
        assert(f.has_key('technical_replicate'))
        assert(f['md5sum'])
        assert(f['dataset'])

