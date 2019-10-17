import pytest


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


def test_types_utils_ensure_list():
    from encoded.types.utils import ensure_list
    assert ensure_list('abc') == ['abc']
    assert ensure_list(['abc']) == ['abc']
    assert ensure_list({'a': 'b'}) == [{'a': 'b'}]
    assert ensure_list([{'a': 'b'}, {'c': 'd'}]) == [{'a': 'b'}, {'c': 'd'}]


def test_types_utils_take_one_or_return_none():
    from encoded.types.utils import take_one_or_return_none
    assert take_one_or_return_none(['just one']) == 'just one'
    assert take_one_or_return_none(['one', 'and', 'two']) is None
    assert take_one_or_return_none('just one') is None


def test_types_utils_try_to_get_field_from_item_with_skip_calculated_first_is_calculated_field(testapp, fastq_pair_1, dummy_request, threadlocals, mocker):
    from encoded.types.utils import try_to_get_field_from_item_with_skip_calculated_first
    mocker.spy(dummy_request, 'embed')
    r = testapp.post_json('/file', fastq_pair_1, status=201)
    file_id = r.json['@graph'][0]['@id']
    r = testapp.get(file_id + '@@object?skip_calculated=true')
    assert 'assay_term_name' not in r.json
    assay_term_name = try_to_get_field_from_item_with_skip_calculated_first(
        dummy_request,
        'assay_term_name',
        file_id
    )
    assert assay_term_name == 'RNA-seq'
    # Multiple calls if calculated property.
    assert dummy_request.embed.call_count == 2


def test_types_utils_try_to_get_field_from_item_with_skip_calculated_first_is_not_calculated_field(testapp, fastq_pair_1, dummy_request, threadlocals, mocker):
    from encoded.types.utils import try_to_get_field_from_item_with_skip_calculated_first
    mocker.spy(dummy_request, 'embed')
    r = testapp.post_json('/file', fastq_pair_1, status=201)
    file_id = r.json['@graph'][0]['@id']
    status = try_to_get_field_from_item_with_skip_calculated_first(
        dummy_request,
        'status',
        file_id
    )
    assert status == 'in progress'
    # One call if not calculated property.
    assert dummy_request.embed.call_count == 1


def test_types_utils_ensure_list_and_try_to_get_field_from_item_with_skip_calculated_first(testapp, experiment, target_H3K27ac, fastq_pair_1, dummy_request, threadlocals, mocker):
    from encoded.types.utils import ensure_list
    from encoded.types.utils import try_to_get_field_from_item_with_skip_calculated_first
    mocker.spy(dummy_request, 'embed')
    testapp.patch_json(
        experiment['@id'],
        {
            'assay_term_name': 'ChIP-seq',
            'target': target_H3K27ac['@id']
        }
    )
    r = testapp.post_json('/file', fastq_pair_1, status=201)
    file_id = r.json['@graph'][0]['@id']
    value = ensure_list(
        try_to_get_field_from_item_with_skip_calculated_first(
            dummy_request,
            'target',
            file_id
        )
    )
    assert value == ['/targets/H3K27ac-human/']


def test_types_utils_try_to_get_field_from_item_with_skip_calculated_first_take_one_or_return_none(testapp, experiment, target_H3K27ac, fastq_pair_1, dummy_request, threadlocals, mocker):
    from encoded.types.utils import ensure_list
    from encoded.types.utils import take_one_or_return_none
    from encoded.types.utils import try_to_get_field_from_item_with_skip_calculated_first
    mocker.spy(dummy_request, 'embed')
    testapp.patch_json(
        experiment['@id'],
        {
            'assay_term_name': 'ChIP-seq',
            'target': target_H3K27ac['@id']
        }
    )
    r = testapp.post_json('/file', fastq_pair_1, status=201)
    file_id = r.json['@graph'][0]['@id']
    value = take_one_or_return_none(
        ensure_list(
            try_to_get_field_from_item_with_skip_calculated_first(
                dummy_request,
                'target',
                file_id
            )
        )
    )
    assert value == '/targets/H3K27ac-human/'
