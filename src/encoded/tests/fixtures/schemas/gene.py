import pytest


@pytest.fixture
def gene_base(testapp, human):
    item = {
        'uuid': 'd358f63b-63d6-408f-baca-13881c6c79a1',
        'assembly': 'GRCh38',
        'gene_id': '4609',
        'symbol': 'MYC',
        'gene_status': 'current',
        'gencode_version': '32',
        'gene_version': 3
    }
    return testapp.post_json('/gene', item, status=201).json['@graph'][0]
