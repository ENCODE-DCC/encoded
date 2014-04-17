import pytest


@pytest.fixture
def chip_experiment(submitter, lab, award):
    return {
        'award': award['uuid'],
        'biosample_term_name': 'NTR:0000022',
        'biosample_term_name': 'myocyte',
        'biosample_type': 'in vitro differentiated cells',
        'lab': lab['uuid'],
        'submitted_by': submitter['uuid'],
        'assay_term_name': 'ChIP-seq',
        'assay_term_id': "OBI:0000716",
    }


def test_audit_experiment_target(testapp, chip_experiment):
    res = testapp.post_json('/biosample', chip_experiment)
    res = testapp.get(res.location + '@@index-data')
    error, = res.json['audit']
    assert error['category'] == 'missing target'