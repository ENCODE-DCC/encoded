import pytest


@pytest.fixture
def annotation_8(award, lab):
    return {
        'award': award['@id'],
        'lab': lab['@id'],
        'schema_version': '8',
        'annotation_type': 'encyclopedia',
        'status': 'released'
    }


@pytest.fixture
def annotation_12(award, lab):
    return {
        'award': award['@id'],
        'lab': lab['@id'],
        'schema_version': '12',
        'annotation_type': 'candidate regulatory regions',
        'status': 'released'
    }


@pytest.fixture
def annotation_14(award, lab):
    return {
        'award': award['@id'],
        'lab': lab['@id'],
        'schema_version': '14',
        'annotation_type': 'candidate regulatory regions',
        'status': 'proposed'
    }


@pytest.fixture
def annotation_16(award, lab):
    return {
        'award': award['@id'],
        'lab': lab['@id'],
        'schema_version': '16',
        'biosample_type': 'immortalized cell line'
    }


@pytest.fixture
def annotation_17(award, lab):
    return {
        'award': award['@id'],
        'lab': lab['@id'],
        'schema_version': '17',
        'biosample_type': 'immortalized cell line',
        'status': 'started'
    }


@pytest.fixture
def annotation_19(award, lab):
    return {
        'award': award['@id'],
        'lab': lab['@id'],
        'schema_version': '19',
        'biosample_type': 'stem cell',
        'biosample_term_name': 'mammary stem cell',
        'status': 'started'
    }


@pytest.fixture
def annotation_20(award, lab):
    return {
        'award': award['@id'],
        'lab': lab['@id'],
        'schema_version': '19',
        'biosample_type': 'primary cell',
        'biosample_term_id': 'CL:0000765',
        'biosample_term_name': 'erythroblast',
        'internal_tags': ['cre_inputv10', 'cre_inputv11', 'ENCYCLOPEDIAv3']
    }

@pytest.fixture
def annotation_21(award, lab):
    return {
        'award': award['@id'],
        'lab': lab['@id'],
        'schema_version': '24',
        'annotation_type': 'candidate regulatory elements'
    }


@pytest.fixture
def annotation_25(award, lab):
    return {
        'award': award['@id'],
        'lab': lab['@id'],
        'schema_version': '25',
        'encyclopedia_version': '1'
    }


@pytest.fixture
def annotation_26(award, lab):
    return {
        'award': award['@id'],
        'lab': lab['@id'],
        'schema_version': '26',
        'dbxrefs': ['IHEC:IHECRE00000998.1'],
    }


@pytest.fixture
def annotation_dataset(testapp, lab, award):
    item = {
        'award': award['@id'],
        'lab': lab['@id'],
        'annotation_type': 'imputation'
    }
    return testapp.post_json('/annotation', item).json['@graph'][0]


@pytest.fixture
def annotation_27(award, lab):
    return {
        'award': award['@id'],
        'lab': lab['@id'],
        'schema_version': '27',
        'annotation_type': 'representative DNase hypersensitivity sites',
    }


@pytest.fixture
def annotation_28(award, lab):
    return {
        'award': award['@id'],
        'lab': lab['@id'],
        'schema_version': '28',
        'relevant_timepoint': '3',
        'relevant_timepoint_units': 'stage',
        'notes': 'Lorem ipsum'
    }


@pytest.fixture
def annotation_29(award, lab):
    return {
        'award': award['@id'],
        'lab': lab['@id'],
        'schema_version': '29',
        'annotation_type': 'representative DNase hypersensitivity sites (rDHSs)',
    }


@pytest.fixture
def annotation_30(award, lab):
    return {
        'award': award['@id'],
        'lab': lab['@id'],
        'schema_version': '30',
        'annotation_type': 'blacklist',
    }
