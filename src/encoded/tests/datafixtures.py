import pytest


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
        'viewing_group': 'ENCODE3',
    }
    return testapp.post_json('/award', item).json['@graph'][0]


@pytest.fixture
def award_modERN(testapp):
    item = {
        'name': 'modERN-award',
        'rfa': 'modERN',
        'project': 'modERN',
        'viewing_group': 'ENCODE3',
    }
    return testapp.post_json('/award', item).json['@graph'][0]


@pytest.fixture
def remc_award(testapp):
    item = {
        'name': 'remc-award',
        'rfa': 'GGR',
        'project': 'GGR',
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
        'viewing_group': 'ENCODE3',
    }
    return testapp.post_json('/award', item).json['@graph'][0]


@pytest.fixture
def source(testapp):
    item = {
        'name': 'sigma',
        'title': 'Sigma-Aldrich',
        'url': 'http://www.sigmaaldrich.com',
    }
    return testapp.post_json('/source', item).json['@graph'][0]


@pytest.fixture
def human(testapp):
    item = {
        'uuid': '7745b647-ff15-4ff3-9ced-b897d4e2983c',
        'name': 'human',
        'scientific_name': 'Homo sapiens',
        'taxon_id': '9606',
    }
    return testapp.post_json('/organism', item).json['@graph'][0]


@pytest.fixture
def mouse(testapp):
    item = {
        'uuid': '3413218c-3d86-498b-a0a2-9a406638e786',
        'name': 'mouse',
        'scientific_name': 'Mus musculus',
        'taxon_id': '10090',
    }
    return testapp.post_json('/organism', item).json['@graph'][0]


@pytest.fixture
def fly(testapp):
    item = {
        'uuid': 'ab546d43-8e2a-4567-8db7-a217e6d6eea0',
        'name': 'dmelanogaster',
        'scientific_name': 'Drosophila melanogaster',
        'taxon_id': '7227',
    }
    return testapp.post_json('/organism', item).json['@graph'][0]


@pytest.fixture
def organism(human):
    return human


@pytest.fixture
def biosample(testapp, source, lab, award, organism):
    item = {
        'biosample_term_id': 'UBERON:349829',
        'biosample_type': 'tissue',
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
def experiment(testapp, lab, award):
    item = {
        'lab': lab['@id'],
        'award': award['@id'],
        'assay_term_name': 'RNA-seq'
    }
    return testapp.post_json('/experiment', item).json['@graph'][0]


@pytest.fixture
def base_experiment(testapp, lab, award):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'assay_term_name': 'RNA-seq',
        'status': 'started'
    }
    return testapp.post_json('/experiment', item, status=201).json['@graph'][0]


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
        'award': award['@id'],
        'status': 'in progress',  # avoid s3 upload codepath
    }
    return testapp.post_json('/file', item).json['@graph'][0]


@pytest.fixture
def fastq_file(testapp, lab, award, experiment, replicate):
    item = {
        'dataset': experiment['@id'],
        'file_format': 'fastq',
        'md5sum': '91be74b6e11515393507f4ebfa66d78b',
        'replicate': replicate['@id'],
        'output_type': 'reads',
        "read_length": 36,
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
        'organism': organism['@id'],
        'investigated_as': ['transcription factor'],
    }
    return testapp.post_json('/target', item).json['@graph'][0]


@pytest.fixture
def target_H3K27ac(testapp, organism):
    item = {
        'label': 'H3K27ac',
        'organism': organism['@id'],
        'investigated_as': ['histone modification',
                            'histone',
                            'narrow histone mark']
    }
    return testapp.post_json('/target', item).json['@graph'][0]


@pytest.fixture
def target_H3K9me3(testapp, organism):
    item = {
        'label': 'H3K9me3',
        'organism': organism['@id'],
        'investigated_as': ['histone modification',
                            'histone',
                            'broad histone mark']
    }
    return testapp.post_json('/target', item).json['@graph'][0]


@pytest.fixture
def target_control(testapp, organism):
    item = {
        'label': 'Control',
        'organism': organism['@id'],
        'investigated_as': ['control']
    }
    return testapp.post_json('/target', item).json['@graph'][0]


@pytest.fixture
def target_promoter(testapp, fly):
    item = {
        'label': 'daf-2',
        'organism': fly['@id'],
        'investigated_as': ['other context']
    }
    return testapp.post_json('/target', item).json['@graph'][0]

RED_DOT = """data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUA
AAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO
9TXL0Y4OHwAAAABJRU5ErkJggg=="""


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
def antibody_approval(testapp, award, lab, target, antibody_lot, antibody_characterization):
    item = {
        'antibody': antibody_lot['@id'],
        'characterizations': [antibody_characterization['@id']],
        'target': target['@id'],
        'award': award['@id'],
        'lab': lab['@id'],
        'status': 'pending dcc review',
    }
    return testapp.post_json('/antibody_approval', item).json['@graph'][0]


@pytest.fixture
def rnai(testapp, lab, award, target):
    item = {
        'target': target['@id'],
        'award': award['@id'],
        'lab': lab['@id'],
        'rnai_sequence': 'TATATGGGGAA',
        'rnai_type': 'shRNA',
    }
    return testapp.post_json('/rnai', item).json['@graph'][0]


@pytest.fixture
def construct(testapp, lab, award, target, source, target_control):
    item = {
        'target': target['@id'],
        'award': award['@id'],
        'lab': lab['@id'],
        'source': source['@id'],
        'construct_type': 'fusion protein',
        'tags': [{'name': 'eGFP', 'location': 'C-terminal'}],
    }
    return testapp.post_json('/construct', item).json['@graph'][0]


@pytest.fixture
def ucsc_browser_composite(testapp, lab, award):
    item = {
        'award': award['@id'],
        'lab': lab['@id'],
    }
    return testapp.post_json('/ucsc_browser_composite', item).json['@graph'][0]


@pytest.fixture
def publication_data(testapp, lab, award):
    item = {
        'award': award['@id'],
        'lab': lab['@id'],
        'references': [],
    }
    return testapp.post_json('/publication_data', item).json['@graph'][0]


@pytest.fixture
def annotation_dataset(testapp, lab, award):
    item = {
        'award': award['@id'],
        'lab': lab['@id']
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
        'assay_term_name': 'RNA-seq'
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
        'name': 'fastqc',
        'title': 'fastqc',
        'input_file_types': ['reads'],
        'analysis_step_types': ['QA calculation'],

    }
    return testapp.post_json('/analysis_step', item).json['@graph'][0]


@pytest.fixture
def analysis_step_version(testapp, analysis_step, software_version):
    item = {
        'analysis_step': analysis_step['@id'],
        'software_versions': [
            software_version['@id'],
        ],
    }
    return testapp.post_json('/analysis_step_version', item).json['@graph'][0]


@pytest.fixture
def analysis_step_run(testapp, analysis_step_version):
    item = {
        'analysis_step_version': analysis_step_version['@id'],
        'status': 'finished',
    }
    return testapp.post_json('/analysis_step_run', item).json['@graph'][0]


@pytest.fixture
def quality_metric(testapp, analysis_step_run, award, lab):
    item = {
        'step_run': analysis_step_run['@id'],
        'award': award['@id'],
        'lab': lab['@id']
    }
    return testapp.post_json('/fastqc_quality_metric', item).json['@graph'][0]


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
def base_biosample(testapp, lab, award, source, organism):
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
        'name': 'bamqc',
        'title': 'bamqc',
        'input_file_types': ['reads'],
        'analysis_step_types': ['QA calculation']
    }
    return testapp.post_json('/analysis_step', item).json['@graph'][0]


@pytest.fixture
def analysis_step_version_bam(testapp, analysis_step_bam, software_version):
    item = {
        'analysis_step': analysis_step_bam['@id'],
        'software_versions': [
            software_version['@id'],
        ],
    }
    return testapp.post_json('/analysis_step_version', item).json['@graph'][0]


@pytest.fixture
def analysis_step_run_bam(testapp, analysis_step_version_bam):
    item = {
        'analysis_step_version': analysis_step_version_bam['@id'],
        'status': 'finished',
        'aliases': ['modern:chip-seq-bwa-alignment-step-run-v-1-virtual']
    }
    return testapp.post_json('/analysis_step_run', item).json['@graph'][0]


@pytest.fixture
def pipeline_bam(testapp, lab, award, analysis_step_bam):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'title': "ChIP-seq read mapping",
        'assay_term_name': 'ChIP-seq',
        'analysis_steps': [analysis_step_bam['@id']]
    }
    return testapp.post_json('/pipeline', item).json['@graph'][0]


@pytest.fixture
def encode_lab(testapp):
    item = {
        'name': 'encode-processing-pipeline',
        'title': 'ENCODE Processing Pipeline',
        'status': 'current'
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
