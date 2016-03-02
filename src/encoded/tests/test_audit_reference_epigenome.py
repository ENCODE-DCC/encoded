import pytest

@pytest.fixture
def reference_epigenome_1(testapp, lab, award):
    item = {
        'award': award['@id'],
        'lab': lab['@id']
    }
    return testapp.post_json('/reference_epigenome', item).json['@graph'][0]


@pytest.fixture
def reference_experiment_RNA_seq(testapp, lab, award):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'status': 'in progress',
        'assay_term_name': 'RNA-seq'

    }
    return testapp.post_json('/experiment', item, status=201).json['@graph'][0]


@pytest.fixture
def reference_experiment_RRBS(testapp, lab, award):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'status': 'in progress',
        'assay_term_name': 'RRBS'

    }
    return testapp.post_json('/experiment', item, status=201).json['@graph'][0]


@pytest.fixture
def reference_experiment_WGBS(testapp, lab, award):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'status': 'in progress',
        'assay_term_name': 'WGBS'

    }
    return testapp.post_json('/experiment', item, status=201).json['@graph'][0]


@pytest.fixture
def reference_experiment_chip_seq_control(testapp, lab, award, target_control):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'status': 'in progress',
        'assay_term_name': 'ChIP-seq',
        'target': target_control['uuid']

    }
    return testapp.post_json('/experiment', item, status=201).json['@graph'][0]


@pytest.fixture
def reference_experiment_chip_seq_H3K27me3(testapp, lab, award, target_H3K27me3):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'status': 'in progress',
        'assay_term_name': 'ChIP-seq',
        'target': target_H3K27me3['uuid']

    }
    return testapp.post_json('/experiment', item, status=201).json['@graph'][0]


@pytest.fixture
def reference_experiment_chip_seq_H3K36me3(testapp, lab, award, target_H3K36me3):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'status': 'in progress',
        'assay_term_name': 'ChIP-seq',
        'target': target_H3K36me3['uuid']

    }
    return testapp.post_json('/experiment', item, status=201).json['@graph'][0]


@pytest.fixture
def reference_experiment_chip_seq_H3K4me1(testapp, lab, award, target_H3K4me1):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'status': 'in progress',
        'assay_term_name': 'ChIP-seq',
        'target': target_H3K4me1['uuid']

    }
    return testapp.post_json('/experiment', item, status=201).json['@graph'][0]


@pytest.fixture
def reference_experiment_chip_seq_H3K4me3(testapp, lab, award, target_H3K4me3):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'status': 'in progress',
        'assay_term_name': 'ChIP-seq',
        'target': target_H3K4me3['uuid']

    }
    return testapp.post_json('/experiment', item, status=201).json['@graph'][0]


@pytest.fixture
def reference_experiment_chip_seq_H3K27ac(testapp, lab, award, target_H3K27ac):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'status': 'in progress',
        'assay_term_name': 'ChIP-seq',
        'target': target_H3K27ac['uuid']

    }
    return testapp.post_json('/experiment', item, status=201).json['@graph'][0]


@pytest.fixture
def reference_experiment_chip_seq_H3K9me3(testapp, lab, award, target_H3K9me3):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'status': 'in progress',
        'assay_term_name': 'ChIP-seq',
        'target': target_H3K9me3['uuid']

    }
    return testapp.post_json('/experiment', item, status=201).json['@graph'][0]


@pytest.fixture
def target_control(testapp, organism):
    item = {
        'label': 'Control',
        'organism': organism['@id'],
        'investigated_as': ['control']
    }
    return testapp.post_json('/target', item).json['@graph'][0]


@pytest.fixture
def target_H3K27me3(testapp, organism):
    item = {
        'label': 'H3K27me3',
        'organism': organism['@id'],
        'investigated_as': ['histone modification']
    }
    return testapp.post_json('/target', item).json['@graph'][0]


@pytest.fixture
def target_H3K36me3(testapp, organism):
    item = {
        'label': 'H3K36me3',
        'organism': organism['@id'],
        'investigated_as': ['histone modification']
    }
    return testapp.post_json('/target', item).json['@graph'][0]


@pytest.fixture
def target_H3K4me1(testapp, organism):
    item = {
        'label': 'H3K4me1',
        'organism': organism['@id'],
        'investigated_as': ['histone modification']
    }
    return testapp.post_json('/target', item).json['@graph'][0]


@pytest.fixture
def target_H3K4me3(testapp, organism):
    item = {
        'label': 'H3K4me3',
        'organism': organism['@id'],
        'investigated_as': ['histone modification']
    }
    return testapp.post_json('/target', item).json['@graph'][0]


@pytest.fixture
def target_H3K27ac(testapp, organism):
    item = {
        'label': 'H3K27ac',
        'organism': organism['@id'],
        'investigated_as': ['histone modification']
    }
    return testapp.post_json('/target', item).json['@graph'][0]


@pytest.fixture
def target_H3K9me3(testapp, organism):
    item = {
        'label': 'H3K9me3',
        'organism': organism['@id'],
        'investigated_as': ['histone modification']
    }
    return testapp.post_json('/target', item).json['@graph'][0]


def test_reference_epigenome_without_required_assays(testapp, reference_epigenome_1):
    res = testapp.get(reference_epigenome_1['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'missing IHEC required assay' for error in errors_list)


def test_reference_epigenome_with_required_assays(testapp, reference_epigenome_1,
                                                  reference_experiment_RNA_seq,
                                                  reference_experiment_RRBS,
                                                  reference_experiment_WGBS,
                                                  reference_experiment_chip_seq_control,
                                                  reference_experiment_chip_seq_H3K27me3,
                                                  reference_experiment_chip_seq_H3K36me3,
                                                  reference_experiment_chip_seq_H3K4me1,
                                                  reference_experiment_chip_seq_H3K4me3,
                                                  reference_experiment_chip_seq_H3K27ac,
                                                  reference_experiment_chip_seq_H3K9me3,
                                                  ):
    testapp.patch_json(reference_epigenome_1['@id'], {'related_datasets':
                                                      [reference_experiment_RNA_seq['@id'],
                                                       reference_experiment_RRBS['@id'],
                                                       reference_experiment_WGBS['@id'],
                                                       reference_experiment_chip_seq_control['@id'],
                                                       reference_experiment_chip_seq_H3K27me3['@id'],
                                                       reference_experiment_chip_seq_H3K36me3['@id'],
                                                       reference_experiment_chip_seq_H3K4me1['@id'],
                                                       reference_experiment_chip_seq_H3K4me3['@id'],
                                                       reference_experiment_chip_seq_H3K27ac['@id'],
                                                       reference_experiment_chip_seq_H3K9me3['@id']
                                                       ]})
    res = testapp.get(reference_epigenome_1['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert all(error['category'] != 'missing IHEC required assay' for error in errors_list)
