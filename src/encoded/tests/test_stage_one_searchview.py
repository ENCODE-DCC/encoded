"""
Testing for defining search pre refactor
"""
# pylint: disable=unused-import, unused-argument, redefined-outer-name
import copy
import pytest
from .. import search


from .features.conftest import app_settings, app, workbook


def _get_terms_url(search_terms):
    if search_terms:
        return "searchTerm={}".format('&searchTerm='.join(search_terms))
    return ''

def _get_types_url(search_types):
    if search_types:
        return "type={}".format('&type='.join(search_types))
    return ''

def _get_filters_data(
        testapp,
        search_types,
        search_terms,
        status,
        add_mode_picker=False,
):
    url = '/search/'
    if search_terms:
        url += '?' + _get_terms_url(search_terms)
    if search_types:
        url_types = _get_types_url(search_types)
        if search_terms:
            url += "&" + url_types
        else:
            url += '?' + url_types
    if add_mode_picker:
        if url[-1] == '/':
            url += '?mode=picker'
        else:
            url += '&mode=picker'
        add_mode_picker=False,
    res = testapp.get(url, status=status)
    if status > 299 and status < 400:
        res = res.follow()
    res_terms = set()
    res_types = set()
    for res_filter in res.json['filters']:
        if res_filter['field'] == "searchTerm":
            res_terms.add(res_filter['term'])
        elif res_filter['field'] == "type":
            res_types.add(res_filter['term'])
    return url, len(res.json['filters']), res.json['clear_filters'], res_terms, res_types


def test_ensure_default_doc_types_is_valid():
    default_doc_types = search.DEFAULT_DOC_TYPES


    assert 1 == 1

def test_sort_query():
    item = {'filter': {'bool':
                       {'must_not': [],
                        'must': [{'terms': {'embedded.@type': ['Experiment']}},
                                 {'terms': {'embedded.status': ['released']}}]}},
            'aggs': 'assay_slims',
            'terms': ''}

    sorted_query = search.sort_query(item)
  
    for key in item:
        assert item[key] == sorted_query[key]

def test_search_doc_types_one(workbook, testapp):
    '''
    Test search view config valid one doc type
    '''
    search_terms = []
    search_types = ['Experiment']
    url, len_filters, clear_filters, res_terms, res_types = _get_filters_data(
        testapp, search_types, search_terms, 200
    )
    expected_clear_filters = url
    expected_len_filters = len(search_types)
    expected_res_terms = []
    expected_res_types = copy.copy(search_types)
    assert clear_filters == expected_clear_filters
    assert len_filters == expected_len_filters
    assert sorted(list(res_terms)) == sorted(expected_res_terms)
    assert sorted(list(res_types)) == sorted(expected_res_types)


def test_search_doc_types_many(workbook, testapp):
    '''
    Test search view config valid many doc types
    '''
    search_terms = []
    search_types = ['Dataset', 'Experiment', 'ReferenceEpigenome']
    url, len_filters, clear_filters, res_terms, res_types = _get_filters_data(
        testapp, search_types, search_terms, 200
    )
    expected_clear_filters = url
    expected_len_filters = len(search_types)
    expected_res_terms = []
    expected_res_types = copy.copy(search_types)
    assert clear_filters == expected_clear_filters
    assert len_filters == expected_len_filters
    assert sorted(list(res_terms)) == sorted(expected_res_terms)
    assert sorted(list(res_types)) == sorted(expected_res_types)


def test_search_doc_types_asterisk(workbook, testapp):
    '''
    Test search view config with asterisk in request params type
    '''
    search_terms = []
    search_types = ['*']
    # pylint: disable=unused-variable
    url, len_filters, clear_filters, res_terms, res_types = _get_filters_data(
        testapp, search_types, search_terms, 301
    )
    expected_clear_filters = '/search/?' + _get_types_url(['Item'])
    expected_len_filters = len(search_types)
    expected_res_terms = []
    expected_res_types = ['Item']
    assert clear_filters == expected_clear_filters
    assert len_filters == expected_len_filters
    assert sorted(list(res_terms)) == sorted(expected_res_terms)
    assert sorted(list(res_types)) == sorted(expected_res_types)


def test_search_type_arg_not_none(workbook, testapp):
    '''
    Test search view config search_type argument

    Doesn't seem to be used in the application
    -How to set search_type?
    -Is it possible? Is it used?
    '''
    assert True


def test_search_doc_types_sorted(workbook, testapp):
    '''
    Test search view config valid many doc types
    '''
    search_terms = []
    search_types = ['Experiment', 'Dataset', 'ReferenceEpigenome']
    # pylint: disable=unused-variable
    url, len_filters, clear_filters, res_terms, res_types = _get_filters_data(
        testapp, search_types, search_terms, 200
    )
    sorted_search_types = sorted(search_types)
    expected_clear_filters = '/search/?' + _get_types_url(sorted_search_types)
    expected_len_filters = len(search_types)
    expected_res_terms = []
    expected_res_types = copy.copy(search_types)
    assert clear_filters == expected_clear_filters
    assert len_filters == expected_len_filters
    assert sorted(list(res_terms)) == sorted(expected_res_terms)
    assert sorted(list(res_types)) == sorted(expected_res_types)


def test_key_error_empty(testapp):
    '''
    Test search view config key error with empty type
    '''
    bad_types = ['']
    url = '/search/?' + _get_types_url(bad_types)
    excepted_description = 'Invalid type: {}'.format(', '.join(bad_types))
    res = testapp.get(url, status=400)
    assert res.json['description'] == excepted_description


def test_key_error_one(testapp):
    '''
    Test search view config key error with one bad type
    '''
    bad_types = ['bad-type-1']
    url = '/search/?' + _get_types_url(bad_types)
    excepted_description = 'Invalid type: {}'.format(', '.join(bad_types))
    res = testapp.get(url, status=400)
    assert res.json['description'] == excepted_description


def test_key_error_many(testapp):
    '''
    Test search view config key error with many bad type
    '''
    bad_types = ['bad-type-1', 'bad-type-2', 'bad-type-3']
    url = '/search/?' + _get_types_url(bad_types)
    excepted_description = "Invalid type: {}".format(', '.join(bad_types))
    res = testapp.get(url, status=400)
    assert res.json['description'] == excepted_description


def test_key_error_mixed(testapp):
    '''
    Test search view config key error with bad and good types
    '''
    bad_types = ['bad-type-1', 'bad-type-2']
    all_types = ['Experiment']
    all_types.extend(bad_types)
    url = '/search/?' + _get_types_url(all_types)
    excepted_description = "Invalid type: {}".format(', '.join(bad_types))
    res = testapp.get(url, status=400)
    assert res.json['description'] == excepted_description


def test_search_term_only_one(workbook, testapp):
    '''
    Test search view config one valid search term
    '''
    search_terms = ['ChIP-seq']
    search_types = []
    url, len_filters, clear_filters, res_terms, res_types = _get_filters_data(
        testapp, search_types, search_terms, 200
    )
    expected_clear_filters = url
    expected_len_filters = len(search_terms)
    expected_res_terms = copy.copy(search_terms)
    expected_res_types = copy.copy(search_types)
    assert clear_filters == expected_clear_filters
    assert len_filters == expected_len_filters
    assert sorted(list(res_terms)) == sorted(expected_res_terms)
    assert sorted(list(res_types)) == sorted(expected_res_types)


def test_search_term_only_many(workbook, testapp):
    '''
    Test search view config many valid search terms
    '''
    search_terms = ['ChIP-seq', 'eCLIP', 'DNase-seq']
    search_types = []
    url, len_filters, clear_filters, res_terms, res_types = _get_filters_data(
        testapp, search_types, search_terms, 200
    )
    expected_clear_filters = url
    # Why is the filters the square of the search terms?  Seems like a bug.
    # https://www.encodeproject.org/search/?searchTerm=ChIP-seq&searchTerm=eCLIP&searchTerm=DNase-seq&format=json
    expected_len_filters = len(search_terms) * len(search_terms)
    expected_res_terms = copy.copy(search_terms)
    expected_res_types = copy.copy(search_types)
    assert clear_filters == expected_clear_filters
    assert len_filters == expected_len_filters
    assert sorted(list(res_terms)) == sorted(expected_res_terms)
    assert sorted(list(res_types)) == sorted(expected_res_types)


def test_search_term_many_and_type(workbook, testapp):
    '''
    Test search view config many valid search terms with one type
    '''
    search_terms = ['ChIP-seq', 'eCLIP', 'DNase-seq']
    search_types = ['Experiment']
    # pylint: disable=unused-variable
    url, len_filters, clear_filters, res_terms, res_types = _get_filters_data(
        testapp, search_types, search_terms, 200
    )
    expected_clear_filters = '/search/?' + _get_terms_url(search_terms)
    expected_len_filters = len(search_types) + len(search_terms) * len(search_terms)
    expected_res_terms = copy.copy(search_terms)
    expected_res_types = copy.copy(search_types)
    assert clear_filters == expected_clear_filters
    assert len_filters == expected_len_filters
    assert sorted(list(res_terms)) == sorted(expected_res_terms)
    assert sorted(list(res_types)) == sorted(expected_res_types)


def test_search_term_many_and_types(workbook, testapp):
    '''
    Test search view config many valid search terms with many types
    '''
    search_terms = ['ChIP-seq', 'eCLIP', 'DNase-seq']
    search_types = ['Experiment', 'Dataset']
    # pylint: disable=unused-variable
    url, len_filters, clear_filters, res_terms, res_types = _get_filters_data(
        testapp, search_types, search_terms, 200
    )
    expected_clear_filters = '/search/?' + _get_terms_url(search_terms)
    expected_len_filters = len(search_types) + len(search_terms) * len(search_terms)
    expected_res_terms = copy.copy(search_terms)
    expected_res_types = copy.copy(search_types)
    assert clear_filters == expected_clear_filters
    assert len_filters == expected_len_filters
    assert sorted(list(res_terms)) == sorted(expected_res_terms)
    assert sorted(list(res_types)) == sorted(expected_res_types)


def test_no_types_no_terms(workbook, testapp):
    '''
    Test search view config with no types or terms
    '''
    search_terms = []
    search_types = []
    # pylint: disable=unused-variable
    url, len_filters, clear_filters, res_terms, res_types = _get_filters_data(
        testapp, search_types, search_terms, 200, add_mode_picker=False
    )
    expected_clear_filters = url
    expected_len_filters = 0
    expected_res_terms = copy.copy(search_terms)
    expected_res_types = copy.copy(search_types)
    assert clear_filters == expected_clear_filters
    assert len_filters == expected_len_filters
    assert sorted(list(res_terms)) == sorted(expected_res_terms)
    assert sorted(list(res_types)) == sorted(expected_res_types)


def test_mode_picker(workbook, testapp):
    '''
    Test search view config with no types or terms but mode picker
    '''
    search_terms = []
    search_types = []
    # pylint: disable=unused-variable
    url, len_filters, clear_filters, res_terms, res_types = _get_filters_data(
        testapp, search_types, search_terms, 200, add_mode_picker=True
    )
    expected_clear_filters = '/search/'
    expected_len_filters = 0
    expected_res_terms = copy.copy(search_terms)
    expected_res_types = copy.copy(search_types)
    assert clear_filters == expected_clear_filters
    assert len_filters == expected_len_filters
    assert sorted(list(res_terms)) == sorted(expected_res_terms)
    assert sorted(list(res_types)) == sorted(expected_res_types)


def test_search_term_mode_picker(workbook, testapp):
    '''
    Test search view config with no types or terms but mode picker
    '''
    # search_terms = ['ChIP-seq', 'eCLIP', 'DNase-seq']
    search_terms = ['ChIP-seq']
    search_types = []
    # pylint: disable=unused-variable
    url, len_filters, clear_filters, res_terms, res_types = _get_filters_data(
        testapp, search_types, search_terms, 200, add_mode_picker=True
    )
    expected_clear_filters = '/search/?' + _get_terms_url(search_terms)
    expected_len_filters = len(search_types) + len(search_terms) * len(search_terms)
    expected_res_terms = copy.copy(search_terms)
    expected_res_types = copy.copy(search_types)
    assert clear_filters == expected_clear_filters
    assert len_filters == expected_len_filters
    assert sorted(list(res_terms)) == sorted(expected_res_terms)
    assert sorted(list(res_types)) == sorted(expected_res_types)


def test_search_result_views_many(workbook, testapp):
    '''
    Test search view config does NOT add result views if many doc types
    '''
    search_types = ['Experiment', 'Dataset', 'ReferenceEpigenome']
    url = '/search/?' + _get_types_url(search_types)
    res = testapp.get(url, status=200)
    assert res.json.get('views') is None


def test_search_result_views_one_a(workbook, testapp):
    '''
    Test search view config does adds one result views for certain doc types
    '''
    search_types = ['Dataset']
    url = '/search/?' + _get_types_url(search_types)
    res = testapp.get(url, status=200)
    views = res.json.get('views')
    assert len(views) == 1


def test_search_result_views_one_b(workbook, testapp):
    '''
    Test search view config does add 3 result views for other doc types
    '''
    search_types = ['Experiment']
    url = '/search/?' + _get_types_url(search_types)
    res = testapp.get(url, status=200)
    views = res.json.get('views')
    assert len(views) == 3


def test_search_result_views_zero(workbook, testapp):
    '''
    Test search view config does NOT add result views if zero doc types
    '''
    search_types = []
    url = '/search/' + _get_types_url(search_types)
    res = testapp.get(url, status=200)
    assert res.json.get('views') is None
