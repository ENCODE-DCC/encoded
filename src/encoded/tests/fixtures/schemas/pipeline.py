import pytest


@pytest.fixture
def pipeline_short_rna(testapp, lab, award, analysis_step_bam):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'title': "Small RNA-seq single-end pipeline",
        'analysis_steps': [analysis_step_bam['@id']]
    }
    return testapp.post_json('/pipeline', item).json['@graph'][0]


@pytest.fixture
def pipeline_chip_encode4(testapp, lab, award, analysis_step_chip_encode4):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'title': "Histone ChIP-seq 2",
        'analysis_steps': [analysis_step_chip_encode4['@id']]
    }
    return testapp.post_json('/pipeline', item).json['@graph'][0]


@pytest.fixture
def pipeline_dnase_encode4(testapp, lab, award, analysis_step_dnase_encode4):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'title': "DNase-seq pipeline",
        'analysis_steps': [analysis_step_dnase_encode4['@id']]
    }
    return testapp.post_json('/pipeline', item).json['@graph'][0]


@pytest.fixture
def pipeline_rna_encode4(testapp, lab, award, analysis_step_rna_encode4):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'title': "RNA-seq pipeline",
        'analysis_steps': [analysis_step_rna_encode4['@id']]
    }
    return testapp.post_json('/pipeline', item).json['@graph'][0]


@pytest.fixture
def pipeline_1():
    return {
        'schema_version': '1',
        'status': 'active',
        'title': 'Test pipeline',
    }


@pytest.fixture
def pipeline_2(award, lab):
    return {
        'schema_version': '2',
        'status': 'active',
        'title': 'Test pipeline',
        'award': award['uuid'],
        'lab': lab['uuid'],
    }


@pytest.fixture
def pipeline_7(award, lab):
    return {
        'assay_term_name': 'MNase-seq',
        'schema_version': '7',
        'status': 'active',
        'title': 'Test pipeline',
        'award': award['uuid'],
        'lab': lab['uuid'],
    }


@pytest.fixture
def pipeline_8(award, lab):
    return {
        'assay_term_names': ['MNase-seq'],
        'schema_version': '8',
        'status': 'active',
        'title': 'Test pipeline',
        'award': award['uuid'],
        'lab': lab['uuid'],
    }


@pytest.fixture
def pipeline_bam(testapp, lab, award, analysis_step_bam):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'title': "ChIP-seq read mapping",
        'assay_term_names': ['ChIP-seq'],
        'analysis_steps': [analysis_step_bam['@id']]
    }
    return testapp.post_json('/pipeline', item).json['@graph'][0]


@pytest.fixture
def pipeline_without_assay_term_names_bam(testapp, lab, award, analysis_step_bam):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'title': "ChIP-seq read mapping",
        'analysis_steps': [analysis_step_bam['@id']]
    }
    return testapp.post_json('/pipeline', item).json['@graph'][0]


@pytest.fixture
def pipeline(testapp, lab, award):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'title': "Test pipeline",
        'assay_term_names': ['RNA-seq']
    }
    return testapp.post_json('/pipeline', item).json['@graph'][0]


@pytest.fixture
def pipeline_without_assay_term_names(testapp, lab, award):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'title': "Test pipeline"
    }
    return testapp.post_json('/pipeline', item).json['@graph'][0]


@pytest.fixture
def ATAC_pipeline(testapp, encode_lab, award,
                  analysis_step_atac_encode4_alignment,
                  analysis_step_atac_encode4_pseudoreplicate_concordance,
                  analysis_step_atac_encode4_partition_concordance
                  ):
    item = {
        'award': award['uuid'],
        'lab': encode_lab['uuid'],
        'title': 'ATAC-seq (replicated)',
        'assay_term_names': ['ATAC-seq'],
        'analysis_steps': [analysis_step_atac_encode4_alignment['@id'],
                           analysis_step_atac_encode4_pseudoreplicate_concordance['@id'],
                           analysis_step_atac_encode4_partition_concordance['@id']]
    }
    return testapp.post_json('/pipeline', item).json['@graph'][0]


@pytest.fixture
def ChIA_PIPE_pipeline(
    testapp,
    encode_lab,
    award,
    analysis_step_chia_alignment
):
    item = {
        'award': award['uuid'],
        'lab': encode_lab['uuid'],
        'title': 'Ruan Lab ChIA-PIPE Pipeline',
        'assay_term_names': ['ChIA-PET'],
        'analysis_steps': [analysis_step_chia_alignment['@id']]
    }
    return testapp.post_json('/pipeline', item).json['@graph'][0]


@pytest.fixture
def hic_pipeline(
    testapp,
    encode_lab,
    encode4_award,
    analysis_step_hic_chromatin_interactions
):
    item = {
        'award': encode4_award['uuid'],
        'lab': encode_lab['uuid'],
        'title': 'Hi-C pipeline',
        'assay_term_names': ['HiC'],
        'analysis_steps': [analysis_step_hic_chromatin_interactions['@id']]
    }
    return testapp.post_json('/pipeline', item).json['@graph'][0]
