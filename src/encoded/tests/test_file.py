import pytest


def test_reference_file_by_md5(testapp, file):
    res = testapp.get('/md5:{md5sum}'.format(**file)).follow(status=200)
    assert res.json['@id'] == file['@id']


def test_replaced_file_not_uniqued(testapp, file):
    testapp.patch_json('/{uuid}'.format(**file), {'status': 'replaced'}, status=200)
    testapp.get('/md5:{md5sum}'.format(**file), status=404)


def test_file_post_fastq_no_replicate(testapp, fastq_no_replicate):
    testapp.post_json('/file', fastq_no_replicate, status=422)


def test_file_post_fastq_with_replicate(testapp, fastq):
    testapp.post_json('/file', fastq, status=201)


def test_file_post_mapped_run_type_on_fastq(testapp, mapped_run_type_on_fastq):
    testapp.post_json('/file', mapped_run_type_on_fastq, status=422)


def test_file_post_mapped_run_type_on_bam(testapp, mapped_run_type_on_bam):
    testapp.post_json('/file', mapped_run_type_on_bam, status=201)


def test_file_post_fastq_pair_1_paired_with(testapp, fastq_pair_1_paired_with):
    fastq_pair_1_paired_with['run_type'] = 'paired_ended'
    testapp.post_json('/file', fastq_pair_1_paired_with, status=422)


def test_file_post_fastq_pair_1(testapp, fastq_pair_1):
    testapp.post_json('/file', fastq_pair_1, status=201)


def test_file_post_fastq_pair_2_paired_with(testapp, fastq_pair_1, fastq_pair_2_paired_with):
    testapp.post_json('/file', fastq_pair_1, status=201)
    testapp.post_json('/file', fastq_pair_2_paired_with, status=201)


def test_file_post_fastq_pair_2_paired_with_again(testapp, fastq_pair_1, fastq_pair_2_paired_with):
    testapp.post_json('/file', fastq_pair_1, status=201)
    testapp.post_json('/file', fastq_pair_2_paired_with, status=201)
    item = fastq_pair_2_paired_with.copy()
    item['md5sum'] = '3123456789abcdef0123456789abcdef'
    testapp.post_json('/file', item, status=409)


def test_file_post_fastq_pair_2_no_pair_1(testapp, fastq_pair_2):
    testapp.post_json('/file', fastq_pair_2, status=422)


def test_file_paired_with_back_calculated(testapp, fastq_pair_1, fastq_pair_2_paired_with):
    res = testapp.post_json('/file', fastq_pair_1, status=201)
    location1 = res.json['@graph'][0]['@id']
    res = testapp.post_json('/file', fastq_pair_2_paired_with, status=201)
    location2 = res.json['@graph'][0]['@id']
    res = testapp.get(location1)
    assert res.json['paired_with'] == location2


def test_file_external_accession(testapp, external_accession):
    res = testapp.post_json('/file', external_accession, status=201)
    item = testapp.get(res.location).json
    assert 'accession' not in item
    assert item['@id'] == '/files/EXTERNAL/'

    # Root redirects external accession to canonical path
    response = testapp.get('/EXTERNAL/', status=301)
    assert response.headers['location'].endswith('/files/EXTERNAL/')


def test_file_technical_replicates(testapp, fastq_pair_1):
    res = testapp.post_json('/file', fastq_pair_1, status=201)
    location1 = res.json['@graph'][0]['@id']
    res = testapp.get(location1)
    assert res.json['technical_replicates'] == ['1_1']


def test_file_calculated_assay_term_name(testapp, fastq_pair_1):
    r = testapp.post_json('/file', fastq_pair_1, status=201)
    file_id = r.json['@graph'][0]['@id']
    r = testapp.get(file_id)
    assert r.json['assay_term_name'] == 'RNA-seq'


def test_file_calculated_encylopedia_version(testapp, file_ccre):
    assert file_ccre['encyclopedia_version'] == 'ENCODE v5'


def test_file_calculated_biosample_ontology(testapp, fastq_pair_1):
    r = testapp.post_json('/file', fastq_pair_1, status=201)
    file_id = r.json['@graph'][0]['@id']
    r = testapp.get(file_id + '@@object')
    assert r.json['biosample_ontology'] == '/biosample-types/cell-free_sample_NTR_0000471/'
    r = testapp.get(file_id)
    assert r.json['biosample_ontology']['name'] == 'cell-free_sample_NTR_0000471'


def test_file_calculated_target(testapp, experiment, target_H3K27ac, fastq_pair_1):
    testapp.patch_json(
        experiment['@id'],
        {
            'assay_term_name': 'ChIP-seq',
            'target': target_H3K27ac['@id']
        }
    )
    r = testapp.post_json('/file', fastq_pair_1, status=201)
    file_id = r.json['@graph'][0]['@id']
    r = testapp.get(file_id + '@@object')
    assert r.json['target'] == '/targets/H3K27ac-human/'
    r = testapp.get(file_id)
    assert r.json['target']['label'] == 'H3K27ac'


def test_file_try_to_get_field_from_item_with_skip_calculated_first_is_calculated_field(testapp, fastq_pair_1, dummy_request, threadlocals, mocker):
    from snovault.util import try_to_get_field_from_item_with_skip_calculated_first
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


def test_file_try_to_get_field_from_item_with_skip_calculated_first_is_not_calculated_field(testapp, fastq_pair_1, dummy_request, threadlocals, mocker):
    from snovault.util import try_to_get_field_from_item_with_skip_calculated_first
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


def test_file_ensure_list_and_try_to_get_field_from_item_with_skip_calculated_first(testapp, experiment, target_H3K27ac, fastq_pair_1, dummy_request, threadlocals, mocker):
    from snovault.util import ensure_list_and_filter_none
    from snovault.util import try_to_get_field_from_item_with_skip_calculated_first
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
    value = ensure_list_and_filter_none(
        try_to_get_field_from_item_with_skip_calculated_first(
            dummy_request,
            'target',
            file_id
        )
    )
    assert value == ['/targets/H3K27ac-human/']


def test_file_try_to_get_field_from_item_with_skip_calculated_first_take_one_or_return_none(testapp, experiment, target_H3K27ac, fastq_pair_1, dummy_request, threadlocals, mocker):
    from snovault.util import ensure_list_and_filter_none
    from snovault.util import take_one_or_return_none
    from snovault.util import try_to_get_field_from_item_with_skip_calculated_first
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
        ensure_list_and_filter_none(
            try_to_get_field_from_item_with_skip_calculated_first(
                dummy_request,
                'target',
                file_id
            )
        )
    )
    assert value == '/targets/H3K27ac-human/'
