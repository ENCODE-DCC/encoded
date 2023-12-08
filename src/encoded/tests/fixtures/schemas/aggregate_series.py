import pytest

@pytest.fixture
def aggregate_series_3(testapp, lab, base_experiment_submitted, award):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'related_datasets': [base_experiment_submitted['@id']],
        'schema_version': '3',
        'internal_tags': ['ENCYCLOPEDIAv3', 'ENCYCLOPEDIAv4', 'ENCYCLOPEDIAv5', 'ENCYCLOPEDIAv6']
    }
    return item


@pytest.fixture
def aggregate_series_chip_seq(testapp, lab, award, experiment_chip_H3K4me3):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'related_datasets': [experiment_chip_H3K4me3['@id']]
    }
    return testapp.post_json('/aggregate_series', item, status=201).json['@graph'][0]


@pytest.fixture
def aggregate_series_rna_seq(testapp, lab, award, experiment_rna):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'related_datasets': [experiment_rna['@id']]
    }
    return testapp.post_json('/aggregate_series', item, status=201).json['@graph'][0]
