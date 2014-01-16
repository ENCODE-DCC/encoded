import pytest
from sqlalchemy.engine.base import Engine

import encoded.edw_file as edw_file

pytestmark = [pytest.mark.edw_file]

## TODO: This should be converted to a smoke-type test after build/install is complete

@pytest.mark.skipif(True, reason='Travis-CI cannot use external DB test')
# travis cannot connect to EDW
def test_make_edw():

    edw = edw_file.make_edw()
    assert(type(edw)==Engine)

@pytest.mark.skipif(True, reason='Travis-CI cannot use external DB test')
# travis cannot connect to EDW
def test_get_edw_files():

    ''' test connectivity schema integrity basic query not all options '''
    edw = edw_file.make_edw()
    files = edw_file.get_edw_fileinfo(edw,limit=50)
    assert(len(files)==50)
    for f in files:
        ## quasi validate required fields
        assert(f['accession'])
        assert(f.has_key('biological_replicate'))
        assert(f.has_key('technical_replicate'))
        assert(f['md5sum'])
        assert(f['dataset'])

@pytest.mark.skipif(True, reason='Travis-CI cannot use external DB test')
# travis cannot connect to EDW
def test_get_encode2_encode3():
    edw = edw_file.make_edw()
    ec2_files = edw_file.get_edw_fileinfo(edw,phase=edw_file.ENCODE_PHASE_2, limit=50)
    ec2_set = set([ f['accession'] for f in ec2_files ])
    ec3_files = edw_file.get_edw_fileinfo(edw,phase=edw_file.ENCODE_PHASE_3, limit=50)
    ec3_set = set([ f['accession'] for f in ec3_files ])

    assert(ec2_set != ec3_set)
