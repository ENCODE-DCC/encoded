# Use workbook fixture from BDD tests (including elasticsearch)
from .features.conftest import app_settings, app, workbook
import json, pytest
from ..batch_download import lookup_column_value, filter_restricted_files

@pytest.fixture
def lookup_column_value_item():
    item = {'assay_term_name': 'ISO-seq',
           'lab': {'title': 'John Stamatoyannopoulos, UW'},
           'accession': 'ENCSR751ISO',
           'assay_title': 'ISO-seq',
           'award': {'project': 'Roadmap'},
           'status': 'released',
           '@id': '/experiments/ENCSR751ISO/',
           '@type': ['Experiment', 'Dataset', 'Item'],
        'biosample_term_name': 'midbrain'}
    return item

@pytest.fixture
def lookup_column_value_validate():
    valid = {'assay_term_name' : 'ISO-seq',
            'lab.title' : 'John Stamatoyannopoulos, UW',
            'audit' : '',
            'award.project' : 'Roadmap',
            '@id' : '/experiments/ENCSR751ISO/',
            'level.name' : ''}
    return valid

def test_batch_download_report_download(testapp, workbook):
    res = testapp.get('/report.tsv?type=Experiment&sort=accession')
    assert res.headers['content-type'] == 'text/tsv; charset=UTF-8'
    disposition = res.headers['content-disposition']
    assert disposition.startswith('attachment;filename="Experiment Report') and disposition.endswith('.tsv"')
    lines = res.body.splitlines()
    assert lines[1].split(b'\t') == [
        b'ID', b'Accession', b'Assay Type', b'Assay Nickname', b'Target label',
        b'Target gene', b'Biosample summary', b'Biosample', b'Description', b'Lab',
        b'Project', b'Status', b'Biological replicate', b'Technical replicate',
        b'Linked Antibody', b'Species', b'Life stage', b'Age', b'Age Units',
        b'Treatment', b'Term ID', b'Concentration', b'Concentration units',
        b'Duration', b'Duration units', b'Synchronization',
        b'Post-synchronization time', b'Post-synchronization time units',
        b'Replicates',
    ]
    # Sorting for scan and limit=all is disabled currently
    # assert lines[1].split(b'\t') == [
    #     b'/experiments/ENCSR000AAL/', b'ENCSR000AAL', b'RNA-seq', b'RNA-seq',
    #     b'', b'K562', b'RNA Evaluation K562 Small Total RNA-seq from Gingeras',
    #     b'Thomas Gingeras, CSHL', b'ENCODE', b'released', b'',
    #     b'', b'', b'', b'', b'', b'', b'', b'', b'',
    #     b'', b'', b'', b'', b'', b'', b''
    # ]
    assert len(lines) == 47

def test_batch_download_files_txt(testapp, workbook):
    results = testapp.get('/batch_download/type%3DExperiment')
    assert results.headers['Content-Type'] == 'text/plain; charset=UTF-8'
    assert results.headers['Content-Disposition'] == 'attachment; filename="files.txt"'
    lines = results.body.splitlines()
    assert len(lines) > 0

def test_batch_download_filter_restricted_files(testapp, workbook):
    results = testapp.get('/search/?limit=all&field=files.href&field=files.file_type&field=files&type=Experiment')
    assert results.headers['Content-Type'] == 'application/json; charset=UTF-8'
    results = results.body.decode("utf-8")
    results = json.loads(results)
    files = filter_restricted_files(results)
    for file in files:
        assert file.get('restricted', 'false') == 'false'

def test_batch_download_lookup_column_value(lookup_column_value_item, lookup_column_value_validate):
    for path in lookup_column_value_validate.keys():
        assert lookup_column_value_validate[path] == lookup_column_value(lookup_column_value_item, path)