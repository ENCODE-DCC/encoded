import pytest
import json
from sqlalchemy.engine.base import Engine

import encoded.edw_file
import edw_test_data

pytestmark = [pytest.mark.edw_file]

## TODO: This should be converted to a smoke-type test after build/install is complete

#@pytest.mark.xfail
# travis cannot connect to EDW
def test_make_edw():

    edw = encoded.edw_file.make_edw()
    assert(type(edw)==Engine)

#@pytest.mark.xfail
# travis cannot connect to EDW
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

