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
    assert len(lines) == 70


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
