# Use workbook fixture from BDD tests (including elasticsearch)
import pytest
from encoded.tests.features.conftest import app_settings, app, workbook  # pylint: disable=unused-import


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
    assert res['title'] == 'Matrix'
    assert res['total'] > 0
    assert 'filters' in res
    assert 'matrix' in res
    assert res['matrix']['x']['group_by'] == 'assay_title'
    assert res['matrix']['x']['label'] == 'Assay'
    assert res['matrix']['y']['group_by'] == [
        'biosample_ontology.classification', 'biosample_ontology.term_name']
    assert res['matrix']['y']['label'] == 'Biosample'
    assert len(res['matrix']['y'][
        'biosample_ontology.classification']['buckets']) > 0
    assert len(res['matrix']['y'][
        'biosample_ontology.classification']['buckets'][0]['biosample_ontology.term_name']['buckets']) > 0
