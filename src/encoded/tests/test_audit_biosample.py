import pytest

@pytest.fixture
def ntr_biosample(submitter, lab, award, source, organism):
    return {
        'award': award['uuid'],
        'biosample_term_id': 'NTR:0000022',
        'biosample_term_name': 'myocyte',
        'biosample_type': 'in vitro differentiated cells',
        'lab': lab['uuid'],
        'organism': organism['uuid'],
        'source': source['uuid'],
    }


def test_audit_biosample_term_ntr(testapp, ntr_biosample):
    res = testapp.post_json('/biosample', ntr_biosample)
    res = testapp.get(res.location + '@@index-data')
    error, = res.json['audit']
    assert error['category'] == 'NTR'
