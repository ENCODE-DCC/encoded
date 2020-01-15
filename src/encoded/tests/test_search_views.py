import pytest

from encoded.tests.features.conftest import app_settings, app, workbook


def test_search_views_search_view_with_filters(workbook, testapp):
    r = testapp.get(
        '/search/?type=Experiment&award.@id=/awards/ENCODE2-Mouse/&accession=ENCSR000ADI&status=released'
    )
    assert r.json['title'] == 'Search'
    assert len(r.json['@graph']) == 1
    assert r.json['@graph'][0]['accession'] == 'ENCSR000ADI'
    assert r.json['@graph'][0]['status'] == 'released'
    assert 'Experiment' in r.json['@graph'][0]['@type']
    assert len(r.json['facets']) >= 30
    assert r.json['@id'] == '/search/?type=Experiment&award.@id=/awards/ENCODE2-Mouse/&accession=ENCSR000ADI&status=released'
    assert r.json['@context'] == '/terms/'
    assert r.json['@type'] == ['Search']
    assert r.json['total'] == 1
    assert r.json['notification'] == 'Success'
    assert len(r.json['filters']) == 4
    assert r.status_code == 200
    assert r.json['clear_filters'] == '/search/?type=Experiment'
    assert 'debug' not in r.json
    assert 'columns' in r.json
    assert 'sort' in r.json


def test_search_views_search_view_with_limit(workbook, testapp):
    r = testapp.get(
        '/search/?type=Experiment&limit=5'
    )
    assert len(r.json['@graph']) == 5
    assert 'all' in r.json
    r = testapp.get(
        '/search/?type=Experiment&limit=26'
    )
    assert len(r.json['@graph']) == 26
    assert 'all' in r.json
    r = testapp.get(
        '/search/?type=Experiment&limit=all'
    )
    assert len(r.json['@graph']) >= 48
    assert 'all' not in r.json
    r = testapp.get(
        '/search/?type=Experiment&limit=48'
    )
    assert len(r.json['@graph']) == 48
    r = testapp.get(
        '/search/?type=Experiment&limit=100000'
    )
    assert len(r.json['@graph']) >= 48
    assert 'all' not in r.json


def test_search_views_search_view_with_limit_zero(workbook, testapp):
    r = testapp.get(
        '/search/?type=Experiment&limit=0'
    )
    assert len(r.json['@graph']) == 0
    assert 'all' in r.json
    assert r.json['total'] >= 48


def test_search_views_search_view_values(workbook, testapp):
    r = testapp.get(
        '/search/?status=released'
    )
    assert r.json['all'] == '/search/?status=released&limit=all'
    assert r.json['notification'] == 'Success'
    assert r.json['filters'][0] == {'field': 'status', 'remove': '/search/', 'term': 'released'}
    assert r.json['clear_filters'] == '/search/'


def test_search_views_search_view_values_no_results(workbook, testapp):
    r = testapp.get(
        '/search/?status=current&type=Experiment',
        status=404
    )
    assert r.json['notification'] == 'No results found'


def test_search_views_search_view_values_malformed_query_string(workbook, testapp):
    r = testapp.get(
        '/search/?status=current&type=Experiment&status=&format=json',
        status=404
    )
    assert r.json['notification'] == 'No results found'


def test_search_views_search_view_values_bad_type(workbook, testapp):
    r = testapp.get(
        '/search/?status=released&type=Exp',
        status=400
    )
    assert r.json['description'] == "Invalid types: ['Exp']"
    r = testapp.get(
        '/search/?status=released&type=Exp&type=Per',
        status=400
    )
    assert r.json['description'] == "Invalid types: ['Exp', 'Per']"


def test_search_views_search_view_values_item_wildcard(workbook, testapp):
    r = testapp.get(
        '/search/?type=*',
    )
    assert r.json['notification'] == 'Success'
    assert r.json['total'] >= 795


def test_search_views_search_view_values_invalid_search_term(workbook, testapp):
    r = testapp.get(
        '/search/?searchTerm=[',
        status=404
    )


def test_search_views_search_view_values_invalid_advanced_query(workbook, testapp):
    r = testapp.get(
        '/search/?advancedQuery=[',
        status=400
    )
    assert r.json['description'] == 'Invalid query: ([)'


def test_search_views_search_view_embedded_frame(workbook, testapp):
    r = testapp.get(
        '/search/?type=Experiment&frame=embedded'
    )
    assert r.json['@graph'][0]['lab']['name']


def test_search_views_search_view_object_frame(workbook, testapp):
    r = testapp.get(
        '/search/?type=Experiment&frame=object'
    )
    res = r.json['@graph'][0]
    assert all(
        [
            x in res
            for x in ['accession', '@type', '@id', 'status']
        ]
    )

def test_search_views_search_view_debug_query(workbook, testapp):
    r = testapp.get(
        '/search/?type=Experiment&debug=true'
    )
    assert 'debug' in r.json
    assert 'post_filter' in r.json['debug']['raw_query']


def test_search_views_search_view_no_type(workbook, testapp):
    r = testapp.get('/search/')
    assert 'total' in r.json
    assert 'filters' in r.json
    assert len(r.json['filters']) == 0


def test_search_views_search_view_no_type_debug(workbook, testapp):
    r = testapp.get('/search/?debug=true')
    assert not r.json['debug']['raw_query']['post_filter']['bool']


def test_search_views_search_raw_view_raw_response(workbook, testapp):
    r = testapp.get('/searchv2_raw/?type=Experiment')
    assert 'hits' in r.json
    assert 'aggregations' in r.json
    assert '_shards' in r.json
    assert 'timed_out' in r.json
    assert 'took' in r.json


def test_search_views_search_raw_view_raw_response_limit_all(workbook, testapp):
    r = testapp.get('/searchv2_raw/?type=*&limit=all')
    assert 'hits' in r.json
    assert len(r.json['hits']['hits']) > 170


def test_search_views_search_quick_view_limit_all(workbook, testapp):
    r = testapp.get('/searchv2_quick/?type=*&limit=all')
    assert '@graph' in r.json
    assert len(r.json['@graph']) > 170
    assert '@id' in r.json['@graph'][0]
    assert len(r.json.keys()) == 1


def test_search_views_search_quick_view_one_item(workbook, testapp):
    r = testapp.get(
        '/searchv2_quick/?type=Experiment&award.@id=/awards/ENCODE2-Mouse/&accession=ENCSR000ADI&status=released'
    )
    assert len(r.json['@graph']) == 1


def test_search_views_search_quick_view_specify_field(workbook, testapp):
    r = testapp.get('/searchv2_quick/?type=Experiment&field=@id')
    assert '@id' in r.json['@graph'][0]
    assert '@type' in r.json['@graph'][0]
    assert len(r.json['@graph'][0].keys()) == 2


def test_search_generator(workbook, threadlocals, dummy_request):
    from snovault.elasticsearch.searches.parsers import ParamsParser
    from snovault.elasticsearch import ELASTIC_SEARCH
    from elasticsearch import Elasticsearch
    from types import GeneratorType
    dummy_request.environ['QUERY_STRING'] = (
        'type=*&limit=all'
    )
    dummy_request.registry[ELASTIC_SEARCH] = Elasticsearch(port=9201)
    from encoded.search_views import search_generator
    r = search_generator(dummy_request)
    assert '@graph' in r
    assert len(r.keys()) == 1
    assert isinstance(r['@graph'], GeneratorType)
    hits = [dict(h) for h in r['@graph']]
    assert len(hits) > 800
    assert '@id' in hits[0]


def test_search_generator_field_specified(workbook, threadlocals, dummy_request):
    from snovault.elasticsearch.searches.parsers import ParamsParser
    from snovault.elasticsearch import ELASTIC_SEARCH
    from elasticsearch import Elasticsearch
    from types import GeneratorType
    dummy_request.environ['QUERY_STRING'] = (
        'type=Experiment&field=@id&limit=5'
    )
    dummy_request.registry[ELASTIC_SEARCH] = Elasticsearch(port=9201)
    from encoded.search_views import search_generator
    r = search_generator(dummy_request)
    assert '@graph' in r
    assert len(r.keys()) == 1
    assert isinstance(r['@graph'], GeneratorType)
    hits = [dict(h) for h in r['@graph']]
    assert len(hits) == 5
    assert '@id' in hits[0]
    assert len(hits[0].keys()) == 2


def test_search_views_report_view(workbook, testapp):
    r = testapp.get(
        '/report/?type=Experiment&award.@id=/awards/ENCODE2-Mouse/&accession=ENCSR000ADI&status=released'
    )
    assert r.json['title'] == 'Report'
    assert len(r.json['@graph']) == 1
    assert r.json['@graph'][0]['accession'] == 'ENCSR000ADI'
    assert r.json['@graph'][0]['status'] == 'released'
    assert 'Experiment' in r.json['@graph'][0]['@type']
    assert len(r.json['facets']) >= 30
    assert r.json['@id'] == '/report/?type=Experiment&award.@id=/awards/ENCODE2-Mouse/&accession=ENCSR000ADI&status=released'
    assert r.json['@context'] == '/terms/'
    assert r.json['@type'] == ['Report']
    assert r.json['total'] == 1
    assert r.json['notification'] == 'Success'
    assert len(r.json['filters']) == 4
    assert r.status_code == 200
    assert r.json['clear_filters'] == '/report/?type=Experiment'
    assert 'debug' not in r.json
    assert 'columns' in r.json
    assert 'non_sortable' in r.json
    assert 'sort' in r.json


def test_search_views_report_response_with_search_term_type_only_clear_filters(workbook, testapp):
    r = testapp.get('/report/?type=File&searchTerm=bam')
    assert 'clear_filters' in r.json
    assert r.json['clear_filters'] == '/report/?type=File'


def test_search_views_report_view_with_limit(workbook, testapp):
    r = testapp.get(
        '/report/?type=Experiment&limit=5'
    )
    assert len(r.json['@graph']) == 5
    assert 'all' in r.json
    r = testapp.get(
        '/report/?type=Experiment&limit=26'
    )
    assert len(r.json['@graph']) == 26
    assert 'all' in r.json
    r = testapp.get(
        '/report/?type=Experiment&limit=all'
    )
    assert len(r.json['@graph']) >= 48
    assert 'all' not in r.json
    r = testapp.get(
        '/report/?type=Experiment&limit=48'
    )
    assert len(r.json['@graph']) == 48
    r = testapp.get(
        '/report/?type=Experiment&limit=100000'
    )
    assert len(r.json['@graph']) >= 48


def test_search_views_report_view_with_limit_zero(workbook, testapp):
    r = testapp.get(
        '/report/?type=Experiment&limit=0'
    )
    assert len(r.json['@graph']) == 0
    assert 'all' in r.json
    assert r.json['total'] >= 48


def test_search_views_report_view_with_limit_zero_from_zero(workbook, testapp):
    r = testapp.get(
        '/report/?type=Experiment&limit=0&from=0'
    )
    assert len(r.json['@graph']) == 0
    assert 'all' in r.json
    assert r.json['total'] >= 48


def test_search_views_report_view_values_bad_type(workbook, testapp):
    r = testapp.get(
        '/report/?status=released&type=Exp',
        status=400
    )
    assert r.json['description'] == "Invalid types: ['Exp']"
    r = testapp.get(
        '/report/?status=released&type=Exp&type=Per',
        status=400
    )
    assert r.json['description'] == "Report view requires specifying a single type: [('type', 'Exp'), ('type', 'Per')]"


def test_search_views_report_view_values_single_subtype(workbook, testapp):
    r = testapp.get(
        '/report/?status=released&type=Item',
        status=400
    )
    assert 'Report view requires a type with no child types:' in r.json['description']


def test_search_views_report_view_values_no_type(workbook, testapp):
    r = testapp.get(
        '/report/?status=released',
        status=400
    )
    assert r.json['description'] == 'Report view requires specifying a single type: []'


def test_search_views_matrix_raw_view_raw_response(workbook, testapp):
    r = testapp.get('/matrixv2_raw/?type=Experiment')
    assert 'hits' in r.json
    assert r.json['hits']['total'] >= 22
    assert len(r.json['hits']['hits']) == 0
    assert 'aggregations' in r.json
    assert 'x' in r.json['aggregations']
    assert 'y' in r.json['aggregations']
    assert 'assay_title' in r.json['aggregations']['x']
    assert 'biosample_ontology.classification' in r.json['aggregations']['y']
    assert '_shards' in r.json
    assert 'timed_out' in r.json
    assert 'took' in r.json


def test_search_views_matrix_raw_view_no_matrix_defined(workbook, testapp):
    r = testapp.get(
        '/matrixv2_raw/?type=Biosample',
        status=400
    )
    assert r.json['description'] == 'Item type does not have requested view defined: {}'


def test_search_views_matrix_raw_view_invalid_type(workbook, testapp):
    r = testapp.get(
        '/matrixv2_raw/?type=Exp',
        status=400
    )
    assert r.json['description'] == "Invalid types: ['Exp']"


def test_search_views_matrix_raw_view_mutiple_types(workbook, testapp):
    r = testapp.get(
        '/matrixv2_raw/?type=Experiment&type=Experiment',
        status=400
    )
    assert 'Matrix view requires specifying a single type' in r.json['description']


def test_search_views_matrix_raw_view_no_types(workbook, testapp):
    r = testapp.get(
        '/matrixv2_raw/',
        status=400
    )
    assert r.json['description'] == 'Matrix view requires specifying a single type: []'


def test_search_views_matrix_response(workbook, testapp):
    r = testapp.get('/matrix/?type=Experiment')
    assert 'aggregations' not in r.json
    assert 'facets' in r.json
    assert 'total' in r.json
    assert r.json['title'] == 'Matrix'
    assert r.json['@type'] == ['Matrix']
    assert r.json['clear_filters'] == '/matrix/?type=Experiment'
    assert r.json['filters'] == [{'term': 'Experiment', 'remove': '/matrix/', 'field': 'type'}]
    assert r.json['@id'] == '/matrix/?type=Experiment'
    assert r.json['total'] >= 22
    assert r.json['notification'] == 'Success'
    assert r.json['title'] == 'Matrix'
    assert 'facets' in r.json
    assert r.json['@context'] == '/terms/'
    assert 'matrix' in r.json
    assert r.json['matrix']['x']['group_by'] == 'assay_title'
    assert r.json['matrix']['y']['group_by'] == [
        'biosample_ontology.classification',
        'biosample_ontology.term_name'
    ]
    assert 'buckets' in r.json['matrix']['y']['biosample_ontology.classification']
    assert 'key' in r.json['matrix']['y']['biosample_ontology.classification']['buckets'][0]
    assert 'biosample_ontology.term_name' in r.json['matrix']['y']['biosample_ontology.classification']['buckets'][0]
    assert 'search_base' in r.json
    assert r.json['search_base'] == '/search/?type=Experiment'


def test_search_views_matrix_response_with_search_term_type_only_clear_filters(workbook, testapp):
    r = testapp.get('/matrix/?type=Experiment&searchTerm=A549')
    assert 'clear_filters' in r.json
    assert r.json['clear_filters'] == '/matrix/?type=Experiment'


def test_search_views_matrix_response_debug(workbook, testapp):
    r = testapp.get('/matrix/?type=Experiment&debug=true')
    assert 'debug' in r.json


def test_search_views_matrix_response_no_results(workbook, testapp):
    r = testapp.get(
        '/matrix/?type=Experiment&status=no_status',
        status=404
    )
    assert r.json['notification'] == 'No results found'


def test_search_views_summary_response(workbook, testapp):
    r = testapp.get('/summary/?type=Experiment')
    assert 'aggregations' not in r.json
    assert 'total' in r.json
    assert r.json['title'] == 'Summary'
    assert r.json['@type'] == ['Summary']
    assert r.json['clear_filters'] == '/summary/?type=Experiment'
    assert r.json['filters'] == [{'term': 'Experiment', 'remove': '/summary/', 'field': 'type'}]
    assert r.json['@id'] == '/summary/?type=Experiment'
    assert r.json['total'] >= 22
    assert r.json['notification'] == 'Success'
    assert r.json['title'] == 'Summary'
    assert 'facets' in r.json
    assert r.json['@context'] == '/terms/'
    assert 'matrix' in r.json
    assert r.json['matrix']['x']['group_by'] == 'status'
    assert r.json['matrix']['y']['group_by'] == ['replication_type']
    assert 'buckets' in r.json['matrix']['y']['replication_type']
    assert 'key' in r.json['matrix']['y']['replication_type']['buckets'][0]
    assert 'status' in r.json['matrix']['y']['replication_type']['buckets'][0]
    assert 'search_base' in r.json
    assert r.json['search_base'] == '/search/?type=Experiment'


def test_search_views_collection_listing_es_view(workbook, testapp):
    r = testapp.get(
        '/experiments/'
    )
    assert '@graph' in r.json
    assert '@id' in r.json
    assert 'facets' in r.json
    assert 'filters' in r.json
    assert 'all' in r.json
    assert 'columns' in r.json
    assert 'clear_filters' in r.json
    assert r.json['clear_filters'] == '/search/?type=Experiment'
    assert r.json['@type'] == ['ExperimentCollection', 'Collection']
    assert r.json['@context'] == '/terms/'


def test_search_views_collection_listing_es_view_item(workbook, testapp):
    r = testapp.get(
        '/Experiment'
    )
    r = r.follow()
    assert '@graph' in r.json
    assert '@id' in r.json
    assert 'facets' in r.json
    assert 'filters' in r.json
    assert r.json['@type'] == ['ExperimentCollection', 'Collection']
    assert r.json['@context'] == '/terms/'


def test_search_views_collection_listing_db_view(workbook, testapp):
    r = testapp.get(
        '/experiments/?datastore=database'
    )
    assert '@graph' in r.json
    assert '@id' in r.json
    assert 'facets' not in r.json
    assert 'filters' not in r.json
    assert r.json['@type'] == ['ExperimentCollection', 'Collection']
    assert r.json['@context'] == '/terms/'
    assert r.json['description'] == 'Listing of Experiments'


def test_search_views_audit_response(workbook, testapp):
    r = testapp.get('/audit/?type=File')
    assert 'aggregations' not in r.json
    assert 'total' in r.json
    assert r.json['title'] == 'Audit'
    assert r.json['@type'] == ['Audit']
    assert r.json['clear_filters'] == '/audit/?type=File'
    assert r.json['filters'] == [{'term': 'File', 'remove': '/audit/', 'field': 'type'}]
    assert r.json['@id'] == '/audit/?type=File'
    assert r.json['total'] >= 22
    assert r.json['notification'] == 'Success'
    assert 'facets' in r.json
    assert r.json['@context'] == '/terms/'
    assert 'matrix' in r.json
    assert r.json['matrix']['x']['group_by'] == 'file_format'
    assert r.json['matrix']['audit.ERROR.category']
    assert r.json['matrix']['audit.WARNING.category']
    assert r.json['matrix']['audit.NOT_COMPLIANT.category']
    assert r.json['matrix']['audit.INTERNAL_ACTION.category']
    assert 'search_base' in r.json
    assert r.json['search_base'] == '/search/?type=File'


def test_search_views_audit_response_with_search_term_type_only_clear_filters(workbook, testapp):
    r = testapp.get('/audit/?type=File&searchTerm=bam')
    assert 'clear_filters' in r.json
    assert r.json['clear_filters'] == '/audit/?type=File'


def test_search_views_audit_response_debug(workbook, testapp):
    r = testapp.get('/audit/?type=File&debug=true')
    assert 'debug' in r.json


def test_search_views_audit_response_no_results(workbook, testapp):
    r = testapp.get(
        '/audit/?type=File&status=no_status',
        status=404
    )
    assert r.json['notification'] == 'No results found'


def test_search_views_audit_view_no_matrix_defined(workbook, testapp):
    r = testapp.get(
        '/audit/?type=Biosample',
        status=400
    )
    assert r.json['description'] == 'Item type does not have requested view defined: {}'


def test_search_views_reference_epigenome_matrix_response(workbook, testapp):
    r = testapp.get(
        '/reference-epigenome-matrix/'
        '?type=Experiment&related_series.@type=ReferenceEpigenome'
        '&replicates.library.biosample.donor.organism.scientific_name=Mus+musculus'
    )
    assert 'aggregations' not in r.json
    assert 'facets' in r.json
    assert 'total' in r.json
    assert r.json['@type'] == ['ReferenceEpigenomeMatrix']
    assert r.json['@id'] == (
        '/reference-epigenome-matrix/'
        '?type=Experiment&related_series.@type=ReferenceEpigenome'
        '&replicates.library.biosample.donor.organism.scientific_name=Mus+musculus'
    )
    assert r.json['@context'] == '/terms/'
    assert r.json['notification'] == 'Success'
    assert r.json['title'] == 'Reference Epigenome Matrix'
    assert r.json['total'] > 0
    assert 'filters' in r.json
    assert 'matrix' in r.json
    assert r.json['matrix']['x']['group_by'] == ['assay_title', 'target.label']
    assert r.json['matrix']['x']['label'] == 'Assay'
    assert r.json['matrix']['y']['group_by'] == [
        'biosample_ontology.classification',
        'biosample_ontology.term_name'
    ]
    assert r.json['matrix']['y']['label'] == 'Biosample'
    assert len(
        r.json['matrix']['y']['biosample_ontology.classification']['buckets']
    ) > 0
    assert len(
        r.json['matrix']['y']['biosample_ontology.classification']['buckets'][0]['biosample_ontology.term_name']['buckets']
    ) > 0


def test_search_views_entex_matrix_response(workbook, testapp):
    r = testapp.get(
        '/entex-matrix/'
        '?type=Experiment&status=released&internal_tags=ENTEx'
    )
    assert 'aggregations' not in r.json
    assert 'facets' in r.json
    assert 'total' in r.json
    assert r.json['title'] == 'ENTEx Matrix'
    assert r.json['@type'] == ['EntexMatrix']
    assert r.json['@id'] == (
        '/entex-matrix/'
        '?type=Experiment&status=released&internal_tags=ENTEx'
    )
    assert r.json['@context'] == '/terms/'
    assert r.json['notification'] == 'Success'
    assert r.json['title'] == 'ENTEx Matrix'
    assert r.json['total'] >= 4
    assert 'filters' in r.json
    assert 'matrix' in r.json
    assert r.json['matrix']['x']['group_by'] == ['assay_title', ['target.label', 'no_target'], 'replicates.library.biosample.donor.sex', 'replicates.library.biosample.donor.accession']
    assert r.json['matrix']['x']['label'] == 'Assay'
    assert r.json['matrix']['y']['group_by'] == [
        'biosample_ontology.classification',
        'biosample_ontology.term_name'
    ]
    assert r.json['matrix']['y']['label'] == 'Biosample'
    assert 'buckets' in r.json['matrix']['y']['biosample_ontology.classification']
    assert 'key' in r.json['matrix']['y']['biosample_ontology.classification']['buckets'][0]
    assert 'biosample_ontology.term_name' in r.json['matrix']['y']['biosample_ontology.classification']['buckets'][0]
    assert 'search_base' in r.json
    assert r.json['search_base'] == '/search/?type=Experiment&status=released&internal_tags=ENTEx'
    assert len(
        r.json['matrix']['y']['biosample_ontology.classification']['buckets']
    ) > 0
    assert len(
        r.json['matrix']['y']['biosample_ontology.classification']['buckets'][0]['biosample_ontology.term_name']['buckets']
    ) > 0
