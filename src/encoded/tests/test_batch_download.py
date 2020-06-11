# Use workbook fixture from BDD tests (including elasticsearch)
import json
import pytest
import mock
from collections import OrderedDict
from encoded.tests.features.conftest import app
from encoded.tests.features.conftest import app_settings
from encoded.tests.features.conftest import workbook
from encoded.batch_download import lookup_column_value
from encoded.batch_download import restricted_files_present
from encoded.batch_download import files_prop_param_list
from encoded.batch_download import make_cell
from encoded.batch_download import make_audit_cell
from encoded.batch_download import format_row
from encoded.batch_download import _convert_camel_to_snake
from encoded.batch_download import ELEMENT_CHUNK_SIZE
from encoded.batch_download import _tsv_mapping
from encoded.batch_download import _audit_mapping
from encoded.batch_download import _tsv_mapping_annotation
from encoded.batch_download import _excluded_columns
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

def test__tsv_mapping_value():
    expected = _tsv_mapping
    target = OrderedDict([
        ('File accession', ['files.title']),
        ('File format', ['files.file_type']),
        ('File type', ['files.file_format']),
        ('File format type', ['files.file_format_type']),
        ('Output type', ['files.output_type']),
        ('File assembly', ['files.assembly']),
        ('Experiment accession', ['accession']),
        ('Assay', ['assay_term_name', 'files.assay_term_name']),
        ('Biosample term id', ['biosample_ontology.term_id']),
        ('Biosample term name', ['biosample_ontology.term_name']),
        ('Biosample type', ['biosample_ontology.classification']),
        ('Biosample organism', ['replicates.library.biosample.organism.scientific_name']),
        ('Biosample treatments', ['replicates.library.biosample.treatments.treatment_term_name']),
        ('Biosample treatments amount', ['replicates.library.biosample.treatments.amount',
                                     'replicates.library.biosample.treatments.amount_units']),
        ('Biosample treatments duration', ['replicates.library.biosample.treatments.duration',
                                       'replicates.library.biosample.treatments.duration_units']),
        ('Biosample genetic modifications methods', ['replicates.library.biosample.applied_modifications.method']),
        ('Biosample genetic modifications categories', ['replicates.library.biosample.applied_modifications.category']),                                   
        ('Biosample genetic modifications targets', ['replicates.library.biosample.applied_modifications.modified_site_by_target_id']),                                   
        ('Biosample genetic modifications gene targets', ['replicates.library.biosample.applied_modifications.modified_site_by_gene_id']),                                   
        ('Biosample genetic modifications site coordinates', ['replicates.library.biosample.applied_modifications.modified_site_by_coordinates.assembly',
                                                          'replicates.library.biosample.applied_modifications.modified_site_by_coordinates.chromosome',
                                                          'replicates.library.biosample.applied_modifications.modified_site_by_coordinates.start',
                                                          'replicates.library.biosample.applied_modifications.modified_site_by_coordinates.end']),                                   
        ('Biosample genetic modifications zygosity', ['replicates.library.biosample.applied_modifications.zygosity']), 
        ('Experiment target', ['target.name']),
        ('Library made from', ['replicates.library.nucleic_acid_term_name']),
        ('Library depleted in', ['replicates.library.depleted_in_term_name']),
        ('Library extraction method', ['replicates.library.extraction_method']),
        ('Library lysis method', ['replicates.library.lysis_method']),
        ('Library crosslinking method', ['replicates.library.crosslinking_method']),
        ('Library strand specific', ['replicates.library.strand_specificity']),
        ('Experiment date released', ['date_released']),
        ('Project', ['award.project']),
        ('RBNS protein concentration', ['files.replicate.rbns_protein_concentration', 'files.replicate.rbns_protein_concentration_units']),
        ('Library fragmentation method', ['files.replicate.library.fragmentation_method']),
        ('Library size range', ['files.replicate.library.size_range']),
        ('Biological replicate(s)', ['files.biological_replicates']),
        ('Technical replicate(s)', ['files.technical_replicates']),
        ('Read length', ['files.read_length']),
        ('Mapped read length', ['files.mapped_read_length']),
        ('Run type', ['files.run_type']),
        ('Paired end', ['files.paired_end']),
        ('Paired with', ['files.paired_with']),
        ('Derived from', ['files.derived_from']),
        ('Size', ['files.file_size']),
        ('Lab', ['files.lab.title']),
        ('md5sum', ['files.md5sum']),
        ('dbxrefs', ['files.dbxrefs']),
        ('File download URL', ['files.href']),
        ('Genome annotation', ['files.genome_annotation']),
        ('Platform', ['files.platform.title']),
        ('Controlled by', ['files.controlled_by']),
        ('File Status', ['files.status']),
        ('No File Available', ['files.no_file_available']),
        ('Restricted', ['files.restricted']),
        ('s3_uri', ['files.s3_uri']),
    ])
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
        ('S3 URL', ['files.cloud_metadata']),
        ('Size', ['files.file_size']),
        ('No File Available', ['file.no_file_available']),
        ('Restricted', ['files.restricted'])
    ])
    assert expected == target


def test__excluded_columns_value():
    expected = _excluded_columns
    target = ('Restricted', 'No File Available')
    assert expected == target


@mock.patch('encoded.batch_download._tsv_mapping')
@mock.patch('encoded.batch_download.simple_path_ids')
def test_make_cell_for_vanilla_assignment(simple_path_ids, tsv_mapping):
    expected = ['a1', 'a2']
    simple_path_ids.return_value = ['a1', 'a2']
    tsv_mapping_data = {'file1': ['f1']}
    tsv_mapping.__getitem__.side_effect = tsv_mapping_data.__getitem__
    tsv_mapping.__iter__.side_effect = tsv_mapping_data.__iter__
    target = []
    make_cell('file1', [], target)
    target = sorted([t.strip() for t in target[0].split(',')])
    assert expected == target


@mock.patch('encoded.batch_download._tsv_mapping')
@mock.patch('encoded.batch_download.simple_path_ids')
def test_make_cell_for_post_sychronization(simple_path_ids, tsv_mapping):
    expected = ['a1 + a1', 'a2']
    simple_path_ids.return_value = ['a1', 'a2']
    tsv_mapping_data = {'file1': [
        'f1',
        'replicates.library.biosample.post_synchronization_time',
    ]}
    tsv_mapping.__getitem__.side_effect = tsv_mapping_data.__getitem__
    tsv_mapping.__iter__.side_effect = tsv_mapping_data.__iter__
    target = []
    make_cell('file1', [], target)
    target = sorted([t.strip() for t in target[0].split(',')])
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


def test_batch_download_report_download(testapp, workbook):
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
    assert len(lines) == 66


def test_batch_download_matched_set_report_download(testapp, workbook):
    res = testapp.get('/report.tsv?type=MatchedSet&sort=accession')
    disposition = res.headers['content-disposition']
    assert disposition.startswith('attachment;filename="matched_set_report') and disposition.endswith('.tsv"')
    res = testapp.get('/report.tsv?type=matched_set&sort=accession')
    disposition = res.headers['content-disposition']
    assert disposition.startswith('attachment;filename="matched_set_report') and disposition.endswith('.tsv"')


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


def test_batch_download_view(testapp, workbook):
    r = testapp.get('/batch_download/?type=Experiment&status=released')
    lines = r.text.split('\n')
    assert lines[0] == (
        'http://localhost/metadata/?type=Experiment&status=released'
    )
    assert len(lines) >= 79
    assert 'http://localhost/files/ENCFF002MXF/@@download/ENCFF002MXF.fastq.gz' in lines


def test_batch_download_header_and_rows(testapp, workbook):
    results = testapp.get('/batch_download/?type=Experiment')
    assert results.headers['Content-Type'] == 'text/plain; charset=UTF-8'
    assert results.headers['Content-Disposition'] == 'attachment; filename="files.txt"'
    lines = results.text.split('\n')
    assert len(lines) > 0
    assert '/metadata/?type=Experiment' in lines[0]
    for line in lines[1:]:
        assert '@@download' in line


def test_batch_download_view_file_plus(testapp, workbook):
    r = testapp.get(
        '/batch_download/?type=Experiment&files.file_type=bigBed+bed3%2B&format=json'
    )
    lines = r.text.split('\n')
    assert lines[0] == (
        'http://localhost/metadata/?type=Experiment&files.file_type=bigBed+bed3%2B&format=json'
    )
    assert 'http://localhost/files/ENCFF880XNW/@@download/ENCFF880XNW.bigBed' in lines


def test_metadata_view(testapp, workbook):
    r = testapp.get('/metadata/?type=Experiment')
    lines = r.text.split('\n')
    assert len(lines) >= 81
    

@pytest.mark.parametrize("test_input,expected", [
    (files_prop_param_list(exp_file_1, param_list_2), False),
    (files_prop_param_list(exp_file_1, param_list_1), True),
    (files_prop_param_list(exp_file_2, param_list_1), False),
    (files_prop_param_list(exp_file_3, param_list_3), True),
    (files_prop_param_list(exp_file_1, param_list_3), False),
])
def test_files_prop_param_list(test_input, expected):
    assert test_input == expected


@pytest.mark.parametrize("test_input,expected", [
    (restricted_files_present(exp_file_1), True),
    (restricted_files_present(exp_file_2), False),
    (restricted_files_present(exp_file_3), False),
])
def test_restricted_files_present(test_input, expected):
    assert test_input == expected


def test_metadata_tsv_fields(testapp, workbook):
    from encoded.batch_download import (
        _tsv_mapping,
        _excluded_columns,
    )
    r = testapp.get('/metadata/?type=Experiment')
    lines = r.text.split('\n')
    headers = lines[0].split('\t')
    assert len(headers) == len(set(headers))
    expected_headers = set(_tsv_mapping.keys()) - set(_excluded_columns)
    assert len(expected_headers - set(headers)) == 0


def test_metadata_contains_audit_values(testapp, workbook):
     r = testapp.get('/metadata/?type=Experiment&audit=*')
     audit_values = [
         'biological replicates with identical biosample',
         'experiment not submitted to GEO',
         'inconsistent assay_term_name',
         'inconsistent library biosample',
         'lacking processed data',
         'inconsistent platforms',
         'mismatched status',
         'missing documents',
         'unreplicated experiment'
     ]
     for value in audit_values:
         assert value in r.text
