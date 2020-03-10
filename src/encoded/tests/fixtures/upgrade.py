import pytest
from ..constants import *



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




# ----- Annotation
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


# ----- biosample
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


# ----- Dataset
@pytest.fixture
def dataset_upgrade_2():
    return {
        'schema_version': '2',
        'aliases': ['ucsc_encode_db:mm9-wgEncodeCaltechTfbs', 'barbara-wold:mouse-TFBS'],
        'geo_dbxrefs': ['GSE36024'],
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


# ----- Experiment
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
def experiment_upgrade_3():
    return {
        'schema_version': '3',
        'status': "DELETED",
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


# ---- treatment
@pytest.fixture
def treatment_upgrade():
    return{
        'treatment_type': 'chemical',
        'treatment_term_name': 'estradiol',
        'treatment_term_id': 'CHEBI:23965'
    }

@pytest.fixture
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

# ----- library
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

# ----- publication
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


# ----- replicate
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


# ----- source
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


# ----- star quality metric
@pytest.fixture
def star_quality_metric(pipeline, analysis_step_run, bam_file):
    return {
        'status': "finished",
        'pipeline': pipeline['uuid'],
        'step_run': analysis_step_run['uuid'],
        'schema_version': '2',
        'quality_metric_of': [bam_file['uuid']]
    }


# ----- steps
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


# ----- target
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
