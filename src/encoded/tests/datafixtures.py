import pytest
from .constants import *




@pytest.fixture
def attachment():
    return {'download': 'red-dot.png', 'href': RED_DOT}


@pytest.fixture
def fastq(fastq_no_replicate, replicate):
    item = fastq_no_replicate.copy()
    item['replicate'] = replicate['@id']
    return item


@pytest.fixture
def fastq_pair_1(fastq):
    item = fastq.copy()
    item['paired_end'] = '1'
    return item


@pytest.fixture
def base_matched_set(testapp, lab, award):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid']
    }
    return testapp.post_json('/matched_set', item, status=201).json['@graph'][0]



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
def matched_set(testapp, lab, award):
    item = {
        'lab': lab['@id'],
        'award': award['@id']
    }
    return item



@pytest.fixture
def gene_locations_wrong_assembly(testapp, human):
    item = {
        'uuid': 'd358f63b-63d6-408f-baca-13881c6c79a1',
        'dbxrefs': ['HGNC:7553'],
        'geneid': '4609',
        'symbol': 'MYC',
        'ncbi_entrez_status': 'live',
        'organism': human['uuid'],
        'locations': [{'assembly': 'mm10', 'chromosome': 'chr18', 'start': 47808713, 'end': 47814692}]
    }
    return item



@pytest.fixture
def crispr_deletion(lab, award):
    return {
        'lab': lab['@id'],
        'award': award['@id'],
        'category': 'deletion',
        'purpose': 'repression',
        'method': 'CRISPR'
    }


@pytest.fixture
def tale_deletion(lab, award):
    return {
        'lab': lab['@id'],
        'award': award['@id'],
        'category': 'deletion',
        'purpose': 'repression',
        'method': 'TALEN',
        'zygosity': 'heterozygous'
    }


@pytest.fixture
def crispr_tag(lab, award):
    return {
        'lab': lab['@id'],
        'award': award['@id'],
        'category': 'insertion',
        'purpose': 'tagging',
        'method': 'CRISPR'
    }


@pytest.fixture
def bombardment_tag(lab, award):
    return {
        'lab': lab['@id'],
        'award': award['@id'],
        'category': 'insertion',
        'purpose': 'tagging',
        'method': 'bombardment'
    }


@pytest.fixture
def recomb_tag(lab, award):
    return {
        'lab': lab['@id'],
        'award': award['@id'],
        'category': 'insertion',
        'purpose': 'tagging',
        'method': 'site-specific recombination'
    }


@pytest.fixture
def transfection_tag(lab, award):
    return {
        'lab': lab['@id'],
        'award': award['@id'],
        'category': 'insertion',
        'purpose': 'tagging',
        'method': 'stable transfection'
    }


@pytest.fixture
def crispri(lab, award):
    return {
        'lab': lab['@id'],
        'award': award['@id'],
        'category': 'interference',
        'purpose': 'repression',
        'method': 'CRISPR'
    }


@pytest.fixture
def rnai(lab, award):
    return {
        'lab': lab['@id'],
        'award': award['@id'],
        'category': 'interference',
        'purpose': 'repression',
        'method': 'RNAi'
    }


@pytest.fixture
def mutagen(lab, award):
    return {
        'lab': lab['@id'],
        'award': award['@id'],
        'category': 'mutagenesis',
        'purpose': 'repression',
        'method': 'mutagen treatment'
    }


@pytest.fixture
def tale_replacement(lab, award):
    return {
        'lab': lab['@id'],
        'award': award['@id'],
        'category': 'replacement',
        'purpose': 'characterization',
        'method': 'TALEN',
        'zygosity': 'heterozygous'
    }

@pytest.fixture
def mpra(lab, award):
    return {
        'lab': lab['@id'],
        'award': award['@id'],
        'category': 'insertion',
        'purpose': 'characterization',
        'method': 'transduction'
    }


@pytest.fixture
def starr_seq(lab, award):
    return {
        'lab': lab['@id'],
        'award': award['@id'],
        'category': 'episome',
        'purpose': 'characterization',
        'method': 'transient transfection'
    }


@pytest.fixture
def introduced_elements(lab, award):
    return {
        'lab': lab['@id'],
        'award': award['@id'],
        'category': 'episome',
        'purpose': 'characterization',
        'method': 'transient transfection',
        'introduced_elements': 'genomic DNA regions'
    }


@pytest.fixture(scope='session')
def test_accession_app(request, check_constraints, zsa_savepoints, app_settings):
    from encoded import main
    app_settings = app_settings.copy()
    app_settings['accession_factory'] = 'encoded.server_defaults.test_accession'
    return main({}, **app_settings)


@pytest.fixture
def test_accession_anontestapp(request, test_accession_app, external_tx, zsa_savepoints):
    '''TestApp with JSON accept header.
    '''
    from webtest import TestApp
    environ = {
        'HTTP_ACCEPT': 'application/json',
    }
    return TestApp(test_accession_app, environ)



@pytest.fixture
def reference_epigenome_16(award, lab):
    return {
        'award': award['@id'],
        'lab': lab['@id'],
        'schema_version': '16',
        'dbxrefs': ['IHEC:IHECRE00004643.1'],
    }


@pytest.fixture
def crispr(lab, award, source):
    return {
        'lab': lab['uuid'],
        'award': award['uuid'],
        'source': source['uuid'],
        'guide_rna_sequences': [
            "ACA",
            "GCG"
        ],
        'insert_sequence': 'TCGA',
        'aliases': ['encode:crispr_technique1'],
        '@type': ['Crispr', 'ModificationTechnique', 'Item'],
        '@id': '/crisprs/79c1ec08-c878-4419-8dba-66aa4eca156b/',
        'uuid': '79c1ec08-c878-4419-8dba-66aa4eca156b'
    }



@pytest.fixture
def lookup_column_value_validate():
    valid = {
        'assay_term_name': 'long read RNA-seq',
        'lab.title': 'John Stamatoyannopoulos, UW',
        'audit': '',
        'award.project': 'Roadmap',
        '@id': '/experiments/ENCSR751ISO/',
        'level.name': '',
        '@type': 'Experiment,Dataset,Item'
    }
    return valid



@pytest.fixture
def testing_download(testapp):
    url = '/testing-downloads/'
    item = {
        'attachment': {
            'download': 'red-dot.png',
            'href': RED_DOT,
        },
        'attachment2': {
            'download': 'blue-dot.png',
            'href': BLUE_DOT,
        },
    }
    res = testapp.post_json(url, item, status=201)
    return res.location


@pytest.fixture
def mapped_run_type_on_fastq(award, experiment, lab, platform1):
    return {
        'award': award['@id'],
        'dataset': experiment['@id'],
        'lab': lab['@id'],
        'file_format': 'fastq',
        'file_size': 2535345,
        'platform': platform1['@id'],
        'run_type': 'paired-ended',
        'mapped_run_type': 'single-ended',
        'md5sum': '01234567890123456789abcdefabcdef',
        'output_type': 'raw data',
        'status': 'in progress',
    }
    

@pytest.fixture
def mapped_run_type_on_bam(award, experiment, lab):
    return {
        'award': award['@id'],
        'dataset': experiment['@id'],
        'lab': lab['@id'],
        'file_format': 'bam',
        'assembly': 'mm10',
        'file_size': 2534535,
        'mapped_run_type': 'single-ended',
        'md5sum': 'abcdef01234567890123456789abcdef',
        'output_type': 'alignments',
        'status': 'in progress',
    }

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
def spearman_correlation_quality_metric(testapp, analysis_step_run_bam, file_tsv_1_2, award, lab):
    item = {
        'step_run': analysis_step_run_bam['@id'],
        'quality_metric_of': [file_tsv_1_2['@id']],
        'Spearman correlation': 0.7,
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
def ontology():
    ontology = {
        'UBERON:0002469': {
            'part_of': [
                'UBERON:0001043',
                'UBERON:0001096',
                'UBERON:1111111'
            ]
        },
        'UBERON:1111111': {
            'part_of': []
        },
        'UBERON:0001096': {
            'part_of': []
        },
        'UBERON:0001043': {
            'part_of': [
                'UBERON:0001007',
                'UBERON:0004908'
            ]
        },
        'UBERON:0001007': {
            'part_of': []
        },
        'UBERON:0004908': {
            'part_of': [
                'UBERON:0001043',
                'UBERON:1234567'
            ]
        },
        'UBERON:1234567': {
            'part_of': [
                'UBERON:0006920'
            ]
        },
        'UBERON:0006920': {
            'part_of': []
        },
        'UBERON:1231231': {
            'name': 'liver'
        }
    }
    return ontology


@pytest.fixture
def lookup_column_value_item():
    item = {
        'assay_term_name': 'long read RNA-seq',
        'lab': {'title': 'John Stamatoyannopoulos, UW'},
        'accession': 'ENCSR751ISO',
        'assay_title': 'long read RNA-seq',
        'award': {'project': 'Roadmap'},
        'status': 'released',
        '@id': '/experiments/ENCSR751ISO/',
        '@type': ['Experiment', 'Dataset', 'Item'],
        'biosample_ontology': {'term_name': 'midbrain'}
    }
    return item


@pytest.fixture
def lookup_column_value_validate():
    valid = {
        'assay_term_name': 'long read RNA-seq',
        'lab.title': 'John Stamatoyannopoulos, UW',
        'audit': '',
        'award.project': 'Roadmap',
        '@id': '/experiments/ENCSR751ISO/',
        'level.name': '',
        '@type': 'Experiment,Dataset,Item'
    }
    return valid


@pytest.fixture
def review(lab, submitter):
    review = {
        'reviewed_by': submitter['@id'],
        'status': 'compliant',
        'lab': lab['@id'],
    }
    return review



@pytest.fixture
def external_accession(fastq_pair_1):
    item = fastq_pair_1.copy()
    item['external_accession'] = 'EXTERNAL'
    return item
