import pytest
from .constants import *

@pytest.fixture
def lab(testapp):
    item = {
        'name': 'encode-lab',
        'title': 'ENCODE lab',
    }
    return testapp.post_json('/lab', item).json['@graph'][0]


@pytest.fixture
def remc_lab(testapp):
    item = {
        'name': 'remc-lab',
        'title': 'REMC lab',
    }
    return testapp.post_json('/lab', item).json['@graph'][0]


@pytest.fixture
def admin(testapp):
    item = {
        'first_name': 'Test',
        'last_name': 'Admin',
        'email': 'admin@example.org',
        'groups': ['admin'],
    }
    # User @@object view has keys omitted.
    res = testapp.post_json('/user', item)
    return testapp.get(res.location).json


@pytest.fixture
def wrangler(testapp):
    item = {
        # antibody_characterization reviewed_by has linkEnum
        'uuid': '4c23ec32-c7c8-4ac0-affb-04befcc881d4',
        'first_name': 'Wrangler',
        'last_name': 'Admin',
        'email': 'wrangler@example.org',
        'groups': ['admin'],
    }
    # User @@object view has keys omitted.
    res = testapp.post_json('/user', item)
    return testapp.get(res.location).json


@pytest.fixture
def verified_member(testapp, lab, award):
    item = {
        'first_name': 'ENCODE',
        'last_name': 'VerifiedMember',
        'email': 'Verified_member@example.org',
        'groups': ['verified'],
    }
    # User @@object view has keys omitted.
    res = testapp.post_json('/user', item)
    return testapp.get(res.location).json


@pytest.fixture
def unverified_member(testapp, lab, award):
    item = {
        'first_name': 'ENCODE',
        'last_name': 'NonVerifiedMember',
        'email': 'Non_verified_member@example.org',
    }
    # User @@object view has keys omitted.
    res = testapp.post_json('/user', item)
    return testapp.get(res.location).json


@pytest.fixture
def submitter(testapp, lab, award):
    item = {
        'first_name': 'ENCODE',
        'last_name': 'Submitter',
        'email': 'encode_submitter@example.org',
        'submits_for': [lab['@id']],
        'viewing_groups': [award['viewing_group']],
    }
    # User @@object view has keys omitted.
    res = testapp.post_json('/user', item)
    return testapp.get(res.location).json


@pytest.fixture
def access_key(testapp, submitter):
    description = 'My programmatic key'
    item = {
        'user': submitter['@id'],
        'description': description,
    }
    res = testapp.post_json('/access_key', item)
    result = res.json['@graph'][0].copy()
    result['secret_access_key'] = res.json['secret_access_key']
    return result


@pytest.fixture
def viewing_group_member(testapp, award):
    item = {
        'first_name': 'Viewing',
        'last_name': 'Group',
        'email': 'viewing_group_member@example.org',
        'viewing_groups': [award['viewing_group']],
    }
    # User @@object view has keys omitted.
    res = testapp.post_json('/user', item)
    return testapp.get(res.location).json


@pytest.fixture
def remc_member(testapp, remc_lab):
    item = {
        'first_name': 'REMC',
        'last_name': 'Member',
        'email': 'remc_member@example.org',
        'submits_for': [remc_lab['@id']],
        'viewing_groups': ['REMC'],
    }
    # User @@object view has keys omitted.
    res = testapp.post_json('/user', item)
    return testapp.get(res.location).json


@pytest.fixture
def award(testapp):
    item = {
        'name': 'encode3-award',
        'rfa': 'ENCODE3',
        'project': 'ENCODE',
        'title': 'A Generic ENCODE3 Award',
        'viewing_group': 'ENCODE3',
    }
    return testapp.post_json('/award', item).json['@graph'][0]


@pytest.fixture
def award_encode4(testapp):
    item = {
        'name': 'encode4-award',
        'rfa': 'ENCODE4',
        'project': 'ENCODE',
        'title': 'A Generic ENCODE4 Award',
        'viewing_group': 'ENCODE4',
    }
    return testapp.post_json('/award', item).json['@graph'][0]


@pytest.fixture
def award_modERN(testapp):
    item = {
        'name': 'modERN-award',
        'rfa': 'modERN',
        'project': 'modERN',
        'title': 'A Generic modERN Award',
        'viewing_group': 'ENCODE3',
    }
    return testapp.post_json('/award', item).json['@graph'][0]


@pytest.fixture
def remc_award(testapp):
    item = {
        'name': 'remc-award',
        'rfa': 'GGR',
        'project': 'GGR',
        'title': 'A Generic REMC Award',
        'viewing_group': 'REMC',
    }
    return testapp.post_json('/award', item).json['@graph'][0]


@pytest.fixture
def encode2_award(testapp):
    item = {
        # upgrade/shared.py ENCODE2_AWARDS
        'uuid': '1a4d6443-8e29-4b4a-99dd-f93e72d42418',
        'name': 'encode2-award',
        'rfa': 'ENCODE2',
        'project': 'ENCODE',
        'title': 'A Generic ENCODE2 Award',
        'viewing_group': 'ENCODE3',
    }
    return testapp.post_json('/award', item).json['@graph'][0]


@pytest.fixture
def source(testapp):
    item = {
        'name': 'sigma',
        'title': 'Sigma-Aldrich',
        'url': 'http://www.sigmaaldrich.com',
        'status': 'released'
    }
    return testapp.post_json('/source', item).json['@graph'][0]


@pytest.fixture
def human(testapp):
    item = {
        'uuid': '7745b647-ff15-4ff3-9ced-b897d4e2983c',
        'name': 'human',
        'scientific_name': 'Homo sapiens',
        'taxon_id': '9606',
        'status': 'released'
    }
    return testapp.post_json('/organism', item).json['@graph'][0]


@pytest.fixture
def mouse(testapp):
    item = {
        'uuid': '3413218c-3d86-498b-a0a2-9a406638e786',
        'name': 'mouse',
        'scientific_name': 'Mus musculus',
        'taxon_id': '10090',
        'status': 'released'
    }
    return testapp.post_json('/organism', item).json['@graph'][0]


@pytest.fixture
def fly(testapp):
    item = {
        'uuid': 'ab546d43-8e2a-4567-8db7-a217e6d6eea0',
        'name': 'dmelanogaster',
        'scientific_name': 'Drosophila melanogaster',
        'taxon_id': '7227',
        'status': 'released'
    }
    return testapp.post_json('/organism', item).json['@graph'][0]


@pytest.fixture
def organism(human):
    return human


@pytest.fixture
def ctcf(testapp, organism):
    item = {
        'uuid': 'a9288b44-6ef4-460e-a3d6-464fd625b103',
        'dbxrefs': ['HGNC:13723'],
        'geneid': '10664',
        'symbol': 'CTCF',
        'ncbi_entrez_status': 'live',
        'organism': organism['uuid'],
    }
    return testapp.post_json('/gene', item).json['@graph'][0]


@pytest.fixture
def gene(ctcf):
    return ctcf


@pytest.fixture
def bap1(testapp, organism):
    item = {
        'uuid': '91205c22-2748-47e1-b261-8c38236f4e98',
        'dbxrefs': ['HGNC:950'],
        'geneid': '8314',
        'symbol': 'BAP1',
        'ncbi_entrez_status': 'live',
        'organism': organism['uuid'],
    }
    return testapp.post_json('/gene', item).json['@graph'][0]


@pytest.fixture
def gene(bap1):
    return bap1


@pytest.fixture
def heart(testapp):
    item = {
        'term_id': 'UBERON:0000948',
        'term_name': 'heart',
        'classification': 'tissue',
    }
    return testapp.post_json('/biosample_type', item).json['@graph'][0]


@pytest.fixture
def biosample(testapp, source, lab, award, organism, heart):
    item = {
        'biosample_ontology': heart['uuid'],
        'source': source['@id'],
        'lab': lab['@id'],
        'award': award['@id'],
        'organism': organism['@id'],
    }
    return testapp.post_json('/biosample', item).json['@graph'][0]


@pytest.fixture
def library(testapp, lab, award, biosample):
    item = {
        'nucleic_acid_term_name': 'DNA',
        'lab': lab['@id'],
        'award': award['@id'],
        'biosample': biosample['@id'],
    }
    return testapp.post_json('/library', item).json['@graph'][0]


@pytest.fixture
def cell_free(testapp):
    item = {
        'term_id': 'NTR:0000471',
        'term_name': 'cell-free sample',
        'classification': 'cell-free sample',
    }
    return testapp.post_json('/biosample_type', item).json['@graph'][0]


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
def replicate(testapp, experiment, library):
    item = {
        'experiment': experiment['@id'],
        'library': library['@id'],
        'biological_replicate_number': 1,
        'technical_replicate_number': 1,
    }
    return testapp.post_json('/replicate', item).json['@graph'][0]


@pytest.fixture
def file(testapp, lab, award, experiment):
    item = {
        'dataset': experiment['@id'],
        'file_format': 'fasta',
        'md5sum': 'd41d8cd98f00b204e9800998ecf8427e',
        'output_type': 'raw data',
        'lab': lab['@id'],
        'file_size': 34,
        'award': award['@id'],
        'status': 'in progress',  # avoid s3 upload codepath
    }
    return testapp.post_json('/file', item).json['@graph'][0]


@pytest.fixture
def fastq_file(testapp, lab, award, experiment, replicate, platform1):
    item = {
        'dataset': experiment['@id'],
        'file_format': 'fastq',
        'md5sum': '91be74b6e11515393507f4ebfa66d78b',
        'replicate': replicate['@id'],
        'output_type': 'reads',
        "read_length": 36,
        'file_size': 34,
        'platform': platform1['@id'],
        'run_type': 'single-ended',
        'lab': lab['@id'],
        'award': award['@id'],
        'status': 'in progress',  # avoid s3 upload codepath
    }
    return testapp.post_json('/file', item).json['@graph'][0]


@pytest.fixture
def bam_file(testapp, lab, award, experiment):
    item = {
        'dataset': experiment['@id'],
        'file_format': 'bam',
        'file_size': 34,
        'md5sum': '91be74b6e11515393507f4ebfa66d78c',
        'output_type': 'alignments',
        'assembly': 'hg19',
        'lab': lab['@id'],
        'award': award['@id'],
        'status': 'in progress',  # avoid s3 upload codepath
    }
    return testapp.post_json('/file', item).json['@graph'][0]


@pytest.fixture
def bigWig_file(testapp, lab, award, experiment):
    item = {
        'dataset': experiment['@id'],
        'file_format': 'bigWig',
        'md5sum': '91be74b6e11515393507f4ebfa66d78d',
        'output_type': 'signal of unique reads',
        'assembly': 'mm10',
        'file_size': 34,
        'lab': lab['@id'],
        'award': award['@id'],
        'status': 'in progress',  # avoid s3 upload codepath
    }
    return testapp.post_json('/file', item).json['@graph'][0]


@pytest.fixture
def file_ucsc_browser_composite(testapp, lab, award, ucsc_browser_composite):
    item = {
        'dataset': ucsc_browser_composite['@id'],
        'file_format': 'fasta',
        'md5sum': '91be74b6e11515393507f4ebfa66d77a',
        'output_type': 'raw data',
        'file_size': 34,
        'lab': lab['@id'],
        'award': award['@id'],
        'status': 'in progress',  # avoid s3 upload codepath
    }
    return testapp.post_json('/file', item).json['@graph'][0]


@pytest.fixture
def antibody_lot(testapp, lab, award, source, mouse, target):
    item = {
        'product_id': 'WH0000468M1',
        'lot_id': 'CB191-2B3',
        'award': award['@id'],
        'lab': lab['@id'],
        'source': source['@id'],
        'host_organism': mouse['@id'],
        'targets': [target['@id']],
    }
    return testapp.post_json('/antibody_lot', item).json['@graph'][0]


@pytest.fixture
def target(testapp, organism):
    item = {
        'label': 'ATF4',
        'target_organism': organism['@id'],
        'investigated_as': ['transcription factor'],
    }
    return testapp.post_json('/target', item).json['@graph'][0]


@pytest.fixture
def target_H3K27ac(testapp, organism):
    item = {
        'label': 'H3K27ac',
        'target_organism': organism['@id'],
        'investigated_as': ['histone',
                            'narrow histone mark']
    }
    return testapp.post_json('/target', item).json['@graph'][0]


@pytest.fixture
def target_H3K9me3(testapp, organism):
    item = {
        'label': 'H3K9me3',
        'target_organism': organism['@id'],
        'investigated_as': ['histone',
                            'broad histone mark']
    }
    return testapp.post_json('/target', item).json['@graph'][0]


@pytest.fixture
def target_promoter(testapp, fly):
    item = {
        'label': 'daf-2',
        'target_organism': fly['@id'],
        'investigated_as': ['other context']
    }
    return testapp.post_json('/target', item).json['@graph'][0]


@pytest.fixture
def treatment(testapp, organism):
    item = {
        'treatment_term_name': 'ethanol',
        'treatment_type': 'chemical'
    }
    return testapp.post_json('/treatment', item).json['@graph'][0]


@pytest.fixture
def attachment():
    return {'download': 'red-dot.png', 'href': RED_DOT}


@pytest.fixture
def antibody_characterization(testapp, award, lab, target, antibody_lot, attachment):
    item = {
        'characterizes': antibody_lot['@id'],
        'target': target['@id'],
        'award': award['@id'],
        'lab': lab['@id'],
        'attachment': attachment,
        'secondary_characterization_method': 'dot blot assay',
    }
    return testapp.post_json('/antibody_characterization', item).json['@graph'][0]


@pytest.fixture
def construct_genetic_modification(
        testapp,
        lab,
        award,
        document,
        target,
        target_promoter):
    item = {
        'award': award['@id'],
        'documents': [document['@id']],
        'lab': lab['@id'],
        'category': 'insertion',
        'purpose': 'tagging',
        'method': 'stable transfection',
        'introduced_tags': [{'name':'eGFP', 'location': 'C-terminal', 'promoter_used': target_promoter['@id']}],
        'modified_site_by_target_id': target['@id']
    }
    return testapp.post_json('/genetic_modification', item).json['@graph'][0]

@pytest.fixture
def construct_genetic_modification_N(
        testapp,
        lab,
        award,
        document,
        target):
    item = {
        'award': award['@id'],
        'documents': [document['@id']],
        'lab': lab['@id'],
        'category': 'insertion',
        'purpose': 'tagging',
        'method': 'stable transfection',
        'introduced_tags': [{'name':'eGFP', 'location': 'N-terminal'}],
        'modified_site_by_target_id': target['@id']
    }
    return testapp.post_json('/genetic_modification', item).json['@graph'][0]


@pytest.fixture
def interference_genetic_modification(
        testapp,
        lab,
        award,
        document,
        target):
    item = {
        'award': award['@id'],
        'documents': [document['@id']],
        'lab': lab['@id'],
        'category': 'interference',
        'purpose': 'repression',
        'method': 'RNAi',        
        'modified_site_by_target_id': target['@id']
    }
    return testapp.post_json('/genetic_modification', item).json['@graph'][0]


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
def publication_data(testapp, lab, award, publication):
    item = {
        'award': award['@id'],
        'lab': lab['@id'],
        'references': [publication['@id']],
    }
    return testapp.post_json('/publication_data', item).json['@graph'][0]


@pytest.fixture
def annotation_dataset(testapp, lab, award):
    item = {
        'award': award['@id'],
        'lab': lab['@id'],
        'annotation_type': 'imputation'
    }
    return testapp.post_json('/annotation', item).json['@graph'][0]


@pytest.fixture
def publication(testapp, lab, award):
    item = {
        # upgrade/shared.py has a REFERENCES_UUID mapping.
        'uuid': '8312fc0c-b241-4cb2-9b01-1438910550ad',
        'title': "Test publication",
        'award': award['@id'],
        'lab': lab['@id'],
        'identifiers': ["doi:10.1214/11-AOAS466"],
    }
    print('submit publication')
    return testapp.post_json('/publication', item).json['@graph'][0]


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
def software(testapp, award, lab):
    item = {
        "name": "fastqc",
        "title": "FastQC",
        "description": "A quality control tool for high throughput sequence data.",
        "award": award['@id'],
        "lab": lab['@id'],
    }
    return testapp.post_json('/software', item).json['@graph'][0]


@pytest.fixture
def software_version(testapp, software):
    item = {
        'version': 'v0.11.2',
        'software': software['@id'],
    }
    return testapp.post_json('/software_version', item).json['@graph'][0]


@pytest.fixture
def analysis_step(testapp):
    item = {
        'step_label': 'fastqc-step',
        'title': 'fastqc step',
        'major_version': 1,
        'input_file_types': ['reads'],
        'analysis_step_types': ['QA calculation'],

    }
    return testapp.post_json('/analysis_step', item).json['@graph'][0]


@pytest.fixture
def analysis_step_version(testapp, analysis_step, software_version):
    item = {
        'analysis_step': analysis_step['@id'],
        'minor_version': 0,
        'software_versions': [
            software_version['@id'],
        ],
    }
    return testapp.post_json('/analysis_step_version', item).json['@graph'][0]


@pytest.fixture
def analysis_step_run(testapp, analysis_step_version):
    item = {
        'analysis_step_version': analysis_step_version['@id'],
        'status': 'released',
    }
    return testapp.post_json('/analysis_step_run', item).json['@graph'][0]


@pytest.fixture
def document(testapp, lab, award):
    item = {
        'award': award['@id'],
        'lab': lab['@id'],
        'document_type': 'growth protocol',
    }
    return testapp.post_json('/document', item).json['@graph'][0]


@pytest.fixture
def biosample_characterization(testapp, award, lab, biosample, attachment):
    item = {
        'characterizes': biosample['@id'],
        'award': award['@id'],
        'lab': lab['@id'],
        'attachment': attachment,
    }
    return testapp.post_json('/biosample_characterization', item).json['@graph'][0]


@pytest.fixture
def fly_donor(testapp, award, lab, fly):
    item = {
        'award': award['@id'],
        'lab': lab['@id'],
        'organism': fly['@id'],
    }
    return testapp.post_json('/fly_donor', item).json['@graph'][0]


@pytest.fixture
def mouse_donor(testapp, award, lab, mouse):
    item = {
        'award': award['@id'],
        'lab': lab['@id'],
        'organism': mouse['@id'],
    }
    return testapp.post_json('/mouse_donor', item).json['@graph'][0]


@pytest.fixture
def mouse_donor_1(testapp, award, lab, mouse):
    item = {
        'award': award['@id'],
        'lab': lab['@id'],
        'organism': mouse['@id'],
    }
    return testapp.post_json('/mouse_donor', item).json['@graph'][0]


@pytest.fixture
def mouse_donor_2(testapp, award, lab, mouse):
    item = {
        'award': award['@id'],
        'lab': lab['@id'],
        'organism': mouse['@id'],
    }
    return testapp.post_json('/mouse_donor', item).json['@graph'][0]


@pytest.fixture
def replicate_1_1(testapp, base_experiment):
    item = {
        'biological_replicate_number': 1,
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
def replicate_2_1(testapp, base_experiment):
    item = {
        'biological_replicate_number': 2,
        'technical_replicate_number': 1,
        'experiment': base_experiment['@id'],
    }
    return testapp.post_json('/replicate', item, status=201).json['@graph'][0]


@pytest.fixture
def base_biosample(testapp, lab, award, source, organism, heart):
    item = {
        'award': award['uuid'],
        'biosample_ontology': heart['uuid'],
        'lab': lab['uuid'],
        'organism': organism['uuid'],
        'source': source['uuid']
    }
    return testapp.post_json('/biosample', item, status=201).json['@graph'][0]


@pytest.fixture
def liver(testapp):
    item = {
        'term_id': 'UBERON:0002107',
        'term_name': 'liver',
        'classification': 'tissue',
    }
    return testapp.post_json('/biosample_type', item).json['@graph'][0]


@pytest.fixture
def biosample_1(testapp, lab, award, source, organism, liver):
    item = {
        'award': award['uuid'],
        'biosample_ontology': liver['uuid'],
        'lab': lab['uuid'],
        'organism': organism['uuid'],
        'source': source['uuid']
    }
    return testapp.post_json('/biosample', item, status=201).json['@graph'][0]


@pytest.fixture
def biosample_2(testapp, lab, award, source, organism, liver):
    item = {
        'award': award['uuid'],
        'biosample_ontology': liver['uuid'],
        'lab': lab['uuid'],
        'organism': organism['uuid'],
        'source': source['uuid']
    }
    return testapp.post_json('/biosample', item, status=201).json['@graph'][0]


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
def donor_1(testapp, lab, award, organism):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'organism': organism['uuid']
    }
    return testapp.post_json('/human-donors', item, status=201).json['@graph'][0]


@pytest.fixture
def donor_2(testapp, lab, award, organism):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'organism': organism['uuid']
    }
    return testapp.post_json('/human-donors', item, status=201).json['@graph'][0]


@pytest.fixture
def analysis_step_bam(testapp):
    item = {
        'step_label': 'bamqc-step',
        'title': 'bamqc step',
        'input_file_types': ['reads'],
        'analysis_step_types': ['QA calculation'],
        'major_version': 2
    }
    return testapp.post_json('/analysis_step', item).json['@graph'][0]


@pytest.fixture
def analysis_step_version_bam(testapp, analysis_step_bam, software_version):
    item = {
        'analysis_step': analysis_step_bam['@id'],
        'minor_version': 0,
        'software_versions': [
            software_version['@id'],
        ],
    }
    return testapp.post_json('/analysis_step_version', item).json['@graph'][0]


@pytest.fixture
def analysis_step_run_bam(testapp, analysis_step_version_bam):
    item = {
        'analysis_step_version': analysis_step_version_bam['@id'],
        'status': 'released',
        'aliases': ['modern:chip-seq-bwa-alignment-step-run-v-1-released']
    }
    return testapp.post_json('/analysis_step_run', item).json['@graph'][0]


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
def encode_lab(testapp):
    item = {
        'name': 'encode-processing-pipeline',
        'title': 'ENCODE Processing Pipeline',
        'status': 'current',
        'uuid': 'a558111b-4c50-4b2e-9de8-73fd8fd3a67d',
        }
    return testapp.post_json('/lab', item, status=201).json['@graph'][0]


@pytest.fixture
def platform1(testapp):
    item = {
        'term_id': 'OBI:0002001',
        'term_name': 'HiSeq2000'
    }
    return testapp.post_json('/platform', item).json['@graph'][0]


@pytest.fixture
def platform2(testapp):
    item = {
        'term_id': 'OBI:0002049',
        'term_name': 'HiSeq4000'
    }
    return testapp.post_json('/platform', item).json['@graph'][0]


@pytest.fixture
def platform3(testapp):
    item = {
        'term_id': 'NTR:0000430',
        'term_name': 'Pacific Biosciences Sequel',
        'uuid': 'ced61406-dcc6-43c4-bddd-4c977cc676e8',
    }
    return testapp.post_json('/platform', item).json['@graph'][0]


@pytest.fixture
def platform4(testapp):
    item = {
        'term_id': 'NTR:0000448',
        'term_name': 'Oxford Nanopore - MinION',
        'uuid': '6c275b37-018d-4bf8-85f6-6e3b830524a9',
    }
    return testapp.post_json('/platform', item).json['@graph'][0]


@pytest.fixture
def encode4_award(testapp):
    item = {
        'name': 'encode4-award',
        'rfa': 'ENCODE4',
        'project': 'ENCODE',
        'title': 'A Generic ENCODE4 Award',
        'viewing_group': 'ENCODE4',
    }
    return testapp.post_json('/award', item).json['@graph'][0]


@pytest.fixture
def a549(testapp):
    item = {
        'term_id': 'EFO:0001086',
        'term_name': 'A549',
        'classification': 'cell line',
        'dbxrefs': ['Cellosaurus:CVCL_0023']
    }
    return testapp.post_json('/biosample-types', item, status=201).json['@graph'][0]


@pytest.fixture
def biosample_type(a549):
    return a549


@pytest.fixture
def k562(testapp):
    item = {
        'term_id': 'EFO:0001086',
        'term_name': 'K562',
        'classification': 'cell line',
    }
    return testapp.post_json('/biosample-types', item, status=201).json['@graph'][0]


@pytest.fixture
def hepg2(testapp):
    item = {
        'term_id': 'EFO:0001187',
        'term_name': 'HepG2',
        'classification': 'cell line',
    }
    return testapp.post_json('/biosample-types', item, status=201).json['@graph'][0]


@pytest.fixture
def mel(testapp):
    item = {
            'term_name': 'MEL cell line',
            'term_id': 'EFO:0003971',
            'classification': 'cell line',
    }
    return testapp.post_json('/biosample-types', item, status=201).json['@graph'][0]


@pytest.fixture
def h1(testapp):
    item = {
            'term_id': "EFO:0003042",
            'term_name': 'H1-hESC',
            'classification': 'cell line'
    }
    return testapp.post_json('/biosample-types', item, status=201).json['@graph'][0]


@pytest.fixture
def ileum(testapp):
    item = {
            'term_id': "UBERON:0002116",
            'term_name': 'ileum',
            'classification': 'tissue'
    }
    return testapp.post_json('/biosample-types', item, status=201).json['@graph'][0]


@pytest.fixture
def brain(testapp):
    item = {
            'term_id': "UBERON:0000955",
            'term_name': 'brain',
            'classification': 'tissue'
    }
    return testapp.post_json('/biosample-types', item, status=201).json['@graph'][0]


@pytest.fixture
def whole_organism(testapp):
    item = {
            'uuid': '25d5ad53-15fd-4a44-878a-ece2f7e86509',
            'term_id': "UBERON:0000468",
            'term_name': 'multi-cellular organism',
            'classification': 'whole organisms'
    }
    return testapp.post_json('/biosample-types', item, status=201).json['@graph'][0]


@pytest.fixture
def erythroblast(testapp):
    item = {
            'term_id': "CL:0000765",
            'term_name': 'erythroblast',
            'classification': 'primary cell'
    }
    return testapp.post_json('/biosample-types', item, status=201).json['@graph'][0]


@pytest.fixture
def gm12878(testapp):
    item = {
            'term_id': "EFO:0002784",
            'term_name': 'GM12878',
            'classification': 'cell line'
    }
    return testapp.post_json('/biosample-types', item, status=201).json['@graph'][0]


@pytest.fixture
def s2r_plus(testapp):
    item = {
            'term_id': "EFO:0005837",
            'term_name': 'S2R+',
            'classification': 'cell line'
    }
    return testapp.post_json('/biosample-types', item, status=201).json['@graph'][0]


@pytest.fixture
def single_cell(testapp):
    item = {
            'term_id': "UBERON:349829",
            'term_name': 'heart',
            'classification': 'single cell'
    }
    return testapp.post_json('/biosample-types', item, status=201).json['@graph'][0]


@pytest.fixture
def inconsistent_biosample_type(testapp):
    item = {
        'term_id': 'EFO:0002067',
        'term_name': 'heart',
        'classification': 'single cell',
    }
    return testapp.post_json('/biosample-types', item, status=201).json['@graph'][0]


@pytest.fixture
def base_replicate(testapp, base_experiment):
    item = {
        'biological_replicate_number': 1,
        'technical_replicate_number': 1,
        'experiment': base_experiment['@id'],
    }
    return testapp.post_json('/replicate', item, status=201).json['@graph'][0]


@pytest.fixture
def file_fastq(testapp, lab, award, base_experiment, base_replicate, platform1):
    item = {
        'dataset': base_experiment['@id'],
        'replicate': base_replicate['@id'],
        'file_format': 'fastq',
        'md5sum': '91b574b6411514393507f4ebfa66d47a',
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
def file_with_external_sheet(file, root):
    file_item = root.get_by_uuid(file['uuid'])
    properties = file_item.upgrade_properties()
    file_item.update(
        properties,
        sheets={
            'external': {
                'service': 's3',
                'key': 'xyz.bed',
                'bucket': 'test_file_bucket',
            }
        }
    )
    return file


@pytest.fixture
def public_file_with_public_external_sheet(file, root):
    file_item = root.get_by_uuid(file['uuid'])
    properties = file_item.upgrade_properties()
    properties['status'] = 'released'
    file_item.update(
        properties,
        sheets={
            'external': {
                'service': 's3',
                'key': 'xyz.bed',
                'bucket': 'pds_public_bucket_test',
            }
        }
    )
    return file


@pytest.fixture
def file_with_no_external_sheet(file, root):
    file_item = root.get_by_uuid(file['uuid'])
    properties = file_item.upgrade_properties()
    file_item.update(
        properties,
        sheets={
            'external': {}
        }
    )
    return file


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
def library_schema_9(lab, award):
    return {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'extraction_method': 'Trizol (Invitrogen 15596-026)',
        'lysis_method': 'Possibly Trizol',
        'library_size_selection_method': 'Gel',
    }


@pytest.fixture
def library_schema_9b(lab, award):
    return {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'extraction_method': 'see document ',
        'lysis_method': 'test',
    }


@pytest.fixture
def dataset_reference_1(lab, award):
    return {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'dbxrefs': ['UCSC-ENCODE-hg19:wgEncodeEH000325', 'IHEC:IHECRE00004703'],
    }


@pytest.fixture
def dataset_reference_2(lab, award):
    return {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'dbxrefs': ['IHEC:IHECRE00004703'],
        'notes': 'preexisting comment.'
    }


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
def base_matched_set(testapp, lab, award):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid']
    }
    return testapp.post_json('/matched_set', item, status=201).json['@graph'][0]
####################################################

RED_DOT = """data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUA
AAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO
9TXL0Y4OHwAAAABJRU5ErkJggg=="""

####################################################


##################

@pytest.fixture
def no_login_submitter(testapp, lab, award):
    item = {
        'first_name': 'ENCODE',
        'last_name': 'Submitter',
        'email': 'no_login_submitter@example.org',
        'submits_for': [lab['@id']],
        'status': 'disabled',
    }
    # User @@object view has keys omitted.
    res = testapp.post_json('/user', item)
    return testapp.get(res.location).json


@pytest.fixture
def no_login_access_key(testapp, no_login_submitter):
    description = 'My programmatic key'
    item = {
        'user': no_login_submitter['@id'],
        'description': description,
    }
    res = testapp.post_json('/access_key', item)
    result = res.json['@graph'][0].copy()
    result['secret_access_key'] = res.json['secret_access_key']
    return result

###################

# also tests schema_formats generally
@pytest.fixture
def human_donor(lab, award, organism):
    return {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'organism': organism['uuid']        
    }

###################

@pytest.fixture
def base_antibody_characterization(testapp, lab, ENCODE3_award, target, antibody_lot, organism, k562):
    characterization_review_list = [{
        'lane': 2,
        'organism': organism['uuid'],
        'biosample_ontology': k562['uuid'],
        'lane_status': 'pending dcc review'
    }]
    item = {
        'award': ENCODE3_award['uuid'],
        'target': target['uuid'],
        'lab': lab['uuid'],
        'characterizes': antibody_lot['uuid'],
        'attachment': {'download': 'red-dot.png', 'href': RED_DOT},
        'primary_characterization_method': 'immunoblot',
        'characterization_reviews': characterization_review_list,
        'status': 'pending dcc review'
    }
    return testapp.post_json('/antibody-characterizations', item, status=201).json['@graph'][0]


@pytest.fixture
def base_characterization_review(testapp, organism, k562):
    return {
        'lane': 2,
        'organism': organism['uuid'],
        'biosample_ontology': k562['uuid'],
        'lane_status': 'pending dcc review'
    }


@pytest.fixture
def base_characterization_review2(testapp, organism, hepg2):
    return {
        'lane': 3,
        'organism': organism['uuid'],
        'biosample_ontology': hepg2['uuid'],
        'lane_status': 'compliant'
    }


@pytest.fixture
def base_document(testapp, lab, award):
    item = {
        'lab': lab['uuid'],
        'award': award['uuid'],
        'document_type': 'growth protocol'
    }
    return testapp.post_json('/document', item, status=201).json['@graph'][0]


@pytest.fixture
def standards_document(testapp, lab, award):
    item = {
        'lab': lab['uuid'],
        'award': award['uuid'],
        'document_type': 'standards document'
    }
    return testapp.post_json('/document', item, status=201).json['@graph'][0]


@pytest.fixture
def base_target(testapp, organism):
    item = {
        'target_organism': organism['uuid'],
        'label': 'TAF1',
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
def base_antibody(award, lab, source, organism, target):
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
def recombinant_target(testapp, gene):
    item = {
        'label': 'HA-ABCD',
        'investigated_as': ['transcription factor'],
        'genes': [gene['uuid']],
        'modifications': [{'modification': 'HA'}]
    }
    return testapp.post_json('/target', item, status=201).json['@graph'][0]


@pytest.fixture
def ENCODE3_award(testapp):
    item = {
        'name': 'ABC1234',
        'rfa': 'ENCODE3',
        'project': 'ENCODE',
        'title': 'A Generic ENCODE3 Award'
    }
    return testapp.post_json('/award', item, status=201).json['@graph'][0]



###################

@pytest.fixture
def base_target1(testapp, gene):
    item = {
        'genes': [gene['uuid']],
        'label': 'ABCD',
        'investigated_as': ['transcription factor']
    }
    return testapp.post_json('/target', item, status=201).json['@graph'][0]


@pytest.fixture
def base_target2(testapp, gene):
    item = {
        'genes': [gene['uuid']],
        'label': 'EFGH',
        'investigated_as': ['transcription factor']
    }
    return testapp.post_json('/target', item, status=201).json['@graph'][0]


@pytest.fixture
def base_antibody_characterization1(testapp, lab, award, base_target1, antibody_lot, organism, k562, hepg2):
    item = {
        'award': award['uuid'],
        'target': base_target1['uuid'],
        'lab': lab['uuid'],
        'characterizes': antibody_lot['uuid'],
        'primary_characterization_method': 'immunoblot',
        'status': 'pending dcc review',
        'attachment': {'download': 'red-dot.png', 'href': RED_DOT},
        'characterization_reviews': [
            {
                'lane': 2,
                'organism': organism['uuid'],
                'biosample_ontology': k562['uuid'],
                'lane_status': 'pending dcc review'
            },
            {
                'lane': 3,
                'organism': organism['uuid'],
                'biosample_ontology': hepg2['uuid'],
                'lane_status': 'pending dcc review'
            }
        ]
    }
    return testapp.post_json('/antibody-characterizations', item, status=201).json['@graph'][0]


@pytest.fixture
def base_antibody_characterization2(testapp, lab, award, base_target2, antibody_lot, organism):
    item = {
        'award': award['uuid'],
        'target': base_target2['uuid'],
        'lab': lab['uuid'],
        'characterizes': antibody_lot['uuid'],
        'secondary_characterization_method': 'dot blot assay',
        'attachment': {'download': 'red-dot.png', 'href': RED_DOT},
        'status': 'pending dcc review'
    }
    return testapp.post_json('/antibody-characterizations', item, status=201).json['@graph'][0]


@pytest.fixture
def gfp_target(testapp, organism):
    item = {
        'label': 'gfp',
        'target_organism': organism['@id'],
        'investigated_as': ['tag'],
    }
    return testapp.post_json('/target', item).json['@graph'][0]


@pytest.fixture
def encode4_tag_antibody_lot(testapp, lab, encode4_award, source, mouse, gfp_target):
    item = {
        'product_id': 'WH0000468M1',
        'lot_id': 'CB191-2B3',
        'award': encode4_award['@id'],
        'lab': lab['@id'],
        'source': source['@id'],
        'host_organism': mouse['@id'],
        'targets': [gfp_target['@id']],
    }
    return testapp.post_json('/antibody_lot', item).json['@graph'][0]


@pytest.fixture
def control_antibody(testapp, lab, award, source, mouse, target):
    item = {
        'product_id': 'WH0000468M1',
        'lot_id': 'CB191-2B3',
        'award': award['@id'],
        'lab': lab['@id'],
        'source': source['@id'],
        'host_organism': mouse['@id'],
        'control_type': 'isotype control',
        'isotype': 'IgG',
    }
    return testapp.post_json('/antibody_lot', item).json['@graph'][0]


###################

@pytest.fixture
def ntr_biosample_type(testapp):
    item = {
        'term_id': 'NTR:0000022',
        'term_name': 'heart',
        'classification': 'single cell',
    }
    return testapp.post_json('/biosample-types', item, status=201).json['@graph'][0]


@pytest.fixture
def id_nonexist_biosample_type(testapp):
    item = {
        'term_id': 'CL:99999999',
        'term_name': 'heart',
        'classification': 'single cell',
    }
    return testapp.post_json('/biosample-types', item, status=201).json['@graph'][0]



###################

@pytest.fixture
def base_biosample_1(testapp, lab, award, source, organism, heart):
    item = {
        'award': award['uuid'],
        'biosample_ontology': heart['uuid'],
        'lab': lab['uuid'],
        'organism': organism['uuid'],
        'source': source['uuid']
    }
    return testapp.post_json('/biosample', item, status=201).json['@graph'][0]


@pytest.fixture
def base_mouse_biosample(testapp, lab, award, source, mouse, liver):
    item = {
        'award': award['uuid'],
        'biosample_ontology': liver['uuid'],
        'lab': lab['uuid'],
        'organism': mouse['uuid'],
        'source': source['uuid']
    }
    return testapp.post_json('/biosample', item, status=201).json['@graph'][0]


@pytest.fixture
def base_human_donor(testapp, lab, award, organism):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'organism': organism['uuid']
    }
    return testapp.post_json('/human-donors', item, status=201).json['@graph'][0]


@pytest.fixture
def base_chipmunk(testapp):
    item = {
        'name': 'chimpmunk',
        'taxon_id': '12345',
        'scientific_name': 'Chip chipmunicus'
    }
    return testapp.post_json('/organism', item, status=201).json['@graph'][0]


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
def purkinje_cell(testapp):
    item = {
            'term_id': "CL:0000121",
            'term_name': 'Purkinje cell',
            'classification': 'primary cell'
    }
    return testapp.post_json('/biosample-types', item, status=201).json['@graph'][0]


@pytest.fixture
def cerebellum(testapp):
    item = {
            'term_id': "UBERON:0002037",
            'term_name': 'cerebellum',
            'classification': 'tissue'
    }
    return testapp.post_json('/biosample-types', item, status=201).json['@graph'][0]

###################

@pytest.fixture
def review(lab, submitter):
    review = {
        'reviewed_by': submitter['@id'],
        'status': 'compliant',
        'lab': lab['@id'],
    }
    return review

###################

@pytest.fixture
def worm(testapp):
    item = {
        'uuid': '2732dfd9-4fe6-4fd2-9d88-61b7c58cbe20',
        'name': 'celegans',
        'scientific_name': 'Caenorhabditis elegans',
        'taxon_id': '6239',
    }
    return testapp.post_json('/organism', item).json['@graph'][0]


@pytest.fixture
def worm_donor(lab, award, worm, testapp):
    item = {
        'lab': lab['uuid'],
        'award': award['uuid'],
        'organism': worm['uuid'],
        'dbxrefs': ['CGC:OP520'],
        'genotype': 'blahblahblah'
        }
    return testapp.post_json('/WormDonor', item, status=201).json['@graph'][0]


@pytest.fixture
def fly_donor_201(lab, award, fly, testapp):
    item = {
        'lab': lab['uuid'],
        'award': award['uuid'],
        'organism': fly['uuid'],
        'dbxrefs': ['FlyBase:FBst0000003'],
        'genotype': 'blahblah'
        }
    return testapp.post_json('/FlyDonor', item, status=201).json['@graph'][0]

###################

@pytest.fixture
def experiment_series_1(testapp, lab, award, base_experiment):
    item = {
        'award': award['@id'],
        'lab': lab['@id'],
        'related_datasets': [base_experiment['@id']]
    }
    return testapp.post_json('/experiment_series', item, status=201).json['@graph'][0]


@pytest.fixture
def experiment_chip_H3K4me3(testapp, lab, award, target_H3K4me3, ileum):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'status': 'released',
        'date_released': '2019-10-08',
        'biosample_ontology': ileum['uuid'],
        'assay_term_name': 'ChIP-seq',
        'target': target_H3K4me3['uuid']

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
def target_H3K4me3(testapp, organism):
    item = {
        'label': 'H3K4me3',
        'target_organism': organism['@id'],
        'investigated_as': ['histone']
    }
    return testapp.post_json('/target', item).json['@graph'][0]


@pytest.fixture
def target_CTCF(testapp, organism):
    item = {
        'label': 'CTCF',
        'target_organism': organism['@id'],
        'investigated_as': ['transcription factor']
    }
    return testapp.post_json('/target', item).json['@graph'][0]


@pytest.fixture
def replicate_dnase(testapp, experiment_dnase, library_1):
    item = {
        'experiment': experiment_dnase['@id'],
        'library': library_1['@id'],
        'biological_replicate_number': 1,
        'technical_replicate_number': 1,
    }
    return testapp.post_json('/replicate', item).json['@graph'][0]


@pytest.fixture
def replicate_rna(testapp, experiment_rna, library_2):
    item = {
        'experiment': experiment_rna['@id'],
        'library': library_2['@id'],
        'biological_replicate_number': 1,
        'technical_replicate_number': 1,
    }
    return testapp.post_json('/replicate', item).json['@graph'][0]

###################

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
def base_replicate_two(testapp, base_experiment):
    item = {
        'biological_replicate_number': 1,
        'technical_replicate_number': 2,
        'experiment': base_experiment['@id'],
    }
    return testapp.post_json('/replicate', item, status=201).json['@graph'][0]


@pytest.fixture
def base_target_1(testapp, gene):
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
def tag_antibody(testapp, award, lab, source, organism, tag_target):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'source': source['uuid'],
        'host_organism': organism['uuid'],
        'targets': [tag_target['uuid']],
        'product_id': 'eGFP',
        'lot_id': '1'
    }
    return testapp.post_json('/antibodies', item, status=201).json['@graph'][0]


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
def IgG_antibody(testapp, award, lab, source, organism):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'source': source['uuid'],
        'host_organism': organism['uuid'],
        'control_type': 'isotype control',
        'isotype': 'IgG',
        'product_id': 'ABCDEF',
        'lot_id': '321'
    }
    return testapp.post_json('/antibodies', item, status=201).json['@graph'][0]


@pytest.fixture
def base_antibody_characterization1_2(testapp, lab, award, target, antibody_lot, organism, k562):
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
def file_fastq_no_read_length(testapp, lab, award, experiment, replicate_1_1, platform3):
    item = {
        'dataset': experiment['@id'],
        'replicate': replicate_1_1['@id'],
        'file_format': 'fastq',
        'file_size': 68,
        'platform': platform3['@id'],
        'output_type': 'reads',
        'md5sum': '21be74b6e11515393507f4ebfa66d77a',
        'lab': lab['@id'],
        'award': award['@id'],
        'aliases': ['encode:no read length alias'],
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
def micro_rna_quantification_quality_metric_1_2(testapp, analysis_step_run_bam, file_tsv_1_2, award, lab):
    item = {
        'step_run': analysis_step_run_bam['@id'],
        'quality_metric_of': [file_tsv_1_2['@id']],
        'expressed_mirnas': 250,
        'award': award['@id'],
        'lab': lab['@id']
    }
    return testapp.post_json('/micro_rna_quantification_quality_metric', item).json['@graph'][0]


@pytest.fixture
def micro_rna_mapping_quality_metric_2_1(
    testapp,
    analysis_step_run_bam,
    file_bam_2_1,
    award,
    lab
):
    item = {
        'step_run': analysis_step_run_bam['@id'],
        'quality_metric_of': [file_bam_2_1['@id']],
        'aligned_reads': 4000000,
        'award': award['@id'],
        'lab': lab['@id']
    }
    return testapp.post_json('/micro_rna_mapping_quality_metric', item).json['@graph'][0]


@pytest.fixture
def long_read_rna_quantification_quality_metric_1_2(testapp, analysis_step_run_bam, file_tsv_1_2, award, lab):
    item = {
        'step_run': analysis_step_run_bam['@id'],
        'quality_metric_of': [file_tsv_1_2['@id']],
        'genes_detected': 5000,
        'award': award['@id'],
        'lab': lab['@id']
    }
    return testapp.post_json('/long_read_rna_quantification_quality_metric', item).json['@graph'][0]


@pytest.fixture
def long_read_rna_mapping_quality_metric_2_1(
    testapp,
    analysis_step_run_bam,
    file_bam_2_1,
    award,
    lab
):
    item = {
        'step_run': analysis_step_run_bam['@id'],
        'quality_metric_of': [file_bam_2_1['@id']],
        'full_length_non_chimeric_read_count': 500000,
        'mapping_rate': 0.5,
        'award': award['@id'],
        'lab': lab['@id']
    }
    return testapp.post_json('/long_read_rna_mapping_quality_metric', item).json['@graph'][0]


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

###################


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
def file_rep(replicate, file_exp, testapp):
    item = {
        'experiment': file_exp['uuid'],
        'biological_replicate_number': 1,
        'technical_replicate_number': 1
    }
    return testapp.post_json('/replicate', item, status=201).json['@graph'][0]


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
def file_rep2(replicate, file_exp2, testapp):
    item = {
        'experiment': file_exp2['uuid'],
        'biological_replicate_number': 1,
        'technical_replicate_number': 1
    }
    return testapp.post_json('/replicate', item, status=201).json['@graph'][0]


@pytest.fixture
def file_rep1_2(replicate, file_exp, testapp):
    item = {
        'experiment': file_exp['uuid'],
        'biological_replicate_number': 2,
        'technical_replicate_number': 1
    }
    return testapp.post_json('/replicate', item, status=201).json['@graph'][0]


@pytest.fixture
def file1_2(file_exp, award, lab, file_rep1_2, platform1, testapp):
    item = {
        'dataset': file_exp['uuid'],
        'replicate': file_rep1_2['uuid'],
        'file_format': 'fastq',
        'platform': platform1['@id'],
        'md5sum': '91be74b6e11515393507f4ebfa66d58a',
        'output_type': 'raw data',
        'file_size': 34,
        'run_type': 'single-ended',
        'award': award['uuid'],
        'lab': lab['uuid'],
        'status': 'released'
    }
    return testapp.post_json('/file', item, status=201).json['@graph'][0]


@pytest.fixture
def file2(file_exp2, award, lab, file_rep2, platform1, testapp):
    item = {
        'dataset': file_exp2['uuid'],
        'replicate': file_rep2['uuid'],
        'file_format': 'fastq',
        'md5sum': '91be74b6e11515393507f4ebfa66d58b',
        'output_type': 'raw data',
        'file_size': 34,
        'run_type': 'single-ended',
        'platform': platform1['uuid'],
        'award': award['uuid'],
        'lab': lab['uuid'],
        'status': 'released'
    }
    return testapp.post_json('/file', item, status=201).json['@graph'][0]


@pytest.fixture
def file1(file_exp, award, lab, file_rep, file2, platform1, testapp):
    item = {
        'dataset': file_exp['uuid'],
        'replicate': file_rep['uuid'],
        'file_format': 'fastq',
        'md5sum': '91be74b6e11515393507f4ebfa66d58c',
        'output_type': 'reads',
        "read_length": 50,
        'file_size': 34,
        'run_type': 'single-ended',
        'platform': platform1['uuid'],
        'award': award['uuid'],
        'lab': lab['uuid'],
        'status': 'released',
        'controlled_by': [file2['uuid']]
    }
    return testapp.post_json('/file', item, status=201).json['@graph'][0]


@pytest.fixture
def file3(file_exp, award, lab, file_rep, platform1, testapp):
    item = {
        'dataset': file_exp['uuid'],
        'replicate': file_rep['uuid'],
        'file_format': 'fastq',
        'file_size': 34,
        'md5sum': '91be74b6e11515393507f4ebfa56d78d',
        'output_type': 'reads',
        "read_length": 50,
        'platform': platform1['uuid'],
        'run_type': 'single-ended',
        'award': award['uuid'],
        'lab': lab['uuid'],
        'status': 'released'
    }
    return testapp.post_json('/file', item, status=201).json['@graph'][0]


@pytest.fixture
def file4(file_exp2, award, lab, file_rep2, platform1, testapp):
    item = {
        'dataset': file_exp2['uuid'],
        'replicate': file_rep2['uuid'],
        'file_format': 'fastq',
        'md5sum': '91ae74b6e11515393507f4ebfa66d78a',
        'output_type': 'reads',
        'platform': platform1['uuid'],
        "read_length": 50,
        'file_size': 34,
        'run_type': 'single-ended',
        'award': award['uuid'],
        'lab': lab['uuid'],
        'status': 'released'
    }
    return testapp.post_json('/file', item, status=201).json['@graph'][0]


@pytest.fixture
def file6(file_exp2, award, encode_lab, testapp, analysis_step_run_bam):
    item = {
        'dataset': file_exp2['uuid'],
        'file_format': 'bam',
        'file_size': 3,
        'md5sum': '91ce74b6e11515393507f4ebfa66d78a',
        'output_type': 'alignments',
        'award': award['uuid'],
        'file_size': 34,
        'assembly': 'hg19',
        'lab': encode_lab['uuid'],
        'status': 'released',
        'step_run': analysis_step_run_bam['uuid']
    }
    return testapp.post_json('/file', item, status=201).json['@graph'][0]


@pytest.fixture
def file7(file_exp2, award, encode_lab, testapp, analysis_step_run_bam):
    item = {
        'dataset': file_exp2['uuid'],
        'file_format': 'tsv',
        'file_size': 3,
        'md5sum': '91be74b6e11515394507f4ebfa66d78a',
        'output_type': 'gene quantifications',
        'award': award['uuid'],
        'lab': encode_lab['uuid'],
        'status': 'released',
        'step_run': analysis_step_run_bam['uuid']
    }
    return testapp.post_json('/file', item, status=201).json['@graph'][0]


@pytest.fixture
def chipseq_bam_quality_metric(testapp, analysis_step_run_bam, file6, lab, award):
    item = {
        'step_run': analysis_step_run_bam['@id'],
        'award': award['@id'],
        'lab': lab['@id'],
        'quality_metric_of': [file6['@id']],
        'total': 20000000
    }

    return testapp.post_json('/samtools_flagstats_quality_metric', item).json['@graph'][0]


@pytest.fixture
def chipseq_bam_quality_metric_2(testapp, analysis_step_run_bam, file7, lab, award):
    item = {
        'step_run': analysis_step_run_bam['@id'],
        'award': award['@id'],
        'lab': lab['@id'],
        'quality_metric_of': [file7['@id']],
        'total': 20000000
    }

    return testapp.post_json('/samtools_flagstats_quality_metric', item).json['@graph'][0]


@pytest.fixture
def analysis_step_bam(testapp):
    item = {
        'step_label': 'bamqc-step',
        'title': 'bamqc step',
        'major_version': 1,
        'input_file_types': ['reads'],
        'analysis_step_types': ['QA calculation']
    }
    return testapp.post_json('/analysis_step', item).json['@graph'][0]


@pytest.fixture
def pipeline_short_rna(testapp, lab, award, analysis_step_bam):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'title': "Small RNA-seq single-end pipeline",
        'analysis_steps': [analysis_step_bam['@id']]
    }
    return testapp.post_json('/pipeline', item).json['@graph'][0]



###################

@pytest.fixture
def genetic_modification_1(testapp, lab, award):
    item = {
        'award': award['@id'],
        'lab': lab['@id'],
        'modified_site_by_coordinates': {
            'assembly': 'GRCh38',
            'chromosome': '11',
            'start': 20000,
            'end': 21000
        },
        'purpose': 'repression',
        'category': 'deletion',
        'method': 'CRISPR',
        'zygosity': 'homozygous'
    }
    return testapp.post_json('/genetic_modification', item).json['@graph'][0]


@pytest.fixture
def genetic_modification_RNAi(testapp, lab, award):
    item = {
        'award': award['@id'],
        'lab': lab['@id'],
        'modified_site_by_coordinates': {
            'assembly': 'GRCh38',
            'chromosome': '11',
            'start': 20000,
            'end': 21000
        },
        'purpose': 'repression',
        'category': 'deletion',
        'method': 'RNAi'
    }
    return testapp.post_json('/genetic_modification', item).json['@graph'][0]


@pytest.fixture
def tagged_target(testapp, gene):
    item = {
        'genes': [gene['uuid']],
        'modifications': [{'modification': 'eGFP'}],
        'label': 'eGFP-CTCF',
        'investigated_as': ['transcription factor']
    }
    return testapp.post_json('/target', item, status=201).json['@graph'][0]


@pytest.fixture
def genetic_modification_source(testapp, lab, award, source, gene):
    item = {
        'lab': lab['@id'],
        'award': award['@id'],
        'category': 'insertion',
        'introduced_gene': gene['@id'],
        'purpose': 'expression',
        'method': 'CRISPR',
        'reagents': [
            {
                'source': source['@id'],
                'identifier': 'sigma:ABC123'
            }
        ]
    }
    return testapp.post_json('/genetic_modification', item).json['@graph'][0]

###################

@pytest.fixture
def reference_epigenome_1(testapp, lab, award):
    item = {
        'award': award['@id'],
        'lab': lab['@id']
    }
    return testapp.post_json('/reference_epigenome', item).json['@graph'][0]


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
def reference_experiment_chip_seq_H3K4me3(testapp, lab, award, target_H3K4me3_1, ileum):
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
def reference_experiment_chip_seq_H3K27ac(testapp, lab, award, target_H3K27ac_1, ileum):
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
def reference_experiment_chip_seq_H3K9me3(testapp, lab, award, target_H3K9me3_1, ileum):
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


@pytest.fixture
def target_H3K27me3(testapp, organism):
    item = {
        'label': 'H3K27me3',
        'target_organism': organism['@id'],
        'investigated_as': ['histone']
    }
    return testapp.post_json('/target', item).json['@graph'][0]


@pytest.fixture
def target_H3K36me3(testapp, organism):
    item = {
        'label': 'H3K36me3',
        'target_organism': organism['@id'],
        'investigated_as': ['histone']
    }
    return testapp.post_json('/target', item).json['@graph'][0]


@pytest.fixture
def target_H3K4me1(testapp, organism):
    item = {
        'label': 'H3K4me1',
        'target_organism': organism['@id'],
        'investigated_as': ['histone']
    }
    return testapp.post_json('/target', item).json['@graph'][0]


@pytest.fixture
def target_H3K4me3_1(testapp, organism):
    item = {
        'label': 'H3K4me3',
        'target_organism': organism['@id'],
        'investigated_as': ['histone']
    }
    return testapp.post_json('/target', item).json['@graph'][0]


@pytest.fixture
def target_H3K27ac_1(testapp, organism):
    item = {
        'label': 'H3K27ac',
        'target_organism': organism['@id'],
        'investigated_as': ['histone']
    }
    return testapp.post_json('/target', item).json['@graph'][0]


@pytest.fixture
def target_H3K9me3_1(testapp, organism):
    item = {
        'label': 'H3K9me3',
        'target_organism': organism['@id'],
        'investigated_as': ['histone']
    }
    return testapp.post_json('/target', item).json['@graph'][0]

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

###################

@pytest.fixture
def rep1(experiment, testapp):
    item = {
        'experiment': experiment['uuid'],
        'biological_replicate_number': 5,
        'technical_replicate_number': 4,
        'status': 'released'
    }
    return testapp.post_json('/replicate', item, status=201).json['@graph'][0]


@pytest.fixture
def rep2(experiment, testapp):
    item = {
        'experiment': experiment['uuid'],
        'biological_replicate_number': 5,
        'technical_replicate_number': 4,
        'status': 'released'
    }
    return testapp.post_json('/replicate', item, status=201).json['@graph'][0]

###################

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

###################

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

###################

@pytest.fixture
def uploading_file(testapp, award, experiment, lab, replicate, dummy_request):
    item = {
        'award': award['@id'],
        'dataset': experiment['@id'],
        'lab': lab['@id'],
        'replicate': replicate['@id'],
        'file_format': 'tsv',
        'file_size': 2534535,
        'md5sum': '00000000000000000000000000000000',
        'output_type': 'raw data',
        'status': 'uploading',
    }
    return item


###################

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
def file_object(testapp, award, experiment, lab, replicate):
    item = {
        'award': award['@id'],
        'dataset': experiment['@id'],
        'lab': lab['@id'],
        'replicate': replicate['@id'],
        'file_format': 'tsv',
        'file_size': 2534535,
        'md5sum': '00000000000000000000000000000000',
        'output_type': 'raw data',
        'status': 'in progress',
    }
    res = testapp.post_json('/file', item)
    return res.json['@graph'][0]


@pytest.fixture
def fastq_pair_1_paired_with(fastq_pair_1, file_object):
    item = fastq_pair_1.copy()
    item['paired_with'] = file_object['@id']
    return item


@pytest.fixture
def fastq_pair_2(fastq):
    item = fastq.copy()
    item['paired_end'] = '2'
    item['md5sum'] = '2123456789abcdef0123456789abcdef'
    return item


@pytest.fixture
def fastq_pair_2_paired_with(fastq_pair_2, fastq_pair_1):
    item = fastq_pair_2.copy()
    item['paired_with'] = 'md5:' + fastq_pair_1['md5sum']
    return item


@pytest.fixture
def external_accession(fastq_pair_1):
    item = fastq_pair_1.copy()
    item['external_accession'] = 'EXTERNAL'
    return item

###################




###################
# TODO: replace yield_fixture
@pytest.yield_fixture(scope='session')
def minitestdata(app, conn):
    tx = conn.begin_nested()

    from webtest import TestApp
    environ = {
        'HTTP_ACCEPT': 'application/json',
        'REMOTE_USER': 'TEST',
    }
    testapp = TestApp(app, environ)

    item = {
        'name': 'human',
        'scientific_name': 'Homo sapiens',
        'taxon_id': '9606',
    }
    testapp.post_json('/organism', item, status=201)

    yield
    tx.rollback()

# TODO: replace yield_fixture
@pytest.yield_fixture(scope='session')
def minitestdata2(app, conn):
    tx = conn.begin_nested()

    from webtest import TestApp
    environ = {
        'HTTP_ACCEPT': 'application/json',
        'REMOTE_USER': 'TEST',
    }
    testapp = TestApp(app, environ)

    item = {
        'name': 'human',
        'scientific_name': 'Homo sapiens',
        'taxon_id': '9606',
    }
    testapp.post_json('/organism', item, status=201)

    yield
    tx.rollback()


###################

###################




###################




###################




###################

