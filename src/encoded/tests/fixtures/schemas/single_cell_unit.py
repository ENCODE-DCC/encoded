import pytest


@pytest.fixture
def single_cell_unit_1(testapp, lab, award, heart, analysis_1):
    item = {
        'lab': lab['@id'],
        'award': award['@id'],
        'assay_term_name': 'single-nucleus ATAC-seq',
        'biosample_ontology': heart['uuid'],
        'analysis_objects': [analysis_1['uuid']],
        'schema_version': '1'
    }
    return item

@pytest.fixture
def single_cell_unit_2(testapp, lab, award, heart, analysis_1):
    item = {
        'lab': lab['@id'],
        'award': award['@id'],
        'assay_term_name': 'single-nucleus ATAC-seq',
        'biosample_ontology': heart['uuid'],
        'analysis_objects': [analysis_1['uuid']],
        'schema_version': '2',
        'internal_tags': ['ENCYCLOPEDIAv3', 'ENCYCLOPEDIAv4', 'ENCYCLOPEDIAv5', 'ENCYCLOPEDIAv6']
    }
    return item
