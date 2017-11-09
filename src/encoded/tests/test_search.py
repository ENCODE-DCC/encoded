# Use workbook fixture from BDD tests (including elasticsearch)
from .features.conftest import app_settings, app, workbook
from webob.multidict import MultiDict
import pytest


# Integration tests

def test_search_view(workbook, testapp):
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
        'biosample_type']['buckets'][0][
        'biosample_term_name']['buckets']) > 0


# Unit tests

class FakeRequest(object):
    path = '/search/'

    def __init__(self, params):
        self.params = MultiDict(params)


def test_set_filters():
    from encoded.search import set_filters

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
    from encoded.search import set_filters

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
    from encoded.search import set_filters

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
    from encoded.search import set_filters

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
    from encoded.search import set_filters

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
    from encoded.search import set_filters

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
    from encoded.search import set_filters

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
            'bool': {}
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
    from collections import OrderedDict
    from encoded.search import set_facets
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
                        'size': 100,
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
                        'size': 100,
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
                        'size': 100,
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
    assert(expected == aggs)


def test_set_facets_negated_filter():
    from collections import OrderedDict
    from encoded.search import set_facets
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
                        'size': 100,
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
    from collections import OrderedDict
    from encoded.search import set_facets
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
                        {'terms': {'embedded.@type': ['Snowball']}},
                        {'missing': {'field': 'embedded.field2'}},
                    ],
                    'must_not': []
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
    from encoded.search import format_facets
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
    from encoded.search import format_facets
    result = format_facets({}, [], [], [], 0, [])
    assert result == []


def test_format_facets_skips_single_bucket_facets():
    from encoded.search import format_facets
    es_result = {
        'aggregations': {
            'field1': {
                'field1': {
                    'buckets': [
                        {
                            'key': 'value1',
                            'doc_count': 2,
                        },
                    ]
                },
                'doc_count': 2,
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
    from encoded.search import format_facets
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
