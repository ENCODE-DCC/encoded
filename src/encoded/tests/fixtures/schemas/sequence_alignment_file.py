import pytest


@pytest.fixture
def sequence_alignment_file_base(testapp, dataset_base, raw_sequence_file_base):
    item = {
        'dataset': dataset_base['@id'],
        'file_format': 'bam',
        'derivation_process': ['alignment'],
        'output_types': ['genome alignments'],
        'derived_from': [raw_sequence_file_base['uuid']],
    }
    return testapp.post_json('/sequence_alignment_file', item).json['@graph'][0]
