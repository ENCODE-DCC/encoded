import pytest


@pytest.fixture
def experiment_1(root, experiment, file, file_ucsc_browser_composite):
    item = root.get_by_uuid(experiment['uuid'])
    properties = item.properties.copy()
    assert root.get_by_uuid(file['uuid']).properties['dataset'] == str(item.uuid)
    assert root.get_by_uuid(file_ucsc_browser_composite['uuid']).properties['dataset'] != str(item.uuid)
    properties.update({
        'schema_version': '1',
        'files': [file['uuid'], file_ucsc_browser_composite['uuid']]
    })
    return properties


@pytest.fixture
def experiment_2():
    return {
        'schema_version': '2',
        'encode2_dbxrefs': ['wgEncodeEH002945'],
        'geo_dbxrefs': ['GSM99494'],
    }


@pytest.fixture
def dataset_2():
    return {
        'schema_version': '2',
        'aliases': ['ucsc_encode_db:mm9-wgEncodeCaltechTfbs', 'barbara-wold:mouse-TFBS'],
        'geo_dbxrefs': ['GSE36024'],
    }


@pytest.fixture
def experiment_3():
    return {
        'schema_version': '3',
        'status': "DELETED",
    }


@pytest.fixture
def dataset_3():
    return {
        'schema_version': '3',
        'status': 'CURRENT',
        'award': '2a27a363-6bb5-43cc-99c4-d58bf06d3d8e',
    }


@pytest.fixture
def dataset_5(publication):
    return {
        'schema_version': '5',
        'references': [publication['identifiers'][0]],
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
def annotation_8(award, lab):
    return {
        'award': award['@id'],
        'lab': lab['@id'],
        'schema_version': '8',
        'annotation_type': 'encyclopedia',
        'status': 'released'
    }


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


def test_experiment_upgrade(root, upgrader, experiment, experiment_1, file_ucsc_browser_composite, threadlocals, dummy_request):
    context = root.get_by_uuid(experiment['uuid'])
    dummy_request.context = context
    value = upgrader.upgrade('experiment', experiment_1, current_version='1', target_version='2', context=context)
    assert value['schema_version'] == '2'
    assert 'files' not in value
    assert value['related_files'] == [file_ucsc_browser_composite['uuid']]


def test_experiment_upgrade_dbxrefs(root, upgrader, experiment_2, threadlocals, dummy_request):
    value = upgrader.upgrade('experiment', experiment_2, current_version='2', target_version='3')
    assert value['schema_version'] == '3'
    assert 'encode2_dbxrefs' not in value
    assert 'geo_dbxrefs' not in value
    assert value['dbxrefs'] == ['UCSC-ENCODE-hg19:wgEncodeEH002945', 'GEO:GSM99494']


def test_experiment_upgrade_dbxrefs_mouse(root, upgrader, experiment_2, threadlocals, dummy_request):
    experiment_2['encode2_dbxrefs'] = ['wgEncodeEM008391']
    value = upgrader.upgrade('experiment', experiment_2, current_version='2', target_version='3')
    assert value['schema_version'] == '3'
    assert 'encode2_dbxrefs' not in value
    assert 'geo_dbxrefs' not in value
    assert value['dbxrefs'] == ['UCSC-ENCODE-mm9:wgEncodeEM008391', 'GEO:GSM99494']


def test_dataset_upgrade_dbxrefs(root, upgrader, dataset_2, threadlocals, dummy_request):
    value = upgrader.upgrade('ucsc_browser_composite', dataset_2, current_version='2', target_version='3')
    assert value['schema_version'] == '3'
    assert value['dbxrefs'] == ['GEO:GSE36024', 'UCSC-GB-mm9:wgEncodeCaltechTfbs']
    assert value['aliases'] == ['barbara-wold:mouse-TFBS']
    assert 'geo_dbxrefs' not in value


def test_dataset_upgrade_dbxrefs_human(root, upgrader, dataset_2, threadlocals, dummy_request):
    dataset_2['aliases'] = ['ucsc_encode_db:hg19-wgEncodeSydhTfbs']
    value = upgrader.upgrade('ucsc_browser_composite', dataset_2, current_version='2', target_version='3')
    assert value['schema_version'] == '3'
    assert value['dbxrefs'] == ['GEO:GSE36024', 'UCSC-GB-hg19:wgEncodeSydhTfbs']
    assert value['aliases'] == []
    assert 'geo_dbxrefs' not in value


def test_dataset_upgrade_dbxrefs_alias(root, upgrader, dataset_2, threadlocals, dummy_request):
    dataset_2['aliases'] = ['ucsc_encode_db:wgEncodeEH002945']
    value = upgrader.upgrade('ucsc_browser_composite', dataset_2, current_version='2', target_version='3')
    assert value['schema_version'] == '3'
    assert value['dbxrefs'] == ['GEO:GSE36024', 'UCSC-ENCODE-hg19:wgEncodeEH002945']
    assert value['aliases'] == []
    assert 'geo_dbxrefs' not in value


def test_experiment_upgrade_status(root, upgrader, experiment_3, threadlocals, dummy_request):
    value = upgrader.upgrade('experiment', experiment_3, current_version='2', target_version='4')
    assert value['schema_version'] == '4'
    assert value['status'] == 'deleted'


def test_dataset_upgrade_status(root, upgrader, dataset_3, threadlocals, dummy_request):
    value = upgrader.upgrade('ucsc_browser_composite', dataset_3, current_version='3', target_version='4')
    assert value['schema_version'] == '4'
    assert value['status'] == 'released'


def test_experiment_upgrade_status_encode3(root, upgrader, experiment_3, threadlocals, dummy_request):
    experiment_3['award'] = '529e3e74-3caa-4842-ae64-18c8720e610e'
    experiment_3['status'] = 'CURRENT'
    value = upgrader.upgrade('experiment', experiment_3, current_version='3', target_version='4')
    assert value['schema_version'] == '4'
    assert value['status'] == 'submitted'


def test_dataset_upgrade_no_status_encode2(root, upgrader, dataset_3, threadlocals, dummy_request):
    del dataset_3['status']
    value = upgrader.upgrade('ucsc_browser_composite', dataset_3, current_version='3', target_version='4')
    assert value['schema_version'] == '4'
    assert value['status'] == 'released'


def test_experiment_upgrade_no_status_encode3(root, upgrader, experiment_3, threadlocals, dummy_request):
    experiment_3['award'] = '529e3e74-3caa-4842-ae64-18c8720e610e'
    del experiment_3['status']
    value = upgrader.upgrade('experiment', experiment_3, current_version='3', target_version='4')
    assert value['schema_version'] == '4'
    assert value['status'] == 'submitted'


def test_dataset_upgrade_references(root, upgrader, ucsc_browser_composite, dataset_5, publication, threadlocals, dummy_request):
    context = root.get_by_uuid(ucsc_browser_composite['uuid'])
    dummy_request.context = context
    value = upgrader.upgrade('ucsc_browser_composite', dataset_5, current_version='5', target_version='6', context=context)
    assert value['schema_version'] == '6'
    assert value['references'] == [publication['uuid']]


def test_experiment_upgrade_no_dataset_type(root, upgrader, experiment_6, threadlocals, dummy_request):
    value = upgrader.upgrade('experiment', experiment_6, current_version='6', target_version='7')
    assert value['schema_version'] == '7'
    assert 'dataset_type' not in value


def test_experiment_unique_array(root, upgrader, experiment, experiment_7, dummy_request):
    context = root.get_by_uuid(experiment['uuid'])
    dummy_request.context = context
    value = upgrader.upgrade('experiment', experiment_7, current_version='7', target_version='8')
    assert value['schema_version'] == '8'
    assert len(value['dbxrefs']) == len(set(value['dbxrefs']))
    assert len(value['aliases']) == len(set(value['aliases']))


def test_experiment_upgrade_status_encode3_1(root, upgrader, experiment_3):
    experiment_3['status'] = 'in progress'
    value = upgrader.upgrade('experiment', experiment_3, current_version='8', target_version='9')
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
    value = upgrader.upgrade('experiment', experiment_10, current_version='10', target_version='11')
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
