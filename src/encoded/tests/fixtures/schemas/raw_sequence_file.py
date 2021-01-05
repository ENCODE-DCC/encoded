import pytest


@pytest.fixture
def raw_sequence_file_base(testapp, dataset_base, sequencing_run_base):
    item = {
        'dataset': dataset_base['uuid'],
        'file_format': 'fastq',
        'output_types': ['assigned reads'],
        'derived_from': sequencing_run_base['uuid'],
        'uuid': '4b000ca8-8ba2-48cd-977f-fff4c900630d'
    }
    return testapp.post_json('/raw_sequence_file', item, status=201).json['@graph'][0]
