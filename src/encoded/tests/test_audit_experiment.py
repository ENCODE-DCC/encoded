import pytest

RED_DOT = """data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUA
AAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO
9TXL0Y4OHwAAAABJRU5ErkJggg=="""

@pytest.fixture
def library_no_biosample(testapp, lab, award):
    item = {
        'nucleic_acid_term_id': 'SO:0000352',
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
        'nucleic_acid_term_id': 'SO:0000352',
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
def base_target(testapp, organism):
    item = {
        'organism': organism['uuid'],
        'gene_name': 'XYZ',
        'label': 'XYZ',
        'investigated_as': ['transcription factor']
    }
    return testapp.post_json('/target', item, status=201).json['@graph'][0]


@pytest.fixture
def tag_target(testapp, organism):
    item = {
        'organism': organism['uuid'],
        'label': 'eGFP',
        'investigated_as': ['tag']
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
def histone_target(testapp, fly_organism):
    item = {
        'organism': fly_organism['uuid'],
        'label': 'Histone',
        'investigated_as': ['histone modification', 'histone']
    }
    return testapp.post_json('/target', item, status=201).json['@graph'][0]


@pytest.fixture
def control_target(testapp, organism):
    item = {
        'organism': organism['uuid'],
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
def base_antibody_characterization1(testapp, lab, award, target, antibody_lot, organism):
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
                'biosample_term_name': 'K562',
                'biosample_term_id': 'EFO:0002067',
                'biosample_type': 'immortalized cell line',
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
def ctrl_experiment(testapp, lab, award, control_target):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'status': 'started',
        'assay_term_name': 'ChIP-seq',
        'assay_term_id': 'OBI:0000716'
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
def library_1(testapp, lab, award, base_biosample):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'nucleic_acid_term_id': 'SO:0000352',
        'nucleic_acid_term_name': 'DNA',
        'biosample': base_biosample['uuid']
    }
    return testapp.post_json('/library', item, status=201).json['@graph'][0]
@pytest.fixture
def library_2(testapp, lab, award, base_biosample):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'nucleic_acid_term_id': 'SO:0000352',
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
def biosample_1(testapp, lab, award, source, organism):
    item = {
        'award': award['uuid'],
        'biosample_term_id': 'UBERON:349829',
        'biosample_type': 'tissue',
        'lab': lab['uuid'],
        'organism': organism['uuid'],
        'source': source['uuid']
    }
    return testapp.post_json('/biosample', item, status=201).json['@graph'][0]


@pytest.fixture
def biosample_2(testapp, lab, award, source, organism):
    item = {        
        'award': award['uuid'],
        'biosample_term_id': 'UBERON:349829',
        'biosample_type': 'tissue',
        'lab': lab['uuid'],
        'organism': organism['uuid'],
        'source': source['uuid']
    }
    return testapp.post_json('/biosample', item, status=201).json['@graph'][0]


@pytest.fixture
def file_fastq(testapp, lab, award, base_experiment, base_replicate):
    item = {
        'dataset': base_experiment['@id'],
        'replicate': base_replicate['@id'],
        'file_format': 'fastq',
        'md5sum': 'd41d8cd98f00b2042e9800998ecf8427e',
        'output_type': 'reads',
        'run_type': "single-ended",
        'lab': lab['@id'],
        'award': award['@id'],
        'status': 'in progress',  # avoid s3 upload codepath
    }
    return testapp.post_json('/file', item).json['@graph'][0]


@pytest.fixture
def file_fastq_2(testapp, lab, award, base_experiment, base_replicate):
    item = {
        'dataset': base_experiment['@id'],
        'replicate': base_replicate['@id'],
        'file_format': 'fastq',
        'md5sum': 'd41d8cd98f00b204e9800998ecf8427123e',
        'run_type': "paired-ended",
        'output_type': 'reads',
        'lab': lab['@id'],
        'award': award['@id'],
        'status': 'in progress',  # avoid s3 upload codepath
    }
    return testapp.post_json('/file', item).json['@graph'][0]

@pytest.fixture
def file_fastq_3(testapp, lab, award, base_experiment, replicate_1_1):
    item = {
        'dataset': base_experiment['@id'],
        'replicate': replicate_1_1['@id'],
        'file_format': 'fastq',
        'output_type': 'reads',
        'md5sum': 'd41d8cd98f00b204e9dh5800998ecf8427123e',
        'run_type': "paired-ended",
        'lab': lab['@id'],
        'award': award['@id'],
        'status': 'in progress',  # avoid s3 upload codepath
    }
    return testapp.post_json('/file', item).json['@graph'][0]


@pytest.fixture
def file_fastq_4(testapp, lab, award, base_experiment, replicate_2_1):
    item = {
        'dataset': base_experiment['@id'],
        'replicate': replicate_2_1['@id'],
        'file_format': 'fastq',
        'md5sum': 'd41d8cd98f00b204e9800998ecww3f8427123e',
        'run_type': "paired-ended",
        'output_type': 'reads',
        'lab': lab['@id'],
        'award': award['@id'],
        'status': 'in progress',  # avoid s3 upload codepath
    }
    return testapp.post_json('/file', item).json['@graph'][0]


@pytest.fixture
def file_fastq_5(testapp, lab, award, base_experiment, replicate_2_1):
    item = {
        'dataset': base_experiment['@id'],
        'replicate': replicate_2_1['@id'],
        'file_format': 'fastq',
        'md5sum': 'd41d8cdq427123e',
        'run_type': "paired-ended",
        'output_type': 'reads',
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
        'md5sum': 'd41d8cd98f03wsqa50b204et3f8427123e',
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
        'md5sum': 'd41d8cd98f00b204et300gtf8427123e',
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
        "md5sum": "100d8c998f00bfdf2204e9800998ecf8428b",
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
        'md5sum': '100d8c998f00b2204e9800998ecf8428b',
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
        'md5sum': '100d8c998f040b2204e9800998ecf8428b',
        'output_type': 'gene quantifications',
        'award': award['uuid'],
        'lab': encode_lab['uuid'],
        'status': 'released',
        'step_run': analysis_step_run_bam['uuid']
    }
    return testapp.post_json('/file', item, status=201).json['@graph'][0]


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
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'mixed libraries' for error in errors_list)


def test_audit_experiment_released_with_unreleased_files(testapp, base_experiment, file_fastq):
    testapp.patch_json(base_experiment['@id'], {'status': 'released',
                                                'date_released': '2016-01-01'})
    testapp.patch_json(file_fastq['@id'], {'status': 'in progress'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'mismatched file status' for error in errors_list)


def test_ChIP_possible_control(testapp, base_experiment, ctrl_experiment, IgG_ctrl_rep):
    testapp.patch_json(base_experiment['@id'], {'possible_controls': [ctrl_experiment['@id']],
                                                'assay_term_name': 'ChIP-seq',
                                                'assay_term_id': 'OBI:0000716'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'invalid possible_control' for error in errors_list)


def test_ChIP_possible_control_roadmap(testapp, base_experiment, ctrl_experiment, IgG_ctrl_rep,
                                       award):
    testapp.patch_json(award['@id'], {'rfa': 'Roadmap'})
    testapp.patch_json(base_experiment['@id'], {'possible_controls': [ctrl_experiment['@id']],
                                                'assay_term_name': 'ChIP-seq',
                                                'assay_term_id': 'OBI:0000716'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'invalid possible_control' for error in errors_list)


def test_audit_input_control(testapp, base_experiment,
                             ctrl_experiment, IgG_ctrl_rep,
                             control_target):
    testapp.patch_json(ctrl_experiment['@id'], {'target': control_target['@id']})
    testapp.patch_json(base_experiment['@id'], {'possible_controls': [ctrl_experiment['@id']],
                                                'assay_term_name': 'ChIP-seq',
                                                'assay_term_id': 'OBI:0000716'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'missing input control' for error in errors_list)


def test_audit_experiment_target(testapp, base_experiment):
    testapp.patch_json(base_experiment['@id'], {'assay_term_id': 'OBI:0000716',
                                                'assay_term_name': 'ChIP-seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'missing target' for error in errors_list)


def test_audit_experiment_replicated(testapp, base_experiment, base_replicate, base_library):
    testapp.patch_json(base_experiment['@id'], {'status': 'ready for review'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'unreplicated experiment' for error in errors_list)


def test_audit_experiment_technical_replicates_same_library(testapp, base_experiment,
                                                            base_replicate, base_replicate_two,
                                                            base_library):
    testapp.patch_json(base_replicate['@id'], {'library': base_library['@id']})
    testapp.patch_json(base_replicate_two['@id'], {'library': base_library['@id']})
    testapp.patch_json(base_experiment['@id'], {'replicates': [base_replicate['@id'],base_replicate_two['@id']]})
    res = testapp.get(base_experiment['@id'] + '@@index-data')    

    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])

    assert any(error['category'] == 'sequencing runs labeled as technical replicates' for error in errors_list)


def test_audit_experiment_biological_replicates_biosample(testapp, base_experiment,base_biosample, library_1, library_2, replicate_1_1, replicate_2_1):
    testapp.patch_json(library_1['@id'], {'biosample': base_biosample['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': base_biosample['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])        
    assert any(error['category'] == 'biological replicates with identical biosample' for error in errors_list)


def test_audit_experiment_technical_replicates_biosample(testapp, base_experiment, biosample_1, biosample_2, library_1, library_2, replicate_1_1, replicate_1_2):
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_2['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_1_2['@id'], {'library': library_2['@id']})

    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])        
    assert any(error['category'] == 'technical replicates with not identical biosample' for error in errors_list)


def test_audit_experiment_with_libraryless_replicated(testapp, base_experiment, base_replicate, base_library):
    testapp.patch_json(base_experiment['@id'], {'status': 'ready for review'})
    testapp.patch_json(base_experiment['@id'], {'replicates': [base_replicate['@id']]})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'replicate with no library' for error in errors_list)


def test_audit_experiment_single_cell_replicated(testapp, base_experiment, base_replicate,
                                                 base_library):
    testapp.patch_json(base_experiment['@id'], {'status': 'ready for review'})
    testapp.patch_json(base_experiment['@id'], {'assay_term_name':
                                                'single cell isolation followed by RNA-seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert all(error['category'] != 'unreplicated experiment' for error in errors_list)


def test_audit_experiment_RNA_bind_n_seq_replicated(testapp, base_experiment, base_replicate,
                                                    base_library):
    testapp.patch_json(base_experiment['@id'], {'status': 'ready for review'})
    testapp.patch_json(base_experiment['@id'], {'assay_term_name':
                                                'RNA Bind-n-Seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert all(error['category'] != 'unreplicated experiment' for error in errors_list)


def test_audit_experiment_roadmap_replicated(testapp, base_experiment, base_replicate, base_library, award):
    testapp.patch_json(award['@id'], {'rfa': 'Roadmap'})
    testapp.patch_json(base_experiment['@id'], {'award': award['@id']})
    testapp.patch_json(base_experiment['@id'], {'status': 'released', 'date_released': '2016-01-01'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert all(error['category'] != 'unreplicated experiment' for error in errors_list)


def test_audit_experiment_spikeins(testapp, base_experiment, base_replicate, base_library):
    testapp.patch_json(base_experiment['@id'], {'assay_term_id': 'OBI:0001271', 'assay_term_name': 'RNA-seq'})
    testapp.patch_json(base_library['@id'], {'size_range': '>200'})
    testapp.patch_json(base_replicate['@id'], {'library': base_library['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'missing spikeins' for error in errors_list)


def test_audit_experiment_not_tag_antibody(testapp, base_experiment, base_replicate, organism, antibody_lot):
    other_target = testapp.post_json('/target', {'organism': organism['uuid'], 'label': 'eGFP-AVCD', 'investigated_as': ['recombinant protein']}).json['@graph'][0]
    testapp.patch_json(base_replicate['@id'], {'antibody': antibody_lot['uuid']})
    testapp.patch_json(base_experiment['@id'], {'assay_term_id': 'OBI:0000716', 'assay_term_name': 'ChIP-seq', 'target': other_target['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'not tagged antibody' for error in errors_list)


def test_audit_experiment_target_tag_antibody(testapp, base_experiment, base_replicate, organism, base_antibody, tag_target):
    ha_target = testapp.post_json('/target', {'organism': organism['uuid'], 'label': 'HA-ABCD', 'investigated_as': ['recombinant protein']}).json['@graph'][0]
    base_antibody['targets'] = [tag_target['@id']]
    tag_antibody = testapp.post_json('/antibody_lot', base_antibody).json['@graph'][0]
    testapp.patch_json(base_replicate['@id'], {'antibody': tag_antibody['@id']})
    testapp.patch_json(base_experiment['@id'], {'assay_term_id': 'OBI:0000716', 'assay_term_name': 'ChIP-seq', 'target': ha_target['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'mismatched tag target' for error in errors_list)


def test_audit_experiment_target_mismatch(testapp, base_experiment, base_replicate, base_target, antibody_lot):
    testapp.patch_json(base_replicate['@id'], {'antibody': antibody_lot['uuid']})
    testapp.patch_json(base_experiment['@id'], {'assay_term_id': 'OBI:0000716', 'assay_term_name': 'ChIP-seq', 'target': base_target['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'inconsistent target' for error in errors_list)


def test_audit_experiment_eligible_antibody(testapp, base_experiment, base_replicate, base_library, base_biosample, antibody_lot, target, base_antibody_characterization1, base_antibody_characterization2):
    testapp.patch_json(base_replicate['@id'], {'antibody': antibody_lot['@id'], 'library': base_library['@id']})
    testapp.patch_json(base_experiment['@id'], {'assay_term_id': 'OBI:0000716', 'assay_term_name': 'ChIP-seq', 'biosample_term_id': 'EFO:0002067', 'biosample_term_name': 'K562',  'biosample_type': 'immortalized cell line', 
                                                'target': target['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'not eligible antibody' for error in errors_list)


def test_audit_experiment_eligible_histone_antibody(testapp, base_experiment, base_replicate, base_library, base_biosample, base_antibody, histone_target, base_antibody_characterization1, base_antibody_characterization2, fly_organism):
    base_antibody['targets'] = [histone_target['@id']]
    histone_antibody = testapp.post_json('/antibody_lot', base_antibody).json['@graph'][0]
    testapp.patch_json(base_biosample['@id'], {'organism': fly_organism['uuid']})
    testapp.patch_json(base_antibody_characterization1['@id'], {'target': histone_target['@id'], 'characterizes': histone_antibody['@id']})
    testapp.patch_json(base_antibody_characterization2['@id'], {'target': histone_target['@id'], 'characterizes': histone_antibody['@id']})
    testapp.patch_json(base_replicate['@id'], {'antibody': histone_antibody['@id'], 'library': base_library['@id']})
    testapp.patch_json(base_experiment['@id'], {'assay_term_id': 'OBI:0000716', 'assay_term_name': 'ChIP-seq', 'biosample_term_id': 'EFO:0002067', 'biosample_term_name': 'K562',  'biosample_type': 'immortalized cell line', 'target': 
                                                histone_target['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'not eligible antibody' for error in errors_list)


def test_audit_experiment_biosample_type_missing(testapp, base_experiment):
    testapp.patch_json(base_experiment['@id'], {'biosample_term_id': "EFO:0002067",
                                                'biosample_term_name': 'K562'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'missing biosample_type' for error in errors_list)


def test_audit_experiment_biosample_match(testapp, base_experiment,
                                          base_biosample, base_replicate,
                                          base_library):
    testapp.patch_json(base_biosample['@id'], {'biosample_term_id': "EFO:0003042",
                                               'biosample_term_name': 'H1-hESC',
                                               'biosample_type': 'stem cell'})
    testapp.patch_json(base_replicate['@id'], {'library': base_library['@id']})
    testapp.patch_json(base_experiment['@id'], {'biosample_term_id': "UBERON:0002116",
                                                'biosample_term_name': 'ileum',
                                                'biosample_type': 'tissue'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'inconsistent library biosample' for error in errors_list)


def test_audit_experiment_documents(testapp, base_experiment, base_library, base_replicate):
    testapp.patch_json(base_replicate['@id'], {'library': base_library['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'missing documents' for error in errors_list)


def test_audit_experiment_documents_excluded(testapp, base_experiment,
                                             base_library, award, base_replicate):
    testapp.patch_json(base_replicate['@id'], {'library': base_library['@id']})
    testapp.patch_json(award['@id'], {'rfa': 'modENCODE'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] != 'missing documents' for error in errors_list)


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
    testapp.patch_json(biosample_1['@id'], {'model_organism_sex': 'male'})
    testapp.patch_json(biosample_2['@id'], {'model_organism_sex': 'female'})
    testapp.patch_json(biosample_1['@id'], {'model_organism_age_units': 'day',
                                            'model_organism_age': '54'})
    testapp.patch_json(biosample_2['@id'], {'model_organism_age_units': 'day',
                                            'model_organism_age': '54'})
    testapp.patch_json(biosample_1['@id'], {'organism': '/organisms/mouse/'})
    testapp.patch_json(biosample_2['@id'], {'organism': '/organisms/mouse/'})
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_2['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'inconsistent sex' for error in errors_list)


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
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'inconsistent age' for error in errors_list)


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
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'inconsistent donor' for error in errors_list)


def test_audit_experiment_with_library_without_biosample(testapp, base_experiment, base_replicate,
                                                         library_no_biosample):
    testapp.patch_json(base_replicate['@id'], {'library': library_no_biosample['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'missing biosample' for error in errors_list)


def test_audit_experiment_with_RNA_library_no_size_range(testapp, base_experiment, base_replicate,
                                                         base_library):
    testapp.patch_json(base_library['@id'], {'nucleic_acid_term_id':
                                             'SO:0000356', 'nucleic_acid_term_name': 'RNA'})
    testapp.patch_json(base_replicate['@id'], {'library': base_library['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'missing RNA fragment size' for error in errors_list)


def test_audit_experiment_with_RNA_library_with_size_range(testapp, base_experiment, base_replicate,
                                                           base_library):
    testapp.patch_json(base_library['@id'], {'nucleic_acid_term_id': 'SO:0000356',
                                             'nucleic_acid_term_name': 'RNA', 'size_range': '>200'})
    testapp.patch_json(base_replicate['@id'], {'library': base_library['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert all(error['category'] != 'missing RNA fragment size' for error in errors_list)


def test_audit_experiment_with_RNA_library_array_size_range(testapp, base_experiment,
                                                            base_replicate,
                                                            base_library):
    testapp.patch_json(base_library['@id'], {'nucleic_acid_term_id': 'SO:0000356',
                                             'nucleic_acid_term_name': 'RNA'})
    testapp.patch_json(base_replicate['@id'], {'library': base_library['@id']})
    testapp.patch_json(base_experiment['@id'], {'assay_term_name':
                                                'transcription profiling by array assay'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert all(error['category'] != 'missing RNA fragment size' for error in errors_list)


def test_audit_experiment_needs_pipeline(testapp,  replicate, library, experiment, fastq_file):
    testapp.patch_json(experiment['@id'], {'status': 'released', 'date_released': '2016-01-01'})
    testapp.patch_json(library['@id'], {'size_range': '>200'})
    testapp.patch_json(replicate['@id'], {'library': library['@id']})
    testapp.patch_json(fastq_file['@id'], {'run_type': 'single-ended'})
    testapp.patch_json(experiment['@id'], {'assay_term_name': 'RNA-seq'})
    res = testapp.get(experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'needs pipeline run' for error in errors_list)


def test_audit_experiment_biosample_term_id(testapp, base_experiment):
    testapp.patch_json(base_experiment['@id'], {'biosample_term_id': 'CL:349829',
                                                'biosample_type': 'tissue',
                                                'status': 'released',
                                                'date_released': '2016-01-01'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] ==
               'experiment with biosample term-type mismatch' for error in errors_list)


def test_audit_experiment_biosample_ntr_term_id(testapp, base_experiment):
    testapp.patch_json(base_experiment['@id'], {'biosample_term_id': 'NTR:349829',
                                                'biosample_type': 'tissue',
                                                'status': 'released',
                                                'date_released': '2016-01-01'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert all(error['category'] !=
               'experiment with biosample term-type mismatch' for error in errors_list)


def test_audit_experiment_replicate_with_file(testapp, file_fastq,
                                              base_experiment,
                                              base_replicate,
                                              base_library):
    testapp.patch_json(file_fastq['@id'], {'replicate': base_replicate['@id']})
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'RNA-seq'})
    testapp.patch_json(base_experiment['@id'], {'status': 'released',
                                                'date_released': '2016-01-01'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert all((error['category'] != 'missing raw data in replicate') for error in errors_list)


def test_audit_experiment_pipeline_assay_term_id_consistency(
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
                                             'assay_term_id': 'OBI:0000716',
                                             'assay_term_name': 'RNA-seq'})
    testapp.patch_json(experiment['@id'], {'assay_term_name': 'RNA-seq',
                                           'assay_term_id': 'OBI:0001271'})
    res = testapp.get(experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'inconsistent assay_term_id' for error in errors_list)


def test_audit_experiment_needs_pipeline_and_has_one(testapp,  replicate, library,
                                                     experiment, fastq_file, bam_file,
                                                     analysis_step_run_bam,
                                                     analysis_step_version_bam, analysis_step_bam,
                                                     pipeline_bam):
    testapp.patch_json(experiment['@id'], {'status': 'released', 'date_released': '2016-01-01'})
    testapp.patch_json(library['@id'], {'size_range': '>200'})
    testapp.patch_json(replicate['@id'], {'library': library['@id']})
    testapp.patch_json(fastq_file['@id'], {'run_type': 'single-ended'})
    testapp.patch_json(bam_file['@id'], {'step_run': analysis_step_run_bam['@id']})
    testapp.patch_json(pipeline_bam['@id'], {'title':
                                             'RNA-seq of long RNAs (single-end, unstranded)'})
    testapp.patch_json(experiment['@id'], {'assay_term_name': 'RNA-seq'})
    res = testapp.get(experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert all(error['category'] != 'needs pipeline run' for error in errors_list)


def test_audit_experiment_needs_pipeline_chip_seq(testapp, replicate, library,
                                                  experiment, fastq_file,
                                                  target_H3K27ac):
    testapp.patch_json(experiment['@id'], {'status': 'released',
                                           'target': target_H3K27ac['@id'],
                                           'date_released': '2016-01-01'})
    testapp.patch_json(library['@id'], {'size_range': '200-600'})
    testapp.patch_json(replicate['@id'], {'library': library['@id']})
    testapp.patch_json(fastq_file['@id'], {'run_type': 'single-ended'})
    testapp.patch_json(experiment['@id'], {'assay_term_name': 'ChIP-seq'})
    res = testapp.get(experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'needs pipeline run' for error in errors_list)


def test_audit_experiment_needs_pipeline_chip_seq_and_has_one(testapp, replicate, library,
                                                              experiment, fastq_file,
                                                              target_H3K27ac,  bam_file,
                                                              analysis_step_run_bam,
                                                              analysis_step_version_bam,
                                                              analysis_step_bam,
                                                              pipeline_bam):
    testapp.patch_json(experiment['@id'], {'status': 'released',
                                           'target': target_H3K27ac['@id'],
                                           'date_released': '2016-01-01'})
    testapp.patch_json(library['@id'], {'size_range': '200-600'})
    testapp.patch_json(replicate['@id'], {'library': library['@id']})
    testapp.patch_json(fastq_file['@id'], {'run_type': 'single-ended'})
    testapp.patch_json(bam_file['@id'], {'step_run': analysis_step_run_bam['@id']})
    testapp.patch_json(pipeline_bam['@id'], {'title':
                                             'Histone ChIP-seq'})
    testapp.patch_json(experiment['@id'], {'assay_term_name': 'ChIP-seq'})
    res = testapp.get(experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert all(error['category'] != 'needs pipeline run' for error in errors_list)


def test_audit_experiment_replicate_with_no_files(testapp,
                                                  base_experiment,
                                                  base_replicate,
                                                  base_library):
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'RNA-seq'})
    testapp.patch_json(base_experiment['@id'], {'status': 'released',
                                                'date_released': '2016-01-01'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'missing raw data in replicate' for error in errors_list)


def test_audit_experiment_replicate_with_no_files_dream(testapp,
                                                        base_experiment,
                                                        base_replicate,
                                                        base_library):
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'RNA-seq',
                                                'internal_tags': ['DREAM'],
                                                'status': 'released',
                                                'date_released': '2016-01-01'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert all(error['category'] != 'missing raw data in replicate' for error in errors_list)


def test_audit_experiment_replicate_with_no_files_warning(testapp, file_bed_methyl,
                                                          base_experiment,
                                                          base_replicate,
                                                          base_library):
    testapp.patch_json(file_bed_methyl['@id'], {'replicate': base_replicate['@id']})
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'RNA-seq'})
    testapp.patch_json(base_experiment['@id'], {'status': 'started'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        if error_type == 'ERROR':
            errors_list.extend(errors[error_type])
    assert any(error['category'] == 'missing raw data in replicate' for error in errors_list)


def test_audit_experiment_missing_biosample_term_id(testapp, base_experiment):
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] ==
               'experiment missing biosample_term_id' for error in errors_list)


def test_audit_experiment_bind_n_seq_missing_biosample_term_id(testapp, base_experiment):
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'RNA Bind-n-Seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert all(error['category'] !=
               'experiment missing biosample_term_id' for error in errors_list)


def test_audit_experiment_missing_biosample_type(testapp, base_experiment):
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] ==
               'experiment missing biosample_type' for error in errors_list)


def test_audit_experiment_with_biosample_type(testapp, base_experiment):
    testapp.patch_json(base_experiment['@id'], {'biosample_type': 'immortalized cell line'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert all(error['category'] !=
               'experiment missing biosample_type' for error in errors_list)


def test_audit_experiment_replicate_with_no_fastq_files(testapp, file_bam,
                                                        base_experiment,
                                                        base_replicate,
                                                        base_library):
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'RNA-seq'})
    testapp.patch_json(base_experiment['@id'], {'status': 'released',
                                                'date_released': '2016-01-01'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'missing raw data in replicate' for error in errors_list)


def test_audit_experiment_mismatched_length_sequencing_files(testapp, file_bam, file_fastq,
                                                             base_experiment, file_fastq_2,
                                                             base_replicate,
                                                             base_library):
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'ChIP-seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'mixed run types'
               for error in errors_list)


def test_audit_experiment_mismatched_platforms(testapp, file_fastq,
                                               base_experiment, file_fastq_2,
                                               base_replicate, platform1,
                                               base_library, platform2):
    testapp.patch_json(file_fastq['@id'], {'platform': platform1['@id']})
    testapp.patch_json(file_fastq_2['@id'], {'platform': platform2['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'inconsistent platforms'
               for error in errors_list)


def test_audit_experiment_archived_files_mismatched_platforms(
        testapp, file_fastq, base_experiment, file_fastq_2, base_replicate,
        platform1, base_library, platform2):
    testapp.patch_json(file_fastq['@id'], {'platform': platform1['@id'],
                                           'status': 'archived'})
    testapp.patch_json(file_fastq_2['@id'], {'platform': platform2['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert all(error['category'] != 'inconsistent platforms'
               for error in errors_list)


def test_audit_experiment_internal_tag(testapp, base_experiment,
                                       base_biosample,
                                       library_1,
                                       replicate_1_1):
    testapp.patch_json(base_biosample['@id'], {'internal_tags': ['ENTEx']})
    testapp.patch_json(library_1['@id'], {'biosample': base_biosample['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'inconsistent internal tags' for error in errors_list)


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
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'inconsistent internal tags' for error in errors_list)


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
    #testapp.patch_json(biosample_2['@id'], {'internal_tags': ['ENTEx', 'SESCC']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_2['@id']})
    testapp.patch_json(replicate_1_2['@id'], {'library': library_2['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'inconsistent internal tags' for error in errors_list)

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
                                                                   file_fastq_3,
                                                                   file_fastq_4):
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'ChIP-seq'})
    testapp.patch_json(file_fastq_3['@id'], {'run_type': "single-ended"})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'mixed run types'
               for error in errors_list)


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
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'mixed read lengths'
               for error in errors_list)


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
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert all(error['category'] != 'mixed read lengths'
               for error in errors_list)


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
                                                'assay_term_id': 'OBI:0001864',
                                                'assay_term_name': 'RAMPAGE'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])

    assert any(error['category'] == 'insufficient read depth' for error in errors_list)


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
                                                'assay_term_id': 'OBI:0001864',
                                                'assay_term_name': 'RNA-seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'low read depth' for error in errors_list)


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
                                                'assay_term_id': 'OBI:0001864',
                                                'assay_term_name': 'RNA-seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'low replicate concordance' for error in errors_list)


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
                                                'assay_term_id': 'OBI:0001864',
                                                'assay_term_name': 'CRISPR genome editing followed by RNA-seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'insufficient read depth' for error in errors_list) and \
        any(error['category'] == 'missing spikeins' for error in errors_list)


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
                                                'assay_term_id': 'OBI:0001864',
                                                'assay_term_name': 'RNA-seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'insufficient read depth' for error in errors_list)


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
                                             'Histone ChIP-seq'})
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
                                                'assay_term_id': 'OBI:0001864',
                                                'assay_term_name': 'ChIP-seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'low read depth' for error in errors_list)


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
                                             'Histone ChIP-seq'})
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
                                                'assay_term_id': 'OBI:0001864',
                                                'assay_term_name': 'ChIP-seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'insufficient read depth' for error in errors_list)


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
                                             'Histone ChIP-seq'})

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
                                                'assay_term_id': 'OBI:0001864',
                                                'assay_term_name': 'ChIP-seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'missing target' for error in errors_list)


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
                                             'Histone ChIP-seq'})

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
                                                'assay_term_id': 'OBI:0001864',
                                                'assay_term_name': 'ChIP-seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'severe bottlenecking' for error in errors_list)


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
                                             'Histone ChIP-seq'})
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
                                                'assay_term_id': 'OBI:0001864',
                                                'assay_term_name': 'ChIP-seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert all(error['category'] != 'missing read depth' for error in errors_list)


def test_audit_experiment_out_of_date_analysis_added_fastq(testapp,
                                                           base_experiment,
                                                           replicate_1_1,
                                                           replicate_2_1,
                                                           file_fastq_3,
                                                           file_fastq_4,
                                                           file_bam_1_1,
                                                           file_bam_2_1):
    testapp.patch_json(file_bam_1_1['@id'], {'derived_from': [file_fastq_3['@id']]})
    testapp.patch_json(file_bam_2_1['@id'], {'derived_from': [file_fastq_3['@id']]})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'out of date analysis' for error in errors_list)


def test_audit_experiment_out_of_date_analysis_removed_fastq(testapp,
                                                             base_experiment,
                                                             replicate_1_1,
                                                             replicate_2_1,
                                                             file_fastq_3,
                                                             file_fastq_4,
                                                             file_bam_1_1,
                                                             file_bam_2_1):
    testapp.patch_json(file_bam_1_1['@id'], {'derived_from': [file_fastq_3['@id']]})
    testapp.patch_json(file_bam_2_1['@id'], {'derived_from': [file_fastq_4['@id']]})
    testapp.patch_json(file_fastq_3['@id'], {'status': 'deleted'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'out of date analysis' for error in errors_list)


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
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert all(error['category'] != 'out of date analysis' for error in errors_list)


def test_audit_experiment_modERN_control_missing_files(testapp,
                                                       award,
                                                       base_experiment,
                                                       replicate_1_1,
                                                       library_1,
                                                       biosample_1,
                                                       file_fastq_3,
                                                       file_fastq_4,
                                                       file_bam_1_1,
                                                       file_bam_2_1,
                                                       file_tsv_1_2,
                                                       analysis_step_run_bam,
                                                       analysis_step_version_bam,
                                                       analysis_step_bam,
                                                       pipeline_bam,
                                                       target_control):
    testapp.patch_json(pipeline_bam['@id'], {'title':
                                             'Transcription factor ChIP-seq pipeline (modERN)'})
    testapp.patch_json(base_experiment['@id'], {'target': target_control['@id'],
                                                'status': 'released',
                                                'date_released': '2016-01-01',
                                                "assay_term_id": "OBI:0001271",
                                                "assay_term_name": "ChIP-seq"})
    testapp.patch_json(award['@id'], {'rfa': 'modERN'})
    testapp.patch_json(file_fastq_4['@id'], {'replicate': replicate_1_1['@id']})
    testapp.patch_json(file_bam_1_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'assembly': 'mm10',
                                             'output_type': 'alignments',
                                             'file_format': 'bam',
                                             'derived_from': [file_fastq_3['@id']]})
    testapp.patch_json(file_bam_2_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'assembly': 'mm10',
                                             'output_type': 'signal of unique reads',
                                             'file_format': 'bigWig',
                                             'derived_from': [file_fastq_4['@id']]})
    testapp.patch_json(file_tsv_1_2['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'assembly': 'mm9',
                                             'output_type': 'read-depth normalized signal',
                                             'file_format': 'bigWig',
                                             'status': 'released',
                                             'derived_from': [file_fastq_4['@id']]})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'missing pipeline files' for error in errors_list)


def test_audit_experiment_modERN_experiment_missing_files(testapp,
                                                          award,
                                                          base_experiment,
                                                          replicate_1_1,
                                                          library_1,
                                                          biosample_1,
                                                          file_fastq_3,
                                                          file_fastq_4,
                                                          file_bam_1_1,
                                                          file_bam_2_1,
                                                          file_tsv_1_2,
                                                          analysis_step_run_bam,
                                                          analysis_step_version_bam,
                                                          analysis_step_bam,
                                                          pipeline_bam,
                                                          target_H3K9me3):

    testapp.patch_json(pipeline_bam['@id'], {'title':
                                             'Transcription factor ChIP-seq pipeline (modERN)'})
    testapp.patch_json(award['@id'], {'rfa': 'modERN'})
    testapp.patch_json(base_experiment['@id'], {'target': target_H3K9me3['@id'],
                                                'status': 'released',
                                                'date_released': '2016-01-01',
                                                'assay_term_id': 'OBI:0001864',
                                                'assay_term_name': 'ChIP-seq'})

    testapp.patch_json(file_fastq_4['@id'], {'replicate': replicate_1_1['@id']})
    testapp.patch_json(file_bam_1_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'assembly': 'mm10',
                                             'output_type': 'alignments',
                                             'file_format': 'bam',
                                             'derived_from': [file_fastq_3['@id']]})
    testapp.patch_json(file_bam_2_1['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'assembly': 'mm10',
                                             'output_type': 'signal of unique reads',
                                             'file_format': 'bigWig',
                                             'derived_from': [file_fastq_4['@id']]})
    testapp.patch_json(file_tsv_1_2['@id'], {'step_run': analysis_step_run_bam['@id'],
                                             'assembly': 'mm10',
                                             'output_type': 'read-depth normalized signal',
                                             'file_format': 'bigWig',
                                             'derived_from': [file_fastq_4['@id']]})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'missing pipeline files' for error in errors_list)


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
                                                'assay_term_id': 'OBI:0001863',
                                                'assay_term_name': 'whole-genome shotgun bisulfite sequencing'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'high lambda C methylation ratio' for error in errors_list)


def test_audit_experiment_ntr_term_id_mismatch(testapp, base_experiment):
    testapp.patch_json(base_experiment['@id'], {'assay_term_id': 'NTR:0000763',
                                                'assay_term_name': 'ChIP-seq'})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'mismatched assay_term_name' for error in errors_list)


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
                                                    target_H3K9me3,
                                                    award_modERN):

    testapp.patch_json(chip_seq_quality_metric['@id'], {'quality_metric_of': [file_bam_1_1['@id']],
                                                        'processing_stage': 'unfiltered',
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
    testapp.patch_json(base_experiment['@id'], {'target': target_H3K9me3['@id'],
                                                'status': 'released',
                                                'date_released': '2016-01-01',
                                                'assay_term_id': 'OBI:0001864',
                                                'assay_term_name': 'ChIP-seq',
                                                'award': award_modERN['@id']})
    res = testapp.get(base_experiment['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []

    for error_type in errors:
        errors_list.extend(errors[error_type])
        
        '''print (error_type)
        for e in errors[error_type]:
            print (e)
            print (e['category'])
            #if (e['category'].startswith('ChIP-seq')):
            print (e)
        '''
    assert any(error['category'] == 'insufficient read depth' for error in errors_list)
