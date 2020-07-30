# Use fixtures from features, indexing workbook
import json
import pytest
import mock
from collections import OrderedDict
from encoded.tests.features.conftest import app, app_settings, index_workbook
from encoded.batch_download import lookup_column_value
from encoded.batch_download import restricted_files_present
from encoded.batch_download import make_audit_cell
from encoded.batch_download import format_row
from encoded.batch_download import _convert_camel_to_snake
from encoded.batch_download import ELEMENT_CHUNK_SIZE
from encoded.batch_download import _audit_mapping
from encoded.batch_download import _tsv_mapping_annotation
from encoded.batch_download import _tsv_mapping_publicationdata
from encoded.batch_download import get_biosample_accessions


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

def test__audit_mapping_value():
    expected = _audit_mapping
    target = OrderedDict([
        ('Audit WARNING', ['audit.WARNING.path',
                       'audit.WARNING.category',
                       'audit.WARNING.detail']),
        ('Audit INTERNAL_ACTION', ['audit.INTERNAL_ACTION.path',
                               'audit.INTERNAL_ACTION.category',
                               'audit.INTERNAL_ACTION.detail']),
        ('Audit NOT_COMPLIANT', ['audit.NOT_COMPLIANT.path',
                             'audit.NOT_COMPLIANT.category',
                             'audit.NOT_COMPLIANT.detail']),
        ('Audit ERROR', ['audit.ERROR.path',
                     'audit.ERROR.category',
                     'audit.ERROR.detail'])
    ])
    assert expected == target

def test__tsv_mapping_annotation_value():
    expected = _tsv_mapping_annotation
    target = OrderedDict([
        ('File accession', ['files.title']),
        ('File format', ['files.file_type']),
        ('Output type', ['files.output_type']),
        ('Assay term name', ['files.assay_term_name']),
        ('Dataset accession', ['accession']),
        ('Annotation type', ['annotation_type']),
        ('Software used', ['software_used.software.title']),
        ('Encyclopedia Version', ['encyclopedia_version']),
        ('Biosample term id', ['biosample_ontology.term_id']),
        ('Biosample term name', ['biosample_ontology.term_name']),
        ('Biosample type', ['biosample_ontology.classification']),
        ('Life stage', ['relevant_life_stage']),
        ('Age', ['relevant_timepoint']),
        ('Age units', ['relevant_timepoint_units']),
        ('Organism', ['organism.scientific_name']),
        ('Targets', ['targets.name']),
        ('Dataset date released', ['date_released']),
        ('Project', ['award.project']),
        ('Lab', ['files.lab.title']),
        ('md5sum', ['files.md5sum']),
        ('dbxrefs', ['files.dbxrefs']),
        ('File download URL', ['files.href']),
        ('Assembly', ['files.assembly']),
        ('Controlled by', ['files.controlled_by']),
        ('File Status', ['files.status']),
        ('Derived from', ['files.derived_from']),
        ('S3 URL', ['files.cloud_metadata.url']),
        ('Size', ['files.file_size']),
        ('No File Available', ['file.no_file_available']),
        ('Restricted', ['files.restricted'])
    ])
    assert expected == target

def test__tsv_mapping_publicationdata_value():
    expected = _tsv_mapping_publicationdata
    target = OrderedDict([
        ('File accession', ['files.title']),
        ('File dataset', ['files.dataset']),
        ('File type', ['files.file_format']),
        ('File format', ['files.file_type']),
        ('File output type', ['files.output_type']),
        ('Assay term name', ['files.assay_term_name']),
        ('Biosample term id', ['files.biosample_ontology.term_id']),
        ('Biosample term name', ['files.biosample_ontology.term_name']),
        ('Biosample type', ['files.biosample_ontology.classification']),
        ('File target', ['files.target.label']),
        ('Dataset accession', ['accession']),
        ('Dataset date released', ['date_released']),
        ('Project', ['award.project']),
        ('Lab', ['files.lab.title']),
        ('md5sum', ['files.md5sum']),
        ('dbxrefs', ['files.dbxrefs']),
        ('File download URL', ['files.href']),
        ('Assembly', ['files.assembly']),
        ('File status', ['files.status']),
        ('Derived from', ['files.derived_from']),
        ('S3 URL', ['files.cloud_metadata.url']),
        ('Size', ['files.file_size']),
        ('No File Available', ['file.no_file_available']),
        ('Restricted', ['files.restricted'])
    ])
    assert expected == target


@mock.patch('encoded.batch_download._audit_mapping')
@mock.patch('encoded.batch_download.simple_path_ids')
def test_make_audit_cell_for_vanilla(simple_path_ids, audit_mapping):
    expected = 'a2, a1'
    simple_path_ids.return_value = ['a1', 'a2']
    audit_mapping_data = {'file1': [
        ['path', '/files/',],
        ['category',],
    ]}
    audit_mapping.__getitem__.side_effect = audit_mapping_data.__getitem__
    audit_mapping.__iter__.side_effect = audit_mapping_data.__iter__
    file_json = {}
    target = make_audit_cell('file1', [], file_json)
    is_target_valid = True
    for i in target:
        if i not in expected:
            is_target_valid = False
            break
    assert is_target_valid


def test_format_row_removes_special_characters():
    columns = ['col1', 'col2\t', 'col4\n\t', 'col4\t\n\r', 'col5']
    expected = b'col1\tcol2\tcol4\tcol4\tcol5\r\n'
    target = format_row(columns)
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

@pytest.mark.indexing
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

@pytest.mark.indexing
def test_batch_download_matched_set_report_download(testapp, index_workbook):
    res = testapp.get('/report.tsv?type=MatchedSet&sort=accession')
    disposition = res.headers['content-disposition']
    assert disposition.startswith('attachment;filename="matched_set_report') and disposition.endswith('.tsv"')
    res = testapp.get('/report.tsv?type=matched_set&sort=accession')
    disposition = res.headers['content-disposition']
    assert disposition.startswith('attachment;filename="matched_set_report') and disposition.endswith('.tsv"')

@pytest.mark.indexing
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

@pytest.mark.indexing
def test_batch_download_view(testapp, index_workbook):
    r = testapp.get('/batch_download/?type=Experiment&status=released')
    lines = r.text.split('\n')
    assert lines[0] == (
        'http://localhost/metadata/?type=Experiment&status=released'
    )
    assert len(lines) >= 79
    assert 'http://localhost/files/ENCFF002MXF/@@download/ENCFF002MXF.fastq.gz' in lines

@pytest.mark.indexing
def test_batch_download_header_and_rows(testapp, index_workbook):
    results = testapp.get('/batch_download/?type=Experiment')
    assert results.headers['Content-Type'] == 'text/plain; charset=UTF-8'
    assert results.headers['Content-Disposition'] == 'attachment; filename="files.txt"'
    lines = results.text.split('\n')
    assert len(lines) > 0
    assert '/metadata/?type=Experiment' in lines[0]
    for line in lines[1:]:
        assert '@@download' in line

@pytest.mark.indexing
def test_batch_download_view_file_plus(testapp, index_workbook):
    r = testapp.get(
        '/batch_download/?type=Experiment&files.file_type=bigBed+bed3%2B&format=json'
    )
    lines = r.text.split('\n')
    assert lines[0] == (
        'http://localhost/metadata/?type=Experiment&files.file_type=bigBed+bed3%2B&format=json'
    )
    assert 'http://localhost/files/ENCFF880XNW/@@download/ENCFF880XNW.bigBed' in lines
