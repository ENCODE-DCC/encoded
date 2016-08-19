import pytest


@pytest.fixture
def file_bigBed(testapp, lab, award, experiment):
    item = {
        'dataset': experiment['@id'],
        'file_format': 'bigBed',
        'md5sum': 'd41d8cd98f00b204de9800998ecf8427e',
        'output_type': 'replicated peaks',
        'file_format_type': 'bed6',
        'lab': lab['@id'],
        'award': award['@id'],
        'status': 'in progress',  # avoid s3 upload codepath
    }
    return testapp.post_json('/file', item).json['@graph'][0]


@pytest.fixture
def file_bedRnaElements(testapp, lab, award, experiment, replicate):
    item = {
        'dataset': experiment['@id'],
        'file_format': 'bigBed',
        'file_format_type': 'bedRnaElements',
        'md5sum': 'd4s1d8cd9f00b204e9800998ecf8427e',
        'replicate': replicate['@id'],
        'output_type': 'raw signal',
        'lab': lab['@id'],
        'award': award['@id'],
        'status': 'in progress',  # avoid s3 upload codepath
    }
    return testapp.post_json('/file', item).json['@graph'][0]


@pytest.fixture
def file_narrowPeak(testapp, lab, award, experiment):
    item = {
        'dataset': experiment['@id'],
        'file_format': 'bigBed',
        'file_format_type': 'narrowPeak',
        'md5sum': 'd41d8cd9sf00b204e9800998ecf86674427e',
        'output_type': 'peaks',
        'lab': lab['@id'],
        'award': award['@id'],
        'status': 'in progress',  # avoid s3 upload codepath
    }
    return testapp.post_json('/file', item).json['@graph'][0]


@pytest.fixture
def ucsc_composite(testapp, lab, award):
    item = {
        'award': award['@id'],
        'lab': lab['@id'],

    }
    return testapp.post_json('/ucsc_browser_composite', item).json['@graph'][0]


def test_ucsc_composite_released_assembly(testapp,
                                          ucsc_composite,  file_bigBed,
                                          file_bedRnaElements,  file_narrowPeak):
    testapp.patch_json(file_bigBed['@id'], {'status': 'released',
                                            'assembly': 'mm10'})
    testapp.patch_json(file_bedRnaElements['@id'], {'status': 'in progress',
                                                    'assembly': 'hg19'})
    testapp.patch_json(file_narrowPeak['@id'], {'status': 'released',
                                                'assembly': 'mm9'})
    testapp.patch_json(ucsc_composite['@id'], {'related_files': [file_bigBed['@id'],
                                                                 file_bedRnaElements['@id']],
                                               'status': 'released',
                                               'date_released': '2011-10-31'})
    testapp.patch_json(file_narrowPeak['@id'], {'dataset': ucsc_composite['@id']})

    res = testapp.get(ucsc_composite['@id'] + '@@index-data')
    assert sorted(res.json['object']['assembly']) == sorted(['mm10', 'mm9'])


def test_ucsc_composite_not_released_assembly(testapp,
                                              ucsc_composite,
                                              file_bigBed,
                                              file_bedRnaElements,
                                              file_narrowPeak):
    testapp.patch_json(file_bigBed['@id'], {'status': 'released',
                                            'assembly': 'mm10'})
    testapp.patch_json(file_bedRnaElements['@id'], {'status': 'in progress',
                                                    'assembly': 'hg19'})
    testapp.patch_json(file_narrowPeak['@id'], {'status': 'released',
                                                'assembly': 'mm9'})
    testapp.patch_json(ucsc_composite['@id'], {'related_files': [file_bigBed['@id'],
                                                                 file_bedRnaElements['@id']],
                                               'status': 'started'})
    testapp.patch_json(file_narrowPeak['@id'], {'dataset': ucsc_composite['@id']})

    res = testapp.get(ucsc_composite['@id'] + '@@index-data')
    assert sorted(res.json['object']['assembly']) == sorted(['mm10', 'hg19', 'mm9'])
