# Use fixtures from features, indexing workbook
import pytest
from encoded.tests.features.conftest import app, app_settings, index_workbook
from encoded.batch_download import lookup_column_value
from encoded.batch_download import format_row
from encoded.batch_download import _convert_camel_to_snake


pytestmark = [
    pytest.mark.indexing,
    pytest.mark.usefixtures('index_workbook'),
]

def test_format_row():
    columns = ['col1', 'col2', 'col3']
    expected = b'col1\tcol2\tcol3\r\n'
    target = format_row(columns)
    assert expected == target


def test_convert_camel_to_snake_with_two_words():
    expected = 'camel_case'
    target = _convert_camel_to_snake('CamelCase')
    assert expected == target


def test_convert_camel_to_snake_with_one_words():
    expected = 'camel'
    target = _convert_camel_to_snake('Camel')
    assert expected == target


def test_batch_download_report_download(testapp, index_workbook, threadlocals):
    res = testapp.get('/report.tsv?type=Experiment&sort=accession')
    assert res.headers['content-type'] == 'text/tsv; charset=UTF-8'
    disposition = res.headers['content-disposition']
    assert disposition.startswith('attachment;filename="experiment_report') and disposition.endswith('.tsv"')
    lines = res.body.splitlines()
    assert b'/report/' in lines[0]
    assert lines[1].split(b'\t') == [
        b'ID', b'Accession', b'Assay name', b'Assay title', b'Target of assay',
        b'Target gene symbol', b'Biosample summary', b'Biosample term name', b'Dbxrefs', b'Description', b'Lab',
        b'Project', b'Status', b'Files', b'Related series', b'Biosample accession', b'Biological replicate',
        b'Technical replicate', b'Linked antibody', b'Organism', b'Life stage', b'Biosample age',
        b'Biosample treatment', b'Biosample treatment ontology ID', b'Biosample treatment amount', b'Biosample treatment amount units',
        b'Biosample treatment duration', b'Biosample treatment duration units', b'Synchronization',
        b'Post-synchronization time', b'Post-synchronization time units',
        b'Replicates', b'Mixed biosamples',
    ]
    assert len(lines) == 85


def test_batch_download_report_download_with_cart(testapp, index_workbook, threadlocals):
    res = testapp.get('/report.tsv?type=Experiment&cart=/carts/ali-mortazavi-first-cart/')
    assert res.headers['content-type'] == 'text/tsv; charset=UTF-8'
    disposition = res.headers['content-disposition']
    assert disposition.startswith('attachment;filename="experiment_report') and disposition.endswith('.tsv"')
    lines = res.body.splitlines()
    assert b'/cart-report/' in lines[0]
    assert lines[1].split(b'\t') == [
        b'ID', b'Accession', b'Assay name', b'Assay title', b'Target of assay',
        b'Target gene symbol', b'Biosample summary', b'Biosample term name', b'Dbxrefs', b'Description', b'Lab',
        b'Project', b'Status', b'Files', b'Related series', b'Biosample accession', b'Biological replicate',
        b'Technical replicate', b'Linked antibody', b'Organism', b'Life stage', b'Biosample age',
        b'Biosample treatment', b'Biosample treatment ontology ID', b'Biosample treatment amount', b'Biosample treatment amount units',
        b'Biosample treatment duration', b'Biosample treatment duration units', b'Synchronization',
        b'Post-synchronization time', b'Post-synchronization time units',
        b'Replicates', b'Mixed biosamples',
    ]
    assert len(lines) == 7


def test_batch_download_matched_set_report_download(testapp, index_workbook):
    res = testapp.get('/report.tsv?type=MatchedSet&sort=accession')
    disposition = res.headers['content-disposition']
    assert disposition.startswith('attachment;filename="matched_set_report') and disposition.endswith('.tsv"')
    res = testapp.get('/report.tsv?type=matched_set&sort=accession')
    disposition = res.headers['content-disposition']
    assert disposition.startswith('attachment;filename="matched_set_report') and disposition.endswith('.tsv"')


def test_batch_download_lookup_column_value(lookup_column_value_item, lookup_column_value_validate):
    for path in lookup_column_value_validate.keys():
        assert lookup_column_value_validate[path] == lookup_column_value(lookup_column_value_item, path)


def test_batch_download_is_cart_search(dummy_request):
    from encoded.batch_download import is_cart_search
    dummy_request.environ['QUERY_STRING'] = (
        'type=Experiment&limit=all'
    )
    assert not is_cart_search(dummy_request)
    dummy_request.environ['QUERY_STRING'] = (
        'type=Experiment&cart=/carts/abc/&field=@id'
    )
    assert is_cart_search(dummy_request)


def test_batch_download_get_report_search_generator(dummy_request):
    from encoded.batch_download import get_report_search_generator
    dummy_request.environ['QUERY_STRING'] = (
        'type=Experiment&limit=all'
    )
    assert get_report_search_generator(dummy_request).__name__ == 'search_generator'
    dummy_request.environ['QUERY_STRING'] = (
        'type=Experiment&limit=all&cart=1234'
    )
    assert get_report_search_generator(dummy_request).__name__ == 'cart_search_generator'
