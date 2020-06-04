import pytest


def test_experiment_upgrade(root, upgrader, experiment, experiment_1_0, file_ucsc_browser_composite, threadlocals, dummy_request):
    context = root.get_by_uuid(experiment['uuid'])
    dummy_request.context = context
    value = upgrader.upgrade('experiment', experiment_1_0,
                             current_version='1', target_version='2', context=context)
    assert value['schema_version'] == '2'
    assert 'files' not in value
    assert value['related_files'] == [file_ucsc_browser_composite['uuid']]


def test_experiment_upgrade_dbxrefs(root, upgrader, experiment_2_0, threadlocals, dummy_request):
    value = upgrader.upgrade('experiment', experiment_2_0,
                             current_version='2', target_version='3')
    assert value['schema_version'] == '3'
    assert 'encode2_dbxrefs' not in value
    assert 'geo_dbxrefs' not in value
    assert value['dbxrefs'] == [
        'UCSC-ENCODE-hg19:wgEncodeEH002945', 'GEO:GSM99494']


def test_experiment_upgrade_dbxrefs_mouse(root, upgrader, experiment_2_0, threadlocals, dummy_request):
    experiment_2_0['encode2_dbxrefs'] = ['wgEncodeEM008391']
    value = upgrader.upgrade('experiment', experiment_2_0,
                             current_version='2', target_version='3')
    assert value['schema_version'] == '3'
    assert 'encode2_dbxrefs' not in value
    assert 'geo_dbxrefs' not in value
    assert value['dbxrefs'] == [
        'UCSC-ENCODE-mm9:wgEncodeEM008391', 'GEO:GSM99494']


def test_dataset_upgrade_dbxrefs(root, upgrader, dataset_2, threadlocals, dummy_request):
    value = upgrader.upgrade('ucsc_browser_composite',
                             dataset_2, current_version='2', target_version='3')
    assert value['schema_version'] == '3'
    assert value['dbxrefs'] == ['GEO:GSE36024',
                                'UCSC-GB-mm9:wgEncodeCaltechTfbs']
    assert value['aliases'] == ['barbara-wold:mouse-TFBS']
    assert 'geo_dbxrefs' not in value


def test_dataset_upgrade_dbxrefs_human(root, upgrader, dataset_2, threadlocals, dummy_request):
    dataset_2['aliases'] = ['ucsc_encode_db:hg19-wgEncodeSydhTfbs']
    value = upgrader.upgrade('ucsc_browser_composite',
                             dataset_2, current_version='2', target_version='3')
    assert value['schema_version'] == '3'
    assert value['dbxrefs'] == [
        'GEO:GSE36024', 'UCSC-GB-hg19:wgEncodeSydhTfbs']
    assert value['aliases'] == []
    assert 'geo_dbxrefs' not in value


def test_dataset_upgrade_dbxrefs_alias(root, upgrader, dataset_2, threadlocals, dummy_request):
    dataset_2['aliases'] = ['ucsc_encode_db:wgEncodeEH002945']
    value = upgrader.upgrade('ucsc_browser_composite',
                             dataset_2, current_version='2', target_version='3')
    assert value['schema_version'] == '3'
    assert value['dbxrefs'] == ['GEO:GSE36024',
                                'UCSC-ENCODE-hg19:wgEncodeEH002945']
    assert value['aliases'] == []
    assert 'geo_dbxrefs' not in value


def test_experiment_upgrade_status(root, upgrader, experiment_3, threadlocals, dummy_request):
    value = upgrader.upgrade('experiment', experiment_3,
                             current_version='2', target_version='4')
    assert value['schema_version'] == '4'
    assert value['status'] == 'deleted'


def test_dataset_upgrade_status(root, upgrader, dataset_3, threadlocals, dummy_request):
    value = upgrader.upgrade('ucsc_browser_composite',
                             dataset_3, current_version='3', target_version='4')
    assert value['schema_version'] == '4'
    assert value['status'] == 'released'


def test_experiment_upgrade_status_encode3(root, upgrader, experiment_3, threadlocals, dummy_request):
    experiment_3['award'] = '529e3e74-3caa-4842-ae64-18c8720e610e'
    experiment_3['status'] = 'CURRENT'
    value = upgrader.upgrade('experiment', experiment_3,
                             current_version='3', target_version='4')
    assert value['schema_version'] == '4'
    assert value['status'] == 'submitted'


def test_dataset_upgrade_no_status_encode2(root, upgrader, dataset_3, threadlocals, dummy_request):
    del dataset_3['status']
    value = upgrader.upgrade('ucsc_browser_composite',
                             dataset_3, current_version='3', target_version='4')
    assert value['schema_version'] == '4'
    assert value['status'] == 'released'


def test_experiment_upgrade_no_status_encode3(root, upgrader, experiment_3, threadlocals, dummy_request):
    experiment_3['award'] = '529e3e74-3caa-4842-ae64-18c8720e610e'
    del experiment_3['status']
    value = upgrader.upgrade('experiment', experiment_3,
                             current_version='3', target_version='4')
    assert value['schema_version'] == '4'
    assert value['status'] == 'submitted'


def test_dataset_upgrade_references(root, upgrader, ucsc_browser_composite, dataset_5, publication, threadlocals, dummy_request):
    context = root.get_by_uuid(ucsc_browser_composite['uuid'])
    dummy_request.context = context
    value = upgrader.upgrade('ucsc_browser_composite', dataset_5,
                             current_version='5', target_version='6', context=context)
    assert value['schema_version'] == '6'
    assert value['references'] == [publication['uuid']]


def test_experiment_upgrade_no_dataset_type(root, upgrader, experiment_6, threadlocals, dummy_request):
    value = upgrader.upgrade('experiment', experiment_6,
                             current_version='6', target_version='7')
    assert value['schema_version'] == '7'
    assert 'dataset_type' not in value


def test_experiment_unique_array(root, upgrader, experiment, experiment_7, dummy_request):
    context = root.get_by_uuid(experiment['uuid'])
    dummy_request.context = context
    value = upgrader.upgrade('experiment', experiment_7,
                             current_version='7', target_version='8')
    assert value['schema_version'] == '8'
    assert len(value['dbxrefs']) == len(set(value['dbxrefs']))
    assert len(value['aliases']) == len(set(value['aliases']))


def test_experiment_upgrade_status_encode3_1(root, upgrader, experiment_3):
    experiment_3['status'] = 'in progress'
    value = upgrader.upgrade('experiment', experiment_3,
                             current_version='8', target_version='9')
    assert value['schema_version'] == '9'
    assert value['status'] == 'started'


def test_annotation_upgrade_1(registry, annotation_8):
    from snovault import UPGRADER
    upgrader = registry[UPGRADER]
    value = upgrader.upgrade('annotation',
                             annotation_8, registry=registry,
                             current_version='8', target_version='9')
    assert value['annotation_type'] == 'other'


def test_bad_dataset_alias_upgrade_10_11(root, upgrader, experiment_10):
    value = upgrader.upgrade('experiment', experiment_10,
                             current_version='10', target_version='11')
    assert value['schema_version'] == '11'
    assert 'andrew-fire:my_experiment' in value['aliases']
    assert \
        'j-michael-cherry:Lib_XZ_20100107_11--ChIP_XZ_20100104_09_AdiposeNuclei_H3K4Me3' in \
        value['aliases']
    assert \
        'roadmap-epigenomics:Bisulfite-Seq analysis of ucsf-4* stem cell line from UCSF-4_Apr-16-2013_85822' \
        in value['aliases']
    assert 'encode:(this is)_quite_bad' in value['aliases']
    assert 'manuel-garber:10pct DMSO for 2 hours' in value['aliases']
    assert 'encode:Illumina_HiSeq_2000' in value['aliases']
    assert 'UCSC_encode_db:Illumina_HiSeq_2000' not in value['aliases']
    for alias in value['aliases']:
        assert len(alias.split(':')) == 2


def test_anotation_upgrade_12_13(root, upgrader, annotation_12):
    value = upgrader.upgrade('annotation',
                             annotation_12,
                             current_version='12', target_version='13')
    assert value['schema_version'] == '13'
    assert value['annotation_type'] == 'candidate regulatory elements'


def test_experiment_upgrade_status_13_14(root, upgrader, experiment_13):
    value = upgrader.upgrade('experiment', experiment_13,
                             current_version='13', target_version='14')
    assert value['schema_version'] == '14'
    assert value['status'] == 'started'


def test_anotation_upgrade_status_14_15(root, upgrader, annotation_14):
    value = upgrader.upgrade('annotation',
                             annotation_14,
                             current_version='14', target_version='15')
    assert value['schema_version'] == '15'
    assert value['status'] == 'started'


def test_upgrade_annotation_15_16(upgrader, annotation_dataset):
    annotation_dataset['annotation_type'] = 'enhancer-like regions'
    value = upgrader.upgrade('annotation', annotation_dataset,
                             current_version='15', target_version='16')
    assert annotation_dataset['annotation_type'] == 'candidate regulatory elements'
    annotation_dataset['annotation_type'] = 'promoter-like regions'
    value = upgrader.upgrade('annotation', annotation_dataset,
                             current_version='15', target_version='16')
    assert annotation_dataset['annotation_type'] == 'candidate regulatory elements'
    annotation_dataset['annotation_type'] = 'DNase master peaks'
    value = upgrader.upgrade('annotation', annotation_dataset,
                             current_version='15', target_version='16')
    assert annotation_dataset['annotation_type'] == 'representative DNase hypersensitivity sites'


def test_upgrade_experiment_14_15(upgrader, experiment_14):
    value = upgrader.upgrade('experiment', experiment_14,
                             current_version='14', target_version='15')
    assert value['schema_version'] == '15'
    assert value['biosample_type'] == 'cell-free sample'
    assert value['biosample_term_name'] == 'none'
    assert value['biosample_term_id'] == 'NTR:0000471'


def test_upgrade_experiment_15_to_16(upgrader, experiment_15):
    value = upgrader.upgrade('experiment', experiment_15, current_version='15', target_version='16')
    assert value['schema_version'] == '16'
    assert value['biosample_type'] == 'cell line'


def test_upgrade_annotation_16_to_17(upgrader, annotation_16):
    value = upgrader.upgrade('annotation', annotation_16, current_version='16', target_version='17')
    assert value['schema_version'] == '17'
    assert value['biosample_type'] == 'cell line'


def test_upgrade_experiment_16_17(upgrader, experiment_16):
    assert experiment_16['schema_version'] == '16'
    assert experiment_16['status'] == 'ready for review'
    value = upgrader.upgrade('experiment', experiment_16, current_version='16', target_version='17')
    assert value['schema_version'] == '17'
    assert value['status'] == 'submitted'


def test_upgrade_experiment_17_18(upgrader, experiment_17):
    assert experiment_17['schema_version'] == '17'
    assert experiment_17['status'] == 'started'
    value = upgrader.upgrade('experiment', experiment_17, current_version='17', target_version='18')
    assert value['schema_version'] == '18'
    assert value['status'] == 'in progress'


def test_upgrade_annotation_17_to_18(upgrader, annotation_17):
    value = upgrader.upgrade('annotation', annotation_17, current_version='17', target_version='18')
    assert value['schema_version'] == '18'


def test_upgrade_experiment_21_to_22(upgrader, experiment_21):
    assert experiment_21['schema_version'] == '21'
    value = upgrader.upgrade('experiment', experiment_21, current_version='21', target_version='22')
    assert value['schema_version'] == '22'
    assert value['biosample_type'] == 'cell line'


def test_upgrade_annotation_19_to_20(upgrader, annotation_19):
    assert annotation_19['schema_version'] == '19'
    value = upgrader.upgrade('annotation', annotation_19, current_version='19', target_version='20')
    assert value['schema_version'] == '20'
    assert value['biosample_type'] == 'primary cell'


def test_upgrade_experiment_22_to_23(root, upgrader, experiment_22, erythroblast):
    value = upgrader.upgrade(
        'experiment', experiment_22, current_version='22', target_version='23',
        context=root.get_by_uuid(erythroblast['uuid'])
    )
    assert value['biosample_ontology'] == erythroblast['uuid']


def test_upgrade_annotation_20_to_21(root, upgrader, annotation_20, erythroblast):
    value = upgrader.upgrade(
        'annotation', annotation_20, current_version='20', target_version='21',
        context=root.get_by_uuid(erythroblast['uuid'])
    )
    assert value['biosample_ontology'] == erythroblast['uuid']


def test_upgrade_experiment_23_to_24(root, upgrader, experiment_22):
    value = upgrader.upgrade(
        'experiment', experiment_22, current_version='23', target_version='24'
    )
    assert value['internal_tags'] == ['ccre_inputv1', 'ccre_inputv2', 'ENCYCLOPEDIAv3']


def test_upgrade_annotation_21_to_22(root, upgrader, annotation_20):
    value = upgrader.upgrade(
        'annotation', annotation_20, current_version='21', target_version='22'
    )
    assert value['internal_tags'] == ['ccre_inputv1', 'ccre_inputv2', 'ENCYCLOPEDIAv3']


def test_upgrade_experiment_24_to_25(upgrader, experiment_22):
    value = upgrader.upgrade(
        'experiment', experiment_22, current_version='24', target_version='25'
    )
    assert 'biosample_type' not in value
    assert 'biosample_term_id' not in value
    assert 'biosample_term_name' not in value


def test_upgrade_annotation_22_to_23(upgrader, annotation_20):
    value = upgrader.upgrade(
        'annotation', annotation_20, current_version='22', target_version='23'
    )
    assert 'biosample_type' not in value
    assert 'biosample_term_id' not in value
    assert 'biosample_term_name' not in value


def test_upgrade_annotation_23_to_24(upgrader, annotation_20):
    value = upgrader.upgrade(
        'annotation', annotation_20, current_version='23', target_version='24'
    )
    assert 'annotation_type' in value


def test_upgrade_experiment_25_to_26(upgrader, experiment_25):
    assert experiment_25['schema_version'] == '25'
    value = upgrader.upgrade('experiment', experiment_25, current_version='25', target_version='26')
    assert value['schema_version'] == '26'
    assert value['assay_term_name'] == 'long read RNA-seq'


def test_upgrade_annotation_24_to_25(upgrader, annotation_21):
    value = upgrader.upgrade(
        'annotation', annotation_21, current_version='24', target_version='25'
    )
    assert value['schema_version'] == '25'
    assert value['annotation_type'] == 'candidate Cis-Regulatory Elements'


def test_upgrade_experiment_26_to_27(upgrader, experiment_26):
    assert experiment_26['schema_version'] == '26'
    value = upgrader.upgrade('experiment', experiment_26, current_version='26', target_version='27')
    assert value['schema_version'] == '27'
    assert value['assay_term_name'] == 'single-nucleus ATAC-seq'
    experiment_26['schema_version'] = '26'
    experiment_26['assay_term_name'] = 'HiC'
    value = upgrader.upgrade('experiment', experiment_26, current_version='26', target_version='27')
    assert value['schema_version'] == '27'
    assert value['assay_term_name'] == 'HiC'

def test_upgrade_experiment_27_to_28(upgrader, experiment_27):
    assert experiment_27['schema_version'] == '27'
    assert experiment_27['experiment_classification'] == ['functional genomics assay']
    value = upgrader.upgrade('experiment', experiment_27, current_version='27', target_version='28')
    assert experiment_27['schema_version'] == '28'
    assert 'experiment_classification' not in value


def test_upgrade_annotation_25_to_26(upgrader, annotation_25):
    value = upgrader.upgrade(
        'annotation', annotation_25, current_version='25', target_version='26'
    )
    assert value['schema_version'] == '26'
    assert value['encyclopedia_version'] == 'ENCODE v1'


def test_upgrade_annotation_26_to_27(upgrader, annotation_26):
    value = upgrader.upgrade(
        'annotation', annotation_26, current_version='26', target_version='27'
    )
    assert value['schema_version'] == '27'
    assert value['dbxrefs'] == ['IHEC:IHECRE00000998']


def test_upgrade_reference_epigenome_16_to_17(upgrader, reference_epigenome_16):
    value = upgrader.upgrade(
        'reference_epigenome',
        reference_epigenome_16,
        current_version='16',
        target_version='17'
    )
    assert value['schema_version'] == '17'
    assert value['dbxrefs'] == ['IHEC:IHECRE00004643']


def test_upgrade_reference_17_to_18(upgrader, dataset_reference_1, dataset_reference_2):
    value = upgrader.upgrade(
        'reference', dataset_reference_1, current_version='17', target_version='18'
    )
    assert value['schema_version'] == '18'
    assert value['dbxrefs'] == ['UCSC-ENCODE-hg19:wgEncodeEH000325']
    value = upgrader.upgrade(
        'reference', dataset_reference_2, current_version='17', target_version='18'
    )
    assert value['schema_version'] == '18'
    assert 'dbxrefs' not in value
    assert 'IHEC:IHECRE00004703' in value['notes']


def test_upgrade_annotation_27_to_28(upgrader, annotation_27):
    value = upgrader.upgrade(
        'annotation', annotation_27, current_version='27', target_version='28'
    )
    assert value['schema_version'] == '28'
    assert value['annotation_type'] == 'representative DNase hypersensitivity sites (rDHSs)'


def test_upgrade_reference_18_to_19(upgrader, upgrade_18_19_reference):
    upgrade_18_19_reference['examined_loci'] = []
    print(upgrade_18_19_reference['examined_loci'])
    value = upgrader.upgrade(
        'reference', upgrade_18_19_reference, current_version='18', target_version='19')
    assert value['schema_version'] == '19'
    assert 'examined_loci' not in value


def test_upgrade_annotation_27_to_28(upgrader, annotation_28):
    value = upgrader.upgrade(
        'annotation', annotation_28, current_version='28', target_version='29'
    )
    assert value['notes'] == 'Lorem ipsum. Removed timepoint metadata: 3 stage'
    assert 'relevant_timepoint' not in value
    assert 'relevant_timepoint_units' not in value
