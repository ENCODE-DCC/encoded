import pytest


@pytest.fixture
def file_no_replicate(experiment, award, lab):
    return {
        'dataset': experiment['uuid'],
        'lab': lab['uuid'],
        'award': award['uuid'],
        'file_format': 'bam',
        'md5sum': 'e002cd204df36d93dd070ef0712b8eed',
        'output_type': 'alignments'
    }


@pytest.fixture
def file_with_replicate(file_no_replicate, replicate):
    item = file_no_replicate.copy()
    item.update({
        'replicate': replicate['uuid'],
        'uuid': '46e82a90-49e6-4c33-afab-9ac90d89faf3'
    })
    return item


@pytest.fixture
def file_with_derived(file_no_replicate, file_with_replicate):
    item = file_no_replicate.copy()
    item.update({
        'derived_from': [file_with_replicate['uuid']]
    })
    return item


#def test_file_post(testapp, file_no_replicate):
#    testapp.post_json('/file', file_no_replicate)


#def test_file_with_replicate_post(testapp, file_with_replicate):
#    testapp.post_json('/file', file_with_replicate)


#def test_file_with_derived_from_post(testapp, file_with_derived):
#    testapp.post_json('/file', file_with_derived)
