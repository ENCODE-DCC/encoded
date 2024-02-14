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


@pytest.fixture
def annotation_ccre(testapp, award, lab):
    item = {
        'award': award['@id'],
        'lab': lab['@id'],
        'annotation_type': 'candidate Cis-Regulatory Elements',
        'encyclopedia_version': ['ENCODE v2']
    }
    return testapp.post_json('/annotation', item).json['@graph'][0]


@pytest.fixture
def annotation_dhs(testapp, award, lab):
    item = {
        'award': award['@id'],
        'lab': lab['@id'],
        'annotation_type': 'representative DNase hypersensitivity sites',
        'encyclopedia_version': ['ENCODE v2']
    }
    return testapp.post_json('/annotation', item).json['@graph'][0]

@pytest.fixture
def annotation_31(award, lab, analysis_released_2):
    return {
        'award': award['@id'],
        'lab': lab['@id'],
        'schema_version': '31',
        'annotation_type': 'candidate regulatory elements',
        'analysis_objects': [analysis_released_2['uuid']]
    }

@pytest.fixture
def annotation_32(award, lab):
    return {
        'award': award['@id'],
        'lab': lab['@id'],
        'schema_version': '32',
        'internal_tags': ['RegulomeDB']
    }


@pytest.fixture
def annotation_ccre_2(testapp, award, lab):
    return {
        'award': award['@id'],
        'lab': lab['@id'],
        'annotation_type': 'candidate Cis-Regulatory Elements',
    }


@pytest.fixture
def annotation_33(award, lab):
    return {
        'award': award['@id'],
        'lab': lab['@id'],
        'schema_version': '33',
        'annotation_type': 'gkmSVM-model',
    }

@pytest.fixture
def annotation_34(award, lab):
    return {
        'award': award['@id'],
        'lab': lab['@id'],
        'schema_version': '34',
        'assay_term_name': 'DNase-seq',
    }


@pytest.fixture
def annotation_35_experimental_input_array(award, lab, experiment_chip_H3K4me3):
    return {
        'award': award['@id'],
        'lab': lab['@id'],
        'schema_version': '35',
        'assay_term_name': 'DNase-seq',
        'experimental_input': experiment_chip_H3K4me3['@id']
    }

@pytest.fixture
def annotation_36(award, lab):
    return {
        'award': award['@id'],
        'lab': lab['@id'],
        'schema_version': '36',
        'annotation_type': 'dsQTLs',
    }

@pytest.fixture
def annotation_37(award, lab):
    return {
        'award': award['@id'],
        'lab': lab['@id'],
        'schema_version': '37',
        'annotation_type': 'long-range chromatin interactions',
    }


@pytest.fixture
def annotation_38(award, lab):
    return {
        'award': award['@id'],
        'lab': lab['@id'],
        'schema_version': '38',
        'internal_tags': ['ENCYCLOPEDIAv3', 'ENCYCLOPEDIAv4', 'ENCYCLOPEDIAv5', 'ENCYCLOPEDIAv6']
    }


@pytest.fixture
def annotation_39(award, lab):
    return {
        'award': award['@id'],
        'lab': lab['@id'],
        'schema_version': '38',
        'annotation_type': 'element gene link predictions'
    }
