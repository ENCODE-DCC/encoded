import pytest


@pytest.fixture
def raw_matrix_file_base(testapp, dataset_base, raw_sequence_file_base):
    item = {
        'dataset': dataset_base['@id'],
        'file_format': 'hdf5',
        'derivation_process': ['alignment','quantification'],
        'output_types': ['gene quantifications'],
        'derived_from': [raw_sequence_file_base['uuid']],
        'value_units': 'RPKM',
        'background_barcodes_included': True,
        'uuid': 'cf607222-a08a-4172-a3e6-b45be9ec0700'
    }
    return testapp.post_json('/raw_matrix_file', item).json['@graph'][0]
