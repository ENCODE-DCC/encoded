# Use workbook fixture from BDD tests (including elasticsearch)
from collections import OrderedDict
from webob.multidict import MultiDict
import pytest
from encoded.tests.features.conftest import app_settings, app, workbook
from snovault import TYPES
from snovault.helpers.helper import (
    set_filters,
    set_facets,
    format_facets,
    sort_query,
    get_pagination,
    prepare_search_term,
    set_sort_order,
    get_search_fields,
    list_visible_columns_for_schemas,
    list_result_fields,
    build_terms_filter,
    build_aggregation,
    normalize_query
)


class FakeRequest(object):
    path = '/search/'

    def __init__(self, params):
        self.params = MultiDict(params)
        self.permissions = {}

    def set_permission(self, perm_key, perm_value=False):
        self.permissions[perm_key] = perm_value

    def has_permission(self, perm_key):
        if perm_key in self.permissions and self.permissions[perm_key] is True:
            return True
        return False


@pytest.fixture
def sort_query_items():
    return [
        (
            {'d': 'val', 'c': 'val', 'b': 'val', 'a': 'val'},
            OrderedDict([('a', 'val'), ('b', 'val'), ('c', 'val'), ('d', 'val')])
        ),
        (
            {'d': {'b': 'val', 'a': 'val'}},
            OrderedDict([('d', OrderedDict([('a', 'val'), ('b', 'val')]))])
        )
    ]


@pytest.fixture
def get_pagination_item():
    requests = [
        (FakeRequest((('from', '0'), ('limit', '25'))), ('0', 25)),
        (FakeRequest((('from', '10'), ('limit', '50'))), ('10', 50)),
        (FakeRequest((('from', '0'),)), ('0', 25)),
        (FakeRequest((('limit', '50'),)), (0, 50)),
        (FakeRequest((('limit', ''),)), (0, None)),
        (FakeRequest((('limit', 'all'),)), (0, None)),
        (FakeRequest((('key', 'value'),)), (0, 25))
    ]
    return requests


@pytest.fixture
def prepare_search_term_item():
    requests = [
        (FakeRequest(((''),)), '*'),
        (FakeRequest((('searchTerm', ''),)), '*'),
        (FakeRequest((('searchTerm', 'chip'),)), 'chip'),
        (FakeRequest((('searchTerm', '/assay/'),)), '\\/assay\\/'),
        (FakeRequest((('searchTerm', '@type:field'),)), 'embedded.@type:field'),
        (FakeRequest((('searchTerm', 'type:s'),)), 'type\:s'),
        (FakeRequest((('searchTerm', ' '),)), '*'),
        (FakeRequest((('searchTerm', '@type'),)), '@type')
    ]
    return requests


@pytest.fixture
def set_sort_order_item():
    requests = [
        (FakeRequest((('type', 'Experiment'), ('sort', 'assay_title'))), ('*', True)),
        (FakeRequest((('type', 'Experiment'), ('sort', '-assay_title'))), ('*', True)),
        (FakeRequest((('type', 'Experiment'), ('sort', None))), ('*', True),),
        (FakeRequest((('type', 'Experiment'), ('sort', None))), ('search', False)),
        (FakeRequest((('type', 'Experiment'), ('sort', '-accession'))), ('search', True))
    ]
    return requests


@pytest.fixture
def list_visible_columns_item():
    requests = [
        FakeRequest((('type', 'Experiment'), ('field', '@id'))),
        FakeRequest((('type', 'Experiment'), ('field', 'assay_title'))),
        FakeRequest((('type', 'Experiment'), ('field', '@id'), ('field', 'assay_title'))),
        FakeRequest((('type', 'Experiment'), ('field', ' '))),
        FakeRequest((('type', 'Experiment'), ('field', 'random'))),
        FakeRequest((('type', 'Experiment'),))
    ]
    return requests


@pytest.fixture
def list_result_fields_item():
    requests = [
        (FakeRequest((('type', 'Experiment'),)), {}),
        (FakeRequest((('type', 'Experiment'), ('frame', 'object'))), ['object.*']),
        (FakeRequest((('type', 'Experiment'), ('frame', 'embedded'))), ['embedded.*']),
        (FakeRequest((('type', 'Experiment'), ('frame', 'random'))), {}),
        (FakeRequest((('type', 'Experiment'), ('field', '@id'))),
         {'embedded.@id', 'embedded.@type'}),
        (FakeRequest((('type', 'Experiment'), ('field', 'assay_title'), ('frame', 'embedded'))),
         {'embedded.@id', 'embedded.assay_title', 'embedded.@type'})
    ]
    return requests


@pytest.fixture
def build_terms_filter_item():
    return {
        ('status', 'released'): {'must_not': [], 'must': [{'terms': {'embedded.status': ['released']}}]},
        ('status!', 'archived'): {'must_not': [{'terms': {'embedded.status': ['archived']}}], 'must': []},
        ('status', '*'): {'must': [{'exists': {'field': 'embedded.status'}}], 'must_not': []},
        ('status!', '*'): {'must': [], 'must_not': [{'exists': {'field': 'embedded.status'}}]}
    }


@pytest.fixture
def build_aggregation_item():
    arguments = [('replication_type', {'title': 'Replication types'}),
                 ('type', {'title': 'Replication'}),
                 ('audit', {'audit': 'value'}),
                 ('replic_type', {'type': 'exists'})]

    validate = [{'terms': {'field': 'embedded.replication_type',
                           'min_doc_count': 0,
                           'size': 200}},
                {'terms': {'field': 'embedded.@type',
                           'exclude': ['Item'],
                           'min_doc_count': 0,
                           'size': 200}},
                {'terms': {'field': 'audit',
                           'min_doc_count': 0,
                           'size': 200}},
                {'filters': {'filters': {'no':
                                         {'bool':
                                          {'must_not': {'exists': {'field':
                                                                   'embedded.replic_type'}}}},
                                         'yes':
                                         {'bool':
                                          {'must': {'exists': {'field':
                                                               'embedded.replic_type'}}}}}}}]

    return (arguments, validate)


@pytest.fixture
def normalize_query_item():
    requests = {FakeRequest((('type', 'Experiment'),)): '?type=Experiment',
                FakeRequest((('', ''),)): '?=',
                FakeRequest((('key', 'value'),)): '?key=value',
                FakeRequest((('key1', 'value1'), ('key2', 'value2'))): '?key1=value1&key2=value2'}
    return requests


def test_search_view(workbook, testapp):
    # pylint: disable=redefined-outer-name, unused-argument
    res = testapp.get('/search/').json
    assert res['@type'] == ['Search']
    assert res['@id'] == '/search/'
    assert res['@context'] == '/terms/'
    assert res['notification'] == 'Success'
    assert res['title'] == 'Search'
    assert res['total'] > 0
    assert 'facets' in res
    assert 'filters' in res
    assert 'columns' in res
    assert '@graph' in res


def test_report_view(workbook, testapp):
    # pylint: disable=redefined-outer-name, unused-argument
    res = testapp.get('/report/?type=Experiment').json
    assert res['@type'] == ['Report']
    assert res['@id'] == '/report/?type=Experiment'
    assert res['@context'] == '/terms/'
    assert res['notification'] == 'Success'
    assert res['title'] == 'Report'
    assert res['total'] > 0
    assert 'facets' in res
    assert 'filters' in res
    assert 'columns' in res
    assert '@graph' in res


def test_matrix_view(workbook, testapp):
    # pylint: disable=redefined-outer-name, unused-argument
    res = testapp.get('/matrix/?type=Experiment').json
    assert res['@type'] == ['Matrix']
    assert res['@id'] == '/matrix/?type=Experiment'
    assert res['@context'] == '/terms/'
    assert res['notification'] == 'Success'
    assert res['title'] == 'Experiment Matrix'
    assert res['total'] > 0
    assert 'facets' in res
    assert 'filters' in res
    assert 'matrix' in res
    assert res['matrix']['max_cell_doc_count'] > 0
    assert res['matrix']['search_base'] == '/search/?type=Experiment'
    assert res['matrix']['x']['group_by'] == 'assay_title'
    assert res['matrix']['x']['label'] == 'Assay'
    assert res['matrix']['x']['limit'] == 20
    assert len(res['matrix']['x']['buckets']) > 0
    assert len(res['matrix']['x']['facets']) > 0
    assert res['matrix']['y']['group_by'] == [
        'biosample_type', 'biosample_term_name']
    assert res['matrix']['y']['label'] == 'Biosample'
    assert res['matrix']['y']['limit'] == 5
    assert len(res['matrix']['y'][
        'biosample_type']['buckets']) > 0
    assert len(res['matrix']['y'][
        'biosample_type']['buckets'][0]['biosample_term_name']['buckets']) > 0


def test_set_filters():
    request = FakeRequest((
        ('field1', 'value1'),
    ))
    query = {
        'query': {
            'query_string': {}
        },
        'post_filter': {
            'bool': {
                'must': [],
                'must_not': []
            }
        }
    }
    result = {'filters': []}
    used_filters = set_filters(request, query, result)

    assert used_filters == {'field1': ['value1']}
    assert query == {
        'query': {
            'query_string': {}
        },
        'post_filter': {
            'bool': {
                'must': [
                    {
                        'terms': {
                            'embedded.field1': ['value1'],
                        },
                    },
                ],
                'must_not': []
            }
        }
    }
    assert result == {
        'filters': [
            {
                'field': 'field1',
                'term': 'value1',
                'remove': '/search/?'
            }
        ]
    }


def test_set_filters_searchTerm():
    request = FakeRequest((
        ('searchTerm', 'value1'),
    ))
    query = {
        'query': {
            'query_string': {}
        },
        'post_filter': {
            'bool': {
                'must': [],
                'must_not': []
            }
        }
    }
    result = {'filters': []}
    used_filters = set_filters(request, query, result)

    assert used_filters == {}
    assert query == {
        'query': {
            'query_string': {}
        },
        'post_filter': {
            'bool': {
                'must': [],
                'must_not': []
            }
        }
    }
    assert result == {
        'filters': [
            {
                'field': 'searchTerm',
                'term': 'value1',
                'remove': '/search/?'
            }
        ]
    }


# Reserved params should NOT act as filters
@pytest.mark.parametrize('param', [
    'type', 'limit', 'mode',
    'format', 'frame', 'datastore', 'field', 'sort', 'from', 'referrer'])
def test_set_filters_reserved_params(param):

    request = FakeRequest((
        (param, 'foo'),
    ))
    query = {
        'query': {
            'query_string': {}
        },
        'post_filter': {
            'bool': {
                'must': [],
                'must_not': []
            }
        }
    }
    result = {'filters': []}
    used_filters = set_filters(request, query, result)

    assert used_filters == {}
    assert query == {
        'query': {
            'query_string': {}
        },
        'post_filter': {
            'bool': {
                'must': [],
                'must_not': []
            }
        }
    }
    assert result == {
        'filters': [],
    }


def test_set_filters_multivalued():
    request = FakeRequest((
        ('field1', 'value1'),
        ('field1', 'value2'),
    ))
    query = {
        'query': {
            'query_string': {}
        },
        'post_filter': {
            'bool': {
                'must': [],
                'must_not': []
            }
        }
    }
    result = {'filters': []}
    used_filters = set_filters(request, query, result)

    assert used_filters == {'field1': ['value1', 'value2']}
    assert query == {
        'query': {
            'query_string': {}
        },
        'post_filter': {
            'bool': {
                'must': [
                    {
                        'terms': {
                            'embedded.field1': ['value1', 'value2']
                        }
                    }
                ],
                'must_not': []
            }
        }
    }
    assert result == {
        'filters': [
            {
                'field': 'field1',
                'term': 'value1',
                'remove': '/search/?field1=value2'
            },
            {
                'field': 'field1',
                'term': 'value2',
                'remove': '/search/?field1=value1'
            }
        ]
    }


def test_set_filters_negated():
    request = FakeRequest((
        ('field1!', 'value1'),
    ))
    query = {
        'query': {
            'query_string': {}
        },
        'post_filter': {
            'bool': {
                'must': [],
                'must_not': []
            }
        }
    }
    result = {'filters': []}
    used_filters = set_filters(request, query, result)

    assert used_filters == {'field1!': ['value1']}
    assert query == {
        'query': {
            'query_string': {}
        },
        'post_filter': {
            'bool': {
                'must_not': [
                    {
                        'terms': {
                            'embedded.field1': ['value1']
                        }
                    }
                ],
                'must': []
            }
        }
    }
    assert result == {
        'filters': [
            {
                'field': 'field1!',
                'term': 'value1',
                'remove': '/search/?'
            },
        ],
    }


def test_set_filters_audit():
    request = FakeRequest((
        ('audit.foo', 'value1'),
    ))
    query = {
        'query': {
            'query_string': {}
        },
        'post_filter': {
            'bool': {
                'must': [],
                'must_not': []
            }
        }
    }
    result = {'filters': []}
    used_filters = set_filters(request, query, result)

    assert used_filters == {'audit.foo': ['value1']}
    assert query == {
        'query': {
            'query_string': {}
        },
        'post_filter': {
            'bool': {
                'must': [
                    {
                        'terms': {
                            'audit.foo': ['value1']
                        },
                    },
                ],
                'must_not': []
            }
        }
    }
    assert result == {
        'filters': [
            {
                'field': 'audit.foo',
                'term': 'value1',
                'remove': '/search/?'
            },
        ],
    }


def test_set_filters_exists_missing():

    request = FakeRequest((
        ('field1', '*'),
        ('field2!', '*'),
    ))
    query = {
        'query': {
            'query_string': {}
        },
        'post_filter': {
            'bool': {
                'must': [],
                'must_not': []
            }
        }
    }
    result = {'filters': []}
    used_filters = set_filters(request, query, result)

    assert used_filters == {
        'field1': ['*'],
        'field2!': ['*'],
    }

    assert query == {
        'query': {
            'query_string': {}
        },
        'post_filter': {
            'bool': {
                'must': [
                    {
                        'exists': {
                            'field': 'embedded.field1'
                        }
                    },
                ],
                'must_not': [
                    {
                        'exists': {
                            'field': 'embedded.field2'
                        }
                    }

                ]
            }
        }
    }

    assert result == {
        'filters': [
            {
                'field': 'field1',
                'term': '*',
                'remove': '/search/?field2%21=%2A',
            },
            {
                'field': 'field2!',
                'term': '*',
                'remove': '/search/?field1=%2A',
            }
        ],
    }


def test_set_facets():
    facets = [
        ('type', {'title': 'Type'}),
        ('audit.foo', {'title': 'Audit'}),
        ('facet1', {'title': 'Facet 1'}),
    ]
    used_filters = OrderedDict((
        ('facet1', ['value1']),
        ('audit.foo', ['value2']),
    ))
    principals = ['group.admin']
    doc_types = ['Snowball']
    aggs = set_facets(facets, used_filters, principals, doc_types)

    expected = {
        'type': {
            'aggs': {
                'type': {
                    'terms': {
                        'field': 'embedded.@type',
                        'exclude': ['Item'],
                        'min_doc_count': 0,
                        'size': 200,
                    },
                },
            },
            'filter': {
                'bool': {
                    'must': [
                        {'terms': {'principals_allowed.view': ['group.admin']}},
                        {'terms': {'embedded.@type': ['Snowball']}},
                        {'terms': {'embedded.facet1': ['value1']}},
                        {'terms': {'audit.foo': ['value2']}},
                    ],
                    'must_not': []
                },
            },
        },
        'audit-foo': {
            'aggs': {
                'audit-foo': {
                    'terms': {
                        'field': 'audit.foo',
                        'min_doc_count': 0,
                        'size': 200,
                    },
                },
            },
            'filter': {
                'bool': {
                    'must': [
                        {'terms': {'principals_allowed.view': ['group.admin']}},
                        {'terms': {'embedded.@type': ['Snowball']}},
                        {'terms': {'embedded.facet1': ['value1']}},
                    ],
                    'must_not': []
                },
            },
        },
        'facet1': {
            'aggs': {
                'facet1': {
                    'terms': {
                        'field': 'embedded.facet1',
                        'min_doc_count': 0,
                        'size': 200,
                    },
                },
            },
            'filter': {
                'bool': {
                    'must': [
                        {'terms': {'principals_allowed.view': ['group.admin']}},
                        {'terms': {'embedded.@type': ['Snowball']}},
                        {'terms': {'audit.foo': ['value2']}},
                    ],
                    'must_not': []
                },
            },
        }
    }
    assert expected == aggs


def test_set_facets_negated_filter():
    facets = [
        ('facet1', {'title': 'Facet 1'}),
    ]
    used_filters = OrderedDict((
        ('field2!', ['value1']),
    ))
    principals = ['group.admin']
    doc_types = ['Snowball']
    aggs = set_facets(facets, used_filters, principals, doc_types)

    assert {
        'facet1': {
            'aggs': {
                'facet1': {
                    'terms': {
                        'field': 'embedded.facet1',
                        'min_doc_count': 0,
                        'size': 200,
                    },
                },
            },
            'filter': {
                'bool': {
                    'must': [
                        {'terms': {'principals_allowed.view': ['group.admin']}},
                        {'terms': {'embedded.@type': ['Snowball']}}
                    ],
                    'must_not': [
                        {'terms': {'embedded.field2': ['value1']}}
                    ],
                },
            },
        }
    } == aggs


def test_set_facets_type_exists():
    facets = [
        ('field1', {'title': 'Facet 1', 'type': 'exists'}),
        ('field2', {'title': 'Facet 2', 'type': 'exists'}),
    ]
    used_filters = OrderedDict((
        ('field1', ['*']),
        ('field2!', ['*']),
    ))
    principals = ['group.admin']
    doc_types = ['Snowball']
    aggs = set_facets(facets, used_filters, principals, doc_types)

    assert {
        'field1': {
            'aggs': {
                'field1': {
                    'filters': {
                        'filters': {
                            'yes': {
                                'bool': {
                                    'must': {
                                        'exists': {'field': 'embedded.field1'}
                                    }
                                }
                            },
                            'no': {
                                'bool': {
                                    'must_not': {
                                        'exists': {'field': 'embedded.field1'}
                                    }
                                }
                            }
                        },
                    },
                },
            },
            'filter': {
                'bool': {
                    'must': [
                        {'terms': {'principals_allowed.view': ['group.admin']}},
                        {'terms': {'embedded.@type': ['Snowball']}}
                    ],
                    'must_not': [
                        {'exists': {'field': 'embedded.field2'}}
                    ]
                },
            },
        },
        'field2': {
            'aggs': {
                'field2': {
                    'filters': {
                        'filters': {
                            'yes': {
                                'bool': {
                                    'must': {
                                        'exists': {'field': 'embedded.field2'}
                                    }
                                }
                            },
                            'no': {
                                'bool': {
                                    'must_not': {
                                        'exists': {'field': 'embedded.field2'}
                                    }
                                }
                            }
                        },
                    },
                },
            },
            'filter': {
                'bool': {
                    'must': [
                        {'terms': {'principals_allowed.view': ['group.admin']}},
                        {'terms': {'embedded.@type': ['Snowball']}},
                        {'exists': {'field': 'embedded.field1'}},
                    ],
                    'must_not': []
                },
            },
        },
    } == aggs


def test_format_facets():
    es_result = {
        'aggregations': {
            'field1': {
                'field1': {
                    'buckets': [
                        {
                            'key': 'value1',
                            'doc_count': 2,
                        },
                        {
                            'key': 'value2',
                            'doc_count': 1,
                        }
                    ]
                },
                'doc_count': 3,
            }
        }
    }
    facets = [
        ('field1', {'title': 'Field 1'}),
    ]
    used_filters = {}
    schemas = []
    total = 42
    principals = []
    result = format_facets(
        es_result, facets, used_filters, schemas, total, principals)

    assert result == [{
        'field': 'field1',
        'title': 'Field 1',
        'terms': [
            {
                'key': 'value1',
                'doc_count': 2,
            },
            {
                'key': 'value2',
                'doc_count': 1,
            }
        ],
        'total': 3,
        'type': 'terms',
    }]


def test_format_facets_no_aggregations():
    result = format_facets({}, [], [], [], 0, [])
    assert result == []


def test_format_facets_skips_zero_bucket_facets():
    es_result = {
        'aggregations': {
            'field1': {
                'field1': {
                    'buckets': [
                        {
                            'key': 'value1',
                            'doc_count': 0,
                        },
                    ]
                },
                'doc_count': 0,
            }
        }
    }
    facets = [
        ('field1', {'title': 'Field 1'}),
    ]
    used_filters = {}
    schemas = []
    total = 42
    principals = []
    result = format_facets(
        es_result, facets, used_filters, schemas, total, principals)

    assert result == []


def test_format_facets_adds_pseudo_facet_for_extra_filters():
    es_result = {
        'aggregations': {},
    }
    facets = []
    used_filters = {
        'title': ['titlevalue'],
    }
    schemas = [{
        'properties': {
            'title': {
                'title': 'Title',
            },
        },
    }]
    total = 42
    principals = []
    result = format_facets(
        es_result, facets, used_filters, schemas, total, principals)

    assert result == [{
        'field': 'title',
        'title': 'Title',
        'terms': [
            {
                'key': 'titlevalue',
            },
        ],
        'total': 42,
    }]


def test_sort_query(sort_query_items):
    # pylint: disable=redefined-outer-name, unused-argument
    for test_item, test_result_item in sort_query_items:
        sorted_query = sort_query(test_item)
        assert isinstance(sorted_query, OrderedDict)
        assert test_result_item == sorted_query


def test_get_pagination(get_pagination_item):
    # pylint: disable=redefined-outer-name, unused-argument
    for request, validate in get_pagination_item:
        from_, size = get_pagination(request)
        assert from_ == validate[0]
        assert size == validate[1]


def test_prepare_search_term(prepare_search_term_item):
    # pylint: disable=redefined-outer-name, unused-argument
    for request, validate in prepare_search_term_item:
        search_term = prepare_search_term(request)
        assert search_term == validate


def test_set_sort_order(set_sort_order_item):
    # pylint: disable=redefined-outer-name, unused-argument
    doc_types = ['Experiment']
    types = {'Experiment': FakeRequest((('key', 'value'),))}
    types['Experiment'].schema = {}
    types['Experiment'].schema['sort_by'] = {'sort': {'sort': 'asc'}}
    query = {}
    result = {}
    for request, inputs in set_sort_order_item:
        search_term = inputs[0]
        validate = inputs[1]
        res = set_sort_order(request,
                             search_term,
                             types,
                             doc_types,
                             query,
                             result)
        assert res == validate


def test_get_search_fields(registry):
    # pylint: disable=redefined-outer-name, unused-argument
    request = FakeRequest((('key', 'value'),))
    request.registry = registry
    doc_type = ['Experiment']
    fields, highlights = get_search_fields(request, doc_type)
    assert isinstance(highlights, dict)
    assert isinstance(fields, list)


def test_list_visible_columns_for_schemas(list_visible_columns_item, registry):
    # pylint: disable=redefined-outer-name, unused-argument
    types = registry[TYPES]
    doc_types = ['Experiment']
    schemas = [types[doc_type].schema for doc_type in doc_types]
    for request in list_visible_columns_item:
        columns = list_visible_columns_for_schemas(request, schemas)
        for param, value in request.params.items():
            if param != 'type':
                assert value in columns
        assert isinstance(columns, dict)


def test_list_result_fields(list_result_fields_item, registry):
    # pylint: disable=redefined-outer-name, unused-argument
    doc_types = ['Experiment']
    for request, validate in list_result_fields_item:
        request.set_permission('search_audit')
        request.registry = registry
        request.__parent__ = None

        fields = list_result_fields(request, doc_types)
        assert (isinstance(fields, dict) or
                isinstance(fields, list) or
                isinstance(fields, set))
        if validate:
            assert fields == validate
        else:
            assert len(fields) > 1


def test_build_terms_filter(build_terms_filter_item):
    # pylint: disable=redefined-outer-name, unused-argument
    for key, value in build_terms_filter_item.items():
        query_filters = {'must': [],
                         'must_not': []}
        build_terms_filter(query_filters, key[0], [key[1]])
        assert query_filters == value


def test_build_aggregation(build_aggregation_item):
    # pylint: disable=redefined-outer-name, unused-argument
    args = build_aggregation_item[0]
    validate = build_aggregation_item[1]
    for index, arg in enumerate(args):
        actual = validate[index]
        agg_name, agg = build_aggregation(arg[0], arg[1])
        assert agg == actual


def test_normalize_query(normalize_query_item, registry):
    # pylint: disable=redefined-outer-name, unused-argument
    for request, validate in normalize_query_item.items():
        request.registry = registry
        query = normalize_query(request)
        assert query == validate
