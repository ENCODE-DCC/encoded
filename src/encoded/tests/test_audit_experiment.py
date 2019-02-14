import pytest

RED_DOT = """data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUA
AAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO
9TXL0Y4OHwAAAABJRU5ErkJggg=="""


def collect_audit_errors(result, error_types=None):
    errors = result.json['audit']
    errors_list = []
    if error_types:
        for error_type in error_types:
            errors_list.extend(errors[error_type])
    else:
        for error_type in errors:
            errors_list.extend(errors[error_type])
    return errors_list


@pytest.fixture
def library_no_biosample(testapp, lab, award):
    item = {
        'nucleic_acid_term_name': 'DNA',
        'lab': lab['@id'],
        'award': award['@id']
    }
    return testapp.post_json('/library', item).json['@graph'][0]


@pytest.fixture
def base_library(testapp, lab, award, base_biosample):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'nucleic_acid_term_name': 'DNA',
        'biosample': base_biosample['uuid']
    }
    return testapp.post_json('/library', item, status=201).json['@graph'][0]


@pytest.fixture
def base_replicate(testapp, base_experiment):
    item = {
        'biological_replicate_number': 1,
        'technical_replicate_number': 1,
        'experiment': base_experiment['@id'],
    }
    return testapp.post_json('/replicate', item, status=201).json['@graph'][0]


@pytest.fixture
def base_replicate_two(testapp, base_experiment):
    item = {
        'biological_replicate_number': 1,
        'technical_replicate_number': 2,
        'experiment': base_experiment['@id'],
    }
    return testapp.post_json('/replicate', item, status=201).json['@graph'][0]


@pytest.fixture
def base_target(testapp, gene):
    item = {
        'genes': [gene['uuid']],
        'label': 'XYZ',
        'investigated_as': ['transcription factor']
    }
    return testapp.post_json('/target', item, status=201).json['@graph'][0]


@pytest.fixture
def tag_target(testapp, organism):
    item = {
        'target_organism': organism['uuid'],
        'label': 'eGFP',
        'investigated_as': ['tag']
    }
    return testapp.post_json('/target', item, status=201).json['@graph'][0]


@pytest.fixture
def recombinant_target(testapp, gene):
    item = {
        'genes': [gene['uuid']],
        'label': 'eGFP-CTCF',
        'investigated_as': ['recombinant protein', 'transcription factor']
    }
    return testapp.post_json('/target', item, status=201).json['@graph'][0]


@pytest.fixture
def fly_organism(testapp):
    item = {
        'taxon_id': "7227",
        'name': "dmelanogaster",
        'scientific_name': "Drosophila melanogaster"
    }
    return testapp.post_json('/organism', item, status=201).json['@graph'][0]


@pytest.fixture
def mouse_H3K9me3(testapp, mouse):
    item = {
        'target_organism': mouse['@id'],
        'label': 'H3K9me3',
        'investigated_as': ['histone', 'broad histone mark']
    }
    return testapp.post_json('/target', item, status=201).json['@graph'][0]


@pytest.fixture
def control_target(testapp, organism):
    item = {
        'target_organism': organism['uuid'],
        'label': 'Control',
        'investigated_as': ['control']
    }
    return testapp.post_json('/target', item, status=201).json['@graph'][0]


@pytest.fixture
def base_antibody(testapp, award, lab, source, organism, target):
    return {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'source': source['uuid'],
        'host_organism': organism['uuid'],
        'targets': [target['uuid']],
        'product_id': 'KDKF123',
        'lot_id': '123'
    }


@pytest.fixture
def IgG_antibody(testapp, award, lab, source, organism, control_target):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'source': source['uuid'],
        'host_organism': organism['uuid'],
        'targets': [control_target['uuid']],
        'product_id': 'ABCDEF',
        'lot_id': '321'
    }
    return testapp.post_json('/antibodies', item, status=201).json['@graph'][0]


@pytest.fixture
def base_antibody_characterization1(testapp, lab, award, target, antibody_lot, organism, k562):
    item = {
        'award': award['uuid'],
        'target': target['uuid'],
        'lab': lab['uuid'],
        'characterizes': antibody_lot['uuid'],
        'primary_characterization_method': 'immunoblot',
        'attachment': {'download': 'red-dot.png', 'href': RED_DOT},
        'characterization_reviews': [
            {
                'lane': 2,
                'organism': organism['uuid'],
                'biosample_ontology': k562['uuid'],
                'lane_status': 'compliant'
            }
        ]
    }
    return testapp.post_json('/antibody-characterizations', item, status=201).json['@graph'][0]


@pytest.fixture
def base_antibody_characterization2(testapp, lab, award, target, antibody_lot, organism):
    item = {
        'award': award['uuid'],
        'target': target['uuid'],
        'lab': lab['uuid'],
        'characterizes': antibody_lot['uuid'],
        'secondary_characterization_method': 'dot blot assay',
        'attachment': {'download': 'red-dot.png', 'href': RED_DOT}
    }
    return testapp.post_json('/antibody-characterizations', item, status=201).json['@graph'][0]


@pytest.fixture
def ctrl_experiment(testapp, lab, award, control_target, cell_free):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'biosample_ontology': cell_free['uuid'],
        'status': 'in progress',
        'assay_term_name': 'ChIP-seq',
        'experiment_classification': ['functional genomics assay']
    }
    return testapp.post_json('/experiment', item, status=201).json['@graph'][0]


@pytest.fixture
def IgG_ctrl_rep(testapp, ctrl_experiment, IgG_antibody):
    item = {
        'experiment': ctrl_experiment['@id'],
        'biological_replicate_number': 1,
        'technical_replicate_number': 1,
        'antibody': IgG_antibody['@id'],
        'status': 'released'
    }
    return testapp.post_json('/replicate', item, status=201).json['@graph'][0]


@pytest.fixture
def treatment_time_series(testapp, lab, award):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
    }
    return testapp.post_json('/treatment_time_series', item, status=201).json['@graph'][0]


@pytest.fixture
def library_1(testapp, lab, award, base_biosample):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'nucleic_acid_term_name': 'DNA',
        'biosample': base_biosample['uuid']
    }
    return testapp.post_json('/library', item, status=201).json['@graph'][0]


@pytest.fixture
def library_2(testapp, lab, award, base_biosample):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'nucleic_acid_term_name': 'DNA',
        'biosample': base_biosample['uuid']
    }
    return testapp.post_json('/library', item, status=201).json['@graph'][0]


@pytest.fixture
def replicate_1_1(testapp, base_experiment):
    item = {
        'biological_replicate_number': 1,
        'technical_replicate_number': 1,
        'experiment': base_experiment['@id'],
    }
    return testapp.post_json('/replicate', item, status=201).json['@graph'][0]


@pytest.fixture
def replicate_2_1(testapp, base_experiment):
    item = {
        'biological_replicate_number': 2,
        'technical_replicate_number': 1,
        'experiment': base_experiment['@id'],
    }
    return testapp.post_json('/replicate', item, status=201).json['@graph'][0]


@pytest.fixture
def replicate_1_2(testapp, base_experiment):
    item = {
        'biological_replicate_number': 1,
        'technical_replicate_number': 2,
        'experiment': base_experiment['@id'],
    }
    return testapp.post_json('/replicate', item, status=201).json['@graph'][0]


@pytest.fixture
def biosample_1(testapp, lab, award, source, organism, heart):
    item = {
        'award': award['uuid'],
        'biosample_ontology': heart['uuid'],
        'lab': lab['uuid'],
        'organism': organism['uuid'],
        'source': source['uuid']
    }
    return testapp.post_json('/biosample', item, status=201).json['@graph'][0]


@pytest.fixture
def biosample_2(testapp, lab, award, source, organism, heart):
    item = {
        'award': award['uuid'],
        'biosample_ontology': heart['uuid'],
        'lab': lab['uuid'],
        'organism': organism['uuid'],
        'source': source['uuid']
    }
    return testapp.post_json('/biosample', item, status=201).json['@graph'][0]


@pytest.fixture
def file_fastq(testapp, lab, award, base_experiment, base_replicate, platform1):
    item = {
        'dataset': base_experiment['@id'],
        'replicate': base_replicate['@id'],
        'file_format': 'fastq',
        'md5sum': '91b474b6411514393507f4ebfa66d47a',
        'output_type': 'reads',
        'platform': platform1['@id'],
        "read_length": 50,
        'run_type': "single-ended",
        'file_size': 34,
        'lab': lab['@id'],
        'award': award['@id'],
        'status': 'in progress',  # avoid s3 upload codepath
    }
    return testapp.post_json('/file', item).json['@graph'][0]


@pytest.fixture
def file_fastq_2(testapp, lab, award, base_experiment, base_replicate, platform1):
    item = {
        'dataset': base_experiment['@id'],
        'replicate': base_replicate['@id'],
        'file_format': 'fastq',
        'md5sum': '94be74b6e14515393547f4ebfa66d77a',
        'run_type': "paired-ended",
        'platform': platform1['@id'],
        'paired_end': '1',
        'output_type': 'reads',
        "read_length": 50,
        'file_size': 34,
        'lab': lab['@id'],
        'award': award['@id'],
        'status': 'in progress',  # avoid s3 upload codepath
    }
    return testapp.post_json('/file', item).json['@graph'][0]


@pytest.fixture
def file_fastq_3(testapp, lab, award, base_experiment, replicate_1_1, platform1):
    item = {
        'dataset': base_experiment['@id'],
        'replicate': replicate_1_1['@id'],
        'file_format': 'fastq',
        'file_size': 34,
        'platform': platform1['@id'],
        'output_type': 'reads',
        "read_length": 50,
        'md5sum': '21be74b6e11515393507f4ebfa66d77a',
        'run_type': "paired-ended",
        'paired_end': '1',
        'lab': lab['@id'],
        'award': award['@id'],
        'status': 'in progress',  # avoid s3 upload codepath
    }
    return testapp.post_json('/file', item).json['@graph'][0]


@pytest.fixture
def file_fastq_4(testapp, lab, award, base_experiment, replicate_2_1, platform1):
    item = {
        'dataset': base_experiment['@id'],
        'replicate': replicate_2_1['@id'],
        'platform': platform1['@id'],
        'file_format': 'fastq',
        'file_size': 34,
        'md5sum': '11be74b6e11515393507f4ebfa66d77a',
        'run_type': "paired-ended",
        'paired_end': '1',
        'output_type': 'reads',
        "read_length": 50,
        'lab': lab['@id'],
        'award': award['@id'],
        'status': 'in progress',  # avoid s3 upload codepath
    }
    return testapp.post_json('/file', item).json['@graph'][0]


@pytest.fixture
def file_fastq_5(testapp, lab, award, base_experiment, replicate_2_1, platform1):
    item = {
        'dataset': base_experiment['@id'],
        'platform': platform1['@id'],
        'replicate': replicate_2_1['@id'],
        'file_format': 'fastq',
        'md5sum': '91be79b6e11515993509f4ebfa66d77a',
        'run_type': "paired-ended",
        'paired_end': '1',
        "read_length": 50,
        'output_type': 'reads',
        'file_size': 34,
        'lab': lab['@id'],
        'award': award['@id'],
        'status': 'in progress',  # avoid s3 upload codepath
    }
    return testapp.post_json('/file', item).json['@graph'][0]


@pytest.fixture
def file_fastq_6(testapp, lab, award, base_experiment, replicate_1_1, platform1):
    item = {
        'dataset': base_experiment['@id'],
        'replicate': replicate_1_1['@id'],
        'file_format': 'fastq',
        'file_size': 34,
        'platform': platform1['@id'],
        'output_type': 'reads',
        "read_length": 50,
        'md5sum': '21be74b6e11515393507f4ebfa66d77a',
        'run_type': "single-ended",
        'lab': lab['@id'],
        'award': award['@id'],
        'status': 'in progress',  # avoid s3 upload codepath
    }
    return testapp.post_json('/file', item).json['@graph'][0]


@pytest.fixture
def file_bam(testapp, lab, award, base_experiment, base_replicate):
    item = {
        'dataset': base_experiment['@id'],
        'replicate': base_replicate['@id'],
        'file_format': 'bam',
        'md5sum': 'd41d8cd98f00b204e9800998ecf8427e',
        'output_type': 'alignments',
        'assembly': 'mm10',
        'lab': lab['@id'],
        'file_size': 34,
        'award': award['@id'],
        'status': 'in progress',  # avoid s3 upload codepath
    }
    return testapp.post_json('/file', item).json['@graph'][0]


@pytest.fixture
def file_bam_1_1(testapp, encode_lab, award, base_experiment, file_fastq_3):
    item = {
        'dataset': base_experiment['@id'],
        'derived_from': [file_fastq_3['@id']],
        'file_format': 'bam',
        'assembly': 'mm10',
        'file_size': 34,
        'md5sum': '91be44b6e11515394407f4ebfa66d77a',
        'output_type': 'alignments',
        'lab': encode_lab['@id'],
        'award': award['@id'],
        'status': 'in progress',  # avoid s3 upload codepath
    }
    return testapp.post_json('/file', item).json['@graph'][0]


@pytest.fixture
def file_bam_2_1(testapp, encode_lab, award, base_experiment, file_fastq_4):
    item = {
        'dataset': base_experiment['@id'],
        'derived_from': [file_fastq_4['@id']],
        'file_format': 'bam',
        'assembly': 'mm10',
        'file_size': 34,
        'md5sum': '91be71b6e11515377807f4ebfa66d77a',
        'output_type': 'alignments',
        'lab': encode_lab['@id'],
        'award': award['@id'],
        'status': 'in progress',  # avoid s3 upload codepath
    }
    return testapp.post_json('/file', item).json['@graph'][0]


@pytest.fixture
def bam_quality_metric_1_1(testapp, analysis_step_run_bam, file_bam_1_1, award, lab):
    item = {
        'step_run': analysis_step_run_bam['@id'],
        'quality_metric_of': [file_bam_1_1['@id']],
        'Uniquely mapped reads number': 1000,
        'award': award['@id'],
        'lab': lab['@id']
    }

    return testapp.post_json('/star_quality_metric', item).json['@graph'][0]


@pytest.fixture
def bam_quality_metric_2_1(testapp, analysis_step_run_bam, file_bam_2_1, award, lab):
    item = {
        'step_run': analysis_step_run_bam['@id'],
        'quality_metric_of': [file_bam_2_1['@id']],
        'Uniquely mapped reads number': 1000,
        'award': award['@id'],
        'lab': lab['@id']
    }

    return testapp.post_json('/star_quality_metric', item).json['@graph'][0]


@pytest.fixture
def chip_seq_quality_metric(testapp, analysis_step_run_bam, file_bam_1_1, award, lab):
    item = {
        'step_run': analysis_step_run_bam['@id'],
        'quality_metric_of': [file_bam_1_1['@id']],
        'award': award['@id'],
        'lab': lab['@id']
    }
    return testapp.post_json('/samtools_flagstats_quality_metric', item).json['@graph'][0]


@pytest.fixture
def hotspot_quality_metric(testapp, analysis_step_run_bam, file_bam_1_1, award, encode_lab):
    item = {
        'SPOT1 score': 0.3345,
        'step_run': analysis_step_run_bam['@id'],
        'quality_metric_of': [file_bam_1_1['@id']],
        'award': award['@id'],
        'lab': encode_lab['@id']
    }
    return testapp.post_json('/hotspot-quality-metrics', item).json['@graph'][0]


@pytest.fixture
def chipseq_filter_quality_metric(testapp, analysis_step_run_bam, file_bam_1_1, lab, award):
    item = {
        'step_run': analysis_step_run_bam['@id'],
        'award': award['@id'],
        'lab': lab['@id'],
        'quality_metric_of': [file_bam_1_1['@id']],
        'NRF': 0.1,
        'PBC1': 0.3,
        'PBC2': 11
    }

    return testapp.post_json('/chipseq-filter-quality-metrics', item).json['@graph'][0]


@pytest.fixture
def mad_quality_metric_1_2(testapp, analysis_step_run_bam, file_tsv_1_2, award, lab):
    item = {
        'step_run': analysis_step_run_bam['@id'],
        'quality_metric_of': [file_tsv_1_2['@id']],
        'Spearman correlation': 0.1,
        'MAD of log ratios': 3.1,
        'award': award['@id'],
        'lab': lab['@id']
    }

    return testapp.post_json('/mad_quality_metric', item).json['@graph'][0]


@pytest.fixture
def correlation_quality_metric(testapp, analysis_step_run_bam, file_tsv_1_2, award, lab):
    item = {
        'step_run': analysis_step_run_bam['@id'],
        'quality_metric_of': [file_tsv_1_2['@id']],
        'Pearson correlation': 0.1,
        'award': award['@id'],
        'lab': lab['@id']
    }

    return testapp.post_json('/correlation_quality_metric', item).json['@graph'][0]


@pytest.fixture
def duplicates_quality_metric(testapp, analysis_step_run_bam, file_bam_1_1, lab, award):
    item = {
        'step_run': analysis_step_run_bam['@id'],
        'quality_metric_of': [file_bam_1_1['@id']],
        'Percent Duplication': 0.23,
        'award': award['@id'],
        'lab': lab['@id']
    }

    return testapp.post_json('/duplicates_quality_metric', item).json['@graph'][0]


@pytest.fixture
def wgbs_quality_metric(testapp, analysis_step_run_bam, file_bed_methyl, award, lab):
    item = {
        'step_run': analysis_step_run_bam['@id'],
        'award': award['@id'],
        'lab': lab['@id'],
        'quality_metric_of': [file_bed_methyl['@id']],
        'lambda C methylated in CHG context': '13.1%',
        'lambda C methylated in CHH context': '12.5%',
        'lambda C methylated in CpG context': '0.9%'}
    return testapp.post_json('/bismark_quality_metric', item).json['@graph'][0]



@pytest.fixture
def file_bed_methyl(base_experiment, award, encode_lab, testapp, analysis_step_run_bam):
    item = {
        'dataset': base_experiment['uuid'],
        "file_format": "bed",
        "file_format_type": "bedMethyl",
        "file_size": 66569,
        "assembly": "mm10",
        "md5sum": "91be74b6e11515223507f4ebf266d77a",
        "output_type": "methylation state at CpG",
        "award": award["uuid"],
        "lab": encode_lab["uuid"],
        "status": "released",
        "step_run": analysis_step_run_bam['uuid']
    }
    return testapp.post_json('/file', item, status=201).json['@graph'][0]


@pytest.fixture
def file_tsv_1_2(base_experiment, award, encode_lab, testapp, analysis_step_run_bam):
    item = {
        'dataset': base_experiment['uuid'],
        'file_format': 'tsv',
        'file_size': 3654,
        'assembly': 'mm10',
        'genome_annotation': 'M4',
        'md5sum': '912e7ab6e11515393507f42bfa66d77a',
        'output_type': 'gene quantifications',
        'award': award['uuid'],
        'lab': encode_lab['uuid'],
        'status': 'released',
        'step_run': analysis_step_run_bam['uuid']
    }
    return testapp.post_json('/file', item, status=201).json['@graph'][0]


@pytest.fixture
def file_tsv_1_1(base_experiment, award, encode_lab, testapp, analysis_step_run_bam):
    item = {
        'dataset': base_experiment['uuid'],
        'file_format': 'tsv',
        'file_size': 36524,
        'assembly': 'mm10',
        'genome_annotation': 'M4',
        'md5sum': '91be74b6e315153935a7f4ecfa66d77a',
        'output_type': 'gene quantifications',
        'award': award['uuid'],
        'lab': encode_lab['uuid'],
        'status': 'released',
        'step_run': analysis_step_run_bam['uuid']
    }
    return testapp.post_json('/file', item, status=201).json['@graph'][0]


def test_audit_experiment_missing_fragmentation_method(testapp,
                                                       base_experiment,
                                                       replicate_1_1,
                                                       replicate_2_1,
                                                       library_1,
                                                       library_2):
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'HiC'})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'missing fragmentation method'
               for error in collect_audit_errors(res))


def test_audit_experiment_inconsistent_fragmentation_method(testapp,
                                                            base_experiment,
                                                            replicate_1_1,
                                                            replicate_2_1,
                                                            library_1,
                                                            library_2):
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'HiC'})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    testapp.patch_json(library_1['@id'], {'fragmentation_method': 'chemical (HindIII restriction)'})
    testapp.patch_json(library_2['@id'], {'fragmentation_method': 'chemical (MboI restriction)'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'inconsistent fragmentation method'
               for error in collect_audit_errors(res))


def test_audit_experiment_mixed_libraries(testapp,
                                          base_experiment,
                                          replicate_1_1,
                                          replicate_2_1,
                                          library_1,
                                          library_2):
    testapp.patch_json(library_1['@id'], {'nucleic_acid_term_name': 'DNA'})
    testapp.patch_json(library_2['@id'], {'nucleic_acid_term_name': 'RNA'})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'mixed libraries'
               for error in collect_audit_errors(res))


def test_audit_experiment_RNA_library_RIN(testapp,
                                          base_experiment,
                                          replicate_1_1,
                                          library_1):
    testapp.patch_json(library_1['@id'], {'nucleic_acid_term_name': 'RNA'})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'missing RIN'
               for error in collect_audit_errors(res))
    testapp.patch_json(library_1['@id'], {'rna_integrity_number': 7})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert all(error['category'] != 'missing RIN'
               for error in collect_audit_errors(res))


def test_audit_experiment_released_with_unreleased_files(testapp, base_experiment, file_fastq):
    testapp.patch_json(base_experiment['@id'], {'status': 'released',
                                                'date_released': '2016-01-01'})
    testapp.patch_json(file_fastq['@id'], {'status': 'in progress'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'mismatched file status'
               for error in collect_audit_errors(res))


def test_ChIP_possible_control(testapp, base_experiment, ctrl_experiment, IgG_ctrl_rep):
    testapp.patch_json(base_experiment['@id'], {'possible_controls': [ctrl_experiment['@id']],
                                                'assay_term_name': 'ChIP-seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'invalid possible_control'
               for error in collect_audit_errors(res))


def test_ChIP_possible_control_roadmap(testapp, base_experiment, ctrl_experiment, IgG_ctrl_rep,
                                       award):
    testapp.patch_json(award['@id'], {'rfa': 'Roadmap'})
    testapp.patch_json(base_experiment['@id'], {'possible_controls': [ctrl_experiment['@id']],
                                                'assay_term_name': 'ChIP-seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'invalid possible_control'
               for error in collect_audit_errors(res))


def test_audit_input_control(testapp, base_experiment,
                             ctrl_experiment, IgG_ctrl_rep,
                             control_target):
    testapp.patch_json(ctrl_experiment['@id'], {'target': control_target['@id']})
    testapp.patch_json(base_experiment['@id'], {'possible_controls': [ctrl_experiment['@id']],
                                                'assay_term_name': 'ChIP-seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'missing input control'
               for error in collect_audit_errors(res))


def test_audit_experiment_target(testapp, base_experiment):
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'ChIP-seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'missing target'
               for error in collect_audit_errors(res))
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'PLAC-seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'missing target'
               for error in collect_audit_errors(res))


def test_audit_experiment_replicated(testapp, base_experiment, base_replicate, base_library):
    testapp.patch_json(base_experiment['@id'], {'status': 'submitted', 'date_submitted': '2015-03-03'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'unreplicated experiment'
               for error in collect_audit_errors(res))


def test_audit_sc_experiment_replicated(testapp, base_experiment, base_replicate, base_library, single_cell):
    testapp.patch_json(base_experiment['@id'], {
        'status': 'submitted',
        'biosample_ontology': single_cell['uuid'],
        'date_submitted': '2015-03-03'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert all(error['category'] != 'unreplicated experiment'
               for error in collect_audit_errors(res))


def test_audit_experiment_technical_replicates_same_library(testapp, base_experiment,
                                                            base_replicate, base_replicate_two,
                                                            base_library):
    testapp.patch_json(base_replicate['@id'], {'library': base_library['@id']})
    testapp.patch_json(base_replicate_two['@id'], {'library': base_library['@id']})
    testapp.patch_json(base_experiment['@id'], {
                       'replicates': [base_replicate['@id'], base_replicate_two['@id']]})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'sequencing runs labeled as technical replicates'
               for error in collect_audit_errors(res))


def test_audit_experiment_biological_replicates_biosample(
        testapp, base_experiment, base_biosample,
        library_1, library_2, replicate_1_1, replicate_2_1):
    testapp.patch_json(library_1['@id'], {'biosample': base_biosample['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': base_biosample['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'biological replicates with identical biosample'
               for error in collect_audit_errors(res))


def test_audit_experiment_technical_replicates_biosample(
        testapp, base_experiment, biosample_1, biosample_2,
        library_1, library_2, replicate_1_1, replicate_1_2):
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_2['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_1_2['@id'], {'library': library_2['@id']})

    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'technical replicates with not identical biosample'
               for error in collect_audit_errors(res))


def test_audit_experiment_with_libraryless_replicated(
        testapp, base_experiment, base_replicate, base_library):
    testapp.patch_json(base_experiment['@id'], {'status': 'submitted', 'date_submitted': '2015-03-03'})
    testapp.patch_json(base_experiment['@id'], {'replicates': [base_replicate['@id']]})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'replicate with no library'
               for error in collect_audit_errors(res))


def test_audit_experiment_single_cell_replicated(
        testapp, base_experiment, base_replicate, base_library):
    testapp.patch_json(base_experiment['@id'], {'status': 'submitted', 'date_submitted': '2015-03-03'})
    testapp.patch_json(base_experiment['@id'], {'assay_term_name':
                                                'single cell isolation followed by RNA-seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert all(error['category'] != 'unreplicated experiment'
               for error in collect_audit_errors(res))


def test_audit_experiment_RNA_bind_n_seq_replicated(testapp, base_experiment, base_replicate,
                                                    base_library):
    testapp.patch_json(base_experiment['@id'], {'status': 'submitted', 'date_submitted': '2015-03-03'})
    testapp.patch_json(base_experiment['@id'], {'assay_term_name':
                                                'RNA Bind-n-Seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert all(error['category'] != 'unreplicated experiment'
               for error in collect_audit_errors(res))


def test_audit_experiment_roadmap_replicated(
        testapp, base_experiment, base_replicate, base_library, award):
    testapp.patch_json(award['@id'], {'rfa': 'Roadmap'})
    testapp.patch_json(base_experiment['@id'], {'award': award['@id']})
    testapp.patch_json(base_experiment['@id'],
                       {'status': 'released', 'date_released': '2016-01-01'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert all(error['category'] != 'unreplicated experiment'
               for error in collect_audit_errors(res))


def test_audit_experiment_spikeins(testapp, base_experiment, base_replicate, base_library):
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'RNA-seq'})
    testapp.patch_json(base_library['@id'], {'size_range': '>200'})
    testapp.patch_json(base_replicate['@id'], {'library': base_library['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'missing spikeins'
               for error in collect_audit_errors(res))


def test_audit_experiment_not_tag_antibody(
        testapp, base_experiment, base_replicate, organism, antibody_lot):
    other_target = testapp.post_json(
        '/target',
        {'target_organism': organism['uuid'],
            'label': 'eGFP-AVCD',
            'investigated_as': ['recombinant protein']}).json['@graph'][0]
    testapp.patch_json(base_replicate['@id'], {'antibody': antibody_lot['uuid']})
    testapp.patch_json(base_experiment['@id'],
                       {'assay_term_name': 'ChIP-seq', 'target': other_target['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'not tagged antibody'
               for error in collect_audit_errors(res))


def test_audit_experiment_target_tag_antibody(
        testapp, base_experiment, base_replicate, organism, base_antibody, tag_target):
    ha_target = testapp.post_json(
        '/target',
        {'target_organism': organism['uuid'],
            'label': 'HA-ABCD',
            'investigated_as': ['recombinant protein']}).json['@graph'][0]
    base_antibody['targets'] = [tag_target['@id']]
    tag_antibody = testapp.post_json('/antibody_lot', base_antibody).json['@graph'][0]
    testapp.patch_json(base_replicate['@id'], {'antibody': tag_antibody['@id']})
    testapp.patch_json(
        base_experiment['@id'], {'assay_term_name': 'ChIP-seq', 'target': ha_target['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'mismatched tag target'
               for error in collect_audit_errors(res))


def test_audit_experiment_target_mismatch(
        testapp, base_experiment, base_replicate, base_target, antibody_lot):
    testapp.patch_json(base_replicate['@id'], {'antibody': antibody_lot['uuid']})
    testapp.patch_json(
        base_experiment['@id'], {'assay_term_name': 'ChIP-seq', 'target': base_target['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'inconsistent target'
               for error in collect_audit_errors(res))


def test_audit_experiment_no_characterizations_antibody(testapp,
                                                        base_experiment,
                                                        base_replicate,
                                                        base_library,
                                                        base_biosample,
                                                        antibody_lot,
                                                        target,
                                                        k562):
    testapp.patch_json(base_replicate['@id'], {'antibody': antibody_lot['@id'],
                                               'library': base_library['@id']})
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'ChIP-seq',
                                                'biosample_ontology': k562['uuid'],
                                                'target': target['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'uncharacterized antibody'
               for error in collect_audit_errors(res))


def test_audit_experiment_wrong_organism_histone_antibody(testapp,
                                                          base_experiment,
                                                          wrangler,
                                                          base_antibody,
                                                          base_replicate,
                                                          base_library,
                                                          base_biosample,
                                                          mouse_H3K9me3,
                                                          target_H3K9me3,
                                                          base_antibody_characterization1,
                                                          base_antibody_characterization2,
                                                          mouse,
                                                          human,
                                                          k562,
                                                          mel):
    # Mouse biosample in mouse ChIP-seq experiment but supporting antibody characterizations
    # are compliant in human but not mouse.
    base_antibody['targets'] = [mouse_H3K9me3['@id'], target_H3K9me3['@id']]
    histone_antibody = testapp.post_json('/antibody_lot', base_antibody).json['@graph'][0]
    testapp.patch_json(base_biosample['@id'], {'organism': mouse['@id']})
    characterization_reviews = [
        {
            'biosample_ontology': mel['uuid'],
            'organism': mouse['@id'],
            'lane_status': 'not compliant',
            'lane': 1
        },
        {
            'biosample_ontology': k562['uuid'],
            'organism': human['@id'],
            'lane_status': 'compliant',
            'lane': 2
        }
    ]
    testapp.patch_json(
        base_antibody_characterization1['@id'],
        {'target': target_H3K9me3['@id'],
            'characterizes': histone_antibody['@id'],
            'status': 'compliant',
            'reviewed_by': wrangler['@id'],
            'characterization_reviews': characterization_reviews})
    testapp.patch_json(
        base_antibody_characterization2['@id'],
        {'target': target_H3K9me3['@id'],
            'characterizes': histone_antibody['@id'],
            'status': 'compliant',
            'reviewed_by': wrangler['@id']})
    testapp.patch_json(base_replicate['@id'], {'antibody': histone_antibody['@id'],
                                               'library': base_library['@id'],
                                               'experiment': base_experiment['@id']})
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'ChIP-seq',
                                                'biosample_ontology': mel['uuid'],
                                                'target': mouse_H3K9me3['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'antibody not characterized to standard'
               for error in collect_audit_errors(res))


def test_audit_experiment_partially_characterized_antibody(testapp,
                                                           base_experiment,
                                                           wrangler,
                                                           base_target,
                                                           base_antibody,
                                                           base_replicate,
                                                           base_library,
                                                           base_biosample,
                                                           base_antibody_characterization1,
                                                           base_antibody_characterization2,
                                                           human,
                                                           hepg2,
                                                           k562):
    # K562 biosample in ChIP-seq experiment with exempt primary in K562 and in progress
    # secondary - leading to partial characterization.
    base_antibody['targets'] = [base_target['@id']]
    TF_antibody = testapp.post_json('/antibody_lot', base_antibody).json['@graph'][0]
    characterization_reviews = [
        {
            'biosample_ontology': hepg2['uuid'],
            'organism': human['@id'],
            'lane_status': 'not compliant',
            'lane': 1
        },
        {
            'biosample_ontology': k562['uuid'],
            'organism': human['@id'],
            'lane_status': 'exempt from standards',
            'lane': 2
        }
    ]
    testapp.patch_json(
        base_antibody_characterization1['@id'],
        {'target': base_target['@id'],
            'characterizes': TF_antibody['@id'],
            'status': 'compliant',
            'reviewed_by': wrangler['@id'],
            'characterization_reviews': characterization_reviews})

    testapp.patch_json(base_replicate['@id'], {'antibody': TF_antibody['@id'],
                                               'library': base_library['@id'],
                                               'experiment': base_experiment['@id']})
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'ChIP-seq',
                                                'biosample_ontology': k562['uuid'],
                                                'target': base_target['@id']})

    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'partially characterized antibody'
               for error in collect_audit_errors(res))


def test_audit_experiment_geo_submission(testapp, base_experiment):
    testapp.patch_json(
        base_experiment['@id'], {'status': 'released', 'date_released': '2016-01-01'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'experiment not submitted to GEO'
               for error in collect_audit_errors(res))


def test_audit_experiment_biosample_match(testapp, base_experiment,
                                          base_biosample, base_replicate,
                                          base_library, h1, ileum):
    testapp.patch_json(base_biosample['@id'], {'biosample_ontology': h1['uuid']})
    testapp.patch_json(base_replicate['@id'], {'library': base_library['@id']})
    testapp.patch_json(base_experiment['@id'], {'biosample_ontology': ileum['uuid']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'inconsistent library biosample'
               for error in collect_audit_errors(res))


def test_audit_experiment_documents(testapp, base_experiment, base_library, base_replicate):
    testapp.patch_json(base_replicate['@id'], {'library': base_library['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'missing documents'
               for error in collect_audit_errors(res))


def test_audit_experiment_documents_excluded(testapp, base_experiment,
                                             base_library, award, base_replicate):
    testapp.patch_json(base_replicate['@id'], {'library': base_library['@id']})
    testapp.patch_json(award['@id'], {'rfa': 'modENCODE'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] != 'missing documents'
               for error in collect_audit_errors(res))


def test_audit_experiment_model_organism_mismatched_sex(testapp,
                                                        base_experiment,
                                                        replicate_1_1,
                                                        replicate_2_1,
                                                        library_1,
                                                        library_2,
                                                        biosample_1,
                                                        biosample_2,
                                                        mouse_donor_1):
    testapp.patch_json(biosample_1['@id'], {'donor': mouse_donor_1['@id']})
    testapp.patch_json(biosample_2['@id'], {'donor': mouse_donor_1['@id']})
    testapp.patch_json(biosample_1['@id'], {'organism': '/organisms/mouse/'})
    testapp.patch_json(biosample_2['@id'], {'organism': '/organisms/mouse/'})
    testapp.patch_json(biosample_1['@id'], {'model_organism_sex': 'male'})
    testapp.patch_json(biosample_2['@id'], {'model_organism_sex': 'female'})
    testapp.patch_json(biosample_1['@id'], {'model_organism_age_units': 'day',
                                            'model_organism_age': '54'})
    testapp.patch_json(biosample_2['@id'], {'model_organism_age_units': 'day',
                                            'model_organism_age': '54'})
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_2['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'inconsistent sex'
               for error in collect_audit_errors(res))


def test_audit_experiment_model_organism_mismatched_age(testapp,
                                                        base_experiment,
                                                        replicate_1_1,
                                                        replicate_2_1,
                                                        library_1,
                                                        library_2,
                                                        biosample_1,
                                                        biosample_2,
                                                        mouse_donor_1,
                                                        mouse_donor_2):
    testapp.patch_json(biosample_1['@id'], {'donor': mouse_donor_1['@id']})
    testapp.patch_json(biosample_2['@id'], {'donor': mouse_donor_1['@id']})
    testapp.patch_json(biosample_1['@id'], {'organism': '/organisms/mouse/'})
    testapp.patch_json(biosample_2['@id'], {'organism': '/organisms/mouse/'})
    testapp.patch_json(biosample_1['@id'], {'model_organism_age_units': 'day',
                                            'model_organism_age': '51'})
    testapp.patch_json(biosample_2['@id'], {'model_organism_age_units': 'day',
                                            'model_organism_age': '54'})
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_2['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})

    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'inconsistent age'
               for error in collect_audit_errors(res))


def test_audit_experiment_model_organism_mismatched_donor(testapp,
                                                          base_experiment,
                                                          replicate_1_1,
                                                          replicate_2_1,
                                                          library_1,
                                                          library_2,
                                                          biosample_1,
                                                          biosample_2,
                                                          mouse_donor_1,
                                                          mouse_donor_2):
    testapp.patch_json(biosample_1['@id'], {'donor': mouse_donor_1['@id']})
    testapp.patch_json(biosample_2['@id'], {'donor': mouse_donor_2['@id']})
    testapp.patch_json(biosample_1['@id'], {'organism': '/organisms/mouse/'})
    testapp.patch_json(biosample_2['@id'], {'organism': '/organisms/mouse/'})
    testapp.patch_json(biosample_1['@id'], {'model_organism_sex': 'mixed'})
    testapp.patch_json(biosample_2['@id'], {'model_organism_sex': 'mixed'})
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_2['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'inconsistent donor'
               for error in collect_audit_errors(res))


def test_audit_experiment_with_library_without_biosample(testapp, base_experiment, base_replicate,
                                                         library_no_biosample):
    testapp.patch_json(base_replicate['@id'], {'library': library_no_biosample['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'missing biosample'
               for error in collect_audit_errors(res))


def test_audit_experiment_with_RNA_library_no_size_range(testapp, base_experiment, base_replicate,
                                                         base_library):
    testapp.patch_json(base_library['@id'], {'nucleic_acid_term_name': 'RNA'})
    testapp.patch_json(base_replicate['@id'], {'library': base_library['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'missing RNA fragment size'
               for error in collect_audit_errors(res))


def test_audit_experiment_with_RNA_library_with_size_range(testapp, base_experiment, base_replicate,
                                                           base_library):
    testapp.patch_json(base_library['@id'], {'nucleic_acid_term_name': 'RNA', 'size_range': '>200'})
    testapp.patch_json(base_replicate['@id'], {'library': base_library['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert all(error['category'] != 'missing RNA fragment size'
               for error in collect_audit_errors(res))


def test_audit_experiment_with_RNA_library_array_size_range(testapp, base_experiment,
                                                            base_replicate,
                                                            base_library):
    testapp.patch_json(base_library['@id'], {'nucleic_acid_term_name': 'RNA'})
    testapp.patch_json(base_replicate['@id'], {'library': base_library['@id']})
    testapp.patch_json(base_experiment['@id'], {'assay_term_name':
                                                'transcription profiling by array assay'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert all(error['category'] != 'missing RNA fragment size'
               for error in collect_audit_errors(res))


def test_audit_experiment_replicate_with_file(testapp, file_fastq,
                                              base_experiment,
                                              base_replicate,
                                              base_library):
    testapp.patch_json(file_fastq['@id'], {'replicate': base_replicate['@id']})
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'RNA-seq'})
    testapp.patch_json(base_experiment['@id'], {'status': 'released',
                                                'date_released': '2016-01-01'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert all((error['category'] != 'missing raw data in replicate')
               for error in collect_audit_errors(res))


def test_audit_experiment_pipeline_assay_term_name_consistency(
        testapp,
        experiment, bam_file,
        analysis_step_run_bam,
        analysis_step_version_bam,
        analysis_step_bam,
        pipeline_bam):
    testapp.patch_json(experiment['@id'], {'status': 'released', 'date_released': '2016-01-01'})
    testapp.patch_json(bam_file['@id'], {'step_run': analysis_step_run_bam['@id']})
    testapp.patch_json(pipeline_bam['@id'], {'title':
                                             'RNA-seq of long RNAs (single-end, unstranded)',
                                             'assay_term_names': ['RNA-seq', 'RAMPAGE']})
    testapp.patch_json(experiment['@id'], {'assay_term_name': 'ChIP-seq'})
    res = testapp.get(experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'inconsistent assay_term_name'
               for error in collect_audit_errors(res))


def test_audit_experiment_replicate_with_no_files(testapp,
                                                  base_experiment,
                                                  base_replicate,
                                                  base_library):
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'RNA-seq'})
    testapp.patch_json(base_experiment['@id'], {'status': 'released',
                                                'date_released': '2016-01-01'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'missing raw data in replicate'
               for error in collect_audit_errors(res))


def test_audit_experiment_replicate_with_no_files_dream(testapp,
                                                        base_experiment,
                                                        base_replicate,
                                                        base_library):
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'RNA-seq',
                                                'internal_tags': ['DREAM'],
                                                'status': 'released',
                                                'date_released': '2016-01-01'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert all(error['category'] != 'missing raw data in replicate'
               for error in collect_audit_errors(res))


def test_audit_experiment_replicate_with_no_files_warning(testapp, file_bed_methyl,
                                                          base_experiment,
                                                          base_replicate,
                                                          base_library):
    testapp.patch_json(file_bed_methyl['@id'], {'replicate': base_replicate['@id']})
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'RNA-seq'})
    testapp.patch_json(base_experiment['@id'], {'status': 'in progress'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] ==
               'missing raw data in replicate' for
               error in collect_audit_errors(res, ['ERROR']))


def test_audit_experiment_not_uploaded_files(testapp, file_bam,
                                             base_experiment,
                                             base_replicate,
                                             base_library):
    testapp.patch_json(file_bam['@id'], {'status': 'upload failed'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'file validation error'
               for error in collect_audit_errors(res))


def test_audit_experiment_uploading_files(testapp, file_bam,
                                          base_experiment,
                                          base_replicate,
                                          base_library):
    testapp.patch_json(file_bam['@id'], {'status': 'uploading'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert all(error['category'] != 'file validation error'
               for error in collect_audit_errors(res))
    assert any(error['category'] == 'file in uploading state'
               for error in collect_audit_errors(res))


def test_audit_experiment_replicate_with_no_fastq_files(testapp, file_bam,
                                                        base_experiment,
                                                        base_replicate,
                                                        base_library):
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'RNA-seq'})
    testapp.patch_json(base_experiment['@id'], {'status': 'released',
                                                'date_released': '2016-01-01'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'missing raw data in replicate'
               for error in collect_audit_errors(res))


def test_audit_experiment_mismatched_length_sequencing_files(testapp, file_bam, file_fastq,
                                                             base_experiment, file_fastq_2,
                                                             base_replicate,
                                                             base_library):
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'ChIP-seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'mixed run types'
               for error in collect_audit_errors(res))


def test_audit_experiment_mismatched_platforms(testapp, file_fastq,
                                               base_experiment, file_fastq_2,
                                               base_replicate, platform1,
                                               base_library, platform2):
    testapp.patch_json(file_fastq['@id'], {'platform': platform1['@id']})
    testapp.patch_json(file_fastq_2['@id'], {'platform': platform2['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'inconsistent platforms'
               for error in collect_audit_errors(res))


def test_audit_experiment_archived_files_mismatched_platforms(
        testapp, file_fastq, base_experiment, file_fastq_2, base_replicate,
        platform1, base_library, platform2):
    testapp.patch_json(file_fastq['@id'], {'platform': platform1['@id'],
                                           'status': 'archived'})
    testapp.patch_json(file_fastq_2['@id'], {'platform': platform2['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert all(error['category'] != 'inconsistent platforms'
               for error in collect_audit_errors(res))


def test_audit_experiment_internal_tag(testapp, base_experiment,
                                       base_biosample,
                                       library_1,
                                       replicate_1_1):
    testapp.patch_json(base_biosample['@id'], {'internal_tags': ['ENTEx']})
    testapp.patch_json(library_1['@id'], {'biosample': base_biosample['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'inconsistent internal tags'
               for error in collect_audit_errors(res))


def test_audit_experiment_internal_tags(testapp, base_experiment,
                                        biosample_1,
                                        biosample_2,
                                        library_1,
                                        library_2,
                                        replicate_1_1,
                                        replicate_1_2):
    testapp.patch_json(biosample_1['@id'], {'internal_tags': ['ENTEx']})
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(biosample_2['@id'], {'internal_tags': ['ENTEx', 'SESCC']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_2['@id']})
    testapp.patch_json(replicate_1_2['@id'], {'library': library_2['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'inconsistent internal tags'
               for error in collect_audit_errors(res))


def test_audit_experiment_internal_tags2(testapp, base_experiment,
                                         biosample_1,
                                         biosample_2,
                                         library_1,
                                         library_2,
                                         replicate_1_1,
                                         replicate_1_2):
    testapp.patch_json(biosample_1['@id'], {'internal_tags': ['ENTEx']})
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_2['@id']})
    testapp.patch_json(replicate_1_2['@id'], {'library': library_2['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] ==
               'inconsistent internal tags' for error in collect_audit_errors(res))


def test_audit_experiment_mismatched_inter_paired_sequencing_files(testapp,
                                                                   base_experiment,
                                                                   replicate_1_1,
                                                                   replicate_2_1,
                                                                   library_1,
                                                                   library_2,
                                                                   biosample_1,
                                                                   biosample_2,
                                                                   mouse_donor_1,
                                                                   mouse_donor_2,
                                                                   file_fastq_6,
                                                                   file_fastq_4):
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'ChIP-seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'mixed run types'
               for error in collect_audit_errors(res))


def test_audit_experiment_DNase_mismatched_inter_paired_sequencing_files(testapp,
                                                                         base_experiment,
                                                                         replicate_1_1,
                                                                         replicate_2_1,
                                                                         library_1,
                                                                         library_2,
                                                                         biosample_1,
                                                                         biosample_2,
                                                                         mouse_donor_1,
                                                                         mouse_donor_2,
                                                                         file_fastq_6,
                                                                         file_fastq_4):
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'DNase-seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert all(error['category'] != 'mixed run types'
               for error in collect_audit_errors(res))


def test_audit_experiment_mismatched_inter_length_sequencing_files(testapp,
                                                                   base_experiment,
                                                                   replicate_1_1,
                                                                   replicate_2_1,
                                                                   library_1,
                                                                   library_2,
                                                                   biosample_1,
                                                                   biosample_2,
                                                                   mouse_donor_1,
                                                                   mouse_donor_2,
                                                                   file_fastq_3,
                                                                   file_fastq_4,
                                                                   file_fastq_5):
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'ChIP-seq'})
    testapp.patch_json(file_fastq_3['@id'], {'read_length': 50})
    testapp.patch_json(file_fastq_5['@id'], {'read_length': 150})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'mixed read lengths'
               for error in collect_audit_errors(res))


def test_audit_experiment_mismatched_valid_inter_length_sequencing_files(testapp,
                                                                         base_experiment,
                                                                         replicate_1_1,
                                                                         replicate_2_1,
                                                                         library_1,
                                                                         library_2,
                                                                         biosample_1,
                                                                         biosample_2,
                                                                         mouse_donor_1,
                                                                         mouse_donor_2,
                                                                         file_fastq_3,
                                                                         file_fastq_4,
                                                                         file_fastq_5):
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'ChIP-seq'})
    testapp.patch_json(file_fastq_3['@id'], {'read_length': 50})
    testapp.patch_json(file_fastq_5['@id'], {'read_length': 52})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert all(error['category'] != 'mixed read lengths'
               for error in collect_audit_errors(res))


def test_audit_experiment_DNase_mismatched_valid_inter_length_sequencing_files(
    testapp, base_experiment,
    replicate_1_1, replicate_2_1,
    library_1, library_2,
    biosample_1, biosample_2,
    mouse_donor_1,  mouse_donor_2,
    file_fastq_3, file_fastq_4,
        file_fastq_5):
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'DNase-seq'})
    testapp.patch_json(file_fastq_4['@id'], {'read_length': 27})
    testapp.patch_json(file_fastq_3['@id'], {'read_length': 27})
    testapp.patch_json(file_fastq_5['@id'], {'read_length': 36})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert all(error['category'] != 'mixed read lengths'
               for error in collect_audit_errors(res))


def test_audit_experiment_rampage_standards(testapp,
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
                                            file_tsv_1_2,
                                            mad_quality_metric_1_2,
                                            bam_quality_metric_1_1,
                                            bam_quality_metric_2_1,
                                            analysis_step_run_bam,
                                            analysis_step_version_bam,
                                            analysis_step_bam,
                                            pipeline_bam):
    testapp.patch_json(file_fastq_3['@id'], {'read_length': 100})
    testapp.patch_json(file_fastq_4['@id'], {'read_length': 100})

    testapp.patch_json(file_bam_1_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'assembly': 'mm10'})
    testapp.patch_json(file_bam_2_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'assembly': 'mm10'})
    testapp.patch_json(bam_quality_metric_1_1['@id'],
                       {'Number of reads mapped to multiple loci': 100})
    testapp.patch_json(bam_quality_metric_2_1['@id'],
                       {'Number of reads mapped to multiple loci': 100})
    testapp.patch_json(pipeline_bam['@id'], {'title':
                                             'RAMPAGE (paired-end, stranded)'})

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
    testapp.patch_json(base_experiment['@id'], {'status': 'released',
                                                'date_released': '2016-01-01',
                                                'assay_term_name': 'RAMPAGE'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] ==
               'extremely low read depth' for error in collect_audit_errors(res))


def test_audit_experiment_small_rna_standards(testapp,
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
                                              file_tsv_1_2,
                                              mad_quality_metric_1_2,
                                              bam_quality_metric_1_1,
                                              bam_quality_metric_2_1,
                                              analysis_step_run_bam,
                                              analysis_step_version_bam,
                                              analysis_step_bam,
                                              pipeline_bam):
    testapp.patch_json(file_fastq_3['@id'], {'read_length': 20})
    testapp.patch_json(file_fastq_4['@id'], {'read_length': 100})

    testapp.patch_json(file_bam_1_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'assembly': 'mm10'})
    testapp.patch_json(file_bam_2_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'assembly': 'mm10'})

    testapp.patch_json(pipeline_bam['@id'], {'title':
                                             'Small RNA-seq single-end pipeline'})

    testapp.patch_json(bam_quality_metric_1_1['@id'], {'Uniquely mapped reads number': 26000000})
    testapp.patch_json(bam_quality_metric_2_1['@id'], {'Uniquely mapped reads number': 26000000})
    testapp.patch_json(bam_quality_metric_1_1['@id'],
                       {'Number of reads mapped to multiple loci': 1000000})
    testapp.patch_json(bam_quality_metric_2_1['@id'],
                       {'Number of reads mapped to multiple loci': 1000000})
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
    testapp.patch_json(base_experiment['@id'], {'status': 'released',
                                                'date_released': '2016-01-01',
                                                'assay_term_name': 'RNA-seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] ==
               'low read depth' for error in collect_audit_errors(res))


def test_audit_experiment_MAD_long_rna_standards(testapp,
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
                                                 file_tsv_1_2,
                                                 mad_quality_metric_1_2,
                                                 bam_quality_metric_1_1,
                                                 bam_quality_metric_2_1,
                                                 analysis_step_run_bam,
                                                 analysis_step_version_bam,
                                                 analysis_step_bam,
                                                 pipeline_bam):
    testapp.patch_json(file_fastq_3['@id'], {'read_length': 20})
    testapp.patch_json(file_fastq_4['@id'], {'read_length': 100})

    testapp.patch_json(file_bam_1_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'assembly': 'mm10'})
    testapp.patch_json(file_bam_2_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'assembly': 'mm10'})

    testapp.patch_json(pipeline_bam['@id'], {'title':
                                             'RNA-seq of long RNAs (paired-end, stranded)'})

    testapp.patch_json(bam_quality_metric_1_1['@id'], {'Uniquely mapped reads number': 29000000})
    testapp.patch_json(bam_quality_metric_2_1['@id'], {'Uniquely mapped reads number': 38000000})
    testapp.patch_json(bam_quality_metric_1_1['@id'],
                       {'Number of reads mapped to multiple loci': 1})
    testapp.patch_json(bam_quality_metric_2_1['@id'],
                       {'Number of reads mapped to multiple loci': 1})
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
    testapp.patch_json(base_experiment['@id'], {'status': 'released',
                                                'date_released': '2016-01-01',
                                                'assay_term_name': 'RNA-seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] ==
               'low replicate concordance' for error in collect_audit_errors(res))


def test_audit_experiment_long_rna_standards_crispr(testapp,
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
                                                    file_tsv_1_2,
                                                    mad_quality_metric_1_2,
                                                    bam_quality_metric_1_1,
                                                    bam_quality_metric_2_1,
                                                    analysis_step_run_bam,
                                                    analysis_step_version_bam,
                                                    analysis_step_bam,
                                                    pipeline_bam):
    testapp.patch_json(file_fastq_3['@id'], {'read_length': 20})
    testapp.patch_json(file_fastq_4['@id'], {'read_length': 100})

    testapp.patch_json(file_bam_1_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'assembly': 'mm10'})
    testapp.patch_json(file_bam_2_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'assembly': 'mm10'})

    testapp.patch_json(pipeline_bam['@id'], {'title':
                                             'RNA-seq of long RNAs (paired-end, stranded)'})

    testapp.patch_json(bam_quality_metric_1_1['@id'], {'Uniquely mapped reads number': 5000000})
    testapp.patch_json(bam_quality_metric_2_1['@id'], {'Uniquely mapped reads number': 10000000})
    testapp.patch_json(bam_quality_metric_1_1['@id'],
                       {'Number of reads mapped to multiple loci': 10})
    testapp.patch_json(bam_quality_metric_2_1['@id'],
                       {'Number of reads mapped to multiple loci': 100})
    testapp.patch_json(biosample_1['@id'], {'donor': mouse_donor_1['@id']})
    testapp.patch_json(biosample_2['@id'], {'donor': mouse_donor_1['@id']})
    testapp.patch_json(biosample_1['@id'], {'organism': '/organisms/mouse/'})
    testapp.patch_json(biosample_2['@id'], {'organism': '/organisms/mouse/'})
    testapp.patch_json(biosample_1['@id'], {'model_organism_sex': 'mixed'})
    testapp.patch_json(biosample_2['@id'], {'model_organism_sex': 'mixed'})
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id'],
                                          'size_range': '>200'})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_2['@id'],
                                          'size_range': '>200'})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    testapp.patch_json(base_experiment['@id'], {'status': 'released',
                                                'date_released': '2016-01-01',
                                                'assay_term_name': 'CRISPR genome editing followed by RNA-seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(
        error['category'] ==
        'insufficient read depth' for error in collect_audit_errors(res)) and \
        any(error['category'] ==
            'missing spikeins' for error in collect_audit_errors(res))


def test_audit_experiment_long_rna_standards(testapp,
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
                                             mad_quality_metric_1_2,
                                             bam_quality_metric_1_1,
                                             bam_quality_metric_2_1,
                                             analysis_step_run_bam,
                                             analysis_step_version_bam,
                                             analysis_step_bam,
                                             pipeline_bam):
    testapp.patch_json(file_fastq_3['@id'], {'read_length': 20})
    testapp.patch_json(file_fastq_4['@id'], {'read_length': 100})

    testapp.patch_json(file_bam_1_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'assembly': 'mm10'})
    testapp.patch_json(file_bam_2_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'assembly': 'mm10'})

    testapp.patch_json(pipeline_bam['@id'], {'title':
                                             'RNA-seq of long RNAs (paired-end, stranded)'})

    testapp.patch_json(bam_quality_metric_1_1['@id'], {'Uniquely mapped reads number': 1000000})
    testapp.patch_json(bam_quality_metric_2_1['@id'], {'Uniquely mapped reads number': 38000000})
    testapp.patch_json(bam_quality_metric_1_1['@id'],
                       {'Number of reads mapped to multiple loci': 10})
    testapp.patch_json(bam_quality_metric_2_1['@id'],
                       {'Number of reads mapped to multiple loci': 30})
    testapp.patch_json(mad_quality_metric_1_2['@id'], {'quality_metric_of': [
                                                       file_tsv_1_1['@id'],
                                                       file_tsv_1_2['@id']]})
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
    testapp.patch_json(base_experiment['@id'], {'status': 'released',
                                                'date_released': '2016-01-01',
                                                'assay_term_name': 'RNA-seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] ==
               'insufficient read depth' for error in collect_audit_errors(res))


def test_audit_experiment_long_rna_standards_encode2(testapp,
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
                                                     mad_quality_metric_1_2,
                                                     bam_quality_metric_1_1,
                                                     bam_quality_metric_2_1,
                                                     analysis_step_run_bam,
                                                     analysis_step_version_bam,
                                                     analysis_step_bam,
                                                     pipeline_bam,
                                                     encode2_award):
    testapp.patch_json(file_fastq_3['@id'], {'read_length': 20})
    testapp.patch_json(file_fastq_4['@id'], {'read_length': 100})

    testapp.patch_json(file_bam_1_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'assembly': 'mm10'})
    testapp.patch_json(file_bam_2_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'assembly': 'mm10'})

    testapp.patch_json(pipeline_bam['@id'], {'title':
                                             'RNA-seq of long RNAs (paired-end, stranded)'})

    testapp.patch_json(bam_quality_metric_1_1['@id'], {'Uniquely mapped reads number': 21000000})
    testapp.patch_json(bam_quality_metric_2_1['@id'], {'Uniquely mapped reads number': 38000000})
    testapp.patch_json(bam_quality_metric_1_1['@id'],
                       {'Number of reads mapped to multiple loci': 10})
    testapp.patch_json(bam_quality_metric_2_1['@id'],
                       {'Number of reads mapped to multiple loci': 30})
    testapp.patch_json(mad_quality_metric_1_2['@id'], {'quality_metric_of': [
                                                       file_tsv_1_1['@id'],
                                                       file_tsv_1_2['@id']]})
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
    testapp.patch_json(base_experiment['@id'], {'status': 'released',
                                                'date_released': '2016-01-01',
                                                'assay_term_name': 'RNA-seq',
                                                'award': encode2_award['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert all(error['category'] !=
               'insufficient read depth' for error in collect_audit_errors(res))


def test_audit_experiment_chip_seq_standards_depth(testapp,
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
                                                   file_tsv_1_2,
                                                   mad_quality_metric_1_2,
                                                   chip_seq_quality_metric,
                                                   analysis_step_run_bam,
                                                   analysis_step_version_bam,
                                                   analysis_step_bam,
                                                   pipeline_bam,
                                                   target_H3K27ac):

    testapp.patch_json(chip_seq_quality_metric['@id'], {'quality_metric_of': [file_bam_1_1['@id'],
                                                                              file_bam_2_1['@id']],
                                                        'processing_stage': 'filtered',
                                                        'total': 30000000,
                                                        'mapped': 30000000,
                                                        'read1': 100, 'read2': 100})
    testapp.patch_json(file_fastq_3['@id'], {'read_length': 20})
    testapp.patch_json(file_fastq_4['@id'], {'read_length': 100})

    testapp.patch_json(file_bam_1_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'assembly': 'mm10',
                                             'derived_from': [file_fastq_3['@id']]})
    testapp.patch_json(file_bam_2_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'assembly': 'mm10',
                                             'derived_from': [file_fastq_4['@id']]})
    testapp.patch_json(pipeline_bam['@id'], {'title':
                                             'ChIP-seq read mapping'})
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
    testapp.patch_json(base_experiment['@id'], {'target': target_H3K27ac['@id'],
                                                'status': 'released',
                                                'date_released': '2016-01-01',
                                                'assay_term_name': 'ChIP-seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] ==
               'low read depth' for error in collect_audit_errors(res))


def test_audit_experiment_chip_seq_redacted_alignments_standards_depth(
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
    file_tsv_1_2,
    mad_quality_metric_1_2,
    chip_seq_quality_metric,
    analysis_step_run_bam,
    analysis_step_version_bam,
    analysis_step_bam,
    pipeline_bam,
    target_H3K27ac):

    testapp.patch_json(chip_seq_quality_metric['@id'], {'quality_metric_of': [file_bam_1_1['@id'],
                                                                              file_bam_2_1['@id']],
                                                        'processing_stage': 'filtered',
                                                        'total': 30000000,
                                                        'mapped': 30000000,
                                                        'read1': 100, 'read2': 100})
    testapp.patch_json(file_fastq_3['@id'], {'read_length': 20})
    testapp.patch_json(file_fastq_4['@id'], {'read_length': 100})

    testapp.patch_json(file_bam_1_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'output_type': 'redacted alignments',
                                             'assembly': 'mm10',
                                             'derived_from': [file_fastq_3['@id']]})
    testapp.patch_json(file_bam_2_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'output_type': 'redacted alignments',
                                             'assembly': 'mm10',
                                             'derived_from': [file_fastq_4['@id']]})
    testapp.patch_json(pipeline_bam['@id'], {'title':
                                             'ChIP-seq read mapping'})
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
    testapp.patch_json(base_experiment['@id'], {'target': target_H3K27ac['@id'],
                                                'status': 'released',
                                                'date_released': '2016-01-01',
                                                'assay_term_name': 'ChIP-seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] ==
               'low read depth' for error in collect_audit_errors(res))


def test_audit_experiment_chip_seq_control_standards(
        testapp,
        base_experiment,
        experiment,
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
        file_tsv_1_2,
        mad_quality_metric_1_2,
        chip_seq_quality_metric,
        analysis_step_run_bam,
        analysis_step_version_bam,
        analysis_step_bam,
        pipeline_bam,
        target_control,
        target_H3K9me3):

    testapp.patch_json(chip_seq_quality_metric['@id'], {'quality_metric_of': [file_bam_2_1['@id']],
                                                        'processing_stage': 'filtered',
                                                        'total': 1000,
                                                        'mapped': 1000,
                                                        'read1': 100, 'read2': 100})
    testapp.patch_json(file_fastq_3['@id'], {'read_length': 20, 
                                             'dataset': base_experiment['@id'],
                                             'controlled_by': [file_fastq_4['@id']]})
    testapp.patch_json(file_fastq_4['@id'], {'read_length': 100,
                                             'dataset': experiment['@id']})
    testapp.patch_json(file_bam_1_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'status': 'in progress',
                                             'assembly': 'mm10', 'dataset': base_experiment['@id'],
                                             'derived_from': [file_fastq_3['@id']]})
    testapp.patch_json(file_bam_2_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'status': 'in progress',
                                             'assembly': 'mm10', 'dataset': experiment['@id'],
                                             'derived_from': [file_fastq_4['@id']]})
    testapp.patch_json(file_tsv_1_2['@id'], {'derived_from': [file_bam_2_1['@id'],
                                                              file_bam_1_1['@id']],
                                             'dataset': base_experiment['@id'],
                                             'file_format_type': 'narrowPeak',
                                             'file_format': 'bed',
                                             'output_type': 'peaks'})
    testapp.patch_json(pipeline_bam['@id'], {'title':
                                             'ChIP-seq read mapping'})
    testapp.patch_json(biosample_1['@id'], {'donor': mouse_donor_1['@id'],
                                            'organism': '/organisms/mouse/',
                                            'model_organism_sex': 'mixed'})
    testapp.patch_json(biosample_2['@id'], {'donor': mouse_donor_1['@id'],
                                            'organism': '/organisms/mouse/',
                                            'model_organism_sex': 'mixed'})
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_2['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    testapp.patch_json(experiment['@id'], {'target': target_control['@id'],
                                           'status': 'released',
                                           'date_released': '2016-01-01',
                                           'assay_term_name': 'ChIP-seq'})
    testapp.patch_json(base_experiment['@id'], {'target': target_H3K9me3['@id'],
                                                'status': 'submitted',
                                                'date_submitted': '2015-01-01',
                                                'possible_controls': [experiment['@id']],
                                                'assay_term_name': 'ChIP-seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] ==
               'control extremely low read depth' for error in collect_audit_errors(res))


def test_audit_experiment_chip_seq_peaks_without_controls(
        testapp,
        base_experiment,
        experiment,
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
        file_tsv_1_2,
        mad_quality_metric_1_2,
        chip_seq_quality_metric,
        analysis_step_run_bam,
        analysis_step_version_bam,
        analysis_step_bam,
        pipeline_bam,
        target_control,
        target_H3K9me3):

    testapp.patch_json(chip_seq_quality_metric['@id'], {'quality_metric_of': [file_bam_2_1['@id']],
                                                        'processing_stage': 'filtered',
                                                        'total': 1000,
                                                        'mapped': 1000,
                                                        'read1': 100, 'read2': 100})
    testapp.patch_json(file_fastq_3['@id'], {'read_length': 20, 
                                             'dataset': base_experiment['@id'],
                                             'controlled_by': [file_fastq_4['@id']]})
    testapp.patch_json(file_fastq_4['@id'], {'read_length': 100,
                                             'dataset': experiment['@id']})
    testapp.patch_json(file_bam_1_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'status': 'in progress',
                                             'assembly': 'mm10', 'dataset': base_experiment['@id'],
                                             'derived_from': [file_fastq_3['@id']]})
    testapp.patch_json(file_bam_2_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'status': 'in progress',
                                             'assembly': 'mm10', 'dataset': experiment['@id'],
                                             'derived_from': [file_fastq_4['@id']]})
    testapp.patch_json(file_tsv_1_2['@id'], {'derived_from': [file_bam_1_1['@id']],
                                             'dataset': base_experiment['@id'],
                                             'file_format_type': 'narrowPeak',
                                             'file_format': 'bed',
                                             'output_type': 'peaks'})
    testapp.patch_json(pipeline_bam['@id'], {'title':
                                             'ChIP-seq read mapping'})
    testapp.patch_json(biosample_1['@id'], {'donor': mouse_donor_1['@id'],
                                            'organism': '/organisms/mouse/',
                                            'model_organism_sex': 'mixed'})
    testapp.patch_json(biosample_2['@id'], {'donor': mouse_donor_1['@id'],
                                            'organism': '/organisms/mouse/',
                                            'model_organism_sex': 'mixed'})
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_2['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    testapp.patch_json(experiment['@id'], {'target': target_control['@id'],
                                           'status': 'released',
                                           'date_released': '2016-01-01',
                                           'assay_term_name': 'ChIP-seq'})
    testapp.patch_json(base_experiment['@id'], {'target': target_H3K9me3['@id'],
                                                'status': 'submitted',
                                                'date_submitted': '2015-01-01',
                                                'possible_controls': [experiment['@id']],
                                                'assay_term_name': 'ChIP-seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] ==
               'missing control alignments' for error in collect_audit_errors(res))


def test_audit_experiment_chip_seq_peaks_with_matched_set(
        testapp,
        base_experiment,
        experiment,
        treatment_time_series,
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
        file_tsv_1_2,
        mad_quality_metric_1_2,
        chip_seq_quality_metric,
        analysis_step_run_bam,
        analysis_step_version_bam,
        analysis_step_bam,
        pipeline_bam,
        target_control,
        target_H3K9me3):

    testapp.patch_json(chip_seq_quality_metric['@id'], {'quality_metric_of': [file_bam_1_1['@id']],
                                                        'processing_stage': 'filtered',
                                                        'total': 1000,
                                                        'mapped': 1000,
                                                        'read1': 100, 'read2': 100})
    testapp.patch_json(file_fastq_3['@id'], {'read_length': 20, 
                                             'dataset': base_experiment['@id'],
                                             'controlled_by': [file_fastq_4['@id']]})
    testapp.patch_json(file_fastq_4['@id'], {'read_length': 100,
                                             'dataset': experiment['@id']})
    testapp.patch_json(file_bam_1_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'status': 'in progress',
                                             'assembly': 'mm10', 'dataset': base_experiment['@id'],
                                             'derived_from': [file_fastq_3['@id']]})
    
    testapp.patch_json(file_tsv_1_2['@id'], {'derived_from': [file_bam_1_1['@id'], file_bam_2_1['@id']],
                                             'dataset': base_experiment['@id'],
                                             'file_format_type': 'narrowPeak',
                                             'file_format': 'bed',
                                             'output_type': 'peaks'})
    testapp.patch_json(pipeline_bam['@id'], {'title':
                                             'ChIP-seq read mapping'})
    testapp.patch_json(biosample_1['@id'], {'donor': mouse_donor_1['@id'],
                                            'organism': '/organisms/mouse/',
                                            'model_organism_sex': 'mixed'})
    testapp.patch_json(biosample_2['@id'], {'donor': mouse_donor_1['@id'],
                                            'organism': '/organisms/mouse/',
                                            'model_organism_sex': 'mixed'})
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_2['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    testapp.patch_json(experiment['@id'], {'target': target_control['@id'],
                                           'status': 'released',
                                           'date_released': '2016-01-01',
                                           'assay_term_name': 'ChIP-seq'})
    testapp.patch_json(treatment_time_series['@id'], {'related_datasets': [experiment['@id']]})
    testapp.patch_json(base_experiment['@id'], {'target': target_H3K9me3['@id'],
                                                'status': 'submitted',
                                                'date_submitted': '2015-01-01',
                                                'possible_controls': [treatment_time_series['@id']],
                                                'assay_term_name': 'ChIP-seq'})
    testapp.patch_json(file_bam_2_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'status': 'in progress',
                                             'assembly': 'mm10', 'dataset': treatment_time_series['@id'],
                                             'derived_from': [file_fastq_4['@id']]})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] ==
               'missing control quality metric' for error in collect_audit_errors(res))
    testapp.patch_json(chip_seq_quality_metric['@id'], {'quality_metric_of': [
        file_bam_1_1['@id'],
        file_bam_2_1['@id']]})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert all(error['category'] !=
               'missing control quality metric' for error in collect_audit_errors(res))


def test_audit_experiment_chip_seq_peaks_with_controls_but_no_qc(
        testapp,
        base_experiment,
        experiment,
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
        file_tsv_1_2,
        mad_quality_metric_1_2,
        chip_seq_quality_metric,
        analysis_step_run_bam,
        analysis_step_version_bam,
        analysis_step_bam,
        pipeline_bam,
        target_control,
        target_H3K9me3):

    testapp.patch_json(chip_seq_quality_metric['@id'], {'quality_metric_of': [file_bam_1_1['@id']],
                                                        'processing_stage': 'filtered',
                                                        'total': 1000,
                                                        'mapped': 1000,
                                                        'read1': 100, 'read2': 100})
    testapp.patch_json(file_fastq_3['@id'], {'read_length': 20, 
                                             'dataset': base_experiment['@id'],
                                             'controlled_by': [file_fastq_4['@id']]})
    testapp.patch_json(file_fastq_4['@id'], {'read_length': 100,
                                             'dataset': experiment['@id']})
    testapp.patch_json(file_bam_1_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'status': 'in progress',
                                             'assembly': 'mm10', 'dataset': base_experiment['@id'],
                                             'derived_from': [file_fastq_3['@id']]})
    testapp.patch_json(file_bam_2_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'status': 'in progress',
                                             'assembly': 'mm10', 'dataset': experiment['@id'],
                                             'derived_from': [file_fastq_4['@id']]})
    testapp.patch_json(file_tsv_1_2['@id'], {'derived_from': [file_bam_1_1['@id'], file_bam_2_1['@id']],
                                             'dataset': base_experiment['@id'],
                                             'file_format_type': 'narrowPeak',
                                             'file_format': 'bed',
                                             'output_type': 'peaks and background as input for IDR'})
    testapp.patch_json(pipeline_bam['@id'], {'title':
                                             'ChIP-seq read mapping'})
    testapp.patch_json(biosample_1['@id'], {'donor': mouse_donor_1['@id'],
                                            'organism': '/organisms/mouse/',
                                            'model_organism_sex': 'mixed'})
    testapp.patch_json(biosample_2['@id'], {'donor': mouse_donor_1['@id'],
                                            'organism': '/organisms/mouse/',
                                            'model_organism_sex': 'mixed'})
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_2['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    testapp.patch_json(experiment['@id'], {'target': target_control['@id'],
                                           'status': 'released',
                                           'date_released': '2016-01-01',
                                           'assay_term_name': 'ChIP-seq'})
    testapp.patch_json(base_experiment['@id'], {'target': target_H3K9me3['@id'],
                                                'status': 'submitted',
                                                'date_submitted': '2015-01-01',
                                                'possible_controls': [experiment['@id']],
                                                'assay_term_name': 'ChIP-seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] ==
               'missing control quality metric' for error in collect_audit_errors(res))
    testapp.patch_json(chip_seq_quality_metric['@id'], {'quality_metric_of': [
        file_bam_1_1['@id'],
        file_bam_2_1['@id']]})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert all(error['category'] !=
               'missing control quality metric' for error in collect_audit_errors(res))


def test_audit_experiment_chip_seq_peaks_with_subsampled_controls(
        testapp,
        base_experiment,
        experiment,
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
        file_tsv_1_2,
        mad_quality_metric_1_2,
        chip_seq_quality_metric,
        analysis_step_run_bam,
        analysis_step_version_bam,
        analysis_step_bam,
        pipeline_bam,
        target_control,
        target_H3K9me3):

    
    testapp.patch_json(analysis_step_bam['@id'], {'title': 'Alignment pooliing and subsampling step'})
    testapp.patch_json(chip_seq_quality_metric['@id'], {'quality_metric_of': [file_bam_1_1['@id'], file_bam_2_1['@id']],
                                                        'processing_stage': 'filtered',
                                                        'total': 1002,
                                                        'mapped': 1002,
                                                        'read1': 100, 'read2': 100})
    testapp.patch_json(file_fastq_3['@id'], {'read_length': 20, 
                                             'dataset': base_experiment['@id'],
                                             'controlled_by': [file_fastq_4['@id']]})
    testapp.patch_json(file_fastq_4['@id'], {'read_length': 100,
                                             'dataset': experiment['@id']})
    testapp.patch_json(file_bam_1_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'status': 'in progress',
                                             'assembly': 'mm10', 'dataset': base_experiment['@id'],
                                             'derived_from': [file_fastq_3['@id']]})
    testapp.patch_json(file_bam_2_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'status': 'in progress',
                                             'assembly': 'mm10', 'dataset': experiment['@id'],
                                             'derived_from': [file_fastq_4['@id']]})
    testapp.patch_json(file_tsv_1_2['@id'], {'derived_from': [file_bam_1_1['@id'], file_bam_2_1['@id']],
                                             'dataset': base_experiment['@id'],
                                             'file_format_type': 'narrowPeak',
                                             'file_format': 'bed',
                                             'output_type': 'peaks and background as input for IDR'})
    testapp.patch_json(pipeline_bam['@id'], {'title':
                                             'Some subsampling pipeline'})
    testapp.patch_json(biosample_1['@id'], {'donor': mouse_donor_1['@id'],
                                            'organism': '/organisms/mouse/',
                                            'model_organism_sex': 'mixed'})
    testapp.patch_json(biosample_2['@id'], {'donor': mouse_donor_1['@id'],
                                            'organism': '/organisms/mouse/',
                                            'model_organism_sex': 'mixed'})
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_2['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    testapp.patch_json(experiment['@id'], {'target': target_control['@id'],
                                           'status': 'released',
                                           'date_released': '2016-01-01',
                                           'assay_term_name': 'ChIP-seq'})
    testapp.patch_json(base_experiment['@id'], {'target': target_H3K9me3['@id'],
                                                'status': 'submitted',
                                                'date_submitted': '2015-01-01',
                                                'possible_controls': [experiment['@id']],
                                                'assay_term_name': 'ChIP-seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] ==
               'missing control alignments' for error in collect_audit_errors(res))
    testapp.patch_json(analysis_step_bam['@id'], {'title': 'Alignment pooling and subsampling step'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert all(error['category'] !=
               'missing control alignments' for error in collect_audit_errors(res))


def test_audit_experiment_chip_seq_standards(testapp,
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
                                             file_tsv_1_2,
                                             mad_quality_metric_1_2,
                                             chip_seq_quality_metric,
                                             analysis_step_run_bam,
                                             analysis_step_version_bam,
                                             analysis_step_bam,
                                             pipeline_bam,
                                             target_H3K9me3):

    testapp.patch_json(chip_seq_quality_metric['@id'], {'quality_metric_of': [file_bam_1_1['@id']],
                                                        'processing_stage': 'unfiltered',
                                                        'total': 10000000,
                                                        'mapped': 10000000,
                                                        'read1': 100, 'read2': 100})
    testapp.patch_json(file_fastq_3['@id'], {'read_length': 20})
    testapp.patch_json(file_fastq_4['@id'], {'read_length': 100})

    testapp.patch_json(file_bam_1_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'assembly': 'mm10',
                                             'derived_from': [file_fastq_3['@id']]})
    testapp.patch_json(file_bam_2_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'assembly': 'mm10',
                                             'derived_from': [file_fastq_4['@id']]})
    testapp.patch_json(pipeline_bam['@id'], {'title':
                                             'ChIP-seq read mapping'})
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
    testapp.patch_json(base_experiment['@id'], {'target': target_H3K9me3['@id'],
                                                'status': 'released',
                                                'date_released': '2016-01-01',
                                                'assay_term_name': 'ChIP-seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] ==
               'insufficient read depth' for error in collect_audit_errors(res))


def test_audit_experiment_chip_seq_standards_encode2(testapp,
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
                                                     file_tsv_1_2,
                                                     mad_quality_metric_1_2,
                                                     chip_seq_quality_metric,
                                                     analysis_step_run_bam,
                                                     analysis_step_version_bam,
                                                     analysis_step_bam,
                                                     pipeline_bam,
                                                     target_H3K9me3,
                                                     encode2_award):

    testapp.patch_json(chip_seq_quality_metric['@id'], {'quality_metric_of': [file_bam_1_1['@id']],
                                                        'processing_stage': 'unfiltered',
                                                        'total': 146000000,
                                                        'mapped': 146000000,
                                                        'read1': 100, 'read2': 100})
    testapp.patch_json(file_fastq_3['@id'], {'read_length': 20})
    testapp.patch_json(file_fastq_4['@id'], {'read_length': 100})

    testapp.patch_json(file_bam_1_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'assembly': 'mm10',
                                             'derived_from': [file_fastq_3['@id']]})
    testapp.patch_json(file_bam_2_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'assembly': 'mm10',
                                             'derived_from': [file_fastq_4['@id']]})
    testapp.patch_json(pipeline_bam['@id'], {'title':
                                             'ChIP-seq read mapping'})
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
    testapp.patch_json(base_experiment['@id'], {'target': target_H3K9me3['@id'],
                                                'status': 'released',
                                                'date_released': '2016-01-01',
                                                'assay_term_name': 'ChIP-seq',
                                                'award': encode2_award['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert all(error['category'] !=
               'insufficient read depth' for error in collect_audit_errors(res))


def test_audit_experiment_chip_seq_no_target_standards(testapp,
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
                                                       file_tsv_1_2,
                                                       mad_quality_metric_1_2,
                                                       chip_seq_quality_metric,
                                                       chipseq_filter_quality_metric,
                                                       analysis_step_run_bam,
                                                       analysis_step_version_bam,
                                                       analysis_step_bam,
                                                       pipeline_bam):

    testapp.patch_json(chip_seq_quality_metric['@id'], {'quality_metric_of': [file_bam_1_1['@id']],
                                                        'processing_stage': 'unfiltered',
                                                        'total': 10000000,
                                                        'mapped': 10000000,
                                                        'read1': 100, 'read2': 100})
    testapp.patch_json(file_fastq_3['@id'], {'read_length': 20})
    testapp.patch_json(file_fastq_4['@id'], {'read_length': 100})

    testapp.patch_json(file_bam_1_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'assembly': 'mm10',
                                             'derived_from': [file_fastq_3['@id']]})
    testapp.patch_json(file_bam_2_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'assembly': 'mm10',
                                             'derived_from': [file_fastq_4['@id']]})

    testapp.patch_json(pipeline_bam['@id'], {'title':
                                             'ChIP-seq read mapping'})

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
    testapp.patch_json(base_experiment['@id'], {'status': 'released',
                                                'date_released': '2016-01-01',
                                                'assay_term_name': 'ChIP-seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] ==
               'missing target' for error in collect_audit_errors(res))


def test_audit_experiment_chip_seq_library_complexity_standards(testapp,
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
                                                                file_tsv_1_2,
                                                                mad_quality_metric_1_2,
                                                                chip_seq_quality_metric,
                                                                chipseq_filter_quality_metric,
                                                                analysis_step_run_bam,
                                                                analysis_step_version_bam,
                                                                analysis_step_bam,
                                                                pipeline_bam,
                                                                target_H3K9me3):
    testapp.patch_json(chip_seq_quality_metric['@id'], {'quality_metric_of': [file_bam_1_1['@id']],
                                                        'processing_stage': 'unfiltered',
                                                        'total': 10000000,
                                                        'mapped': 10000000,
                                                        'read1': 100, 'read2': 100})
    testapp.patch_json(file_fastq_3['@id'], {'read_length': 20})
    testapp.patch_json(file_fastq_4['@id'], {'read_length': 100})

    testapp.patch_json(file_bam_1_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'assembly': 'mm10',
                                             'derived_from': [file_fastq_3['@id']]})
    testapp.patch_json(file_bam_2_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'assembly': 'mm10',
                                             'derived_from': [file_fastq_4['@id']]})

    testapp.patch_json(pipeline_bam['@id'], {'title':
                                             'ChIP-seq read mapping'})

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
    testapp.patch_json(base_experiment['@id'], {'target': target_H3K9me3['@id'],
                                                'status': 'released',
                                                'date_released': '2016-01-01',
                                                'assay_term_name': 'ChIP-seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] ==
               'severe bottlenecking' for error in collect_audit_errors(res))


def test_audit_experiment_dnase_low_spot_score(testapp,
                                               base_experiment,
                                               replicate_1_1,
                                               library_1,
                                               biosample_1,
                                               mouse_donor_1,
                                               file_fastq_3,
                                               file_bam_1_1,
                                               mad_quality_metric_1_2,
                                               hotspot_quality_metric,
                                               analysis_step_run_bam,
                                               analysis_step_version_bam,
                                               analysis_step_bam,
                                               file_tsv_1_1,
                                               pipeline_bam):
    testapp.patch_json(file_tsv_1_1['@id'], {'output_type': 'hotspots'})
    testapp.patch_json(file_fastq_3['@id'], {'read_length': 20})
    testapp.patch_json(file_bam_1_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'assembly': 'mm10',
                                             'output_type': 'alignments',
                                             'derived_from': [file_fastq_3['@id']]})
    testapp.patch_json(pipeline_bam['@id'], {'title':
                                             'DNase-HS pipeline single-end - Version 2'})
    testapp.patch_json(biosample_1['@id'], {'donor': mouse_donor_1['@id']})
    testapp.patch_json(biosample_1['@id'], {'organism': '/organisms/mouse/'})
    testapp.patch_json(biosample_1['@id'], {'model_organism_sex': 'mixed'})
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(base_experiment['@id'], {'status': 'released',
                                                'date_released': '2016-01-01',
                                                'assay_term_name': 'DNase-seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] ==
               'low spot score' for error in collect_audit_errors(res))


def test_audit_experiment_dnase_seq_low_read_depth(testapp,
                                                   base_experiment,
                                                   replicate_1_1,
                                                   library_1,
                                                   biosample_1,
                                                   mouse_donor_1,
                                                   file_fastq_3,
                                                   file_bam_1_1,
                                                   mad_quality_metric_1_2,
                                                   chip_seq_quality_metric,
                                                   analysis_step_run_bam,
                                                   analysis_step_version_bam,
                                                   analysis_step_bam,
                                                   pipeline_bam):
    testapp.patch_json(file_fastq_3['@id'], {'read_length': 20})
    testapp.patch_json(file_bam_1_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'assembly': 'mm10',
                                             'output_type': 'alignments',
                                             'derived_from': [file_fastq_3['@id']]})
    testapp.patch_json(pipeline_bam['@id'], {'title':
                                             'DNase-HS pipeline single-end - Version 2'})
    testapp.patch_json(chip_seq_quality_metric['@id'], {'mapped': 23})
    testapp.patch_json(biosample_1['@id'], {'donor': mouse_donor_1['@id']})
    testapp.patch_json(biosample_1['@id'], {'organism': '/organisms/mouse/'})
    testapp.patch_json(biosample_1['@id'], {'model_organism_sex': 'mixed'})
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(base_experiment['@id'], {'status': 'released',
                                                'date_released': '2016-01-01',
                                                'assay_term_name': 'DNase-seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] ==
               'extremely low read depth' for error in collect_audit_errors(res))


def test_audit_experiment_wgbs_coverage(testapp,
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
                                         file_bed_methyl,
                                         chip_seq_quality_metric,
                                         analysis_step_run_bam,
                                         analysis_step_version_bam,
                                         analysis_step_bam,
                                         pipeline_bam):

    testapp.patch_json(file_bam_1_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'assembly': 'mm10',
                                             'derived_from': [file_fastq_3['@id']]})
    testapp.patch_json(file_bam_2_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'assembly': 'mm10',
                                             'derived_from': [file_fastq_4['@id']]})
    testapp.patch_json(pipeline_bam['@id'], {'title':
                                             'WGBS paired-end pipeline'})

    testapp.patch_json(chip_seq_quality_metric['@id'], {'quality_metric_of': [file_bed_methyl['@id']],
                                                        'processing_stage': 'filtered',
                                                        'total': 30000000,
                                                        'mapped': 30000000,
                                                        'read1': 100, 'read2': 100})
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
    testapp.patch_json(base_experiment['@id'], {'status': 'released',
                                                'date_released': '2016-01-01',
                                                'assay_term_name': 'whole-genome shotgun bisulfite sequencing'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] ==
               'extremely low coverage' for error in collect_audit_errors(res))
   
def test_audit_experiment_dnase_low_read_length(testapp,
                                                base_experiment,
                                                replicate_1_1,
                                                library_1,
                                                biosample_1,
                                                mouse_donor_1,
                                                file_fastq_3,
                                                file_bam_1_1,
                                                mad_quality_metric_1_2,
                                                chip_seq_quality_metric,
                                                analysis_step_run_bam,
                                                analysis_step_version_bam,
                                                analysis_step_bam,
                                                pipeline_bam):
    testapp.patch_json(file_fastq_3['@id'], {'read_length': 20})
    testapp.patch_json(file_bam_1_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'assembly': 'mm10',
                                             'output_type': 'alignments',
                                             'derived_from': [file_fastq_3['@id']]})
    testapp.patch_json(pipeline_bam['@id'], {'title':
                                             'DNase-HS pipeline single-end - Version 2'})
    testapp.patch_json(chip_seq_quality_metric['@id'], {'mapped': 23})
    testapp.patch_json(biosample_1['@id'], {'donor': mouse_donor_1['@id']})
    testapp.patch_json(biosample_1['@id'], {'organism': '/organisms/mouse/'})
    testapp.patch_json(biosample_1['@id'], {'model_organism_sex': 'mixed'})
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(base_experiment['@id'], {'status': 'released',
                                                'date_released': '2016-01-01',
                                                'assay_term_name': 'DNase-seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] ==
               'insufficient read length' for error in collect_audit_errors(res))


def test_audit_experiment_dnase_low_correlation(testapp,
                                                base_experiment,
                                                replicate_1_1,
                                                replicate_2_1,
                                                library_1,
                                                library_2,
                                                biosample_1,
                                                mouse_donor_1,
                                                file_fastq_3,
                                                bigWig_file,
                                                file_bam_1_1,
                                                correlation_quality_metric,
                                                chip_seq_quality_metric,
                                                analysis_step_run_bam,
                                                analysis_step_version_bam,
                                                analysis_step_bam,
                                                pipeline_bam):
    testapp.patch_json(bigWig_file['@id'], {'dataset': base_experiment['@id']})
    testapp.patch_json(
        correlation_quality_metric['@id'], {'quality_metric_of': [bigWig_file['@id']],
                                            'Pearson correlation': 0.15})
    testapp.patch_json(file_bam_1_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'assembly': 'mm10',
                                             'output_type': 'alignments',
                                             'derived_from': [file_fastq_3['@id']]})
    testapp.patch_json(pipeline_bam['@id'], {'title':
                                             'DNase-HS pipeline single-end - Version 2'})
    testapp.patch_json(chip_seq_quality_metric['@id'], {'mapped': 23})
    testapp.patch_json(biosample_1['@id'], {'donor': mouse_donor_1['@id']})
    testapp.patch_json(biosample_1['@id'], {'organism': '/organisms/mouse/'})
    testapp.patch_json(biosample_1['@id'], {'model_organism_sex': 'mixed'})
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    testapp.patch_json(base_experiment['@id'], {'status': 'released',
                                                'date_released': '2016-01-01',
                                                'assay_term_name': 'DNase-seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] ==
               'insufficient replicate concordance' for error in collect_audit_errors(res))

# duplication rate audit was removed from v54


def test_audit_experiment_dnase_seq_missing_read_depth(testapp,
                                                       base_experiment,
                                                       replicate_1_1,
                                                       library_1,
                                                       biosample_1,
                                                       mouse_donor_1,
                                                       file_fastq_3,
                                                       file_bam_1_1,
                                                       mad_quality_metric_1_2,
                                                       analysis_step_run_bam,
                                                       analysis_step_version_bam,
                                                       analysis_step_bam,
                                                       pipeline_bam):
    testapp.patch_json(file_fastq_3['@id'], {'read_length': 20})
    testapp.patch_json(file_bam_1_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'assembly': 'mm10',
                                             'output_type': 'alignments',
                                             'derived_from': [file_fastq_3['@id']]})
    testapp.patch_json(pipeline_bam['@id'], {'title':
                                             'DNase-HS pipeline single-end - Version 2'})
    testapp.patch_json(biosample_1['@id'], {'donor': mouse_donor_1['@id']})
    testapp.patch_json(biosample_1['@id'], {'organism': '/organisms/mouse/'})
    testapp.patch_json(biosample_1['@id'], {'model_organism_sex': 'mixed'})
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(base_experiment['@id'], {'status': 'released',
                                                'date_released': '2016-01-01',
                                                'assay_term_name': 'DNase-seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] ==
               'missing read depth' for error in collect_audit_errors(res))


def test_audit_experiment_chip_seq_unfiltered_missing_read_depth(testapp,
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
                                                                 file_tsv_1_2,
                                                                 mad_quality_metric_1_2,
                                                                 chip_seq_quality_metric,
                                                                 chipseq_filter_quality_metric,
                                                                 analysis_step_run_bam,
                                                                 analysis_step_version_bam,
                                                                 analysis_step_bam,
                                                                 pipeline_bam,
                                                                 target_H3K9me3):
    testapp.patch_json(file_fastq_3['@id'], {'read_length': 20})
    testapp.patch_json(file_fastq_4['@id'], {'read_length': 100})

    testapp.patch_json(file_bam_1_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'assembly': 'mm10',
                                             'output_type': 'unfiltered alignments',
                                             'derived_from': [file_fastq_3['@id']]})
    testapp.patch_json(file_bam_2_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'assembly': 'mm10',
                                             'output_type': 'unfiltered alignments',
                                             'derived_from': [file_fastq_4['@id']]})
    testapp.patch_json(pipeline_bam['@id'], {'title':
                                             'ChIP-seq read mapping'})
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
    testapp.patch_json(base_experiment['@id'], {'target': target_H3K9me3['@id'],
                                                'status': 'released',
                                                'date_released': '2016-01-01',
                                                'assay_term_name': 'ChIP-seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert all(error['category'] !=
               'missing read depth' for error in collect_audit_errors(res))


def test_audit_experiment_out_of_date_analysis_added_fastq(testapp,
                                                           base_experiment,
                                                           replicate_1_1,
                                                           replicate_2_1,
                                                           file_fastq_3,
                                                           file_fastq_4,
                                                           file_bam_1_1,
                                                           file_bam_2_1):
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'ChIP-seq'})
    testapp.patch_json(file_fastq_4['@id'], {'replicate': replicate_1_1['@id']})
    testapp.patch_json(file_bam_1_1['@id'], {'derived_from': [file_fastq_3['@id']]})
    testapp.patch_json(file_bam_2_1['@id'], {'derived_from': [file_fastq_3['@id']]})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] ==
               'out of date analysis' for error in collect_audit_errors(res))


def test_audit_experiment_out_of_date_analysis_removed_fastq(testapp,
                                                             base_experiment,
                                                             replicate_1_1,
                                                             replicate_2_1,
                                                             file_fastq_3,
                                                             file_fastq_4,
                                                             file_bam_1_1,
                                                             file_bam_2_1):
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'ChIP-seq'})
    testapp.patch_json(file_bam_1_1['@id'], {'derived_from': [file_fastq_3['@id']]})
    testapp.patch_json(file_bam_2_1['@id'], {'derived_from': [file_fastq_4['@id']]})
    testapp.patch_json(file_fastq_3['@id'], {'status': 'deleted'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'out of date analysis' for error in collect_audit_errors(res))


def test_audit_experiment_not_out_of_date_analysis_DNase(testapp,
                                                         base_experiment,
                                                         replicate_1_1,
                                                         replicate_1_2,
                                                         file_fastq_3,
                                                         file_fastq_4,
                                                         file_bam_1_1,
                                                         file_bam_2_1):
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'DNase-seq'})
    testapp.patch_json(file_bam_1_1['@id'], {'derived_from': [file_fastq_3['@id']]})
    testapp.patch_json(file_bam_2_1['@id'], {'derived_from': [file_fastq_4['@id']]})
    testapp.patch_json(file_fastq_3['@id'], {'replicate': replicate_1_1['@id']})
    testapp.patch_json(file_fastq_4['@id'], {'replicate': replicate_1_2['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert all(error['category'] != 'out of date analysis' for error in collect_audit_errors(res))


def test_audit_experiment_out_of_date_analysis_DNase(testapp,
                                                     base_experiment,
                                                     replicate_1_1,
                                                     replicate_1_2,
                                                     file_fastq_3,
                                                     file_fastq_4,
                                                     file_bam_1_1,
                                                     file_bam_2_1):
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'DNase-seq'})
    testapp.patch_json(file_bam_1_1['@id'], {'derived_from': [file_fastq_3['@id']]})
    testapp.patch_json(file_bam_2_1['@id'], {'derived_from': [file_fastq_4['@id']]})
    testapp.patch_json(file_fastq_3['@id'], {'replicate': replicate_1_1['@id'],
                                             'status': 'deleted'})
    testapp.patch_json(file_fastq_4['@id'], {'replicate': replicate_1_2['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'out of date analysis' for error in collect_audit_errors(res))


def test_audit_experiment_no_out_of_date_analysis(testapp,
                                                  base_experiment,
                                                  replicate_1_1,
                                                  replicate_2_1,
                                                  file_fastq_3,
                                                  file_fastq_4,
                                                  file_bam_1_1,
                                                  file_bam_2_1):
    testapp.patch_json(file_bam_1_1['@id'], {'derived_from': [file_fastq_3['@id']]})
    testapp.patch_json(file_bam_2_1['@id'], {'derived_from': [file_fastq_4['@id']]})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert all(error['category'] !=
               'out of date analysis' for error in collect_audit_errors(res))


# def test_audit_experiment_modERN_control_missing_files() removed from v54
# def test_audit_experiment_modERN_experiment_missing_files() removed from v54


def test_audit_experiment_wgbs_standards(testapp,
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
                                         file_tsv_1_2,
                                         file_bed_methyl,
                                         wgbs_quality_metric,
                                         analysis_step_run_bam,
                                         analysis_step_version_bam,
                                         analysis_step_bam,
                                         pipeline_bam,
                                         target_H3K9me3):
    testapp.patch_json(file_fastq_3['@id'], {'read_length': 20})
    testapp.patch_json(file_fastq_4['@id'], {'read_length': 100})

    testapp.patch_json(file_bam_1_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'assembly': 'mm10',
                                             'derived_from': [file_fastq_3['@id']]})
    testapp.patch_json(file_bam_2_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'assembly': 'mm10',
                                             'derived_from': [file_fastq_4['@id']]})
    testapp.patch_json(pipeline_bam['@id'], {'title':
                                             'WGBS paired-end pipeline'})

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
    testapp.patch_json(base_experiment['@id'], {'status': 'released',
                                                'date_released': '2016-01-01',
                                                'assay_term_name': 'whole-genome shotgun bisulfite sequencing'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] ==
               'high lambda C methylation ratio' for error in collect_audit_errors(res))


def test_audit_experiment_modern_chip_seq_standards(testapp,
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
                                                    file_tsv_1_2,
                                                    mad_quality_metric_1_2,
                                                    chip_seq_quality_metric,
                                                    analysis_step_run_bam,
                                                    analysis_step_version_bam,
                                                    analysis_step_bam,
                                                    pipeline_bam,
                                                    target,
                                                    award_modERN):

    testapp.patch_json(chip_seq_quality_metric['@id'], {'quality_metric_of': [file_bam_1_1['@id']],
                                                        'processing_stage': 'filtered',
                                                        'total': 100000,
                                                        'mapped': 100000,
                                                        'read1': 100, 'read2': 100})
    testapp.patch_json(file_fastq_3['@id'], {'read_length': 100})
    testapp.patch_json(file_fastq_4['@id'], {'read_length': 100})

    testapp.patch_json(file_bam_1_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'assembly': 'mm10',
                                             'derived_from': [file_fastq_3['@id']]})
    testapp.patch_json(file_bam_2_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'assembly': 'mm10',
                                             'derived_from': [file_fastq_4['@id']]})
    testapp.patch_json(pipeline_bam['@id'], {'title':
                                             'Transcription factor ChIP-seq pipeline (modERN)'})
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
    testapp.patch_json(base_experiment['@id'], {'target': target['@id'],
                                                'status': 'released',
                                                'date_released': '2016-01-01',
                                                'assay_term_name': 'ChIP-seq',
                                                'award': award_modERN['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] ==
               'insufficient read depth' for error in collect_audit_errors(res))


def test_audit_experiment_missing_genetic_modification(
        testapp,
        base_experiment,
        recombinant_target,
        replicate_1_1,
        replicate_2_1,
        library_1,
        library_2,
        biosample_1,
        biosample_2,
        donor_1,
        donor_2,
        k562):

    testapp.patch_json(biosample_1['@id'], {'biosample_ontology': k562['uuid'],
                                            'donor': donor_1['@id']})
    testapp.patch_json(biosample_2['@id'], {'biosample_ontology': k562['uuid'],
                                            'donor': donor_2['@id']})
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_2['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'ChIP-seq',
                                                'target': recombinant_target['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] ==
               'inconsistent genetic modification tags' for error in collect_audit_errors(res))


def test_audit_experiment_tagging_genetic_modification_characterization(
        testapp,
        construct_genetic_modification,
        gm_characterization,
        base_experiment,
        recombinant_target,
        replicate_1_1,
        library_1,
        biosample_1,
        donor_1,
        k562):
    testapp.patch_json(biosample_1['@id'], {'genetic_modifications': [construct_genetic_modification['@id']],
                                            'biosample_ontology': k562['uuid'],
                                            'donor': donor_1['@id']})
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})  
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'ChIP-seq',
                                                'target': recombinant_target['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] ==
               'missing genetic modification characterization' for error in collect_audit_errors(res))
    testapp.patch_json(gm_characterization['@id'], {'characterizes': construct_genetic_modification['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert all(error['category'] !=
               'missing genetic modification characterization' for error in collect_audit_errors(res))


def test_audit_experiment_missing_unfiltered_bams(testapp,
                                                  base_experiment,
                                                  replicate_1_1,
                                                  replicate_2_1,
                                                  file_fastq_3,
                                                  file_bam_1_1,
                                                  file_bam_2_1,
                                                  analysis_step_run_bam,
                                                  analysis_step_version_bam,
                                                  analysis_step_bam,
                                                  pipeline_bam):

    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'ChIP-seq'})
    testapp.patch_json(file_bam_2_1['@id'], {'derived_from': [file_fastq_3['@id']],
                                             'assembly': 'hg19',
                                             'output_type': 'unfiltered alignments'})
    testapp.patch_json(file_bam_1_1['@id'], {'step_run': analysis_step_run_bam['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] ==
               'missing unfiltered alignments' for error in collect_audit_errors(res))


def test_audit_experiment_wrong_modification(
        testapp,
        base_experiment,
        base_target,
        recombinant_target,
        replicate_1_1,
        replicate_2_1,
        library_1,
        library_2,
        biosample_1,
        biosample_2,
        donor_1,
        donor_2,
        construct_genetic_modification,
        k562):

    testapp.patch_json(construct_genetic_modification['@id'],
                       {'modified_site_by_target_id': base_target['@id'],
                        'introduced_tags': [{'name': 'FLAG', 'location': 'internal'}]})
    testapp.patch_json(biosample_1['@id'], {'biosample_ontology': k562['uuid'],
                                            'donor': donor_1['@id']})
    testapp.patch_json(biosample_2['@id'], {'biosample_ontology': k562['uuid'],
                                            'donor': donor_2['@id']})
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_2['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    testapp.patch_json(biosample_1['@id'], {'genetic_modifications': [construct_genetic_modification['@id']]})
    testapp.patch_json(biosample_2['@id'], {'genetic_modifications': [construct_genetic_modification['@id']]})
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'ChIP-seq',
                                                'target': recombinant_target['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] ==
               'inconsistent genetic modification tags' for error in collect_audit_errors(res))


def test_audit_experiment_chip_seq_mapped_read_length(testapp,
                                                      base_experiment,
                                                      file_fastq_3,
                                                      file_fastq_4,
                                                      file_bam_1_1,
                                                      file_bam_2_1,
                                                      file_tsv_1_2):
    testapp.patch_json(file_fastq_3['@id'], {'read_length': 100})
    testapp.patch_json(file_fastq_4['@id'], {'read_length': 130})
    testapp.patch_json(file_bam_1_1['@id'], {'derived_from': [file_fastq_3['@id']]})
    testapp.patch_json(file_bam_2_1['@id'], {'derived_from': [file_fastq_4['@id']]})
    testapp.patch_json(file_tsv_1_2['@id'], {'derived_from': [file_bam_2_1['@id'],
                                                              file_bam_1_1['@id']],
                                             'file_format_type': 'narrowPeak',
                                             'file_format': 'bed',
                                             'output_type': 'peaks'})

    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'ChIP-seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] ==
               'inconsistent mapped reads lengths' for error in collect_audit_errors(res))


def test_audit_experiment_chip_seq_consistent_mapped_read_length(
        testapp,
        base_experiment,
        file_fastq_3,
        file_fastq_4,
        file_bam_1_1,
        file_bam_2_1,
        file_tsv_1_2):
    testapp.patch_json(file_fastq_3['@id'], {'read_length': 124})
    testapp.patch_json(file_fastq_4['@id'], {'read_length': 130})
    testapp.patch_json(file_bam_1_1['@id'], {'derived_from': [file_fastq_3['@id']]})
    testapp.patch_json(file_bam_2_1['@id'], {'derived_from': [file_fastq_4['@id']]})
    testapp.patch_json(file_tsv_1_2['@id'], {'derived_from': [file_bam_2_1['@id'],
                                                              file_bam_1_1['@id']],
                                             'file_format_type': 'narrowPeak',
                                             'file_format': 'bed',
                                             'output_type': 'peaks'})

    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'ChIP-seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert all(error['category'] !=
               'inconsistent mapped reads lengths' for error in collect_audit_errors(res))


def test_audit_experiment_chip_seq_read_count(
        testapp,
        base_experiment,
        file_fastq_3,
        file_fastq_4):
    testapp.patch_json(file_fastq_3['@id'], {'read_count': 124})
    testapp.patch_json(file_fastq_4['@id'], {'read_count': 134})
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'ChIP-seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] ==
               'low read count' for error in collect_audit_errors(res))
    testapp.patch_json(file_fastq_3['@id'], {'read_count': 100000000})
    testapp.patch_json(file_fastq_4['@id'], {'read_count': 100000000})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert all(error['category'] !=
               'low read count' for error in collect_audit_errors(res))


def test_audit_experiment_with_biosample_missing_nih_consent(testapp, experiment, replicate,
                                                             library, biosample, encode4_award):
    testapp.patch_json(experiment['@id'], {'award': encode4_award['@id']})
    r = testapp.get(experiment['@id'] + '@@index-data')
    audits = r.json['audit']
    assert any(
        [
            detail['category'] == 'missing nih_institutional_certification'
            for audit in audits.values() for detail in audit
        ]
    )


def test_audit_experiment_with_biosample_not_missing_nih_consent(testapp, experiment, replicate,
                                                                 library, biosample, encode4_award):
    testapp.patch_json(experiment['@id'], {'award': encode4_award['@id']})
    testapp.patch_json(biosample['@id'], {'nih_institutional_certification': 'NICABC123'})
    r = testapp.get(experiment['@id'] + '@@index-data')
    audits = r.json['audit']
    assert all(
        [
            detail['category'] != 'missing nih_institutional_certification'
            for audit in audits.values() for detail in audit
        ]
    )


def test_is_matching_biosample_control(testapp, biosample, ctrl_experiment, treatment_time_series):
    from encoded.audit.experiment import is_matching_biosample_control
    exp = testapp.get(ctrl_experiment['@id'] + '@@index-data')
    exp_embedded = exp.json['embedded']
    bio = testapp.get(biosample['@id'] + '@@index-data')
    bio_embedded = bio.json['embedded']
    assert is_matching_biosample_control(exp_embedded, bio_embedded['biosample_ontology']['term_id']) == False
    testapp.patch_json(biosample['@id'], {'biosample_ontology': ctrl_experiment['biosample_ontology']})
    bio = testapp.get(biosample['@id'] + '@@index-data')
    bio_embedded = bio.json['embedded']
    assert is_matching_biosample_control(exp_embedded, bio_embedded['biosample_ontology']['term_id']) == True
    series = testapp.get(treatment_time_series['@id'] + '@@index-data')
    series_embedded = series.json['embedded']
    assert is_matching_biosample_control(series_embedded, bio_embedded['biosample_ontology']['term_id']) == False
    testapp.patch_json(treatment_time_series['@id'], {'related_datasets': [ctrl_experiment['@id']]})
    series = testapp.get(treatment_time_series['@id'] + '@@index-data')
    series_embedded = series.json['embedded']
    assert is_matching_biosample_control(series_embedded, bio_embedded['biosample_ontology']['term_id']) == True


def test_is_control_dataset(testapp, control_target, ctrl_experiment, publication_data, treatment_time_series):
    from encoded.audit.experiment import is_control_dataset
    exp = testapp.get(ctrl_experiment['@id'] + '@@index-data')
    exp_embedded = exp.json['embedded']
    assert is_control_dataset(exp_embedded) == False
    testapp.patch_json(ctrl_experiment['@id'], {'target': control_target['@id']})
    exp = testapp.get(ctrl_experiment['@id'] + '@@index-data')
    exp_embedded = exp.json['embedded']
    assert is_control_dataset(exp_embedded) == True
    series = testapp.get(treatment_time_series['@id'] + '@@index-data')
    series_embedded = series.json['embedded']
    assert is_control_dataset(series_embedded) == False
    testapp.patch_json(treatment_time_series['@id'], {'related_datasets': [ctrl_experiment['@id']]})
    series = testapp.get(treatment_time_series['@id'] + '@@index-data')
    series_embedded = series.json['embedded']
    assert is_control_dataset(series_embedded) == True
    file_set = testapp.get(publication_data['@id'] + '@@index-data')
    file_set_embedded = file_set.json['embedded']
    assert is_control_dataset(file_set_embedded) == False


def test_audit_experiment_histone_characterized_no_primary(testapp,
                                                           base_experiment,
                                                           wrangler,
                                                           base_antibody,
                                                           base_replicate,
                                                           base_library,
                                                           base_biosample,
                                                           target_H3K9me3,
                                                           mouse_H3K9me3,
                                                           base_antibody_characterization2,
                                                           mouse,
                                                           mel):
    # Supporting antibody only have secondary characterizations
    testapp.patch_json(base_biosample['@id'], {'organism': mouse['@id']})
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'ChIP-seq',
                                                'biosample_ontology': mel['uuid'],
                                                'target': mouse_H3K9me3['@id']})
    base_antibody['targets'] = [mouse_H3K9me3['@id']]
    no_primary_antibody = testapp.post_json('/antibody_lot', base_antibody).json['@graph'][0]
    testapp.patch_json(base_replicate['@id'], {'antibody': no_primary_antibody['@id'],
                                               'library': base_library['@id'],
                                               'experiment': base_experiment['@id']})
    testapp.patch_json(
        base_antibody_characterization2['@id'],
        {'target': mouse_H3K9me3['@id'],
            'characterizes': no_primary_antibody['@id'],
            'status': 'not compliant',
            'reviewed_by': wrangler['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    assert any(error['category'] == 'antibody not characterized to standard'
               for error in collect_audit_errors(res))


def test_audit_experiment_tag_target(testapp, experiment, ctcf):
    tag_target = testapp.post_json(
        '/target',
        {
            'genes': [ctcf['uuid']],
            'modifications': [{'modification': 'eGFP'}],
            'label': 'eGFP-CTCF',
            'investigated_as': ['recombinant protein']
        }
    ).json['@graph'][0]
    testapp.patch_json(experiment['@id'], {'assay_term_name': 'ChIP-seq',
                                           'target': tag_target['@id']})
    audits = testapp.get(experiment['@id'] + '@@index-data').json['audit']
    assert any(detail['category'] == 'inconsistent experiment target'
               for audit in audits.values() for detail in audit)


def test_audit_experiment_inconsist_mod_target(testapp, experiment, replicate,
                                               library, biosample, ctcf,
                                               construct_genetic_modification):
    tag_target = testapp.post_json(
        '/target',
        {
            'genes': [ctcf['uuid']],
            'modifications': [{'modification': 'eGFP'}],
            'label': 'eGFP-CTCF',
            'investigated_as': ['recombinant protein']
        }
    ).json['@graph'][0]
    testapp.patch_json(
        biosample['@id'],
        {'genetic_modifications': [construct_genetic_modification['@id']]}
    )
    testapp.patch_json(experiment['@id'], {'assay_term_name': 'ChIP-seq',
                                           'target': tag_target['@id']})
    audits = testapp.get(experiment['@id'] + '@@index-data').json['audit']
    assert any(detail['category'] == 'inconsistent genetic modification targets'
               for audit in audits.values() for detail in audit)
