# Use workbook fixture from BDD tests (including elasticsearch)
from .features.conftest import app_settings, app, workbook


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
        'replicates.library.biosample.biosample_type', 'biosample_term_name']
    assert res['matrix']['y']['label'] == 'Biosample'
    assert res['matrix']['y']['limit'] == 5
    assert len(res['matrix']['y'][
        'replicates.library.biosample.biosample_type']['buckets']) > 0
    assert len(res['matrix']['y'][
        'replicates.library.biosample.biosample_type']['buckets'][0][
        'biosample_term_name']['buckets']) > 0


# Unit tests


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
    doc_types = ['Experiment']
    aggs = set_facets(facets, used_filters, principals, doc_types)

    assert aggs == {
        'type': {
            'aggs': {
                'type': {
                    'terms': {
                        'field': 'embedded.@type.raw',
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
                        {'terms': {'embedded.@type.raw': ['Experiment']}},
                        {'terms': {'embedded.facet1.raw': ['value1']}},
                        {'terms': {'audit.foo': ['value2']}},
                    ],
                },
            },
        },
        'audit-foo': {
            'aggs': {
                'audit-foo': {
                    'terms': {
                        'field': 'audit.foo',
                        'exclude': [],
                        'min_doc_count': 0,
                        'size': 100,
                    },
                },
            },
            'filter': {
                'bool': {
                    'must': [
                        {'terms': {'principals_allowed.view': ['group.admin']}},
                        {'terms': {'embedded.@type.raw': ['Experiment']}},
                        {'terms': {'embedded.facet1.raw': ['value1']}},
                    ],
                },
            },
        },
        'facet1': {
            'aggs': {
                'facet1': {
                    'terms': {
                        'field': 'embedded.facet1.raw',
                        'exclude': [],
                        'min_doc_count': 0,
                        'size': 100,
                    },
                },
            },
            'filter': {
                'bool': {
                    'must': [
                        {'terms': {'principals_allowed.view': ['group.admin']}},
                        {'terms': {'embedded.@type.raw': ['Experiment']}},
                        {'terms': {'audit.foo': ['value2']}},
                    ],
                },
            },
        }
    }


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
    doc_types = ['Experiment']
    aggs = set_facets(facets, used_filters, principals, doc_types)

    assert aggs == {
        'facet1': {
            'aggs': {
                'facet1': {
                    'terms': {
                        'field': 'embedded.facet1.raw',
                        'exclude': [],
                        'min_doc_count': 0,
                        'size': 100,
                    },
                },
            },
            'filter': {
                'bool': {
                    'must': [
                        {'terms': {'principals_allowed.view': ['group.admin']}},
                        {'terms': {'embedded.@type.raw': ['Experiment']}},
                        {'not': {'terms': {'embedded.field2.raw': ['value1']}}},
                    ],
                },
            },
        }
    }
