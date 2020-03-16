import pytest

####
# This file is for fixtures that have no specific schema and can be shared across multiples test
####

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


RED_DOT = """data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUA
AAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO
9TXL0Y4OHwAAAABJRU5ErkJggg=="""


@pytest.fixture
def attachment():
    return {'download': 'red-dot.png', 'href': RED_DOT}


@pytest.fixture
def gm_characterization(testapp, award, lab, construct_genetic_modification_N, attachment):
    item = {
        'characterizes': construct_genetic_modification_N['@id'],
        'award': award['@id'],
        'lab': lab['@id'],
        'attachment': attachment,
    }
    return testapp.post_json('/genetic_modification_characterization', item).json['@graph'][0]


@pytest.fixture
def ucsc_browser_composite(testapp, lab, award):
    item = {
        'award': award['@id'],
        'lab': lab['@id'],
    }
    return testapp.post_json('/ucsc_browser_composite', item).json['@graph'][0]


@pytest.fixture
def fastq_no_replicate(award, experiment, lab, platform1):
    return {
        'award': award['@id'],
        'dataset': experiment['@id'],
        'lab': lab['@id'],
        'file_format': 'fastq',
        'platform': platform1['@id'],
        'file_size': 23242,
        'run_type': 'paired-ended',
        'paired_end': '1',
        'md5sum': '0123456789abcdef0123456789abcdef',
        'output_type': 'raw data',
        'status': 'in progress',
    }


@pytest.fixture
def fastq(fastq_no_replicate, replicate_url):
    item = fastq_no_replicate.copy()
    item['replicate'] = replicate_url['@id']
    return item


@pytest.fixture
def fastq_pair_1(fastq):
    item = fastq.copy()
    item['paired_end'] = '1'
    return item
