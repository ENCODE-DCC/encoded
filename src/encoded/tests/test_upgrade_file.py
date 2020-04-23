import pytest


def test_file_upgrade(upgrader, file_1):
    value = upgrader.upgrade('file', file_1, target_version='2')
    assert value['schema_version'] == '2'
    assert value['status'] == 'current'


def test_file_upgrade2(root, upgrader, file_2, file, threadlocals, dummy_request):
    context = root.get_by_uuid(file['uuid'])
    dummy_request.context = context
    value = upgrader.upgrade('file', file_2, target_version='3', context=context)
    assert value['schema_version'] == '3'
    assert value['status'] == 'in progress'


def test_file_upgrade3(root, upgrader, file_3, file, threadlocals, dummy_request):
    context = root.get_by_uuid(file['uuid'])
    dummy_request.context = context
    value = upgrader.upgrade('file', file_3, target_version='4', context=context)
    assert value['schema_version'] == '4'
    assert value['lab'] != ''
    assert value['award'] != ''
    assert 'download_path' not in value


def test_file_upgrade4(root, upgrader, file_4, file, threadlocals, dummy_request):
    context = root.get_by_uuid(file['uuid'])
    dummy_request.context = context
    content_md5sum = '0123456789abcdef0123456789abcdef'
    fake_registry = {
        'backfill_2683': {file['md5sum']: content_md5sum},
    }
    value = upgrader.upgrade(
        'file', file_4, target_version='5', context=context, registry=fake_registry)
    assert value['schema_version'] == '5'
    assert value['file_format'] == 'bed'
    assert value['file_format_type'] == 'bedMethyl'
    assert value['output_type'] == 'base overlap signal'
    assert value['content_md5sum'] == content_md5sum


def test_file_upgrade5(root, upgrader, registry, file_5, file, threadlocals, dummy_request):
    #context = root.get_by_uuid(file['uuid'])
    #dummy_request.context = context
    value = upgrader.upgrade(
        'file', file_5, current_version='5', target_version='6', registry=registry)
    assert value['schema_version'] == '6'
    assert value['output_type'] == 'signal of all reads'


def test_file_upgrade7(upgrader, file_7):
    value = upgrader.upgrade('file', file_7, current_version='7', target_version='8')
    assert value['schema_version'] == '8'


def test_file_upgrade8(upgrader, file_8a, file_8b):
    value_a = upgrader.upgrade('file', file_8a, current_version='8', target_version='9')
    assert value_a['schema_version'] == '9'
    assert 'assembly' not in value_a

    value_b = upgrader.upgrade('file', file_8b, current_version='8', target_version='9')
    assert value_b['schema_version'] == '9'
    assert 'supersedes' in value_b
    assert 'supercedes' not in value_b


def test_file_upgrade_9_to_10(upgrader, file_9):
    value = upgrader.upgrade('file', file_9, current_version='9', target_version='10')
    assert value['date_created'] == '2017-04-28T00:00:00.000000+00:00'


def test_file_upgrade_10_to_11(upgrader, file_10):
    value = upgrader.upgrade('file', file_10, current_version='10', target_version='11')
    assert value['schema_version'] == '11'
    assert value['no_file_available'] is False


def test_file_upgrade_12_to_13(upgrader, file_12):
    value = upgrader.upgrade('file', file_12, current_version='12', target_version='13')
    assert value['schema_version'] == '13'
    assert 'run_type' not in value


def test_file_upgrade_13_to_14(upgrader, file_13):
    value = upgrader.upgrade('file', file_13, current_version='13', target_version='14')
    assert value['schema_version'] == '14'
    assert value['output_type'] == 'candidate Cis-Regulatory Elements'


def test_file_upgrade_14_to_15(upgrader,
                               file_14_optimal,
                               file_14_conservative,
                               file_14_pseudoreplicated):
    value = upgrader.upgrade(
        'file', file_14_optimal, current_version='14', target_version='15'
    )
    assert value['schema_version'] == '15'
    assert value['output_type'] == 'optimal IDR thresholded peaks'
    value = upgrader.upgrade(
        'file', file_14_conservative, current_version='14', target_version='15'
    )
    assert value['schema_version'] == '15'
    assert value['output_type'] == 'conservative IDR thresholded peaks'
    value = upgrader.upgrade(
        'file',
        file_14_pseudoreplicated,
        current_version='14',
        target_version='15'
    )
    assert value['schema_version'] == '15'
    assert value['output_type'] == 'pseudoreplicated IDR thresholded peaks'


def test_file_upgrade_15_to_16(upgrader, file_15):
    value = upgrader.upgrade('file', file_15, current_version='15', target_version='16')
    assert value['schema_version'] == '16'
    assert 'run_type' not in value
    assert 'read_length' not in value

def test_file_upgrade_16_to_17(upgrader, file_16):
    value = upgrader.upgrade('file', file_16, current_version='16', target_version='17')
    assert value['schema_version'] == '17'
    assert 'run_type' not in value
    assert 'read_length' not in value


def test_file_upgrade_17_to_18(upgrader, file_17):
    value = upgrader.upgrade('file', file_17, current_version='17', target_version='18')
    assert value['schema_version'] == '18'
    assert 'assembly' not in value


def test_file_upgrade_18_to_19(upgrader, file_18):
    value = upgrader.upgrade('file', file_18, current_version='18', target_version='19')
    assert value['schema_version'] == '19'
    assert value['output_type'] == 'representative DNase hypersensitivity sites (rDHSs)'
