import pytest


@pytest.fixture
def dataset_2():
    return {
        'schema_version': '2',
        'aliases': ['ucsc_encode_db:mm9-wgEncodeCaltechTfbs', 'barbara-wold:mouse-TFBS'],
        'geo_dbxrefs': ['GSE36024'],
    }


@pytest.fixture
def dataset_3():
    return {
        'schema_version': '3',
        'status': 'CURRENT',
        'award': '2a27a363-6bb5-43cc-99c4-d58bf06d3d8e',
    }


@pytest.fixture
def dataset_5(publication):
    return {
        'schema_version': '5',
        'references': [publication['identifiers'][0]],
    }


@pytest.fixture
def dataset_reference_1(lab, award):
    return {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'dbxrefs': ['UCSC-ENCODE-hg19:wgEncodeEH000325', 'IHEC:IHECRE00004703'],
    }


@pytest.fixture
def dataset_reference_2(lab, award):
    return {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'dbxrefs': ['IHEC:IHECRE00004703'],
        'notes': 'preexisting comment.'
    }


@pytest.fixture
def ucsc_browser_composite(testapp, lab, award):
    item = {
        'award': award['@id'],
        'lab': lab['@id'],
    }
    return testapp.post_json('/ucsc_browser_composite', item).json['@graph'][0]


@pytest.fixture
def transgenic_enhancer_experiment(testapp, lab, award, whole_organism):
    item = {
        'award': award['@id'],
        'lab': lab['@id'],
        'biosample_ontology': whole_organism['uuid'],
        'assay_term_name': 'transgenic enhancer assay'
    }
    return testapp.post_json('/transgenic_enhancer_experiment', item).json['@graph'][0]
