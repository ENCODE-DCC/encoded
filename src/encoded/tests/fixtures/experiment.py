import pytest
from ..constants import *

@pytest.fixture
def experiment(testapp, lab, award, cell_free):
    item = {
        'lab': lab['@id'],
        'award': award['@id'],
        'assay_term_name': 'RNA-seq',
        'biosample_ontology': cell_free['uuid']
    }
    return testapp.post_json('/experiment', item).json['@graph'][0]


@pytest.fixture
def experiment_with_RNA_library(testapp, base_experiment, base_replicate, base_library):
    testapp.patch_json(base_library['@id'], {'nucleic_acid_term_name': 'RNA'})
    testapp.patch_json(base_replicate['@id'], {'library': base_library['@id']})
    return testapp.get(base_experiment['@id'] + '@@index-data')

@pytest.fixture
def base_fcc_experiment(testapp, lab, award, heart):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'assay_term_name': 'MPRA',
        'biosample_ontology': heart['uuid'],
        'status': 'in progress'
    }
    return testapp.post_json('/functional-characterization-experiments', item, status=201).json['@graph'][0]


@pytest.fixture
def pce_fcc_experiment(testapp, lab, award):
        return {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'assay_term_name': 'pooled clone sequencing',
        'schema_version': '2',
        'status': 'in progress'
    }

@pytest.fixture
def micro_rna_experiment(
    testapp,
    base_experiment,
    replicate_1_1,
    replicate_2_1,
    library_1,
    library_2,
    biosample_1,
    biosample_2,
    mouse_donor_1,
    file_fastq_3,
    file_fastq_4,
    file_bam_1_1,
    file_bam_2_1,
    file_tsv_1_1,
    file_tsv_1_2,
    spearman_correlation_quality_metric,
    micro_rna_quantification_quality_metric_1_2,
    micro_rna_mapping_quality_metric_2_1,
    analysis_step_run_bam,
    analysis_step_version_bam,
    analysis_step_bam,
    pipeline_bam,
):
    testapp.patch_json(file_fastq_3['@id'], {'read_length': 20})
    testapp.patch_json(file_fastq_4['@id'], {'read_length': 100})
    testapp.patch_json(
        file_bam_1_1['@id'],
        {'step_run': analysis_step_run_bam['@id'], 'assembly': 'mm10'}
    )
    testapp.patch_json(
        file_bam_2_1['@id'],
        {'step_run': analysis_step_run_bam['@id'], 'assembly': 'mm10'}
    )
    testapp.patch_json(
        pipeline_bam['@id'],
        {'title': 'microRNA-seq pipeline'}
    )
    testapp.patch_json(
        spearman_correlation_quality_metric['@id'],
        {'quality_metric_of': [file_tsv_1_1['@id'], file_tsv_1_2['@id']]}
    )
    testapp.patch_json(biosample_1['@id'], {'donor': mouse_donor_1['@id']})
    testapp.patch_json(biosample_2['@id'], {'donor': mouse_donor_1['@id']})
    testapp.patch_json(biosample_1['@id'], {'organism': '/organisms/mouse/'})
    testapp.patch_json(biosample_2['@id'], {'organism': '/organisms/mouse/'})
    testapp.patch_json(biosample_1['@id'], {'model_organism_sex': 'mixed'})
    testapp.patch_json(biosample_2['@id'], {'model_organism_sex': 'mixed'})
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_2['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    testapp.patch_json(
        base_experiment['@id'],
        {'status': 'released', 'date_released': '2016-01-01', 'assay_term_name': 'microRNA-seq'}
    )
    return testapp.get(base_experiment['@id'] + '@@index-data')


@pytest.fixture
def base_experiment(testapp, lab, award, heart):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'assay_term_name': 'RNA-seq',
        'biosample_ontology': heart['uuid'],
        'status': 'in progress'
    }
    return testapp.post_json('/experiment', item, status=201).json['@graph'][0]

@pytest.fixture
def experiment_1(testapp, lab, award, cell_free):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'assay_term_name': 'RNA-seq',
        'biosample_ontology': cell_free['uuid'],
        'status': 'in progress'
    }
    return testapp.post_json('/experiment', item, status=201).json['@graph'][0]


@pytest.fixture
def experiment_2(testapp, lab, award, cell_free):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'assay_term_name': 'RNA-seq',
        'biosample_ontology': cell_free['uuid'],
        'status': 'in progress'
    }
    return testapp.post_json('/experiment', item, status=201).json['@graph'][0]



@pytest.fixture
def experiment_chip_H3K4me3(testapp, lab, award, target_H3K4me3_1, ileum):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'status': 'released',
        'date_released': '2019-10-08',
        'biosample_ontology': ileum['uuid'],
        'assay_term_name': 'ChIP-seq',
        'target': target_H3K4me3_1['uuid']

    }
    return testapp.post_json('/experiment', item, status=201).json['@graph'][0]


@pytest.fixture
def base_experiment(testapp, lab, award, cell_free):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'assay_term_name': 'RNA-seq',
        'biosample_ontology': cell_free['uuid'],
        'status': 'in progress'
    }
    return testapp.post_json('/experiment', item, status=201).json['@graph'][0]

@pytest.fixture
def experiment_chip_CTCF(testapp, lab, award, target_CTCF_1, k562):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'status': 'released',
        'date_released': '2019-10-08',
        'biosample_ontology': k562['uuid'],
        'assay_term_name': 'ChIP-seq',
        'target': target_CTCF_1['uuid']

    }
    return testapp.post_json('/experiment', item, status=201).json['@graph'][0]


@pytest.fixture
def experiment_rna(testapp, lab, award, h1):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'status': 'released',
        'date_released': '2019-10-08',
        'assay_term_name': 'RNA-seq',
        'biosample_ontology': h1['uuid']

    }
    return testapp.post_json('/experiment', item, status=201).json['@graph'][0]


@pytest.fixture
def experiment_dnase(testapp, lab, award, heart):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'status': 'released',
        'date_released': '2019-10-08',
        'assay_term_name': 'DNase-seq',
        'biosample_ontology': heart['uuid']

    }
    return testapp.post_json('/experiment', item, status=201).json['@graph'][0]

@pytest.fixture
def file_exp(lab, award, testapp, experiment, ileum):
    item = {
        'lab': lab['uuid'],
        'award': award['uuid'],
        'assay_term_name': 'RAMPAGE',
        'biosample_ontology': ileum['uuid'],
        'possible_controls': [experiment['uuid']],
        'status': 'released',
        'date_released': '2016-01-01'
    }
    return testapp.post_json('/experiment', item, status=201).json['@graph'][0]

@pytest.fixture
def file_exp2(lab, award, testapp, ileum):
    item = {
        'lab': lab['uuid'],
        'award': award['uuid'],
        'assay_term_name': 'RAMPAGE',
        'biosample_ontology': ileum['uuid'],
        'status': 'released',
        'date_released': '2016-01-01'
    }
    return testapp.post_json('/experiment', item, status=201).json['@graph'][0]

@pytest.fixture
def ChIP_experiment(testapp, lab, award, cell_free, target, base_matched_set):
    item = {
        'lab': lab['@id'],
        'award': award['@id'],
        'assay_term_name': 'ChIP-seq',
        'biosample_ontology': cell_free['uuid'],
        'target': target['@id'],
        'possible_controls': [
            base_matched_set['@id']]
    }
    return testapp.post_json('/experiment', item).json['@graph'][0]


@pytest.fixture
def base_experiment(testapp, lab, award, cell_free):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'assay_term_name': 'RNA-seq',
        'biosample_ontology': cell_free['uuid'],
        'status': 'submitted',
        'date_submitted': '2015-07-23',
    }
    return testapp.post_json('/experiment', item, status=201).json['@graph'][0]


@pytest.fixture
def ctrl_experiment(testapp, lab, award, cell_free):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'biosample_ontology': cell_free['uuid'],
        'status': 'in progress',
        'assay_term_name': 'ChIP-seq'
    }
    return testapp.post_json('/experiment', item, status=201).json['@graph'][0]

@pytest.fixture
def reference_experiment_RNA_seq_1(testapp, lab, award, ileum):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'status': 'released',
        'date_released': '2019-01-08',
        'biosample_ontology': ileum['uuid'],
        'assay_term_name': 'RNA-seq'

    }
    return testapp.post_json('/experiment', item, status=201).json['@graph'][0]


@pytest.fixture
def reference_experiment_RRBS_1(testapp, lab, award, ileum):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'status': 'released',
        'date_released': '2019-01-08',
        'assay_term_name': 'RRBS',
        'biosample_ontology': ileum['uuid']

    }
    return testapp.post_json('/experiment', item, status=201).json['@graph'][0]

@pytest.fixture
def reference_experiment_WGBS_1(testapp, lab, award, ileum):
    item = {
        'award': award['uuid'],
        'biosample_ontology': ileum['uuid'],
        'lab': lab['uuid'],
        'status': 'released',
        'date_released': '2019-01-08',
        'assay_term_name': 'whole-genome shotgun bisulfite sequencing'

    }
    return testapp.post_json('/experiment', item, status=201).json['@graph'][0]


@pytest.fixture
def reference_experiment_chip_seq_control_1(testapp, lab, award, ileum):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'status': 'released',
        'date_released': '2019-01-08',
        'biosample_ontology': ileum['uuid'],
        'assay_term_name': 'ChIP-seq',
        'control_type': 'control'

    }
    return testapp.post_json('/experiment', item, status=201).json['@graph'][0]

@pytest.fixture
def reference_experiment_chip_seq_H3K27me3_1(testapp, lab, award, target_H3K27me3_1, ileum):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'status': 'released',
        'date_released': '2019-01-08',
        'biosample_ontology': ileum['uuid'],
        'assay_term_name': 'ChIP-seq',
        'target': target_H3K27me3_1['uuid']

    }
    return testapp.post_json('/experiment', item, status=201).json['@graph'][0]


@pytest.fixture
def reference_experiment_chip_seq_H3K36me3_1(testapp, lab, award, target_H3K36me3_1, ileum):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'status': 'released',
        'date_released': '2019-01-08',
        'biosample_ontology': ileum['uuid'],
        'assay_term_name': 'ChIP-seq',
        'target': target_H3K36me3_1['uuid']
    }
    return testapp.post_json('/experiment', item, status=201).json['@graph'][0]

@pytest.fixture
def reference_experiment_chip_seq_H3K4me1_1(testapp, lab, award, target_H3K4me1_1, ileum):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'status': 'released',
        'date_released': '2019-01-08',
        'biosample_ontology': ileum['uuid'],
        'assay_term_name': 'ChIP-seq',
        'target': target_H3K4me1_1['uuid']

    }
    return testapp.post_json('/experiment', item, status=201).json['@graph'][0]


@pytest.fixture
def reference_experiment_chip_seq_H3K4me3_1(testapp, lab, award, target_H3K4me3_1, ileum):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'status': 'released',
        'date_released': '2019-01-08',
        'biosample_ontology': ileum['uuid'],
        'assay_term_name': 'ChIP-seq',
        'target': target_H3K4me3_1['uuid']

    }
    return testapp.post_json('/experiment', item, status=201).json['@graph'][0]

@pytest.fixture
def reference_experiment_chip_seq_H3K27ac_1(testapp, lab, award, target_H3K27ac_1, ileum):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'status': 'released',
        'date_released': '2019-01-08',
        'biosample_ontology': ileum['uuid'],
        'assay_term_name': 'ChIP-seq',
        'target': target_H3K27ac_1['uuid']

    }
    return testapp.post_json('/experiment', item, status=201).json['@graph'][0]


@pytest.fixture
def reference_experiment_chip_seq_H3K9me3_1(testapp, lab, award, target_H3K9me3_1, ileum):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'status': 'released',
        'date_released': '2019-01-08',
        'biosample_ontology': ileum['uuid'],
        'assay_term_name': 'ChIP-seq',
        'target': target_H3K9me3_1['uuid']

    }
    return testapp.post_json('/experiment', item, status=201).json['@graph'][0]


