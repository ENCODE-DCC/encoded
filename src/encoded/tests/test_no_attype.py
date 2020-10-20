import pytest

from encoded.tests.features.conftest import app_settings, app, index_workbook


pytestmark = [
    pytest.mark.indexing,
    pytest.mark.usefixtures('index_workbook'),
]


'''
    Used to test views with no @type property.
'''
def test_no_attype(testapp):
    res = testapp.get('/searchv2_raw/?type=Experiment', status=200)
    assert res.content_type == 'application/json'
    assert res.text
