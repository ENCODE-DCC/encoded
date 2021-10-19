import pytest


@pytest.fixture
def processed_matrix_file_base(testapp, dataset_base, raw_matrix_file_base):
    item = {
        'dataset': dataset_base['@id'],
        'file_format': 'hdf5',
        'derivation_process': ['doublet removal','batch correction','depth normalization'],
        'output_types': ['gene quantifications'],
        'derived_from': [raw_matrix_file_base['uuid']],
        'is_primary_data': True,
        'layers': [
            {
                'normalized': False,
                'value_scale': 'linear',
                'value_units': 'RPKM',
                'label': 'raw',
                'is_primary_data': False
            }
        ]
    }
    return testapp.post_json('/processed_matrix_file', item).json['@graph'][0]
