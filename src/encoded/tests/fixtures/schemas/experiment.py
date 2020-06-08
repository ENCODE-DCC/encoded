import pytest

@pytest.fixture
def experiment_chip_control(testapp, lab, award, ileum):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'status': 'released',
        'date_released': '2019-10-08',
        'biosample_ontology': ileum['uuid'],
        'assay_term_name': 'ChIP-seq',
        'control_type': 'input library'
    }
    return testapp.post_json('/experiment', item, status=201).json['@graph'][0]


@pytest.fixture
def experiment_chip_H3K4me3(testapp, lab, award, target_H3K4me3, ileum, experiment_chip_control):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'status': 'released',
        'date_released': '2019-10-08',
        'biosample_ontology': ileum['uuid'],
        'assay_term_name': 'ChIP-seq',
        'target': target_H3K4me3['uuid'],
        'possible_controls': [experiment_chip_control['@id']]

    }
    return testapp.post_json('/experiment', item, status=201).json['@graph'][0]


@pytest.fixture
def experiment_chip_H3K27me3(testapp, lab, award, target_H3K27me3, experiment_chip_control, ileum):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'biosample_ontology': ileum['uuid'],
        'assay_term_name': 'ChIP-seq',
        'target': target_H3K27me3['uuid'],
        'possible_controls': [experiment_chip_control['uuid']]

    }
    return testapp.post_json('/experiment', item, status=201).json['@graph'][0]


@pytest.fixture
def experiment_chip_CTCF(testapp, lab, award, target_CTCF, k562):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'status': 'released',
        'date_released': '2019-10-08',
        'biosample_ontology': k562['uuid'],
        'assay_term_name': 'ChIP-seq',
        'target': target_CTCF['uuid']

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
def experiment_no_read_length(
    testapp,
    experiment,
    bam_file,
    file_fastq_no_read_length,
    replicate_1_1,
    base_library,
    analysis_step_bam,
    analysis_step_version_bam,
    analysis_step_run_bam,
    encode_lab,
):
    testapp.patch_json(replicate_1_1['@id'], {'experiment': experiment['@id'],
                                              'library': base_library['@id'],
                                              })
    testapp.patch_json(file_fastq_no_read_length['@id'], {'dataset': experiment['@id'],
                                                          'replicate':replicate_1_1['@id'],
                                                          })
    testapp.patch_json(bam_file['@id'], {'dataset': experiment['@id'],
                                         'step_run': analysis_step_run_bam['@id'],
                                         'assembly': 'GRCh38',
                                         'lab': encode_lab['@id'],
                                         'derived_from': [file_fastq_no_read_length['@id']],
                                         })
    testapp.patch_json(experiment['@id'], {'status': 'released',
                                           'date_released': '2016-01-01',
                                           'assay_term_name': 'long read RNA-seq',
                                           })
    return testapp.get(experiment['@id'] + '@@index-data')


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
def reference_experiment_RNA_seq(testapp, lab, award, ileum):
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
def reference_experiment_RRBS(testapp, lab, award, ileum):
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
def reference_experiment_WGBS(testapp, lab, award, ileum):
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
def reference_experiment_chip_seq_control(testapp, lab, award, ileum):
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
def reference_experiment_chip_seq_H3K27me3(testapp, lab, award, target_H3K27me3, ileum):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'status': 'released',
        'date_released': '2019-01-08',
        'biosample_ontology': ileum['uuid'],
        'assay_term_name': 'ChIP-seq',
        'target': target_H3K27me3['uuid']

    }
    return testapp.post_json('/experiment', item, status=201).json['@graph'][0]


@pytest.fixture
def reference_experiment_chip_seq_H3K36me3(testapp, lab, award, target_H3K36me3, ileum):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'status': 'released',
        'date_released': '2019-01-08',
        'biosample_ontology': ileum['uuid'],
        'assay_term_name': 'ChIP-seq',
        'target': target_H3K36me3['uuid']
    }
    return testapp.post_json('/experiment', item, status=201).json['@graph'][0]


@pytest.fixture
def reference_experiment_chip_seq_H3K4me1(testapp, lab, award, target_H3K4me1, ileum):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'status': 'released',
        'date_released': '2019-01-08',
        'biosample_ontology': ileum['uuid'],
        'assay_term_name': 'ChIP-seq',
        'target': target_H3K4me1['uuid']

    }
    return testapp.post_json('/experiment', item, status=201).json['@graph'][0]


@pytest.fixture
def reference_experiment_chip_seq_H3K4me3(testapp, lab, award, target_H3K4me3, ileum):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'status': 'released',
        'date_released': '2019-01-08',
        'biosample_ontology': ileum['uuid'],
        'assay_term_name': 'ChIP-seq',
        'target': target_H3K4me3['uuid']

    }
    return testapp.post_json('/experiment', item, status=201).json['@graph'][0]


@pytest.fixture
def reference_experiment_chip_seq_H3K27ac(testapp, lab, award, target_H3K27ac, ileum):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'status': 'released',
        'date_released': '2019-01-08',
        'biosample_ontology': ileum['uuid'],
        'assay_term_name': 'ChIP-seq',
        'target': target_H3K27ac['uuid']

    }
    return testapp.post_json('/experiment', item, status=201).json['@graph'][0]


@pytest.fixture
def reference_experiment_chip_seq_H3K9me3(testapp, lab, award, target_H3K9me3, ileum):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'status': 'released',
        'date_released': '2019-01-08',
        'biosample_ontology': ileum['uuid'],
        'assay_term_name': 'ChIP-seq',
        'target': target_H3K9me3['uuid']

    }
    return testapp.post_json('/experiment', item, status=201).json['@graph'][0]

@pytest.fixture
def experiment_pipeline_error(testapp, lab, award, cell_free):
    item = {
        'lab': lab['@id'],
        'award': award['@id'],
        'assay_term_name': 'ChIP-seq',
        'biosample_ontology': cell_free['uuid'],
        'internal_status': 'pipeline error',
    }
    return item


@pytest.fixture
def experiment_no_error(testapp, lab, award, cell_free):
    item = {
        'lab': lab['@id'],
        'award': award['@id'],
        'assay_term_name': 'ChIP-seq',
        'biosample_ontology': cell_free['uuid'],
        'internal_status': 'release ready',
    }
    return item


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
def base_experiment_submitted(testapp, lab, award, cell_free):
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
def experiment_1_0(root, experiment, file, file_ucsc_browser_composite):
    item = root.get_by_uuid(experiment['uuid'])
    properties = item.properties.copy()
    assert root.get_by_uuid(
        file['uuid']).properties['dataset'] == str(item.uuid)
    assert root.get_by_uuid(
        file_ucsc_browser_composite['uuid']).properties['dataset'] != str(item.uuid)
    properties.update({
        'schema_version': '1',
        'files': [file['uuid'], file_ucsc_browser_composite['uuid']]
    })
    return properties


@pytest.fixture
def experiment_2_0():
    return {
        'schema_version': '2',
        'encode2_dbxrefs': ['wgEncodeEH002945'],
        'geo_dbxrefs': ['GSM99494'],
    }


@pytest.fixture
def experiment_3():
    return {
        'schema_version': '3',
        'status': "DELETED",
    }


@pytest.fixture
def experiment_6():
    return {
        'schema_version': '6',
        'dataset_type': 'experiment',
    }


@pytest.fixture
def experiment_7(root, experiment):
    item = root.get_by_uuid(experiment['uuid'])
    properties = item.properties.copy()
    properties.update({
        'schema_version': '7',
        'dbxrefs': ['UCSC-ENCODE-cv:K562', 'UCSC-ENCODE-cv:K562'],
        'aliases': ['testing:123', 'testing:123']
    })
    return properties


@pytest.fixture
def experiment_10(root, experiment):
    item = root.get_by_uuid(experiment['uuid'])
    properties = item.properties.copy()
    properties.update({
        'schema_version': '10',
        'status': 'in progress',
        'aliases': [
            'andrew-fire:my_experiment',
            'j-michael-cherry:Lib:XZ:20100107:11--ChIP:XZ:20100104:09:AdiposeNuclei:H3K4Me3',
            'roadmap-epigenomics:Bisulfite-Seq analysis of ucsf-4* stem cell line from UCSF-4||Tue Apr 16 16:10:36 -0500 2013||85822',
            'encode:[this is]_qu#ite:bad" ',
            'manuel-garber:10% DMSO for 2 hours',
            'UCSC_encode_db:Illumina_HiSeq_2000',
            'encode:Illumina_HiSeq_2000'
        ]
    })
    return properties


@pytest.fixture
def experiment_13(root, experiment):
    item = root.get_by_uuid(experiment['uuid'])
    properties = item.properties.copy()
    properties.update({
        'schema_version': '13',
        'status': 'proposed',
    })
    return properties


@pytest.fixture
def experiment_14(root, experiment):
    item = root.get_by_uuid(experiment['uuid'])
    properties = item.properties.copy()
    properties.update({
        'schema_version': '14',
        'biosample_type': 'in vitro sample',
    })
    return properties


@pytest.fixture
def experiment_15(root, experiment):
    item = root.get_by_uuid(experiment['uuid'])
    properties = item.properties.copy()
    properties.update({
        'schema_version': '15',
        'biosample_type': 'immortalized cell line'
    })
    return properties


@pytest.fixture
def experiment_16(root, experiment):
    item = root.get_by_uuid(experiment['uuid'])
    properties = item.properties.copy()
    properties.update({
        'schema_version': '16',
        'biosample_type': 'immortalized cell line',
        'status': 'ready for review'
    })
    return properties


@pytest.fixture
def experiment_17(root, experiment):
    item = root.get_by_uuid(experiment['uuid'])
    properties = item.properties.copy()
    properties.update({
        'schema_version': '17',
        'biosample_type': 'immortalized cell line',
        'status': 'started'
    })
    return properties


@pytest.fixture
def experiment_21(root, experiment):
    item = root.get_by_uuid(experiment['uuid'])
    properties = item.properties.copy()
    properties.update({
        'schema_version': '21',
        'biosample_type': 'induced pluripotent stem cell line',
        'status': 'started'
    })
    return properties


@pytest.fixture
def experiment_22(root, experiment):
    item = root.get_by_uuid(experiment['uuid'])
    properties = item.properties.copy()
    properties.update({
        'schema_version': '22',
        'biosample_type': 'primary cell',
        'biosample_term_id': 'CL:0000765',
        'biosample_term_name': 'erythroblast',
        'internal_tags': ['cre_inputv10', 'cre_inputv11', 'ENCYCLOPEDIAv3'],
        'status': 'started'
    })
    return properties


@pytest.fixture
def experiment_25(root, experiment):
    item = root.get_by_uuid(experiment['uuid'])
    properties = item.properties.copy()
    properties.update({
        'schema_version': '25',
        'assay_term_name': 'ISO-seq'
    })
    return properties


@pytest.fixture
def experiment_26(root, experiment):
    item = root.get_by_uuid(experiment['uuid'])
    properties = item.properties.copy()
    properties.update({
        'schema_version': '26',
        'assay_term_name': 'single-nuclei ATAC-seq'
    })
    return properties


@pytest.fixture
def experiment_27(root, experiment):
    item = root.get_by_uuid(experiment['uuid'])
    properties = item.properties.copy()
    properties.update({
                      'schema_version': '27',
                      'experiment_classification': ['functional genomics assay']
                      
    })
    return properties


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
def experiment_with_RNA_library(
    testapp,
    base_experiment,
    base_replicate,
    base_library,
):
    testapp.patch_json(base_library['@id'], {'nucleic_acid_term_name': 'RNA'})
    testapp.patch_json(base_replicate['@id'], {'library': base_library['@id']})
    return testapp.get(base_experiment['@id'] + '@@index-data')


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
def micro_rna_experiment(
    testapp,
    base_experiment,
    replicate_1_1,
    replicate_2_1,
    library_1,
    library_2,
    biosample_1,
    biosample_2,
    mouse_donor_1_6,
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
    testapp.patch_json(biosample_1['@id'], {'donor': mouse_donor_1_6['@id']})
    testapp.patch_json(biosample_2['@id'], {'donor': mouse_donor_1_6['@id']})
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
def experiment_with_analyses(testapp, lab, award, heart, file_bam_1_1, file_bam_2_1):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'assay_term_name': 'ChIP-seq',
        'status': 'in progress',
        'biosample_ontology': heart['uuid'],
        'analyses': [
            {
                'files': [file_bam_1_1['@id'], file_bam_2_1['@id']]
            }
        ]
    }
    return testapp.post_json('/experiment', item, status=201).json['@graph'][0]


@pytest.fixture
def experiment_with_analyses_2(testapp, lab, award, heart, file_bam_1_1, file_bam_2_1, bam_file):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'assay_term_name': 'ChIP-seq',
        'status': 'in progress',
        'biosample_ontology': heart['uuid'],
        'analyses': [
            {
                'files': [file_bam_1_1['@id'], file_bam_2_1['@id'], bam_file['@id']]
            }
        ]
    }
    return testapp.post_json('/experiment', item, status=201).json['@graph'][0]

@pytest.fixture
def experiment_28(testapp, lab, award, heart):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'assay_term_name': 'Mint-ChIP-seq',
        'biosample_ontology': heart['uuid'],
        'status': 'in progress'
    }
    return testapp.post_json('/experiment', item, status=201).json['@graph'][0]


@pytest.fixture
def experiment_v28(root, experiment):
    item = root.get_by_uuid(experiment['uuid'])
    properties = item.properties.copy()
    properties.update({
            'schema_version': '28',
            'internal_status': 'pipeline error',
            'pipeline_error_detail': 'The pipeline didn\'t work for reasons',
            'notes': 'Insert essential details here'
    })
    return properties


@pytest.fixture
def ATAC_experiment(testapp, lab, award, cell_free):
    item = {
        'lab': lab['@id'],
        'award': award['@id'],
        'assay_term_name': 'ATAC-seq',
        'biosample_ontology': cell_free['uuid']
    }
    return testapp.post_json('/experiment', item).json['@graph'][0]
