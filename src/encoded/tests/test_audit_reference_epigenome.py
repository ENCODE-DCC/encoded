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
        'biosample_type': 'tissue',
        'biosample_term_id': 'UBERON:349829',
        'assay_term_name': 'RNA-seq'

    }
    return testapp.post_json('/experiment', item, status=201).json['@graph'][0]


@pytest.fixture
def reference_experiment_RRBS(testapp, lab, award):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'status': 'in progress',
        'assay_term_name': 'RRBS',
        'biosample_type': 'tissue',
        'biosample_term_id': 'UBERON:349829'

    }
    return testapp.post_json('/experiment', item, status=201).json['@graph'][0]


@pytest.fixture
def reference_experiment_WGBS(testapp, lab, award):
    item = {
        'award': award['uuid'],
        'biosample_type': 'tissue',
        'biosample_term_id': 'UBERON:349829',
        'lab': lab['uuid'],
        'status': 'in progress',
        'assay_term_name': 'whole-genome shotgun bisulfite sequencing'

    }
    return testapp.post_json('/experiment', item, status=201).json['@graph'][0]


@pytest.fixture
def reference_experiment_chip_seq_control(testapp, lab, award, target_control):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'biosample_type': 'tissue',
        'biosample_term_id': 'UBERON:349829',
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
        'biosample_type': 'tissue',
        'biosample_term_id': 'UBERON:349829',
        'assay_term_name': 'ChIP-seq',
        'target': target_H3K27me3['uuid']

    }
    return testapp.post_json('/experiment', item, status=201).json['@graph'][0]


@pytest.fixture
def reference_experiment_chip_seq_H3K36me3(testapp, lab, award, target_H3K36me3):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'biosample_type': 'tissue',
        'biosample_term_id': 'UBERON:349829',
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
        'biosample_type': 'tissue',
        'biosample_term_id': 'UBERON:349829',
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
        'biosample_type': 'tissue',
        'biosample_term_id': 'UBERON:349829',
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
        'biosample_type': 'tissue',
        'biosample_term_id': 'UBERON:349829',
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
        'biosample_type': 'tissue',
        'biosample_term_id': 'UBERON:349829',
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
        'investigated_as': ['histone']
    }
    return testapp.post_json('/target', item).json['@graph'][0]


@pytest.fixture
def target_H3K36me3(testapp, organism):
    item = {
        'label': 'H3K36me3',
        'organism': organism['@id'],
        'investigated_as': ['histone']
    }
    return testapp.post_json('/target', item).json['@graph'][0]


@pytest.fixture
def target_H3K4me1(testapp, organism):
    item = {
        'label': 'H3K4me1',
        'organism': organism['@id'],
        'investigated_as': ['histone']
    }
    return testapp.post_json('/target', item).json['@graph'][0]


@pytest.fixture
def target_H3K4me3(testapp, organism):
    item = {
        'label': 'H3K4me3',
        'organism': organism['@id'],
        'investigated_as': ['histone']
    }
    return testapp.post_json('/target', item).json['@graph'][0]


@pytest.fixture
def target_H3K27ac(testapp, organism):
    item = {
        'label': 'H3K27ac',
        'organism': organism['@id'],
        'investigated_as': ['histone']
    }
    return testapp.post_json('/target', item).json['@graph'][0]


@pytest.fixture
def target_H3K9me3(testapp, organism):
    item = {
        'label': 'H3K9me3',
        'organism': organism['@id'],
        'investigated_as': ['histone']
    }
    return testapp.post_json('/target', item).json['@graph'][0]


def test_reference_epigenome_without_required_assays(testapp, reference_epigenome_1):
    res = testapp.get(reference_epigenome_1['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'partial reference epigenome' for error in errors_list)


@pytest.fixture
def replicate_RNA_seq(testapp, reference_experiment_RNA_seq, library_1):
    item = {
        'experiment': reference_experiment_RNA_seq['@id'],
        'library': library_1['@id'],
        'biological_replicate_number': 1,
        'technical_replicate_number': 1,
    }
    return testapp.post_json('/replicate', item).json['@graph'][0]


@pytest.fixture
def replicate_RRBS(testapp, reference_experiment_RRBS, library_2):
    item = {
        'experiment': reference_experiment_RRBS['@id'],
        'library': library_2['@id'],
        'biological_replicate_number': 1,
        'technical_replicate_number': 1,
    }
    return testapp.post_json('/replicate', item).json['@graph'][0]


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
                                                       reference_experiment_chip_seq_H3K27me3[
                                                       '@id'],
                                                       reference_experiment_chip_seq_H3K36me3[
                                                       '@id'],
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
    assert all(error['category'] != 'partial reference epigenome' for error in errors_list)


def test_reference_epigenome_multiple_biosample_term_names(testapp, reference_epigenome_1,
                                                           reference_experiment_RNA_seq,
                                                           reference_experiment_RRBS,
                                                           replicate_RNA_seq,
                                                           replicate_RRBS,
                                                           library_1,
                                                           library_2,
                                                           biosample_1,
                                                           biosample_2,
                                                           donor_1,
                                                           donor_2):
    testapp.patch_json(biosample_1['@id'], {'donor': donor_1['@id'],
                                            'biosample_term_name': 'liver'})
    testapp.patch_json(biosample_2['@id'], {'donor': donor_2['@id'],
                                            'biosample_term_name': 'aorta'})
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_2['@id']})
    testapp.patch_json(reference_epigenome_1['@id'], {'related_datasets':
                                                      [reference_experiment_RNA_seq['@id'],
                                                       reference_experiment_RRBS['@id']]})
    res = testapp.get(reference_epigenome_1['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'multiple biosample term names in reference epigenome' for
               error in errors_list)


def test_reference_epigenome_multiple_biosample_treatments(testapp, reference_epigenome_1,
                                                           reference_experiment_RNA_seq,
                                                           reference_experiment_RRBS,
                                                           replicate_RNA_seq,
                                                           replicate_RRBS,
                                                           treatment,
                                                           library_1,
                                                           library_2,
                                                           biosample_1,
                                                           biosample_2):
    testapp.patch_json(biosample_1['@id'], {'treatments': [treatment['@id']]})
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_2['@id']})
    testapp.patch_json(reference_epigenome_1['@id'], {'related_datasets':
                                                      [reference_experiment_RNA_seq['@id'],
                                                       reference_experiment_RRBS['@id']]})
    res = testapp.get(reference_epigenome_1['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'multiple biosample treatments in reference epigenome' for
               error in errors_list)
