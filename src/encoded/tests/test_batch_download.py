# Use fixtures from features, indexing workbook
import json
import pytest
import mock
from collections import OrderedDict
from encoded.tests.features.conftest import app, app_settings, index_workbook
from encoded.batch_download import lookup_column_value
from encoded.batch_download import restricted_files_present
from encoded.batch_download import format_row
from encoded.batch_download import _convert_camel_to_snake
from encoded.batch_download import ELEMENT_CHUNK_SIZE
from encoded.batch_download import get_biosample_accessions


pytestmark = [
    pytest.mark.indexing,
    pytest.mark.usefixtures('index_workbook'),
]


param_list_1 = {'files.file_type': 'fastq'}
param_list_2 = {'files.title': 'ENCFF222JUK'}
param_list_3 = {'files.assembly': 'GRCh38'}
exp_file_1 = {'file_type': 'fastq',
              'assembly': 'hg19',
              'restricted': True}
exp_file_2 = {'file_type': 'bam',
              'restricted': False}
exp_file_3 = {'file_type': 'gz',
              'assembly': 'GRCh38'}


def test_ELEMENT_CHUNK_SIZE_value():
    target = 1000
    expected = ELEMENT_CHUNK_SIZE
    assert expected == target


def test_get_biosample_accessions_finds_accession():
    expected = {'test_accession'}
    experiment_json = {
        'files': [{
            'uuid': '123',
            'replicate': {
                'library': {
                    'biosample': {
                        'accession': {
                            'test_accession'
                        }
                    }
                }
            }
        }]
    }
    file_json = {
        'uuid': '123',
        'replicate': {
            'library': {
                'biosample': {
                    'accession': {
                        'test_accession'
                    }
                }
            }
        }
    }
    target = get_biosample_accessions(file_json, experiment_json)
    assert expected == target

def test_get_biosample_accessions_finds_replicate_loop():
    expected = 'test_replicates'
    experiment_json = {
        'replicates': [{
            'library': {
                'biosample': {
                    'accession':
                        'test_replicates'
                }
            }
        }],
        'files': [{
            'uuid': '123',
            'replicate': {
                'library': {
                    'biosample': {
                        'accession': {
                            'test_accession'
                        }
                    }
                }
            },
        }]
    }
    file_json = {
        'uuid': '1235',
        'replicate': {
            'library': {
                'biosample': {
                    'accession': {
                        'test_accession'
                    }
                }
            }
        }
    }
    target = get_biosample_accessions(file_json, experiment_json)
    assert expected == target


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


def test_batch_download_report_download(testapp, index_workbook):
    res = testapp.get('/report.tsv?type=Experiment&sort=accession')
    assert res.headers['content-type'] == 'text/tsv; charset=UTF-8'
    disposition = res.headers['content-disposition']
    assert disposition.startswith('attachment;filename="experiment_report') and disposition.endswith('.tsv"')
    lines = res.body.splitlines()
    assert lines[1].split(b'\t') == [
        b'ID', b'Accession', b'Assay name', b'Assay title', b'Target of assay',
        b'Target gene symbol', b'Biosample summary', b'Biosample term name', b'Description', b'Lab',
        b'Project', b'Status', b'Files', b'Related series', b'Biosample accession', b'Biological replicate',
        b'Technical replicate', b'Linked antibody', b'Organism', b'Life stage', b'Biosample age',
        b'Biosample treatment', b'Biosample treatment ontology ID', b'Biosample treatment concentration', b'Biosample treatment concentration units',
        b'Biosample treatment duration', b'Biosample treatment duration units', b'Synchronization',
        b'Post-synchronization time', b'Post-synchronization time units',
        b'Replicates',
    ]
    assert len(lines) == 69


def test_batch_download_matched_set_report_download(testapp, index_workbook):
    res = testapp.get('/report.tsv?type=MatchedSet&sort=accession')
    disposition = res.headers['content-disposition']
    assert disposition.startswith('attachment;filename="matched_set_report') and disposition.endswith('.tsv"')
    res = testapp.get('/report.tsv?type=matched_set&sort=accession')
    disposition = res.headers['content-disposition']
    assert disposition.startswith('attachment;filename="matched_set_report') and disposition.endswith('.tsv"')


def test_batch_download_restricted_files_present(testapp, index_workbook):
    results = testapp.get('/search/?limit=all&field=files.href&field=files.file_type&field=files&type=Experiment')
    results = results.body.decode("utf-8")
    results = json.loads(results)

    files_gen = (
        exp_file
        for exp in results['@graph']
        for exp_file in exp.get('files', [])
    )
    for exp_file in files_gen:
        assert exp_file.get('restricted', False) == restricted_files_present(exp_file)


def test_batch_download_lookup_column_value(lookup_column_value_item, lookup_column_value_validate):
    for path in lookup_column_value_validate.keys():
        assert lookup_column_value_validate[path] == lookup_column_value(lookup_column_value_item, path)


def test_batch_download_view(testapp, index_workbook):
    r = testapp.get('/batch_download/?type=Experiment&status=released')
    lines = r.text.split('\n')
    assert lines[0] == (
        '"http://localhost/metadata/?type=Experiment&status=released"'
    )
    assert len(lines) >= 79
    assert 'http://localhost/files/ENCFF002MXF/@@download/ENCFF002MXF.fastq.gz' in lines


def test_batch_download_header_and_rows(testapp, index_workbook):
    results = testapp.get('/batch_download/?type=Experiment')
    assert results.headers['Content-Type'] == 'text/plain; charset=UTF-8'
    assert results.headers['Content-Disposition'] == 'attachment; filename="files.txt"'
    lines = results.text.split('\n')
    assert len(lines) > 0
    assert '/metadata/?type=Experiment' in lines[0]
    for line in lines[1:]:
        assert '@@download' in line


def test_batch_download_view_file_plus(testapp, index_workbook):
    r = testapp.get(
        '/batch_download/?type=Experiment&files.file_type=bigBed+bed3%2B&format=json'
    )
    lines = r.text.split('\n')
    assert lines[0] == (
        '"http://localhost/metadata/?type=Experiment&files.file_type=bigBed+bed3%2B&format=json"'
    )
    assert 'http://localhost/files/ENCFF880XNW/@@download/ENCFF880XNW.bigBed' in lines


def test_batch_download_contains_all_values(index_workbook, testapp):
    from pkg_resources import resource_filename
    r = testapp.get('/batch_download/?type=Experiment')
    actual = r.text.split('\n')
    expected_path = resource_filename('encoded', 'tests/data/inserts/expected_batch_download.tsv')
    # To write new expected_batch_download.tsv change 'r' to 'w' and f.write(r.text); return;
    with open(expected_path, 'r') as f:
        expected = [x.strip() for x in f.readlines()]
    assert set(actual) == set(expected), f'{set(actual) - set(expected)} not expected'


def test_batch_download_contains_all_publication_data_values(index_workbook, testapp):
    from pkg_resources import resource_filename
    r = testapp.get('/batch_download/?type=PublicationData&@id=/publication-data/ENCSR727WCB/')
    actual = r.text.split('\n')
    expected_path = resource_filename('encoded', 'tests/data/inserts/expected_publication_data_batch_download.tsv')
    # To write new expected_batch_download.tsv change 'r' to 'w' and f.write(r.text); return;
    with open(expected_path, 'r') as f:
        expected = [x.strip() for x in f.readlines()]
    assert set(actual) == set(expected), f'{set(actual) - set(expected)} not expected'


def test_batch_download_init_batch_download_mixin(dummy_request):
    from encoded.reports.batch_download import BatchDownloadMixin
    bdm = BatchDownloadMixin()
    assert isinstance(bdm, BatchDownloadMixin)


def test_batch_download_init_batch_download(dummy_request):
    from encoded.reports.batch_download import BatchDownload
    dummy_request.environ['QUERY_STRING'] = (
        'type=Experiment&files.file_type=bigWig&files.file_type=bam'
        '&files.replicate.library.size_range=50-100'
        '&files.status!=archived&files.biological_replicates=2'
    )
    bd = BatchDownload(dummy_request)
    assert isinstance(bd, BatchDownload)


def test_batch_download_maybe_add_json_elements_to_metadata_link(dummy_request):
    from encoded.reports.batch_download import BatchDownload
    dummy_request.environ['QUERY_STRING'] = (
        'type=Experiment&files.file_type=bigWig&files.file_type=bam'
        '&files.replicate.library.size_range=50-100'
        '&files.status!=archived&files.biological_replicates=2'
    )
    bd = BatchDownload(dummy_request)
    metadata_link = bd._maybe_add_json_elements_to_metadata_link('')
    assert metadata_link == ''
    dummy_request.json = {'elements': ['/experiments/ENCSR123ABC/']}
    bd = BatchDownload(dummy_request)
    metadata_link = bd._maybe_add_json_elements_to_metadata_link('')
    assert metadata_link == (
        ' -X GET -H "Accept: text/tsv" -H '
        '"Content-Type: application/json" '
        '--data \'{"elements": ["/experiments/ENCSR123ABC/"]}\''
    )
    dummy_request.json = {'elements': []}
    bd = BatchDownload(dummy_request)
    metadata_link = bd._maybe_add_json_elements_to_metadata_link('')
    assert metadata_link == ''
    dummy_request.json = {
        'elements': [
            '/experiments/ENCSR123ABC/',
            '/experiments/ENCSRDEF567/'
        ]
    }
    bd = BatchDownload(dummy_request)
    metadata_link = bd._maybe_add_json_elements_to_metadata_link('')
    assert metadata_link == (
        ' -X GET -H "Accept: text/tsv" -H '
        '"Content-Type: application/json" '
        '--data \'{"elements": ["/experiments/ENCSR123ABC/", "/experiments/ENCSRDEF567/"]}\''
    )


def test_batch_download_get_metadata_link(dummy_request):
    from encoded.reports.batch_download import BatchDownload
    dummy_request.environ['QUERY_STRING'] = (
        'type=Experiment&files.file_type=bigWig&files.file_type=bam'
        '&files.replicate.library.size_range=50-100'
        '&files.status!=archived&files.biological_replicates=2'
    )
    bd = BatchDownload(dummy_request)
    metadata_link = bd._get_metadata_link()
    assert metadata_link == (
        '"http://localhost/metadata/?type=Experiment'
        '&files.file_type=bigWig&files.file_type=bam'
        '&files.replicate.library.size_range=50-100'
        '&files.status%21=archived&files.biological_replicates=2"'
    )
    dummy_request.json = {
        'elements': [
            '/experiments/ENCSR123ABC/',
            '/experiments/ENCSRDEF567/'
        ]
    }
    bd = BatchDownload(dummy_request)
    metadata_link = bd._get_metadata_link()
    assert metadata_link == (
        '"http://localhost/metadata/?type=Experiment'
        '&files.file_type=bigWig&files.file_type=bam'
        '&files.replicate.library.size_range=50-100'
        '&files.status%21=archived&files.biological_replicates=2"'
        ' -X GET -H "Accept: text/tsv" -H "Content-Type: application/json"'
        ' --data \'{"elements": ["/experiments/ENCSR123ABC/", "/experiments/ENCSRDEF567/"]}\''
    )


def test_batch_download_default_params(dummy_request):
    from encoded.reports.batch_download import BatchDownload
    dummy_request.environ['QUERY_STRING'] = (
        'type=Experiment&files.file_type=bigWig&files.file_type=bam'
        '&files.replicate.library.size_range=50-100'
        '&files.status!=archived&files.biological_replicates=2'
    )
    bd = BatchDownload(dummy_request)
    assert bd.DEFAULT_PARAMS == [
        ('limit', 'all'),
        ('field', 'files.href'),
        ('field', 'files.restricted'),
        ('field', 'files.file_format'),
        ('field', 'files.file_format_type'),
        ('field', 'files.status'),
        ('field', 'files.assembly'),
    ]


def test_batch_download_build_header(dummy_request):
    from encoded.reports.batch_download import BatchDownload
    dummy_request.environ['QUERY_STRING'] = (
        'type=Experiment&files.file_type=bigWig&files.file_type=bam'
        '&files.replicate.library.size_range=50-100'
        '&files.status!=archived&files.biological_replicates=2'
    )
    bd = BatchDownload(dummy_request)
    bd._build_header()
    assert bd.header == ['File download URL']


def test_batch_download_get_column_to_field_mapping(dummy_request):
    from encoded.reports.batch_download import BatchDownload
    dummy_request.environ['QUERY_STRING'] = (
        'type=Experiment&files.file_type=bigWig&files.file_type=bam'
        '&files.replicate.library.size_range=50-100'
        '&files.status!=archived&files.biological_replicates=2'
    )
    bd = BatchDownload(dummy_request)
    assert list(bd._get_column_to_fields_mapping().items()) ==  [
        ('File download URL', ['files.href'])
    ]
