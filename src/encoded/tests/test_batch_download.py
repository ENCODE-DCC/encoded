# Use workbook fixture from BDD tests (including elasticsearch)
import json
import pytest

from encoded.tests.features.conftest import app
from encoded.tests.features.conftest import app_settings
from encoded.tests.features.conftest import workbook
from encoded.batch_download import lookup_column_value
from encoded.batch_download import restricted_files_present
from encoded.batch_download import file_type_param_list


param_list_1 = {'files.file_type': 'fastq'}
param_list_2 = {'files.title': 'ENCFF222JUK'}
exp_file_1 = {'file_type': 'fastq',
              'restricted': True}
exp_file_2 = {'file_type': 'bam',
              'restricted': False}
exp_file_3 = {'file_type': 'gz'}


@pytest.fixture
def lookup_column_value_item():
    item = {
        'assay_term_name': 'ISO-seq',
        'lab': {'title': 'John Stamatoyannopoulos, UW'},
        'accession': 'ENCSR751ISO',
        'assay_title': 'ISO-seq',
        'award': {'project': 'Roadmap'},
        'status': 'released',
        '@id': '/experiments/ENCSR751ISO/',
        '@type': ['Experiment', 'Dataset', 'Item'],
        'biosample_term_name': 'midbrain'
    }
    return item


@pytest.fixture
def lookup_column_value_validate():
    valid = {
        'assay_term_name': 'ISO-seq',
        'lab.title': 'John Stamatoyannopoulos, UW',
        'audit': '',
        'award.project': 'Roadmap',
        '@id': '/experiments/ENCSR751ISO/',
        'level.name': '',
        '@type': ['Experiment', 'Dataset', 'Item']
    }
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

    metadata = (lines[0].decode('UTF-8')).split('/')
    assert metadata[-1] == 'metadata.tsv'
    assert metadata[-2] == 'type=Experiment'
    assert metadata[-3] == 'metadata'

    assert len(lines[1:]) > 0
    for url in lines[1:]:
        url_frag = (url.decode('UTF-8')).split('/')
        assert url_frag[2] == metadata[2]
        assert url_frag[3] == 'files'
        assert url_frag[5] == '@@download'
        assert url_frag[4] == (url_frag[6].split('.'))[0]


def test_batch_download_restricted_files_present(testapp, workbook):
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


@pytest.mark.parametrize("test_input,expected", [
    (file_type_param_list(exp_file_1, param_list_2), True),
    (file_type_param_list(exp_file_1, param_list_1), True),
    (file_type_param_list(exp_file_2, param_list_1), False),
])
def test_file_type_param_list(test_input, expected):
    assert test_input == expected


@pytest.mark.parametrize("test_input,expected", [
    (restricted_files_present(exp_file_1), True),
    (restricted_files_present(exp_file_2), False),
    (restricted_files_present(exp_file_3), False),
])
def test_restricted_files_present(test_input, expected):
    assert test_input == expected
