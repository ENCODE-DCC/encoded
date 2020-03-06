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
def library(testapp, lab, award, biosample_1):
    item = {
        'nucleic_acid_term_name': 'DNA',
        'lab': lab['@id'],
        'award': award['@id'],
        'biosample': biosample_1['@id'],
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


# TODO: Figure out biosample
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
def biosample_3(testapp, source, lab, award, organism, heart):
    item = {
        'biosample_ontology': heart['uuid'],
        'source': source['@id'],
        'lab': lab['@id'],
        'award': award['@id'],
        'organism': organism['@id'],
    }
    return testapp.post_json('/biosample', item).json['@graph'][0]

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



@pytest.fixture
def biosample_data(submitter, lab, award, source, human, brain):
    return {
        'award': award['@id'],
        'biosample_ontology': brain['uuid'],
        'lab': lab['@id'],
        'organism': human['@id'],
        'source': source['@id'],
    }


@pytest.fixture
def antibody_characterization_data(submitter, award, lab, antibody_lot, target):
    return {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'target': target['uuid'],
        'characterizes': antibody_lot['uuid']
    }


@pytest.fixture
def biosample_data2(submitter, lab, award, source, organism, heart):
    return {
        'award': award['uuid'],
        'biosample_ontology': heart['uuid'],
        'lab': lab['uuid'],
        'organism': organism['uuid'],
        'source': source['uuid'],
    }

@pytest.fixture
def biosample_depleted_in(mouse_biosample, whole_organism):
    item = mouse_biosample.copy()
    item.update({
        'depleted_in_term_name': ['head'],
        'biosample_ontology': whole_organism['uuid'],
    })
    return item


@pytest.fixture
def biosample_starting_amount(biosample_data2):
    item = biosample_data2.copy()
    item.update({
        'starting_amount': 20
    })
    return item


@pytest.fixture
def mouse_biosample(biosample_data2, mouse):
    item = biosample_data2.copy()
    item.update({
        'organism': mouse['uuid'],
        'model_organism_age': '8',
        'model_organism_age_units': 'day',
        'model_organism_sex': 'female',
        'model_organism_health_status': 'apparently healthy',
        'model_organism_mating_status': 'virgin'
    })
    return item

@pytest.fixture
def organoid(testapp):
    item = {
            'term_id': 'UBERON:0000955',
            'term_name': 'brain',
            'classification': 'organoid'
    }
    return testapp.post_json('/biosample-types', item, status=201).json['@graph'][0]



@pytest.fixture
def mouse_donor_to_test(testapp, lab, award, mouse):
    return {
        'award': award['@id'],
        'lab': lab['@id'],
        'organism': mouse['@id'],
    }




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
def file_no_replicate(testapp, experiment, award, lab):
    item = {
        'dataset': experiment['@id'],
        'lab': lab['@id'],
        'award': award['@id'],
        'file_format': 'bam',
        'file_size': 345,
        'assembly': 'hg19',
        'md5sum': 'e002cd204df36d93dd070ef0712b8eed',
        'output_type': 'alignments',
        'status': 'in progress',  # avoid s3 upload codepath
    }
    return testapp.post_json('/file', item).json['@graph'][0]


@pytest.fixture
def file_with_replicate(testapp, experiment, award, lab, replicate):
    item = {
        'dataset': experiment['@id'],
        'replicate': replicate['@id'],
        'lab': lab['@id'],
        'award': award['@id'],
        'file_format': 'bam',
        'file_size': 345,
        'assembly': 'hg19',
        'md5sum': 'e003cd204df36d93dd070ef0712b8eed',
        'output_type': 'alignments',
        'status': 'in progress',  # avoid s3 upload codepath
    }
    return testapp.post_json('/file', item).json['@graph'][0]


@pytest.fixture
def file_with_derived(testapp, experiment, award, lab, file_with_replicate):
    item = {
        'dataset': experiment['@id'],
        'lab': lab['@id'],
        'award': award['@id'],
        'file_format': 'bam',
        'assembly': 'hg19',
        'file_size': 345,
        'md5sum': 'e004cd204df36d93dd070ef0712b8eed',
        'output_type': 'alignments',
        'status': 'in progress',  # avoid s3 upload codepath
        'derived_from': [file_with_replicate['@id']]
    }
    return testapp.post_json('/file', item).json['@graph'][0]


@pytest.fixture
def file_no_assembly(testapp, experiment, award, lab, replicate):
    item = {
        'dataset': experiment['@id'],
        'replicate': replicate['@id'],
        'lab': lab['@id'],
        'award': award['@id'],
        'file_format': 'bam',
        'file_size': 345,
        'md5sum': '82847a2a5beb8095282c68c00f48e347',
        'output_type': 'alignments',
        'status': 'in progress'
    }
    return item


@pytest.fixture
def file_no_error(testapp, experiment, award, lab, replicate, platform1):
    item = {
        'dataset': experiment['@id'],
        'replicate': replicate['@id'],
        'lab': lab['@id'],
        'file_size': 345,
        'platform': platform1['@id'],
        'award': award['@id'],
        'file_format': 'fastq',
        'run_type': 'paired-ended',
        'paired_end': '1',
        'output_type': 'reads',
        "read_length": 50,
        'md5sum': '136e501c4bacf4aab87debab20d76648',
        'status': 'in progress'
    }
    return item


@pytest.fixture
def file_content_error(testapp, experiment, award, lab, replicate, platform1):
    item = {
        'dataset': experiment['@id'],
        'replicate': replicate['@id'],
        'lab': lab['@id'],
        'file_size': 345,
        'platform': platform1['@id'],
        'award': award['@id'],
        'file_format': 'fastq',
        'run_type': 'single-ended',
        'output_type': 'reads',
        "read_length": 36,
        'md5sum': '99378c852c5be68251cbb125ffcf045a',
        'status': 'content error'
    }
    return item


@pytest.fixture
def file_no_platform(testapp, experiment, award, lab, replicate):
    item = {
        'dataset': experiment['@id'],
        'replicate': replicate['@id'],
        'lab': lab['@id'],
        'file_size': 345,
        'award': award['@id'],
        'file_format': 'fastq',
        'run_type': 'single-ended',
        'output_type': 'reads',
        "read_length": 36,
        'md5sum': '99378c852c5be68251cbb125ffcf045a',
        'status': 'in progress'
    }
    return item


@pytest.fixture
def file_no_paired_end(testapp, experiment, award, lab, replicate, platform1):
    item = {
        'dataset': experiment['@id'],
        'replicate': replicate['@id'],
        'lab': lab['@id'],
        'file_size': 345,
        'award': award['@id'],
        'platform': platform1['@id'],
        'file_format': 'fastq',
        'run_type': 'paired-ended',
        'output_type': 'reads',
        "read_length": 50,
        'md5sum': '136e501c4bacf4aab87debab20d76648',
        'status': 'in progress'
    }
    return item


@pytest.fixture
def file_with_bad_date_created(testapp, experiment, award, lab, replicate, platform1):
    item = {
        'dataset': experiment['@id'],
        'replicate': replicate['@id'],
        'lab': lab['@id'],
        'file_size': 345,
        'date_created': '2017-10-23',
        'platform': platform1['@id'],
        'award': award['@id'],
        'file_format': 'fastq',
        'run_type': 'paired-ended',
        'paired_end': '1',
        'output_type': 'reads',
        "read_length": 50,
        'md5sum': '136e501c4bacf4aab87debab20d76648',
        'status': 'in progress'
    }
    return item


@pytest.fixture
def file_with_bad_revoke_detail(testapp, experiment, award, lab, replicate, platform1):
    item = {
        'dataset': experiment['@id'],
        'replicate': replicate['@id'],
        'lab': lab['@id'],
        'file_size': 345,
        'platform': platform1['@id'],
        'award': award['@id'],
        'file_format': 'fastq',
        'run_type': 'paired-ended',
        'paired_end': '1',
        'output_type': 'reads',
        "read_length": 50,
        'md5sum': '136e501c4bacf4aab87debab20d76648',
        'status': 'in progress',
        'revoke_detail': 'some reason to be revoked'
    }
    return item


@pytest.fixture
def file_processed_output_raw_format(testapp, experiment, award, lab, replicate, platform1):
    item = {
        'dataset': experiment['@id'],
        'replicate': replicate['@id'],
        'lab': lab['@id'],
        'file_size': 345,
        'platform': platform1['@id'],
        'award': award['@id'],
        'file_format': 'fastq',
        'run_type': 'single-ended',
        'output_type': 'peaks',
        'read_length': 36,
        'md5sum': '99378c852c5be68251cbb125ffcf045a',
        'status': 'in progress'
    }
    return item


@pytest.fixture
def file_raw_output_processed_format(testapp, experiment, award, lab, replicate):
    item = {
        'dataset': experiment['@id'],
        'replicate': replicate['@id'],
        'lab': lab['@id'],
        'file_size': 345,
        'award': award['@id'],
        'file_format': 'bam',
        'output_type': 'reads',
        'read_length': 36,
        'assembly': 'hg19',
        'md5sum': '99378c852c5be68251cbb125ffcf045a',
        'status': 'in progress'
    }
    return item


@pytest.fixture
def file_restriction_map(testapp, experiment, award, lab):
    item = {
        'dataset': experiment['@id'],
        'lab': lab['@id'],
        'award': award['@id'],
        'file_format': 'txt',
        'file_size': 3456,
        'assembly': 'hg19',
        'md5sum': 'e002cd204df36d93dd070ef0712b8e12',
        'output_type': 'restriction enzyme site locations',
        'status': 'in progress',  # avoid s3 upload codepath
    }
    return item


@pytest.fixture
def file_no_genome_annotation(testapp, experiment, award, lab, replicate):
    item = {
        'dataset': experiment['@id'],
        'replicate': replicate['@id'],
        'lab': lab['@id'],
        'award': award['@id'],
        'assembly': 'GRCh38',
        'file_format': 'database',
        'file_size': 342,
        'md5sum': '82847a2a5beb8095282c68c00f48e347',
        'output_type': 'transcriptome index',
        'status': 'in progress'
    }
    return item


@pytest.fixture
def file_database_output_type(testapp, experiment, award, lab, replicate):
    item = {
        'dataset': experiment['@id'],
        'replicate': replicate['@id'],
        'lab': lab['@id'],
        'award': award['@id'],
        'assembly': 'GRCh38',
        'file_format': 'database',
        'file_size': 342,
        'genome_annotation': 'V24',
        'md5sum': '82847a2a5beb8095282c68c00f48e348',
        'output_type': 'alignments',
        'status': 'in progress'
    }
    return item


@pytest.fixture
def file_good_bam(testapp, experiment, award, lab, replicate, platform1):
    item = {
        'dataset': experiment['@id'],
        'replicate': replicate['@id'],
        'lab': lab['@id'],
        'file_size': 345,
        'platform': platform1['@id'],
        'award': award['@id'],
        'assembly': 'GRCh38',
        'file_format': 'bam',
        'output_type': 'alignments',
        'md5sum': '136e501c4bacf4fab87debab20d76648',
        'status': 'in progress'
    }
    return item


@pytest.fixture
def file_no_runtype_readlength(testapp, experiment, award, lab, replicate, platform1):
    item = {
        'dataset': experiment['@id'],
        'replicate': replicate['@id'],
        'lab': lab['@id'],
        'file_size': 345,
        'platform': platform1['@id'],
        'award': award['@id'],
        'file_format': 'fastq',
        'output_type': 'reads',
        'md5sum': '99378c852c5be68251cbb125ffcf045a',
        'status': 'in progress'
    }
    return item





@pytest.fixture
def functional_characterization_experiment_item(testapp, lab, award, cell_free):
    item = {
        'lab': lab['@id'],
        'award': award['@id'],
        'assay_term_name': 'STARR-seq',
        'biosample_ontology': cell_free['uuid'],
        'status': 'in progress'
    }
    return item


@pytest.fixture
def functional_characterization_experiment_screen(testapp, lab, award, heart, target):
    item = {
        'lab': lab['@id'],
        'award': award['@id'],
        'assay_term_name': 'CRISPR screen',
        'biosample_ontology': heart['uuid'],
        'status': 'in progress',
        'target': target['uuid']

    }
    return item


@pytest.fixture
def functional_characterization_experiment(testapp, lab, award, cell_free):
    item = {
        'lab': lab['@id'],
        'award': award['@id'],
        'assay_term_name': 'STARR-seq',
        'biosample_ontology': cell_free['uuid'],
        'status': 'in progress'
    }
    return testapp.post_json('/functional_characterization_experiment', item).json['@graph'][0]


@pytest.fixture
def functional_characterization_experiment_4(testapp, lab, award):
    item = {
        'lab': lab['@id'],
        'award': award['@id'],
        'assay_term_name': 'CRISPR screen',
        'status': 'in progress',
        'target_expression_percentile': 70
    }
    return item


@pytest.fixture
def functional_characterization_experiment_5(testapp, lab, award, ctcf):
    item = {
        'lab': lab['@id'],
        'award': award['@id'],
        'assay_term_name': 'CRISPR screen',
        'status': 'in progress',
        'examined_loci': [{
             'gene': ctcf['uuid'],
             'gene_expression_percentile': 80
         }]
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



@pytest.fixture
def publication_data_no_references(testapp, lab, award):
    item = {
        'award': award['@id'],
        'lab': lab['@id'],
        'references': []
    }
    return item



@pytest.fixture
def generic_quality_metric(analysis_step_run, file, award, lab):
    return {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'name': 'Generic QC',
        'step_run': analysis_step_run['uuid'],
        'quality_metric_of': [file['uuid']],
        'attachment': {
            'download': 'test.tgz',
            'type': 'application/x-tar',
            'href': "data:application/x-tar;base64,dG1wLwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADAwMDc1NSAAMDAwNzY2IAAwMDAwMjQgADAwMDAwMDAwMDAwIDEzMDczMjIyMDQ0IDAxMjMxMQAgNQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAB1c3RhcgAwMGVzdGhlcgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAc3RhZmYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAwMDAwMDAgADAwMDAwMCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAB0bXAvYQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMDAwNjQ0IAAwMDA3NjYgADAwMDAyNCAAMDAwMDAwMDAwMDIgMTMwNzEyNDU0NjEgMDEyNDUyACAwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHVzdGFyADAwZXN0aGVyAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABzdGFmZgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADAwMDAwMCAAMDAwMDAwIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADEKAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAdG1wL2IAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADAwMDY0NCAAMDAwNzY2IAAwMDAwMjQgADAwMDAwMDAwMDAyIDEzMDcxMjQ1NDY1IDAxMjQ1NwAgMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAB1c3RhcgAwMGVzdGhlcgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAc3RhZmYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAwMDAwMDAgADAwMDAwMCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAxCgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHRtcC9jAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAwMDA2NDQgADAwMDc2NiAAMDAwMDI0IAAwMDAwMDAwMDAwMiAxMzA3MTI0NTQ2NyAwMTI0NjIAIDAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAdXN0YXIAMDBlc3RoZXIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHN0YWZmAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMDAwMDAwIAAwMDAwMDAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMQoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAB0bXAvZAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMDAwNjQ0IAAwMDA3NjYgADAwMDAyNCAAMDAwMDAwMDAwMDIgMTMwNzEyNDU0NzAgMDEyNDU1ACAwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHVzdGFyADAwZXN0aGVyAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABzdGFmZgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADAwMDAwMCAAMDAwMDAwIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADEKAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAdG1wL2UAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADAwMDY0NCAAMDAwNzY2IAAwMDAwMjQgADAwMDAwMDAwMDAyIDEzMDcxMjQ1NDcyIDAxMjQ2MAAgMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAB1c3RhcgAwMGVzdGhlcgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAc3RhZmYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAwMDAwMDAgADAwMDAwMCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAxCgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="
        }
    }




@pytest.fixture
def replicate2(experiment):
    return {
        'experiment': experiment['uuid'],
        'biological_replicate_number': 1,
        'technical_replicate_number': 1,
    }


@pytest.fixture
def replicate_rbns(replicate2):
    item = replicate2.copy()
    item.update({
        'rbns_protein_concentration': 10,
        'rbns_protein_concentration_units': 'nM',
    })
    return item


@pytest.fixture
def replicate_rbns_no_units(replicate2):
    item = replicate2.copy()
    item.update({
        'rbns_protein_concentration': 10,
    })
    return item



@pytest.fixture
def myc(testapp, human):
    item = {
        'uuid': 'd358f63b-63d6-408f-baca-13881c6c79a1',
        'dbxrefs': ['HGNC:7553'],
        'geneid': '4609',
        'symbol': 'MYC',
        'ncbi_entrez_status': 'live',
        'organism': human['uuid'],
    }
    return testapp.post_json('/gene', item).json['@graph'][0]


@pytest.fixture
def tbp(testapp, mouse):
    item = {
        'uuid': '93def54f-d998-4d85-ba9d-e985d4f736da',
        'dbxrefs': ['MGI:101838'],
        'geneid': '21374',
        'symbol': 'Tbp',
        'ncbi_entrez_status': 'live',
        'organism': mouse['uuid'],
    }
    return testapp.post_json('/gene', item).json['@graph'][0]


@pytest.fixture
def target_nongene(mouse):
    return {
        'label': 'nongene',
        'target_organism': mouse['uuid'],
        'investigated_as': ['other context'],
    }


@pytest.fixture
def target_one_gene(ctcf):
    return {
        'label': 'one-gene',
        'genes': [ctcf['uuid']],
        'investigated_as': ['other context'],
    }


@pytest.fixture
def target_two_same_org(ctcf, myc):
    return {
        'label': 'two-same-org',
        'genes': [ctcf['uuid'], myc['uuid']],
        'investigated_as': ['other context'],
    }


@pytest.fixture
def target_two_diff_orgs(ctcf, tbp):
    return {
        'label': 'two-diff-org',
        'genes': [ctcf['uuid'], tbp['uuid']],
        'investigated_as': ['other context'],
    }


@pytest.fixture
def target_genes_org(human, ctcf, myc):
    return {
        'label': 'genes-org',
        'target_organism': human['uuid'],
        'genes': [ctcf['uuid'], myc['uuid']],
        'investigated_as': ['other context'],
    }


@pytest.fixture
def target_synthetic_tag():
    return {
        'label': 'FLAG',
        'investigated_as': ['synthetic tag'],
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


@pytest.fixture
def human_donor(testapp, award, lab, human):
    item = {
        'award': award['@id'],
        'lab': lab['@id'],
        'organism': human['@id'],
    }
    return testapp.post_json('/human_donor', item).json['@graph'][0]

@pytest.fixture
def cart(testapp, submitter):
    item = {
        'name': 'test cart',
        'submitted_by': submitter['uuid'],
    }
    return testapp.post_json('/cart', item).json['@graph'][0]


@pytest.fixture
def other_cart(testapp, remc_member):
    item = {
        'name': 'test cart',
        'submitted_by': remc_member['uuid'],
    }
    return testapp.post_json('/cart', item).json['@graph'][0]


@pytest.fixture
def deleted_cart(testapp, submitter):
    item = {
        'name': 'test cart',
        'status': 'deleted',
        'elements': [],
        'submitted_by': submitter['uuid'],
    }
    return testapp.post_json('/cart', item).json['@graph'][0]


@pytest.fixture
def autosave_cart(testapp, submitter):
    item = {
        'name': 'test cart',
        'status': 'disabled',
        'elements': [],
        'submitted_by': submitter['uuid'],
    }
    return testapp.post_json('/cart', item).json['@graph'][0]


@pytest.fixture
def cart_submitter_testapp(app, submitter):
    '''TestApp with JSON accept header for non-admin user.
    '''
    from webtest import TestApp
    environ = {
        'HTTP_ACCEPT': 'application/json',
        'REMOTE_USER': submitter['uuid'],
    }
    return TestApp(app, environ)


@pytest.fixture
def other_cart_submitter_testapp(app, remc_member):
    '''TestApp with JSON accept header for non-admin user.
    '''
    from webtest import TestApp
    environ = {
        'HTTP_ACCEPT': 'application/json',
        'REMOTE_USER': remc_member['uuid'],
    }
    return TestApp(app, environ)


@pytest.fixture
def parent_human_donor(testapp, award, lab, human):
    item = {
        'lab': lab['@id'],
        'award': award['@id'],
        'organism': human['@id']
    }
    return testapp.post_json('/human_donor', item).json['@graph'][0]


@pytest.fixture
def child_human_donor(testapp, award, lab, human):
    item = {
        'lab': lab['@id'],
        'award': award['@id'],
        'organism': human['@id']
    }
    return testapp.post_json('/human_donor', item).json['@graph'][0]

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
def base_experiment_series(testapp, lab, award, experiment_1):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'related_datasets': [experiment_1['@id']]
    }
    return testapp.post_json('/experiment-series', item, status=201).json['@graph'][0]


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
def crispr_deletion_1(testapp, lab, award, target):
    item = {
        'lab': lab['@id'],
        'award': award['@id'],
        'category': 'deletion',
        'purpose': 'repression',
        'method': 'CRISPR',
        'modified_site_by_target_id': target['@id'],
        'guide_rna_sequences': ['ACCGGAGA']
    }
    return testapp.post_json('/genetic_modification', item).json['@graph'][0]


@pytest.fixture
def crispr_tag_1(testapp, lab, award, ctcf):
    item = {
        'lab': lab['@id'],
        'award': award['@id'],
        'category': 'insertion',
        'purpose': 'tagging',
        'method': 'CRISPR',
        'modified_site_by_gene_id': ctcf['@id'],
        'introduced_tags': [{'name': 'mAID-mClover', 'location': 'C-terminal'}]
    }
    return testapp.post_json('/genetic_modification', item).json['@graph'][0]


@pytest.fixture
def mpra_1(testapp, lab, award):
    item = {
        'lab': lab['@id'],
        'award': award['@id'],
        'category': 'insertion',
        'purpose': 'characterization',
        'method': 'transduction',
        'introduced_elements': 'synthesized DNA',
        'modified_site_nonspecific': 'random'
    }
    return testapp.post_json('/genetic_modification', item).json['@graph'][0]


@pytest.fixture
def recomb_tag_1(testapp, lab, award, target, treatment, document):
    item = {
        'lab': lab['@id'],
        'award': award['@id'],
        'category': 'insertion',
        'purpose': 'tagging',
        'method': 'site-specific recombination',
        'modified_site_by_target_id': target['@id'],
        'modified_site_nonspecific': 'random',
        'category': 'insertion',
        'treatments': [treatment['@id']],
        'documents': [document['@id']],
        'introduced_tags': [{'name': 'eGFP', 'location': 'C-terminal'}]
    }
    return testapp.post_json('/genetic_modification', item).json['@graph'][0]


@pytest.fixture
def rnai_1(testapp, lab, award, source, target):
    item = {
        'lab': lab['@id'],
        'award': award['@id'],
        'category': 'interference',
        'purpose': 'repression',
        'method': 'RNAi',
        'reagents': [{'source': source['@id'], 'identifier': 'addgene:12345'}],
        'rnai_sequences': ['ATTACG'],
        'modified_site_by_target_id': target['@id']
    }
    return testapp.post_json('/genetic_modification', item).json['@graph'][0]


@pytest.fixture
def base_reference_epigenome(testapp, lab, award):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'status': 'submitted'
    }
    return testapp.post_json('/reference_epigenome', item, status=201).json['@graph'][0]


@pytest.fixture
def base_single_cell_series(testapp, lab, base_experiment, award):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'related_datasets': [base_experiment['@id']]
    }
    return testapp.post_json('/single_cell_rna_series', item, status=201).json['@graph'][0]


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
def hg19_file(testapp, base_reference_epigenome, award, lab):
    item = {
        'dataset': base_reference_epigenome['@id'],
        'lab': lab['@id'],
        'award': award['@id'],
        'file_format': 'bigBed',
        'file_format_type': 'narrowPeak',
        'file_size': 345,
        'assembly': 'hg19',
        'md5sum': 'e002cd204df36d93dd070ef0712b8eed',
        'output_type': 'replicated peaks',
        'status': 'in progress',  # avoid s3 upload codepath
    }
    return testapp.post_json('/file', item, status=201).json['@graph'][0]


@pytest.fixture
def GRCh38_file(testapp, base_experiment, award, lab):
    item = {
        'dataset': base_experiment['@id'],
        'lab': lab['@id'],
        'award': award['@id'],
        'file_format': 'bigBed',
        'file_format_type': 'narrowPeak',
        'file_size': 345,
        'assembly': 'GRCh38',
        'md5sum': 'e002cd204df36d93dd070ef0712b8ee7',
        'output_type': 'replicated peaks',
        'status': 'in progress',  # avoid s3 upload codepath
    }
    return testapp.post_json('/file', item, status=201).json['@graph'][0]



@pytest.fixture
def treatment_1():
    return {
        'treatment_type': 'chemical',
        'treatment_term_name': 'estradiol',
        'treatment_term_id': 'CHEBI:23965'
    }


@pytest.fixture
def submitter_treatment(submitter, lab):
    return {
        'treatment_type': 'chemical',
        'treatment_term_name': 'estradiol',
        'treatment_term_id': 'CHEBI:23965',
        'submitted_by': submitter['@id']
    }


@pytest.fixture
def access_key_1(access_key):
    item = access_key.copy()
    item.update({
        'schema_version': '1'
    })
    return item

'''
This upgrade test is no longer need as the upgrade was also removed. The test and upgrade will remain
in the code for posterity but they both are no longer valid after versionof: was removed as a valid 
namespace according to http://redmine.encodedcc.org/issues/4748

@pytest.fixture
def analysis_step_version_with_alias(testapp, analysis_step, software_version):
    item = {
        'aliases': ['versionof:' + analysis_step['name']],
        'analysis_step': analysis_step['@id'],
        'software_versions': [
            software_version['@id'],
        ],
    }
    return testapp.post_json('/analysis_step_version', item).json['@graph'][0]


@pytest.fixture
def analysis_step_run_1(analysis_step):
    item = {
        'analysis_step': analysis_step['uuid'],
        'status': 'finished',
        'workflow_run': 'does not exist',
    }
    return item


def test_analysis_step_run_1_2(registry, upgrader, analysis_step_run_1, analysis_step_version_with_alias, threadlocals):
    value = upgrader.upgrade('analysis_step_run', analysis_step_run_1, current_version='1', target_version='2', registry=registry)
    assert value['analysis_step_version'] == analysis_step_version_with_alias['uuid']
    assert 'analysis_step' not in value
    assert 'workflows_run' not in value
'''


@pytest.fixture
def analysis_step_run_3(analysis_step, analysis_step_version):
    item = {
        'analysis_step_version': analysis_step_version['uuid'],
        'status': 'finished'
    }
    return item


@pytest.fixture
def analysis_step_run_4(analysis_step, analysis_step_version):
    item = {
        'analysis_step_version': analysis_step_version['uuid'],
        'status': 'virtual'
    }
    return item


@pytest.fixture
def analysis_step_version_3(testapp, analysis_step, software_version):
    item = {
        'schema_version': '3',
        'version': 1,
        'analysis_step': analysis_step['@id'],
        'software_versions': [
            software_version['@id'],
        ],
    }
    return item

@pytest.fixture
def base_analysis_step(testapp, software_version):
    item = {
        'name': 'lrna-pe-star-alignment-step-v-2-0',
        'title': 'Long RNA-seq STAR paired-ended alignment step v2.0',
        'analysis_step_types': ['alignments'],
        'input_file_types': ['reads'],
        'software_versions': [
            software_version['@id'],
        ]
    }
    return item


@pytest.fixture
def analysis_step_1(base_analysis_step):

    item = base_analysis_step.copy()
    item.update({
        'schema_version': '2',
        'output_file_types': ['signal of multi-mapped reads']
    })
    return item


@pytest.fixture
def analysis_step_3(base_analysis_step):
    item = base_analysis_step.copy()
    item.update({
        'schema_version': '3',
        'analysis_step_types': ['alignment', 'alignment'],
        'input_file_types': ['reads', 'reads'],
        'output_file_types': ['transcriptome alignments', 'transcriptome alignments']
    })
    return item


@pytest.fixture
def analysis_step_5(base_analysis_step):
    item = base_analysis_step.copy()
    item.update({
        'schema_version': '5',
        'aliases': ["dnanexus:align-star-se-v-2"],
        'uuid': '8eda9dfa-b9f1-4d58-9e80-535a5e4aaab1',
        'status': 'in progress',
        'analysis_step_types': ['pooling', 'signal generation', 'file format conversion', 'quantification'],
        'input_file_types': ['alignments'],
        'output_file_types': ['methylation state at CHG', 'methylation state at CHH', 'raw signal', 'methylation state at CpG']
    })
    return item


@pytest.fixture
def analysis_step_6(base_analysis_step):
    item = base_analysis_step.copy()
    item.update({
        'schema_version': '6',
        'input_file_types': ['alignments', 'candidate regulatory elements'],
        'output_file_types': ['raw signal', 'candidate regulatory elements']
    })
    return item


@pytest.fixture
def analysis_step_7(base_analysis_step):
    item = base_analysis_step.copy()
    item.update({
        'input_file_types': [
            'peaks',
            'optimal idr thresholded peaks',
            'conservative idr thresholded peaks',
            'pseudoreplicated idr thresholded peaks'
        ],
        'output_file_types': [
            'peaks',
            'optimal idr thresholded peaks',
            'conservative idr thresholded peaks',
            'pseudoreplicated idr thresholded peaks'
        ],
    })
    return item


def test_analysis_step_2_3(registry, upgrader, analysis_step_1, threadlocals):
    value = upgrader.upgrade('analysis_step', analysis_step_1, current_version='2', target_version='3', registry=registry)
    assert 'signal of all reads' in value['output_file_types']
    assert 'signal of multi-mapped reads' not in value['output_file_types']

@pytest.fixture
def antibody_lot_base(lab, award, source):
    return {
        'award': award['uuid'],
        'product_id': 'SAB2100398',
        'lot_id': 'QC8343',
        'lab': lab['uuid'],
        'source': source['uuid'],
    }


@pytest.fixture
def antibody_lot_1(antibody_lot_base):
    item = antibody_lot_base.copy()
    item.update({
        'schema_version': '1',
        'encode2_dbxrefs': ['CEBPZ'],
    })
    return item


@pytest.fixture
def antibody_lot_2(antibody_lot_base):
    item = antibody_lot_base.copy()
    item.update({
        'schema_version': '2',
        'award': '1a4d6443-8e29-4b4a-99dd-f93e72d42418',
        'status': "CURRENT"
    })
    return item


@pytest.fixture
def antibody_lot_3(root, antibody_lot):
    item = root.get_by_uuid(antibody_lot['uuid'])
    properties = item.properties.copy()
    del properties['targets']
    properties.update({
        'schema_version': '3'
    })
    return properties


@pytest.fixture
def antibody_lot_4(root, antibody_lot_3):
    item = antibody_lot_3.copy()
    item.update({
        'schema_version': '4',
        'lot_id_alias': ['testing:456', 'testing:456'],
        'purifications': ['crude', 'crude']
    })
    return item

@pytest.fixture
def award_0():
    return{
        'name': 'ENCODE2',
    }


@pytest.fixture
def award_1(award_0):
    item = award_0.copy()
    item.update({
        'schema_version': '1',
        'rfa': "ENCODE2"
    })
    return item

@pytest.fixture
def award_2(award_1):
    item = award_1.copy()
    item.update({
        'schema_version': '3',
        'viewing_group': 'ENCODE',
    })
    return item


@pytest.fixture
def award_5(award_2):
    item = award_2.copy()
    item.update({
        'schema_version': '6',
        'viewing_group': 'ENCODE',
    })
    return item

@pytest.fixture
def biosample_upgrade_0(submitter, lab, award, source, organism):
    return {
        'award': award['uuid'],
        'biosample_term_id': 'UBERON:0000948',
        'biosample_term_name': 'heart',
        'biosample_type': 'tissue',
        'lab': lab['uuid'],
        'organism': organism['uuid'],
        'source': source['uuid'],
    }


@pytest.fixture
def biosample_upgrade_1(biosample_upgrade_0):
    item = biosample_upgrade_0.copy()
    item.update({
        'schema_version': '1',
        'starting_amount': 1000,
        'starting_amount_units': 'g'
    })
    return item


@pytest.fixture
def biosample_upgrade_2(biosample_upgrade_0):
    item = biosample_upgrade_0.copy()
    item.update({
        'schema_version': '2',
        'subcellular_fraction': 'nucleus',
    })
    return item


@pytest.fixture
def biosample_upgrade_3(biosample_upgrade_0, biosample):
    item = biosample_upgrade_0.copy()
    item.update({
        'schema_version': '3',
        'derived_from': [biosample['uuid']],
        'part_of': [biosample['uuid']],
        'encode2_dbxrefs': ['Liver'],
    })
    return item


@pytest.fixture
def biosample_upgrade_4(biosample_upgrade_0, encode2_award):
    item = biosample_upgrade_0.copy()
    item.update({
        'schema_version': '4',
        'status': 'CURRENT',
        'award': encode2_award['uuid'],
    })
    return item


@pytest.fixture
def biosample_upgrade_6(biosample_upgrade_0):
    item = biosample_upgrade_0.copy()
    item.update({
        'schema_version': '5',
        'sex': 'male',
        'age': '2',
        'age_units': 'week',
        'health_status': 'Normal',
        'life_stage': 'newborn',

    })
    return item


@pytest.fixture
def biosample_upgrade_7(biosample_upgrade_0):
    item = biosample_upgrade_0.copy()
    item.update({
        'schema_version': '7',
        'worm_life_stage': 'embryonic',
    })
    return item


@pytest.fixture
def biosample_upgrade_8(biosample_upgrade_0):
    item = biosample_upgrade_0.copy()
    item.update({
        'schema_version': '8',
        'model_organism_age': '15.0',
        'model_organism_age_units': 'day',
    })
    return item


@pytest.fixture
def biosample_upgrade_9(root, biosample, publication):
    item = root.get_by_uuid(biosample['uuid'])
    properties = item.properties.copy()
    properties.update({
        'schema_version': '9',
        'references': [publication['identifiers'][0]],
    })
    return properties


@pytest.fixture
def biosample_upgrade_10(root, biosample):
    item = root.get_by_uuid(biosample['uuid'])
    properties = item.properties.copy()
    properties.update({
        'schema_version': '10',
        'worm_synchronization_stage': 'starved L1 larva'
    })
    return properties


@pytest.fixture
def biosample__upgrade_11(root, biosample):
    item = root.get_by_uuid(biosample['uuid'])
    properties = item.properties.copy()
    properties.update({
        'schema_version': '11',
        'dbxrefs': ['UCSC-ENCODE-cv:K562', 'UCSC-ENCODE-cv:K562'],
        'aliases': ['testing:123', 'testing:123']
    })
    return properties


@pytest.fixture
def biosample_upgrade_12(biosample_upgrade_0, document):
    item = biosample_upgrade_0.copy()
    item.update({
        'schema_version': '12',
        'starting_amount': 'unknown',
        'starting_amount_units': 'g',
        'note': 'Value in note.',
        'submitter_comment': 'Different value in submitter_comment.',
        'protocol_documents': list(document)
    })
    return item


@pytest.fixture
def biosample__upgrade_13(biosample_upgrade_0, document):
    item = biosample_upgrade_0.copy()
    item.update({
        'schema_version': '13',
        'notes': ' leading and trailing whitespace ',
        'description': ' leading and trailing whitespace ',
        'submitter_comment': ' leading and trailing whitespace ',
        'product_id': ' leading and trailing whitespace ',
        'lot_id': ' leading and trailing whitespace '
    })
    return item


@pytest.fixture
def biosample_upgrade_15(biosample_upgrade_0, biosample):
    item = biosample_upgrade_0.copy()
    item.update({
        'date_obtained': '2017-06-06T20:29:37.059673+00:00',
        'schema_version': '15',
        'derived_from': biosample['uuid'],
        'talens': []
    })
    return item


@pytest.fixture
def biosample_upgrade_18(biosample_upgrade_0, biosample):
    item = biosample_upgrade_0.copy()
    item.update({
        'biosample_term_id': 'EFO:0002067',
        'biosample_term_name': 'K562',
        'biosample_type': 'immortalized cell line',
        'transfection_type': 'stable',
        'transfection_method': 'electroporation'
    })
    return item


@pytest.fixture
def biosample_upgrade_19(biosample_upgrade_0, biosample):
    item = biosample_upgrade_0.copy()
    item.update({
        'biosample_type': 'immortalized cell line',
    })
    return item


@pytest.fixture
def biosample_upgrade_21(biosample_upgrade_0, biosample):
    item = biosample_upgrade_0.copy()
    item.update({
        'biosample_type': 'stem cell',
        'biosample_term_id': 'EFO:0007071',
        'biosample_term_name': 'BG01'
    })
    return item


@pytest.fixture
def bigbed(testapp, lab, award, experiment, analysis_step_run):
    item = {
        'dataset': experiment['@id'],
        'file_format': 'bigBed',
        'file_format_type': 'bedMethyl',
        'md5sum': 'd41d8cd98f00b204e9800998ecf8427e',
        'output_type': 'methylation state at CpG',
        'assembly': 'hg19',
        'file_size': 13224,
        'lab': lab['@id'],
        'award': award['@id'],
        'status': 'in progress',  # avoid s3 upload codepath
        'step_run': analysis_step_run['@id'],
    }
    return testapp.post_json('/file', item).json['@graph'][0]


@pytest.fixture
def bismark_quality_metric_1(pipeline, analysis_step_run, bigbed):
    return {
        'status': "finished",
        'pipeline': pipeline['uuid'],
        'step_run': analysis_step_run['uuid'],
        'schema_version': '1',
    }


@pytest.fixture
def bismark_quality_metric_2(pipeline, analysis_step_run, bigbed):
    return {
        'status': "finished",
        'pipeline': pipeline['uuid'],
        'step_run': analysis_step_run['uuid'],
        'schema_version': '3',
        'quality_metric_of': [bigbed['uuid']]
    }


@pytest.fixture
def antibody_characterization(submitter, award, lab, antibody_lot, target):
    return {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'target': target['uuid'],
        'characterizes': antibody_lot['uuid'],
    }


@pytest.fixture
def biosample_characterization_base(submitter, award, lab, biosample):
    return {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'characterizes': biosample['uuid'],
    }


@pytest.fixture
def antibody_characterization_1(antibody_characterization):
    item = antibody_characterization.copy()
    item.update({
        'schema_version': '1',
        'status': 'SUBMITTED',
        'characterization_method': 'mass spectrometry after IP',
        'attachment': {'download': 'red-dot.png', 'href': RED_DOT}
    })
    return item


@pytest.fixture
def antibody_characterization_2(antibody_characterization):
    item = antibody_characterization.copy()
    item.update({
        'schema_version': '3',
        'status': 'COMPLIANT'
    })
    return item


@pytest.fixture
def biosample_characterization_1(biosample_characterization_base):
    item = biosample_characterization_base.copy()
    item.update({
        'schema_version': '2',
        'status': 'APPROVED',
        'characterization_method': 'immunofluorescence',
    })
    return item


@pytest.fixture
def biosample_characterization_2(biosample_characterization_base):
    item = biosample_characterization_base.copy()
    item.update({
        'schema_version': '3',
        'status': 'IN PROGRESS',
        'award': '1a4d6443-8e29-4b4a-99dd-f93e72d42418'
    })
    return item


@pytest.fixture
def antibody_characterization_3(antibody_characterization):
    item = antibody_characterization.copy()
    item.update({
        'schema_version': '4',
        'characterization_method': 'immunoblot',
    })
    return item


@pytest.fixture
def biosample_characterization_4(root, biosample_characterization, publication):
    item = root.get_by_uuid(biosample_characterization['uuid'])
    properties = item.properties.copy()
    properties.update({
        'schema_version': '4',
        'references': [publication['identifiers'][0]],
    })
    return properties


@pytest.fixture
def antibody_characterization_10(antibody_characterization_1):
    item = antibody_characterization_1.copy()
    item.update({
        'status': 'pending dcc review',
        'characterization_method': 'immunoprecipitation followed by mass spectrometry',
        'comment': 'We tried really hard to characterize this antibody.',
        'notes': 'Your plea has been noted.'
    })
    return item


@pytest.fixture
def antibody_characterization_11(antibody_characterization):
    item = antibody_characterization.copy()
    item.update({
        'characterization_reviews': [{
            'biosample_term_name': 'K562',
            'biosample_term_id': 'EFO:0002067',
            'lane_status': 'exempt from standards',
            'biosample_type': 'immortalized cell line',
            'lane': 2,
            'organism': '/organisms/human/'
        }]
    })
    return item


@pytest.fixture
def antibody_characterization_13(antibody_characterization):
    item = antibody_characterization.copy()
    item.update({
        'characterization_reviews': [{
            'biosample_term_name': 'HUES62',
            'biosample_term_id': 'EFO:0007087',
            'lane_status': 'exempt from standards',
            'biosample_type': 'induced pluripotent stem cell line',
            'lane': 2,
            'organism': '/organisms/human/'
        }]
    })
    return item


@pytest.fixture
def antibody_characterization_14(antibody_characterization):
    item = antibody_characterization.copy()
    item.update({
        'characterization_reviews': [{
            'biosample_term_name': 'A549',
            'biosample_term_id': 'EFO:0001086',
            'lane_status': 'exempt from standards',
            'biosample_type': 'cell line',
            'lane': 2,
            'organism': '/organisms/human/'
        }]
    })
    return item

@pytest.fixture
def chip_peak_enrichment_quality_metric_1(award, lab):
    return{
        "step_run": "63b1b347-f008-4103-8d20-0e12f54d1882",
        "award": award["uuid"],
        "lab": lab["uuid"],
        "quality_metric_of": ["ENCFF003COS"],
        "FRiP":  0.253147998729
    }

@pytest.fixture 
def chip_replication_quality_metric_1(award, lab):
    return{
        "step_run": "63b1b347-f008-4103-8d20-0e12f54d1882",
        "award": award["uuid"],
        "lab": lab["uuid"],
        "quality_metric_of": ["ENCFF003COS"],
        "IDR_dispersion_plot": "ENCFF002DSJ.raw.srt.filt.nodup.srt.filt.nodup.sample.15.SE.tagAlign.gz.cc.plot.pdf"
    }

@pytest.fixture
def experiment_upgrade_1(root, experiment, file, file_ucsc_browser_composite):
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
def experiment_upgrade_2():
    return {
        'schema_version': '2',
        'encode2_dbxrefs': ['wgEncodeEH002945'],
        'geo_dbxrefs': ['GSM99494'],
    }


@pytest.fixture
def dataset_upgrade_2():
    return {
        'schema_version': '2',
        'aliases': ['ucsc_encode_db:mm9-wgEncodeCaltechTfbs', 'barbara-wold:mouse-TFBS'],
        'geo_dbxrefs': ['GSE36024'],
    }


@pytest.fixture
def experiment_upgrade_3():
    return {
        'schema_version': '3',
        'status': "DELETED",
    }


@pytest.fixture
def dataset_upgrade_3():
    return {
        'schema_version': '3',
        'status': 'CURRENT',
        'award': '2a27a363-6bb5-43cc-99c4-d58bf06d3d8e',
    }


@pytest.fixture
def dataset_upgrade_5(publication):
    return {
        'schema_version': '5',
        'references': [publication['identifiers'][0]],
    }


@pytest.fixture
def experiment_upgrade_6():
    return {
        'schema_version': '6',
        'dataset_type': 'experiment',
    }


@pytest.fixture
def experiment_upgrade_7(root, experiment):
    item = root.get_by_uuid(experiment['uuid'])
    properties = item.properties.copy()
    properties.update({
        'schema_version': '7',
        'dbxrefs': ['UCSC-ENCODE-cv:K562', 'UCSC-ENCODE-cv:K562'],
        'aliases': ['testing:123', 'testing:123']
    })
    return properties


@pytest.fixture
def annotation_upgrade_8(award, lab):
    return {
        'award': award['@id'],
        'lab': lab['@id'],
        'schema_version': '8',
        'annotation_type': 'encyclopedia',
        'status': 'released'
    }


@pytest.fixture
def annotation_upgrade_12(award, lab):
    return {
        'award': award['@id'],
        'lab': lab['@id'],
        'schema_version': '12',
        'annotation_type': 'candidate regulatory regions',
        'status': 'released'
    }


@pytest.fixture
def annotation_upgrade_14(award, lab):
    return {
        'award': award['@id'],
        'lab': lab['@id'],
        'schema_version': '14',
        'annotation_type': 'candidate regulatory regions',
        'status': 'proposed'
    }


@pytest.fixture
def experiment_upgrade_10(root, experiment):
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
def experiment_upgrade_13(root, experiment):
    item = root.get_by_uuid(experiment['uuid'])
    properties = item.properties.copy()
    properties.update({
        'schema_version': '13',
        'status': 'proposed',
    })
    return properties


@pytest.fixture
def experiment_upgrade_14(root, experiment):
    item = root.get_by_uuid(experiment['uuid'])
    properties = item.properties.copy()
    properties.update({
        'schema_version': '14',
        'biosample_type': 'in vitro sample',
    })
    return properties


@pytest.fixture
def experiment_upgrade_15(root, experiment):
    item = root.get_by_uuid(experiment['uuid'])
    properties = item.properties.copy()
    properties.update({
        'schema_version': '15',
        'biosample_type': 'immortalized cell line'
    })
    return properties


@pytest.fixture
def experiment_upgrade_16(root, experiment):
    item = root.get_by_uuid(experiment['uuid'])
    properties = item.properties.copy()
    properties.update({
        'schema_version': '16',
        'biosample_type': 'immortalized cell line',
        'status': 'ready for review'
    })
    return properties


@pytest.fixture
def experiment_upgrade_17(root, experiment):
    item = root.get_by_uuid(experiment['uuid'])
    properties = item.properties.copy()
    properties.update({
        'schema_version': '17',
        'biosample_type': 'immortalized cell line',
        'status': 'started'
    })
    return properties


@pytest.fixture
def experiment_upgrade_21(root, experiment):
    item = root.get_by_uuid(experiment['uuid'])
    properties = item.properties.copy()
    properties.update({
        'schema_version': '21',
        'biosample_type': 'induced pluripotent stem cell line',
        'status': 'started'
    })
    return properties


@pytest.fixture
def annotation_upgrade_16(award, lab):
    return {
        'award': award['@id'],
        'lab': lab['@id'],
        'schema_version': '16',
        'biosample_type': 'immortalized cell line'
    }


@pytest.fixture
def annotation_upgrade_17(award, lab):
    return {
        'award': award['@id'],
        'lab': lab['@id'],
        'schema_version': '17',
        'biosample_type': 'immortalized cell line',
        'status': 'started'
    }


@pytest.fixture
def annotation_upgrade_19(award, lab):
    return {
        'award': award['@id'],
        'lab': lab['@id'],
        'schema_version': '19',
        'biosample_type': 'stem cell',
        'biosample_term_name': 'mammary stem cell',
        'status': 'started'
    }


@pytest.fixture
def experiment_upgrade_22(root, experiment):
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
def experiment_upgrade_25(root, experiment):
    item = root.get_by_uuid(experiment['uuid'])
    properties = item.properties.copy()
    properties.update({
        'schema_version': '25',
        'assay_term_name': 'ISO-seq'
    })
    return properties


@pytest.fixture
def experiment_upgrade_26(root, experiment):
    item = root.get_by_uuid(experiment['uuid'])
    properties = item.properties.copy()
    properties.update({
        'schema_version': '26',
        'assay_term_name': 'single-nuclei ATAC-seq'
    })
    return properties

@pytest.fixture
def experiment_upgrade_27(root, experiment):
    item = root.get_by_uuid(experiment['uuid'])
    properties = item.properties.copy()
    properties.update({
                      'schema_version': '27',
                      'experiment_classification': ['functional genomics assay']
                      
    })
    return properties


@pytest.fixture
def annotation_upgrade_20(award, lab):
    return {
        'award': award['@id'],
        'lab': lab['@id'],
        'schema_version': '19',
        'biosample_type': 'primary cell',
        'biosample_term_id': 'CL:0000765',
        'biosample_term_name': 'erythroblast',
        'internal_tags': ['cre_inputv10', 'cre_inputv11', 'ENCYCLOPEDIAv3']
    }

@pytest.fixture
def annotation_upgrade_21(award, lab):
    return {
        'award': award['@id'],
        'lab': lab['@id'],
        'schema_version': '24',
        'annotation_type': 'candidate regulatory elements'
    }


@pytest.fixture
def annotation_upgrade_25(award, lab):
    return {
        'award': award['@id'],
        'lab': lab['@id'],
        'schema_version': '25',
        'encyclopedia_version': '1'
    }


@pytest.fixture
def annotation_upgrade_26(award, lab):
    return {
        'award': award['@id'],
        'lab': lab['@id'],
        'schema_version': '26',
        'dbxrefs': ['IHEC:IHECRE00000998.1'],
    }


@pytest.fixture
def reference_epigenome_16(award, lab):
    return {
        'award': award['@id'],
        'lab': lab['@id'],
        'schema_version': '16',
        'dbxrefs': ['IHEC:IHECRE00004643.1'],
    }

@pytest.fixture
def document_0(publication):
    return {
        'references': [publication['identifiers'][0]],
    }


@pytest.fixture
def document_base(lab, award):
    return {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'document_type': 'growth protocol',
    }


@pytest.fixture
def document_1(document_base):
    item = document_base.copy()
    item.update({
        'schema_version': '2',
        'status': 'CURRENT',
        'award': '4d462953-2da5-4fcf-a695-7206f2d5cf45'
    })
    return item


@pytest.fixture
def document_3(root, document, publication):
    item = root.get_by_uuid(document['uuid'])
    properties = item.properties.copy()
    properties.update({
        'schema_version': '3',
        'references': [publication['identifiers'][0]],
    })
    return properties

@pytest.fixture
def human_donor_upgrade(lab, award, organism):
    return {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'organism': organism['uuid'],
    }


@pytest.fixture
def mouse_donor_base(lab, award):
    return {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'organism': '3413218c-3d86-498b-a0a2-9a406638e786',
    }


@pytest.fixture
def human_donor_1(human_donor_upgrade):
    item = human_donor_upgrade.copy()
    item.update({
        'schema_version': '1',
        'status': 'CURRENT',
        'award': '4d462953-2da5-4fcf-a695-7206f2d5cf45'
    })
    return item


@pytest.fixture
def human_donor_2(human_donor_upgrade):
    item = human_donor_upgrade.copy()
    item.update({
        'schema_version': '2',
        'age': '11.0'
    })
    return item


@pytest.fixture
def mouse_donor_1(mouse_donor_base):
    item = mouse_donor_base.copy()
    item.update({
        'schema_version': '1',
        'status': 'CURRENT',
        'award': '1a4d6443-8e29-4b4a-99dd-f93e72d42418'
    })
    return item


@pytest.fixture
def mouse_donor_2(mouse_donor_base):
    item = mouse_donor_base.copy()
    item.update({
        'schema_version': '2',
        'sex': 'male',

    })
    return item


@pytest.fixture
def mouse_donor_3(root, mouse_donor, publication):
    item = root.get_by_uuid(mouse_donor['uuid'])
    properties = item.properties.copy()
    properties.update({
        'schema_version': '3',
        'references': [publication['identifiers'][0]],

    })
    return properties


@pytest.fixture
def fly_donor_3(award, lab, fly):
    return {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'organism': fly['uuid'],
        'schema_version': '3',
        'aliases': [
            'roadmap-epigenomics:smRNA-Seq analysis of foreskin keratinocytes from skin03||Thu Jan 17 19:05:12 -0600 2013||58540||library',
            'encode:lots:of:colons*'
        ]
    }


@pytest.fixture
def human_donor_6(root, donor_1):
    item = root.get_by_uuid(donor_1['uuid'])
    properties = item.properties.copy()
    properties.update({
        'schema_version': '6',
        'aliases': [
            'encode:why||put||up||bars',
            'encode:lots:and:lots:of:colons!'
        ]
    })
    return properties


@pytest.fixture
def human_donor_9(root, donor_1):
    item = root.get_by_uuid(donor_1['uuid'])
    properties = item.properties.copy()
    properties.update({
        'schema_version': '9',
        'life_stage': 'postnatal',
        'ethnicity': 'caucasian'
    })
    return properties


@pytest.fixture
def fly_donor_7(root, fly, target_promoter):
    item = fly.copy()
    item.update({
        'schema_version': '7',
        'mutated_gene': target_promoter['uuid'],
        'mutagen': 'TMP/UV'
    })
    return item


@pytest.fixture
def human_donor_10(root, donor_1):
    item = root.get_by_uuid(donor_1['uuid'])
    properties = item.properties.copy()
    properties.update({
        'schema_version': '10',
        'genetic_modifications': []
    })
    return properties


@pytest.fixture
def mouse_donor_10(root, mouse_donor):
    item = root.get_by_uuid(mouse_donor['uuid'])
    properties = item.properties.copy()
    properties.update({
        'schema_version': '10',
        'parent_strains': []
    })
    return properties

@pytest.fixture
def fly_donor_9(root, fly, target_promoter):
    item = fly.copy()
    item.update({
        'schema_version': '9',
        'aliases': ['kyoto:test-alias-1'],
        'dbxrefs': ['Kyoto:123456']
    })
    return item


@pytest.fixture
def file_base(experiment):
    return {
        'accession': 'ENCFF000TST',
        'dataset': experiment['uuid'],
        'file_format': 'fasta',
        'file_size': 243434,
        'md5sum': 'd41d8cd98f00b204e9800998ecf8427e',
        'output_type': 'raw data',
    }


@pytest.fixture
def file_1(file_base):
    item = file_base.copy()
    item.update({
        'schema_version': '1',
        'status': 'CURRENT',
        'award': '1a4d6443-8e29-4b4a-99dd-f93e72d42418'
    })
    return item


@pytest.fixture
def file_2(file_base):
    item = file_base.copy()
    item.update({
        'schema_version': '2',
        'status': 'current',
        'download_path': 'bob.bigBed'
    })
    return item


@pytest.fixture
def file_3(file_base):
    item = file_base.copy()
    item.update({
        'schema_version': '3',
        'status': 'current',
        'download_path': 'bob.bigBed'
    })
    return item


@pytest.fixture
def file_4(file_base):
    item = file_base.copy()
    item.update({
        'schema_version': '4',
        'file_format': 'bed_bedMethyl',
        'download_path': 'bob.bigBed',
        'output_type': 'Base_Overlap_Signal'
    })
    return item


@pytest.fixture
def file_5(file_base):
    item = file_base.copy()
    item.update({
        'schema_version': '5',
        'file_format': 'bigWig',
        'output_type': 'signal of multi-mapped reads'
    })
    return item


@pytest.fixture
def file_7(file_base):
    item = file_base.copy()
    item.update({
        'schema_version': '7'
    })
    return item


@pytest.fixture
def file_8a(file_base):
    item = file_base.copy()
    item.update({
        'file_format': 'fastq',
        'assembly': 'hg19',
        'schema_version': '8'
    })
    return item


@pytest.fixture
def file_9(file_base):
    item = file_base.copy()
    item.update({
        'date_created': '2017-04-28'
    })
    return item


@pytest.fixture
def file_10(file_base):
    item = file_base.copy()
    item.update({
        'schema_version': '10'
    })
    return item


@pytest.fixture
def file_12(file_base):
    item = file_base.copy()
    item.update({
        'platform': 'ced61406-dcc6-43c4-bddd-4c977cc676e8',
        'schema_version': '12',
        'file_format': 'fastq',
        'run_type': 'single-ended',
        'read_length': 55,
        'file_size': 243434,
        'md5sum': 'd41d8cd98f00b204e9800998ecf8423e',
        'output_type': 'reads'
    })
    return item


@pytest.fixture
def old_file(experiment):
    return {
        'accession': 'ENCFF000OLD',
        'dataset': experiment['uuid'],
        'file_format': 'fasta',
        'md5sum': 'e41d9ce97b00b204e9811998ecf8427b',
        'output_type': 'raw data',
        'uuid': '627ef1f4-3426-44f4-afc3-d723eccd20bf'
    }


@pytest.fixture
def file_8b(file_base, old_file):
    item = file_base.copy()
    item.update({
        'schema_version': '8',
        'supercedes': list(old_file['uuid'])
    })
    return item

@pytest.fixture
def file_13(file_base):
    item = file_base.copy()
    item.update({
        'output_type': 'candidate regulatory elements'
    })
    return item

@pytest.fixture
def file_14_optimal(file_base):
    item = file_base.copy()
    item.update({
        'output_type': 'optimal idr thresholded peaks'
    })
    return item


@pytest.fixture
def file_14_conservative(file_base):
    item = file_base.copy()
    item.update({
        'output_type': 'conservative idr thresholded peaks'
    })
    return item


@pytest.fixture
def file_14_pseudoreplicated(file_base):
    item = file_base.copy()
    item.update({
        'output_type': 'pseudoreplicated idr thresholded peaks'
    })
    return item


@pytest.fixture
def file_15(file_base):
    item = file_base.copy()
    item.update({
        'platform': 'e2be5728-5744-4da4-8881-cb9526d0389e',
        'schema_version': '15',
        'file_format': 'fastq',
        'run_type': 'single-ended',
        'read_length': 55,
        'file_size': 243434,
        'md5sum': 'd41d8cd98f00b204e9800998ecf8423e',
        'output_type': 'reads'
    })
    return item

@pytest.fixture
def file_16(file_base):
    item = file_base.copy()
    item.update({
        'platform': '6c275b37-018d-4bf8-85f6-6e3b830524a9',
        'schema_version': '16'
    })
    return item


@pytest.fixture
def gene_1(gene):
    item = gene.copy()
    item.update({
        'go_annotations': [
            {
                "go_id": "GO:0000122",
                "go_name": "negative regulation of transcription by RNA polymerase II",
                "go_evidence_code": "IDA",
                "go_aspect": "P"
            },
            {
                "go_id": "GO:0000775",
                "go_name": "chromosome, centromeric region",
                "go_evidence_code": "IDA",
                "go_aspect": "C"
            },
            {
                "go_id": "GO:0000793",
                "go_name": "condensed chromosome",
                "go_evidence_code": "IDA",
                "go_aspect": "C"
            },
        ],
    })
    return item


@pytest.fixture
def genetic_modification_1(lab, award):
    return {
        'modification_type': 'deletion',
        'award': award['uuid'],
        'lab': lab['uuid'],
        'modifiction_description': 'some description'
    }


@pytest.fixture
def genetic_modification_2(lab, award):
    return {
        'modification_type': 'deletion',
        'award': award['uuid'],
        'lab': lab['uuid'],
        'modification_description': 'some description',
        'modification_zygocity': 'homozygous',
        'modification_purpose': 'tagging',
        'modification_treatments': [],
        'modification_genome_coordinates': [{
            'chromosome': '11',
            'start': 5309435,
            'end': 5309451
            }]
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
def genetic_modification_5(lab, award, crispr):
    return {
        'modification_type': 'deletion',
        'award': award['uuid'],
        'lab': lab['uuid'],
        'description': 'blah blah description blah',
        'zygosity': 'homozygous',
        'treatments': [],
        'source': 'sigma',
        'product_id': '12345',
        'modification_techniques': [crispr],
        'modified_site': [{
            'assembly': 'GRCh38',
            'chromosome': '11',
            'start': 5309435,
            'end': 5309451
            }]
    }

@pytest.fixture
def genetic_modification_6(lab, award, crispr, source):
    return {
        'purpose': 'validation',
        'category': 'deeltion',
        'award': award['uuid'],
        'lab': lab['uuid'],
        'description': 'blah blah description blah',
        "method": "CRISPR",
        "modified_site_by_target_id": "/targets/FLAG-ZBTB43-human/",
        "reagents": [
            {
                "identifier": "placeholder_id",
                "source": source['uuid']
            }
        ]
    }


@pytest.fixture
def genetic_modification_7_invalid_reagent(lab, award, crispr):
    return {
        'purpose': 'characterization',
        'category': 'deletion',
        'award': award['uuid'],
        'lab': lab['uuid'],
        'description': 'blah blah description blah',
        "method": "CRISPR",
        "modified_site_by_target_id": "/targets/FLAG-ZBTB43-human/",
        "reagents": [
            {
                "identifier": "placeholder_id",
                "source": "/sources/sigma/"
            }
        ]
    }


@pytest.fixture
def genetic_modification_7_valid_reagent(lab, award, crispr):
    return {
        'purpose': 'characterization',
        'category': 'deletion',
        'award': award['uuid'],
        'lab': lab['uuid'],
        'description': 'blah blah description blah',
        "method": "CRISPR",
        "modified_site_by_target_id": "/targets/FLAG-ZBTB43-human/",
        "reagents": [
            {
                "identifier": "ABC123",
                "source": "/sources/sigma/"
            }
        ]
    }


@pytest.fixture
def genetic_modification_7_addgene_source(testapp):
    item = {
        'name': 'addgene',
        'title': 'Addgene',
        'status': 'released'
    }
    return testapp.post_json('/source', item).json['@graph'][0]


@pytest.fixture
def genetic_modification_7_multiple_matched_identifiers(lab, award, crispr):
    return {
        'purpose': 'characterization',
        'category': 'deletion',
        'award': award['uuid'],
        'lab': lab['uuid'],
        'description': 'blah blah description blah',
        "method": "CRISPR",
        "modified_site_by_target_id": "/targets/FLAG-ZBTB43-human/",
        "reagents": [
            {
                "identifier": "12345",
                "source": "/sources/addgene/"
            }
        ]
    }


@pytest.fixture
def genetic_modification_7_multiple_reagents(lab, award, crispr):
    return {
        'purpose': 'characterization',
        'category': 'deletion',
        'award': award['uuid'],
        'lab': lab['uuid'],
        'description': 'blah blah description blah',
        "method": "CRISPR",
        "modified_site_by_target_id": "/targets/FLAG-ZBTB43-human/",
        "reagents": [
            {
                "identifier": "12345",
                "source": "/sources/addgene/",
                "url": "http://www.addgene.org"
            },
            {
                "identifier": "67890",
                "source": "/sources/addgene/",
                "url": "http://www.addgene.org"
            }
        ]
    }


@pytest.fixture
def genetic_modification_8(lab, award):
    return {
        'purpose': 'analysis',
        'category': 'interference',
        'award': award['uuid'],
        'lab': lab['uuid'],
        "method": "CRISPR",
    }

@pytest.fixture
def lab_0():
    return{
        'name': 'Fake Lab',
    }


@pytest.fixture
def lab_1(lab_0):
    item = lab_0.copy()
    item.update({
        'schema_version': '1',
        'status': 'CURRENT',
    })
    return item


@pytest.fixture
def library_upgrade(lab, award):
    return {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'nucleic_acid_term_id': 'SO:0000352',
        'nucleic_acid_term_name': 'DNA',
    }


@pytest.fixture
def library_1_upgrade(library_upgrade):
    item = library_upgrade.copy()
    item.update({
        'schema_version': '2',
        'status': 'CURRENT',
        'award': '1a4d6443-8e29-4b4a-99dd-f93e72d42418'
    })
    return item


@pytest.fixture
def library_2_upgrade(library_upgrade):
    item = library_upgrade.copy()
    item.update({
        'schema_version': '3',
        'paired_ended': False
    })
    return item


@pytest.fixture
def library_3_upgrade(library_upgrade):
    item = library_upgrade.copy()
    item.update({
        'schema_version': '3',
        'fragmentation_method': 'covaris sheering'
    })
    return item

@pytest.fixture
def library_8_upgrade(library_3_upgrade):
    item = library_3_upgrade.copy()
    item.update({
        'schema_version': '8',
        'status': "in progress"
    })
    return item

@pytest.fixture
def page():
    return{
        'name': 'Fake Page',
    }


@pytest.fixture
def page_1(page):
    item = page.copy()
    item.update({
        'schema_version': '1',
        'news_keywords': ['RNA binding', 'Experiment', 'DNA methylation', 'promoter-like regions', 'Conferences'],
    })
    return item


@pytest.fixture
def page_2(page):
    item = page.copy()
    item.update({
        'schema_version': '1',
        'news_keywords': ['Experiment', 'promoter-like regions'],
    })
    return item


@pytest.fixture
def page_3(page):
    item = page.copy()
    item.update({
        'schema_version': '1',
    })
    return item

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
def platform():
    return{
        'term_name': 'ChIP-seq',
        'term_id': 'OBI:0000716'
    }


@pytest.fixture
def platform_1(platform):
    item = platform.copy()
    item.update({
        'schema_version': '1',
        'encode2_dbxrefs': ['AB_SOLiD_3.5'],
        'geo_dbxrefs': ['GPL9442'],
    })
    return item


@pytest.fixture
def platform_2(platform):
    item = platform.copy()
    item.update({
        'schema_version': '2',
        'status': "CURRENT",
    })
    return item


@pytest.fixture
def platform_6(platform):
    item = platform.copy()
    item.update({
        'schema_version': '6',
        'status': "current",
    })
    return item


@pytest.fixture
def publication_upgrade():
    return{
        'title': "Fake paper"
    }


@pytest.fixture
def publication_1(publication_upgrade):
    item = publication_upgrade.copy()
    item.update({
        'schema_version': '1',
        'references': ['PMID:25409824'],
    })
    return item


@pytest.fixture
def publication_4():
    return {
        'title': 'Fake paper',
        'schema_version': '4'
    }


@pytest.fixture
def publication_5(publication_upgrade):
    item = publication_upgrade.copy()
    item.update({
        'schema_version': '5',
        'status': 'in preparation'
    })
    return item


@pytest.fixture
def quality_metric_1(pipeline, analysis_step_run):
    return {
        'status': 'released',
        'pipeline': pipeline['uuid'],
        'step_run': analysis_step_run['uuid'],
        'schema_version': '1'
    }

@pytest.fixture
def replicate_1_upgrade(root, replicate, library):
    item = root.get_by_uuid(replicate['uuid'])
    properties = item.properties.copy()
    properties.update({
        'schema_version': '1',
        'library': library['uuid'],
        'paired_ended': False
    })
    return properties


@pytest.fixture
def replicate_3_upgrade(root, replicate):
    item = root.get_by_uuid(replicate['uuid'])
    properties = item.properties.copy()
    properties.update({
        'schema_version': '3',
        'notes': 'Test notes',
        'flowcell_details': [
            {
                u'machine': u'Unknown',
                u'lane': u'2',
                u'flowcell': u'FC64KEN'
            },
            {
                u'machine': u'Unknown',
                u'lane': u'3',
                u'flowcell': u'FC64M2B'
            }
        ]
    })
    return properties


@pytest.fixture
def replicate_4_upgrade(root, replicate):
    item = root.get_by_uuid(replicate['uuid'])
    properties = item.properties.copy()
    properties.update({
        'schema_version': '4',
        'notes': 'Test notes',
        'platform': 'encode:HiSeq 2000',
        'paired_ended': False,
        'read_length': 36,
        'read_length_units': 'nt'
    })
    return properties


@pytest.fixture
def replicate_8_upgrade(root, replicate):
    item = root.get_by_uuid(replicate['uuid'])
    properties = item.properties.copy()
    properties.update({
        'schema_version': '8',
        'status': 'proposed'
    })
    return properties


@pytest.fixture
def software_upgrade(software):
    item = software.copy()
    item.update({
        'schema_version': '1',
    })
    return item

@pytest.fixture
def source_upgrade():
    return{
        'title': 'Fake source',
        'name': "fake-source"
    }


@pytest.fixture
def source_1_upgrade(source_upgrade, lab, submitter, award):
    item = source_upgrade.copy()
    item.update({
        'schema_version': '1',
        'status': 'CURRENT',
        'lab': lab['uuid'],
        'submitted_by': submitter['uuid'],
        'award': award['uuid']
    })
    return item


@pytest.fixture
def source_5_upgrade(source_upgrade, lab, submitter, award):
    item = source_upgrade.copy()
    item.update({
        'schema_version': '5',
        'status': 'current',
        'lab': lab['uuid'],
        'submitted_by': submitter['uuid'],
        'award': award['uuid']
    })
    return item

@pytest.fixture
def star_quality_metric(pipeline, analysis_step_run, bam_file):
    return {
        'status': "finished",
        'pipeline': pipeline['uuid'],
        'step_run': analysis_step_run['uuid'],
        'schema_version': '2',
        'quality_metric_of': [bam_file['uuid']]
    }

@pytest.fixture
def target_upgrade(organism):
    return{
        'organism': organism['uuid'],
        'label': 'TEST'
    }


@pytest.fixture
def target_1_upgrade(target_upgrade):
    item = target_upgrade.copy()
    item.update({
        'schema_version': '1',
        'status': 'CURRENT',
    })
    return item


@pytest.fixture
def target_2_upgrade(target_upgrade):
    item = target_upgrade.copy()
    item.update({
        'schema_version': '2',
    })
    return item


@pytest.fixture
def target_5_upgrade(target_upgrade):
    item = target_upgrade.copy()
    item.update({
        'schema_version': '5',
        'status': 'proposed'
    })
    return item


@pytest.fixture
def target_6_upgrade(target_upgrade):
    item = target_upgrade.copy()
    item.update({
        'schema_version': '6',
        'status': 'current',
        'investigated_as': ['histone modification', 'histone']
    })
    return item


@pytest.fixture
def target_8_no_genes(target_upgrade):
    item = target_upgrade.copy()
    item.update({
        'schema_version': '8',
        'dbxref': [
            'UniProtKB:P04908'
        ]
    })
    return item


@pytest.fixture
def target_8_one_gene(target_8_no_genes):
    item = target_8_no_genes.copy()
    item.update({
        'gene_name': 'HIST1H2AE',
        'dbxref': [
            'GeneID:3012',
            'UniProtKB:P04908'
        ]
    })
    return item


@pytest.fixture
def target_8_two_genes(target_8_one_gene):
    item = target_8_one_gene.copy()
    item.update({
        'gene_name': 'Histone H2A',
        'dbxref': [
            'GeneID:8335',
            'GeneID:3012',
            'UniProtKB:P04908'
        ]
    })
    return item


@pytest.fixture
def target_9_empty_modifications(target_8_one_gene):
    item = {
        'investigated_as': ['other context'],
        'modifications': [],
        'label': 'empty-modifications'
    }
    return item


@pytest.fixture
def target_9_real_modifications(target_8_one_gene):
    item = {
        'investigated_as': ['other context'],
        'modifications': [{'modification': '3xFLAG'}],
        'label': 'empty-modifications'
    }
    return item


@pytest.fixture
def gene3012(testapp, organism):
    item = {
        'dbxrefs': ['HGNC:4724'],
        'organism': organism['uuid'],
        'symbol': 'HIST1H2AE',
        'ncbi_entrez_status': 'live',
        'geneid': '3012',
    }
    return testapp.post_json('/gene', item).json['@graph'][0]


@pytest.fixture
def gene8335(testapp, organism):
    item = {
        'dbxrefs': ['HGNC:4734'],
        'organism': organism['uuid'],
        'symbol': 'HIST1H2AB',
        'ncbi_entrez_status': 'live',
        'geneid': '8335',
    }
    return testapp.post_json('/gene', item).json['@graph'][0]


@pytest.fixture
def target_10_nt_mod(organism):
    item = {
        'investigated_as': ['nucleotide modification'],
        'target_organism': organism['uuid'],
        'label': 'nucleotide-modification-target'
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


def target_10_other_ptm(gene8335):
    item = {
        'investigated_as': [
            'other post-translational modification',
            'chromatin remodeller',
            'RNA binding protein'
        ],
        'genes': [gene8335['uuid']],
        'modifications': [{'modification': 'Phosphorylation'}],
        'label': 'nucleotide-modification-target'
    }
    return item


@pytest.fixture
def target_11_control(human):
    item = {
        'investigated_as': ['control'],
        'target_organism': human['uuid'],
        'label': 'No protein target control'
    }
    return item


@pytest.fixture
def target_12_recombinant(ctcf):
    item = {
        'investigated_as': [
            'recombinant protein',
            'chromatin remodeller',
            'RNA binding protein'
        ],
        'genes': [ctcf['uuid']],
        'modifications': [{'modification': 'eGFP'}],
        'label': 'eGFP-CTCF'
    }
    return item




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
def treatment_upgrade():
    return{
        'treatment_type': 'chemical',
        'treatment_term_name': 'estradiol',
        'treatment_term_id': 'CHEBI:23965'
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
def treatment_1_upgrade(treatment_upgrade, award):
    item = treatment_upgrade.copy()
    item.update({
        'schema_version': '1',
        'encode2_dbxrefs': ['Estradiol_1nM'],
        'award': award['uuid'],
    })
    return item


@pytest.fixture
def treatment_2_upgrade(treatment_upgrade):
    item = treatment_upgrade.copy()
    item.update({
        'schema_version': '2',
        'status': 'CURRENT',
    })
    return item


@pytest.fixture
def treatment_3_upgrade(treatment_upgrade):
    item = treatment_upgrade.copy()
    item.update({
        'schema_version': '3',
        'aliases': ['encode:treatment1', 'encode:treatment1']
    })
    return item


@pytest.fixture
def treatment_4_upgrade(treatment_upgrade, document, antibody_lot):
    item = treatment_upgrade.copy()
    item.update({
        'schema_version': '4',
        'protocols': list(document),
        'antibodies': list(antibody_lot),
        'concentration': 0.25,
        'concentration_units': 'mg/mL'
    })
    return item


@pytest.fixture
def external_accession(fastq_pair_1):
    item = fastq_pair_1.copy()
    item['external_accession'] = 'EXTERNAL'
    return item




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















def treatment_8_upgrade(treatment_upgrade, document):
    item = treatment_upgrade.copy()
    item.update({
        'schema_version': '8',
        'treatment_type': 'protein'
    })
    item['treatment_term_id'] = 'UniprotKB:P03823'
    return item


@pytest.fixture
def treatment_9_upgrade(treatment_upgrade, document):
    item = treatment_upgrade.copy()
    item.update({
        'schema_version': '9',
        'treatment_type': 'protein',
        'status': 'current'
    })
    item['treatment_term_id'] = 'UniprotKB:P03823'
    return item


@pytest.fixture
def treatment_10_upgrade(treatment_upgrade, document, lab):
    item = treatment_upgrade.copy()
    item.update({
        'schema_version': '10',
        'treatment_type': 'protein',
        'status': 'in progress',
        'lab': lab['@id']
    })
    item['treatment_term_id'] = 'UniprotKB:P03823'
    return item

@pytest.fixture
def user():
    return{
        'first_name': 'Benjamin',
        'last_name': 'Hitz',
        'email': 'hitz@stanford.edu',
    }


@pytest.fixture
def user_1(user):
    item = user.copy()
    item.update({
        'schema_version': '2',
        'status': 'CURRENT'
    })
    return item

@pytest.fixture
def user_3(user):
    item = user.copy()
    item.update({
        'schema_version': '3',
        'viewing_groups': ['ENCODE'],
    })
    return item

@pytest.fixture
def user_7(user):
    item = user.copy()
    item.update({
        'schema_version': '6',
        'phone1': '206-685-2672',
        'phone2': '206-267-1098',
        'fax': '206-267-1094',
        'skype': 'fake_id',
        'google': 'google',
        'timezone': 'US/Pacific',
    })
    return item

@pytest.fixture
def user_8(user):
    item = user.copy()
    item.update({
        'schema_version': '8',
        'viewing_groups': ['ENCODE'],
        'groups': ['admin', 'verified', 'wrangler'],
    })
    return item
