import pytest


@pytest.fixture
def reference_file_base(testapp):
    item = {
        'file_format': 'gtf',
        'output_types': ['transcriptome reference'],
        'uuid': '3e2a3840-ecc6-4568-8271-df13b94f8425',
        'reference_version': 'GENCODE 32'
    }
    return testapp.post_json('/reference_file', item, status=201).json['@graph'][0]
