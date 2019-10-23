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


@pytest.fixture
def lookup_column_value_item():
    item = {
        'assay_term_name': 'long read RNA-seq',
        'lab': {'title': 'John Stamatoyannopoulos, UW'},
        'accession': 'ENCSR751ISO',
        'assay_title': 'long read RNA-seq',
        'award': {'project': 'Roadmap'},
        'status': 'released',
        '@id': '/experiments/ENCSR751ISO/',
        '@type': ['Experiment', 'Dataset', 'Item'],
        'biosample_ontology': {'term_name': 'midbrain'}
    }
    return item


@pytest.fixture
def lookup_column_value_validate():
    valid = {
        'assay_term_name': 'long read RNA-seq',
        'lab.title': 'John Stamatoyannopoulos, UW',
        'audit': '',
        'award.project': 'Roadmap',
        '@id': '/experiments/ENCSR751ISO/',
        'level.name': '',
        '@type': 'Experiment,Dataset,Item'
    }
    return valid


def test_ELEMENT_CHUNK_SIZE_value():
    target = 1000
    expected = ELEMENT_CHUNK_SIZE
    assert expected == target

def test__tsv_mapping_value():
    expected = _tsv_mapping
    target = OrderedDict([
        ('File accession', ['files.title']),
        ('File format', ['files.file_type']),
        ('Output type', ['files.output_type']),
        ('Experiment accession', ['accession']),
        ('Assay', ['assay_term_name']),
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
        ('Technical replicate', ['files.replicate.technical_replicate_number']),
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
        ('Assembly', ['files.assembly']),
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
        b'Project', b'Status', b'Files', b'Biosample accession', b'Biological replicate',
        b'Technical replicate', b'Linked antibody', b'Organism', b'Life stage', b'Age',
        b'Age units', b'Biosample treatment', b'Biosample treatment ontology ID', b'Biosample treatment concentration', b'Biosample treatment concentration units',
        b'Biosample treatment duration', b'Biosample treatment duration units', b'Synchronization',
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
    assert len(lines) == 51


def test_batch_download_matched_set_report_download(testapp, workbook):
    res = testapp.get('/report.tsv?type=MatchedSet&sort=accession')
    disposition = res.headers['content-disposition']
    assert disposition.startswith('attachment;filename="matched_set_report') and disposition.endswith('.tsv"')
    res = testapp.get('/report.tsv?type=matched_set&sort=accession')
    disposition = res.headers['content-disposition']
    assert disposition.startswith('attachment;filename="matched_set_report') and disposition.endswith('.tsv"')


def test_batch_download_files_txt(testapp, workbook):
    results = testapp.get('/batch_download/type%3DExperiment')
    assert results.headers['Content-Type'] == 'text/plain; charset=UTF-8'
    assert results.headers['Content-Disposition'] == 'attachment; filename="files.txt"'

    lines = results.body.splitlines()
    assert len(lines) > 0

    metadata = (lines[0].decode('UTF-8')).split('/')
    assert metadata[-1] == 'metadata.tsv'
    assert metadata[-2] == 'type%3DExperiment'
    assert metadata[-3] == 'metadata'

    assert len(lines[1:]) > 0
    for url in lines[1:]:
        url_frag = (url.decode('UTF-8')).split('/')
        assert url_frag[2] == metadata[2]
        assert url_frag[3] == 'files'
        assert url_frag[5] == '@@download'
        assert url_frag[4] == (url_frag[6].split('.'))[0]


def test_batch_download_parse_file_plus_correctly(testapp, workbook):
    r = testapp.get(
        '/batch_download/type%3DExperiment%26files.file_type%3DbigBed%2Bbed3%252B%26format%3Djson'
    )
    assert r.body.decode('utf-8') == 'http://localhost/metadata/type%3DExperiment%26files.file_type%3DbigBed%2Bbed3%252B%26format%3Djson/metadata.tsv\nhttp://localhost/files/ENCFF880XNW/@@download/ENCFF880XNW.bigBed'
    

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


@pytest.mark.parametrize('test_url,expected', [
    ('/batch_download/type=Experiment&format=json', 'http://localhost/metadata/type%3DExperiment%26format%3Djson/metadata.tsv\nhttp://localhost/files/ENCFF002MWZ/@@download/ENCFF002MWZ.bam\nhttp://localhost/files/ENCFF002MXF/@@download/ENCFF002MXF.fastq.gz\nhttp://localhost/files/ENCFF946MFS/@@download/ENCFF946MFS.tsv\nhttp://localhost/files/ENCFF413RGP/@@download/ENCFF413RGP.tsv\nhttp://localhost/files/ENCFF355OWW/@@download/ENCFF355OWW.hic\nhttp://localhost/files/ENCFF784GFP/@@download/ENCFF784GFP.hic\nhttp://localhost/files/ENCFF812THZ/@@download/ENCFF812THZ.hic\nhttp://localhost/files/ENCFF123HIC/@@download/ENCFF123HIC.txt\nhttp://localhost/files/ENCFF880XNW/@@download/ENCFF880XNW.bigBed\nhttp://localhost/files/ENCFF000VUS/@@download/ENCFF000VUS.bam\nhttp://localhost/files/ENCFF001MWZ/@@download/ENCFF001MWZ.bam\nhttp://localhost/files/ENCFF001MXA/@@download/ENCFF001MXA.bam\nhttp://localhost/files/ENCFF001MXD/@@download/ENCFF001MXD.bigWig\nhttp://localhost/files/ENCFF002MXD/@@download/ENCFF002MXD.bigWig\nhttp://localhost/files/ENCFF003MXD/@@download/ENCFF003MXD.bigWig\nhttp://localhost/files/ENCFF001MXF/@@download/ENCFF001MXF.fastq.gz\nhttp://localhost/files/ENCFF001MXH/@@download/ENCFF001MXH.fastq.gz\nhttp://localhost/files/ENCFF000VWO/@@download/ENCFF000VWO.bam\nhttp://localhost/files/ENCFF001MXE/@@download/ENCFF001MXE.bam\nhttp://localhost/files/ENCFF001MXG/@@download/ENCFF001MXG.bigWig\nhttp://localhost/files/ENCFF001MYM/@@download/ENCFF001MYM.fastq.gz\nhttp://localhost/files/ENCFF001RCT/@@download/ENCFF001RCT.fastq.gz\nhttp://localhost/files/ENCFF001RCU/@@download/ENCFF001RCU.fastq.gz\nhttp://localhost/files/ENCFF001RCV/@@download/ENCFF001RCV.bam\nhttp://localhost/files/ENCFF001RCW/@@download/ENCFF001RCW.bam\nhttp://localhost/files/ENCFF001RCY/@@download/ENCFF001RCY.bigWig\nhttp://localhost/files/ENCFF001RCZ/@@download/ENCFF001RCZ.bigWig\nhttp://localhost/files/ENCFF130XXF/@@download/ENCFF130XXF.bigWig\nhttp://localhost/files/ENCFF854KQX/@@download/ENCFF854KQX.bigWig\nhttp://localhost/files/ENCFF119LNR/@@download/ENCFF119LNR.bigWig\nhttp://localhost/files/ENCFF000RCC/@@download/ENCFF000RCC.rcc\nhttp://localhost/files/ENCFF000DAT/@@download/ENCFF000DAT.idat\nhttp://localhost/files/SRR1270627/@@download/SRR1270627.sra\nhttp://localhost/files/ENCFF002REP/@@download/ENCFF002REP.bam\nhttp://localhost/files/ENCFF010EPI/@@download/ENCFF010EPI.bam\nhttp://localhost/files/ENCFF790SUA/@@download/ENCFF790SUA.fastq.gz\nhttp://localhost/files/ENCFF002CON/@@download/ENCFF002CON.bam\nhttp://localhost/files/ENCFF009EPI/@@download/ENCFF009EPI.bam\nhttp://localhost/files/ENCFF001EPI/@@download/ENCFF001EPI.fastq.gz\nhttp://localhost/files/ENCFF002EPI/@@download/ENCFF002EPI.bam\nhttp://localhost/files/ENCFF558BPA/@@download/ENCFF558BPA.fastq.gz\nhttp://localhost/files/ENCFF011EPI/@@download/ENCFF011EPI.bam\nhttp://localhost/files/ENCFF001MRN/@@download/ENCFF001MRN.fastq.gz\nhttp://localhost/files/ENCFF002MRN/@@download/ENCFF002MRN.fastq.gz\nhttp://localhost/files/ENCFF003MRN/@@download/ENCFF003MRN.bam\nhttp://localhost/files/ENCFF004MRN/@@download/ENCFF004MRN.bam\nhttp://localhost/files/ENCFF005MRN/@@download/ENCFF005MRN.tsv\nhttp://localhost/files/ENCFF006MRN/@@download/ENCFF006MRN.tsv\nhttp://localhost/files/ENCFF807TRA/@@download/ENCFF807TRA.gtf.gz\nhttp://localhost/files/ENCFF107ADP/@@download/ENCFF107ADP.txt\nhttp://localhost/files/ENCFF003EPI/@@download/ENCFF003EPI.fastq.gz\nhttp://localhost/files/ENCFF004EPI/@@download/ENCFF004EPI.bam\nhttp://localhost/files/ENCFF001ISO/@@download/ENCFF001ISO.fastq.gz\nhttp://localhost/files/ENCFF002ISO/@@download/ENCFF002ISO.fastq.gz\nhttp://localhost/files/ENCFF003ISO/@@download/ENCFF003ISO.bam\nhttp://localhost/files/ENCFF004ISO/@@download/ENCFF004ISO.bam\nhttp://localhost/files/ENCFF005ISO/@@download/ENCFF005ISO.tsv\nhttp://localhost/files/ENCFF006ISO/@@download/ENCFF006ISO.tsv\nhttp://localhost/files/ENCFF007ISO/@@download/ENCFF007ISO.db\nhttp://localhost/files/ENCFF002BAR/@@download/ENCFF002BAR.tsv\nhttp://localhost/files/ENCFF005EPI/@@download/ENCFF005EPI.fastq.gz\nhttp://localhost/files/ENCFF002COS/@@download/ENCFF002COS.bed.gz\nhttp://localhost/files/ENCFF003COS/@@download/ENCFF003COS.bigBed\nhttp://localhost/files/ENCFF006EPI/@@download/ENCFF006EPI.fastq.gz\nhttp://localhost/files/ENCFF007EPI/@@download/ENCFF007EPI.fastq.gz\nhttp://localhost/files/ENCFF001CON/@@download/ENCFF001CON.bam\nhttp://localhost/files/ENCFF003CON/@@download/ENCFF003CON.bam\nhttp://localhost/files/ENCFF001REP/@@download/ENCFF001REP.bam\nhttp://localhost/files/ENCFF003REP/@@download/ENCFF003REP.bam\nhttp://localhost/files/ENCFF008EPI/@@download/ENCFF008EPI.bam\nhttp://localhost/files/ENCFF959VGP/@@download/ENCFF959VGP.fastq.gz\nhttp://localhost/files/ENCFF477MLC/@@download/ENCFF477MLC.fastq.gz\nhttp://localhost/files/ENCFF000LBC/@@download/ENCFF000LBC.csqual.gz\nhttp://localhost/files/ENCFF000LBB/@@download/ENCFF000LBB.csqual.gz\nhttp://localhost/files/ENCFF000LBA/@@download/ENCFF000LBA.csfasta.gz\nhttp://localhost/files/ENCFF000LAZ/@@download/ENCFF000LAZ.csfasta.gz\nhttp://localhost/files/ENCFF010LAO/@@download/ENCFF010LAO.csfasta.gz'),
    ('/batch_download/type=Experiment&status=released&format=json', 'http://localhost/metadata/type%3DExperiment%26status%3Dreleased%26format%3Djson/metadata.tsv\nhttp://localhost/files/ENCFF002MWZ/@@download/ENCFF002MWZ.bam\nhttp://localhost/files/ENCFF002MXF/@@download/ENCFF002MXF.fastq.gz\nhttp://localhost/files/ENCFF946MFS/@@download/ENCFF946MFS.tsv\nhttp://localhost/files/ENCFF413RGP/@@download/ENCFF413RGP.tsv\nhttp://localhost/files/ENCFF355OWW/@@download/ENCFF355OWW.hic\nhttp://localhost/files/ENCFF784GFP/@@download/ENCFF784GFP.hic\nhttp://localhost/files/ENCFF812THZ/@@download/ENCFF812THZ.hic\nhttp://localhost/files/ENCFF123HIC/@@download/ENCFF123HIC.txt\nhttp://localhost/files/ENCFF880XNW/@@download/ENCFF880XNW.bigBed\nhttp://localhost/files/ENCFF000VUS/@@download/ENCFF000VUS.bam\nhttp://localhost/files/ENCFF001MWZ/@@download/ENCFF001MWZ.bam\nhttp://localhost/files/ENCFF001MXA/@@download/ENCFF001MXA.bam\nhttp://localhost/files/ENCFF001MXD/@@download/ENCFF001MXD.bigWig\nhttp://localhost/files/ENCFF002MXD/@@download/ENCFF002MXD.bigWig\nhttp://localhost/files/ENCFF003MXD/@@download/ENCFF003MXD.bigWig\nhttp://localhost/files/ENCFF001MXF/@@download/ENCFF001MXF.fastq.gz\nhttp://localhost/files/ENCFF001MXH/@@download/ENCFF001MXH.fastq.gz\nhttp://localhost/files/ENCFF000VWO/@@download/ENCFF000VWO.bam\nhttp://localhost/files/ENCFF001MXE/@@download/ENCFF001MXE.bam\nhttp://localhost/files/ENCFF001MXG/@@download/ENCFF001MXG.bigWig\nhttp://localhost/files/ENCFF001MYM/@@download/ENCFF001MYM.fastq.gz\nhttp://localhost/files/ENCFF001RCT/@@download/ENCFF001RCT.fastq.gz\nhttp://localhost/files/ENCFF001RCU/@@download/ENCFF001RCU.fastq.gz\nhttp://localhost/files/ENCFF001RCV/@@download/ENCFF001RCV.bam\nhttp://localhost/files/ENCFF001RCW/@@download/ENCFF001RCW.bam\nhttp://localhost/files/ENCFF001RCY/@@download/ENCFF001RCY.bigWig\nhttp://localhost/files/ENCFF001RCZ/@@download/ENCFF001RCZ.bigWig\nhttp://localhost/files/ENCFF130XXF/@@download/ENCFF130XXF.bigWig\nhttp://localhost/files/ENCFF854KQX/@@download/ENCFF854KQX.bigWig\nhttp://localhost/files/ENCFF119LNR/@@download/ENCFF119LNR.bigWig\nhttp://localhost/files/ENCFF000RCC/@@download/ENCFF000RCC.rcc\nhttp://localhost/files/ENCFF000DAT/@@download/ENCFF000DAT.idat\nhttp://localhost/files/SRR1270627/@@download/SRR1270627.sra\nhttp://localhost/files/ENCFF002REP/@@download/ENCFF002REP.bam\nhttp://localhost/files/ENCFF010EPI/@@download/ENCFF010EPI.bam\nhttp://localhost/files/ENCFF790SUA/@@download/ENCFF790SUA.fastq.gz\nhttp://localhost/files/ENCFF009EPI/@@download/ENCFF009EPI.bam\nhttp://localhost/files/ENCFF001EPI/@@download/ENCFF001EPI.fastq.gz\nhttp://localhost/files/ENCFF002EPI/@@download/ENCFF002EPI.bam\nhttp://localhost/files/ENCFF558BPA/@@download/ENCFF558BPA.fastq.gz\nhttp://localhost/files/ENCFF011EPI/@@download/ENCFF011EPI.bam\nhttp://localhost/files/ENCFF001MRN/@@download/ENCFF001MRN.fastq.gz\nhttp://localhost/files/ENCFF002MRN/@@download/ENCFF002MRN.fastq.gz\nhttp://localhost/files/ENCFF003MRN/@@download/ENCFF003MRN.bam\nhttp://localhost/files/ENCFF004MRN/@@download/ENCFF004MRN.bam\nhttp://localhost/files/ENCFF005MRN/@@download/ENCFF005MRN.tsv\nhttp://localhost/files/ENCFF006MRN/@@download/ENCFF006MRN.tsv\nhttp://localhost/files/ENCFF807TRA/@@download/ENCFF807TRA.gtf.gz\nhttp://localhost/files/ENCFF107ADP/@@download/ENCFF107ADP.txt\nhttp://localhost/files/ENCFF003EPI/@@download/ENCFF003EPI.fastq.gz\nhttp://localhost/files/ENCFF004EPI/@@download/ENCFF004EPI.bam\nhttp://localhost/files/ENCFF001ISO/@@download/ENCFF001ISO.fastq.gz\nhttp://localhost/files/ENCFF002ISO/@@download/ENCFF002ISO.fastq.gz\nhttp://localhost/files/ENCFF003ISO/@@download/ENCFF003ISO.bam\nhttp://localhost/files/ENCFF004ISO/@@download/ENCFF004ISO.bam\nhttp://localhost/files/ENCFF005ISO/@@download/ENCFF005ISO.tsv\nhttp://localhost/files/ENCFF006ISO/@@download/ENCFF006ISO.tsv\nhttp://localhost/files/ENCFF007ISO/@@download/ENCFF007ISO.db\nhttp://localhost/files/ENCFF002BAR/@@download/ENCFF002BAR.tsv\nhttp://localhost/files/ENCFF005EPI/@@download/ENCFF005EPI.fastq.gz\nhttp://localhost/files/ENCFF002COS/@@download/ENCFF002COS.bed.gz\nhttp://localhost/files/ENCFF003COS/@@download/ENCFF003COS.bigBed\nhttp://localhost/files/ENCFF006EPI/@@download/ENCFF006EPI.fastq.gz\nhttp://localhost/files/ENCFF007EPI/@@download/ENCFF007EPI.fastq.gz\nhttp://localhost/files/ENCFF001CON/@@download/ENCFF001CON.bam\nhttp://localhost/files/ENCFF003CON/@@download/ENCFF003CON.bam\nhttp://localhost/files/ENCFF001REP/@@download/ENCFF001REP.bam\nhttp://localhost/files/ENCFF003REP/@@download/ENCFF003REP.bam\nhttp://localhost/files/ENCFF008EPI/@@download/ENCFF008EPI.bam\nhttp://localhost/files/ENCFF477MLC/@@download/ENCFF477MLC.fastq.gz\nhttp://localhost/files/ENCFF000LBC/@@download/ENCFF000LBC.csqual.gz\nhttp://localhost/files/ENCFF000LBB/@@download/ENCFF000LBB.csqual.gz\nhttp://localhost/files/ENCFF000LBA/@@download/ENCFF000LBA.csfasta.gz\nhttp://localhost/files/ENCFF000LAZ/@@download/ENCFF000LAZ.csfasta.gz\nhttp://localhost/files/ENCFF010LAO/@@download/ENCFF010LAO.csfasta.gz'),
    ('/batch_download/type=Experiment&award.project!=Roadmap', 'http://localhost/metadata/type%3DExperiment%26award.project%21%3DRoadmap/metadata.tsv\nhttp://localhost/files/ENCFF002MWZ/@@download/ENCFF002MWZ.bam\nhttp://localhost/files/ENCFF002MXF/@@download/ENCFF002MXF.fastq.gz\nhttp://localhost/files/ENCFF946MFS/@@download/ENCFF946MFS.tsv\nhttp://localhost/files/ENCFF413RGP/@@download/ENCFF413RGP.tsv\nhttp://localhost/files/ENCFF355OWW/@@download/ENCFF355OWW.hic\nhttp://localhost/files/ENCFF784GFP/@@download/ENCFF784GFP.hic\nhttp://localhost/files/ENCFF812THZ/@@download/ENCFF812THZ.hic\nhttp://localhost/files/ENCFF123HIC/@@download/ENCFF123HIC.txt\nhttp://localhost/files/ENCFF880XNW/@@download/ENCFF880XNW.bigBed\nhttp://localhost/files/ENCFF000VUS/@@download/ENCFF000VUS.bam\nhttp://localhost/files/ENCFF001MWZ/@@download/ENCFF001MWZ.bam\nhttp://localhost/files/ENCFF001MXA/@@download/ENCFF001MXA.bam\nhttp://localhost/files/ENCFF001MXD/@@download/ENCFF001MXD.bigWig\nhttp://localhost/files/ENCFF002MXD/@@download/ENCFF002MXD.bigWig\nhttp://localhost/files/ENCFF003MXD/@@download/ENCFF003MXD.bigWig\nhttp://localhost/files/ENCFF001MXF/@@download/ENCFF001MXF.fastq.gz\nhttp://localhost/files/ENCFF001MXH/@@download/ENCFF001MXH.fastq.gz\nhttp://localhost/files/ENCFF000VWO/@@download/ENCFF000VWO.bam\nhttp://localhost/files/ENCFF001MXE/@@download/ENCFF001MXE.bam\nhttp://localhost/files/ENCFF001MXG/@@download/ENCFF001MXG.bigWig\nhttp://localhost/files/ENCFF001MYM/@@download/ENCFF001MYM.fastq.gz\nhttp://localhost/files/ENCFF001RCT/@@download/ENCFF001RCT.fastq.gz\nhttp://localhost/files/ENCFF001RCU/@@download/ENCFF001RCU.fastq.gz\nhttp://localhost/files/ENCFF001RCV/@@download/ENCFF001RCV.bam\nhttp://localhost/files/ENCFF001RCW/@@download/ENCFF001RCW.bam\nhttp://localhost/files/ENCFF001RCY/@@download/ENCFF001RCY.bigWig\nhttp://localhost/files/ENCFF001RCZ/@@download/ENCFF001RCZ.bigWig\nhttp://localhost/files/ENCFF130XXF/@@download/ENCFF130XXF.bigWig\nhttp://localhost/files/ENCFF854KQX/@@download/ENCFF854KQX.bigWig\nhttp://localhost/files/ENCFF119LNR/@@download/ENCFF119LNR.bigWig\nhttp://localhost/files/ENCFF000RCC/@@download/ENCFF000RCC.rcc\nhttp://localhost/files/ENCFF000DAT/@@download/ENCFF000DAT.idat\nhttp://localhost/files/SRR1270627/@@download/SRR1270627.sra\nhttp://localhost/files/ENCFF002REP/@@download/ENCFF002REP.bam\nhttp://localhost/files/ENCFF010EPI/@@download/ENCFF010EPI.bam\nhttp://localhost/files/ENCFF790SUA/@@download/ENCFF790SUA.fastq.gz\nhttp://localhost/files/ENCFF002CON/@@download/ENCFF002CON.bam\nhttp://localhost/files/ENCFF009EPI/@@download/ENCFF009EPI.bam\nhttp://localhost/files/ENCFF001EPI/@@download/ENCFF001EPI.fastq.gz\nhttp://localhost/files/ENCFF002EPI/@@download/ENCFF002EPI.bam\nhttp://localhost/files/ENCFF558BPA/@@download/ENCFF558BPA.fastq.gz\nhttp://localhost/files/ENCFF011EPI/@@download/ENCFF011EPI.bam\nhttp://localhost/files/ENCFF003EPI/@@download/ENCFF003EPI.fastq.gz\nhttp://localhost/files/ENCFF004EPI/@@download/ENCFF004EPI.bam\nhttp://localhost/files/ENCFF005EPI/@@download/ENCFF005EPI.fastq.gz\nhttp://localhost/files/ENCFF002COS/@@download/ENCFF002COS.bed.gz\nhttp://localhost/files/ENCFF003COS/@@download/ENCFF003COS.bigBed\nhttp://localhost/files/ENCFF006EPI/@@download/ENCFF006EPI.fastq.gz\nhttp://localhost/files/ENCFF007EPI/@@download/ENCFF007EPI.fastq.gz\nhttp://localhost/files/ENCFF001CON/@@download/ENCFF001CON.bam\nhttp://localhost/files/ENCFF003CON/@@download/ENCFF003CON.bam\nhttp://localhost/files/ENCFF001REP/@@download/ENCFF001REP.bam\nhttp://localhost/files/ENCFF003REP/@@download/ENCFF003REP.bam\nhttp://localhost/files/ENCFF008EPI/@@download/ENCFF008EPI.bam'),
    ('/batch_download/type=Experiment&biosample_ontology.term_name!=basal cell of epithelium of terminal bronchiole', 'http://localhost/metadata/type%3DExperiment%26biosample_ontology.term_name%21%3Dbasal%20cell%20of%20epithelium%20of%20terminal%20bronchiole/metadata.tsv\nhttp://localhost/files/ENCFF002MWZ/@@download/ENCFF002MWZ.bam\nhttp://localhost/files/ENCFF002MXF/@@download/ENCFF002MXF.fastq.gz\nhttp://localhost/files/ENCFF946MFS/@@download/ENCFF946MFS.tsv\nhttp://localhost/files/ENCFF413RGP/@@download/ENCFF413RGP.tsv\nhttp://localhost/files/ENCFF355OWW/@@download/ENCFF355OWW.hic\nhttp://localhost/files/ENCFF784GFP/@@download/ENCFF784GFP.hic\nhttp://localhost/files/ENCFF812THZ/@@download/ENCFF812THZ.hic\nhttp://localhost/files/ENCFF123HIC/@@download/ENCFF123HIC.txt\nhttp://localhost/files/ENCFF880XNW/@@download/ENCFF880XNW.bigBed\nhttp://localhost/files/ENCFF001MWZ/@@download/ENCFF001MWZ.bam\nhttp://localhost/files/ENCFF001MXA/@@download/ENCFF001MXA.bam\nhttp://localhost/files/ENCFF001MXD/@@download/ENCFF001MXD.bigWig\nhttp://localhost/files/ENCFF002MXD/@@download/ENCFF002MXD.bigWig\nhttp://localhost/files/ENCFF003MXD/@@download/ENCFF003MXD.bigWig\nhttp://localhost/files/ENCFF001MXF/@@download/ENCFF001MXF.fastq.gz\nhttp://localhost/files/ENCFF001MXH/@@download/ENCFF001MXH.fastq.gz\nhttp://localhost/files/ENCFF000VWO/@@download/ENCFF000VWO.bam\nhttp://localhost/files/ENCFF001MXE/@@download/ENCFF001MXE.bam\nhttp://localhost/files/ENCFF001MXG/@@download/ENCFF001MXG.bigWig\nhttp://localhost/files/ENCFF001MYM/@@download/ENCFF001MYM.fastq.gz\nhttp://localhost/files/ENCFF001RCT/@@download/ENCFF001RCT.fastq.gz\nhttp://localhost/files/ENCFF001RCU/@@download/ENCFF001RCU.fastq.gz\nhttp://localhost/files/ENCFF001RCV/@@download/ENCFF001RCV.bam\nhttp://localhost/files/ENCFF001RCW/@@download/ENCFF001RCW.bam\nhttp://localhost/files/ENCFF001RCY/@@download/ENCFF001RCY.bigWig\nhttp://localhost/files/ENCFF001RCZ/@@download/ENCFF001RCZ.bigWig\nhttp://localhost/files/ENCFF000RCC/@@download/ENCFF000RCC.rcc\nhttp://localhost/files/ENCFF000DAT/@@download/ENCFF000DAT.idat\nhttp://localhost/files/SRR1270627/@@download/SRR1270627.sra\nhttp://localhost/files/ENCFF002REP/@@download/ENCFF002REP.bam\nhttp://localhost/files/ENCFF010EPI/@@download/ENCFF010EPI.bam\nhttp://localhost/files/ENCFF790SUA/@@download/ENCFF790SUA.fastq.gz\nhttp://localhost/files/ENCFF002CON/@@download/ENCFF002CON.bam\nhttp://localhost/files/ENCFF009EPI/@@download/ENCFF009EPI.bam\nhttp://localhost/files/ENCFF001EPI/@@download/ENCFF001EPI.fastq.gz\nhttp://localhost/files/ENCFF002EPI/@@download/ENCFF002EPI.bam\nhttp://localhost/files/ENCFF558BPA/@@download/ENCFF558BPA.fastq.gz\nhttp://localhost/files/ENCFF011EPI/@@download/ENCFF011EPI.bam\nhttp://localhost/files/ENCFF001MRN/@@download/ENCFF001MRN.fastq.gz\nhttp://localhost/files/ENCFF002MRN/@@download/ENCFF002MRN.fastq.gz\nhttp://localhost/files/ENCFF003MRN/@@download/ENCFF003MRN.bam\nhttp://localhost/files/ENCFF004MRN/@@download/ENCFF004MRN.bam\nhttp://localhost/files/ENCFF005MRN/@@download/ENCFF005MRN.tsv\nhttp://localhost/files/ENCFF006MRN/@@download/ENCFF006MRN.tsv\nhttp://localhost/files/ENCFF807TRA/@@download/ENCFF807TRA.gtf.gz\nhttp://localhost/files/ENCFF107ADP/@@download/ENCFF107ADP.txt\nhttp://localhost/files/ENCFF003EPI/@@download/ENCFF003EPI.fastq.gz\nhttp://localhost/files/ENCFF004EPI/@@download/ENCFF004EPI.bam\nhttp://localhost/files/ENCFF001ISO/@@download/ENCFF001ISO.fastq.gz\nhttp://localhost/files/ENCFF002ISO/@@download/ENCFF002ISO.fastq.gz\nhttp://localhost/files/ENCFF003ISO/@@download/ENCFF003ISO.bam\nhttp://localhost/files/ENCFF004ISO/@@download/ENCFF004ISO.bam\nhttp://localhost/files/ENCFF005ISO/@@download/ENCFF005ISO.tsv\nhttp://localhost/files/ENCFF006ISO/@@download/ENCFF006ISO.tsv\nhttp://localhost/files/ENCFF007ISO/@@download/ENCFF007ISO.db\nhttp://localhost/files/ENCFF002BAR/@@download/ENCFF002BAR.tsv\nhttp://localhost/files/ENCFF005EPI/@@download/ENCFF005EPI.fastq.gz\nhttp://localhost/files/ENCFF002COS/@@download/ENCFF002COS.bed.gz\nhttp://localhost/files/ENCFF003COS/@@download/ENCFF003COS.bigBed\nhttp://localhost/files/ENCFF006EPI/@@download/ENCFF006EPI.fastq.gz\nhttp://localhost/files/ENCFF007EPI/@@download/ENCFF007EPI.fastq.gz\nhttp://localhost/files/ENCFF001CON/@@download/ENCFF001CON.bam\nhttp://localhost/files/ENCFF003CON/@@download/ENCFF003CON.bam\nhttp://localhost/files/ENCFF001REP/@@download/ENCFF001REP.bam\nhttp://localhost/files/ENCFF003REP/@@download/ENCFF003REP.bam\nhttp://localhost/files/ENCFF008EPI/@@download/ENCFF008EPI.bam\nhttp://localhost/files/ENCFF959VGP/@@download/ENCFF959VGP.fastq.gz\nhttp://localhost/files/ENCFF477MLC/@@download/ENCFF477MLC.fastq.gz\nhttp://localhost/files/ENCFF000LBC/@@download/ENCFF000LBC.csqual.gz\nhttp://localhost/files/ENCFF000LBB/@@download/ENCFF000LBB.csqual.gz\nhttp://localhost/files/ENCFF000LBA/@@download/ENCFF000LBA.csfasta.gz\nhttp://localhost/files/ENCFF000LAZ/@@download/ENCFF000LAZ.csfasta.gz\nhttp://localhost/files/ENCFF010LAO/@@download/ENCFF010LAO.csfasta.gz'),
    ('/batch_download/type=Experiment&assembly=hg19&assembly=GRCh38', 'http://localhost/metadata/type%3DExperiment%26assembly%3Dhg19%26assembly%3DGRCh38/metadata.tsv\nhttp://localhost/files/ENCFF946MFS/@@download/ENCFF946MFS.tsv\nhttp://localhost/files/ENCFF413RGP/@@download/ENCFF413RGP.tsv\nhttp://localhost/files/ENCFF355OWW/@@download/ENCFF355OWW.hic\nhttp://localhost/files/ENCFF784GFP/@@download/ENCFF784GFP.hic\nhttp://localhost/files/ENCFF812THZ/@@download/ENCFF812THZ.hic\nhttp://localhost/files/ENCFF123HIC/@@download/ENCFF123HIC.txt\nhttp://localhost/files/ENCFF880XNW/@@download/ENCFF880XNW.bigBed\nhttp://localhost/files/ENCFF000VUS/@@download/ENCFF000VUS.bam\nhttp://localhost/files/ENCFF000VWO/@@download/ENCFF000VWO.bam\nhttp://localhost/files/ENCFF001RCT/@@download/ENCFF001RCT.fastq.gz\nhttp://localhost/files/ENCFF001RCU/@@download/ENCFF001RCU.fastq.gz\nhttp://localhost/files/ENCFF001RCV/@@download/ENCFF001RCV.bam\nhttp://localhost/files/ENCFF001RCW/@@download/ENCFF001RCW.bam\nhttp://localhost/files/ENCFF001RCY/@@download/ENCFF001RCY.bigWig\nhttp://localhost/files/ENCFF001RCZ/@@download/ENCFF001RCZ.bigWig\nhttp://localhost/files/ENCFF130XXF/@@download/ENCFF130XXF.bigWig\nhttp://localhost/files/ENCFF854KQX/@@download/ENCFF854KQX.bigWig\nhttp://localhost/files/ENCFF119LNR/@@download/ENCFF119LNR.bigWig\nhttp://localhost/files/SRR1270627/@@download/SRR1270627.sra\nhttp://localhost/files/ENCFF002REP/@@download/ENCFF002REP.bam\nhttp://localhost/files/ENCFF010EPI/@@download/ENCFF010EPI.bam\nhttp://localhost/files/ENCFF002CON/@@download/ENCFF002CON.bam\nhttp://localhost/files/ENCFF009EPI/@@download/ENCFF009EPI.bam\nhttp://localhost/files/ENCFF001EPI/@@download/ENCFF001EPI.fastq.gz\nhttp://localhost/files/ENCFF002EPI/@@download/ENCFF002EPI.bam\nhttp://localhost/files/ENCFF011EPI/@@download/ENCFF011EPI.bam\nhttp://localhost/files/ENCFF001MRN/@@download/ENCFF001MRN.fastq.gz\nhttp://localhost/files/ENCFF002MRN/@@download/ENCFF002MRN.fastq.gz\nhttp://localhost/files/ENCFF003MRN/@@download/ENCFF003MRN.bam\nhttp://localhost/files/ENCFF004MRN/@@download/ENCFF004MRN.bam\nhttp://localhost/files/ENCFF005MRN/@@download/ENCFF005MRN.tsv\nhttp://localhost/files/ENCFF006MRN/@@download/ENCFF006MRN.tsv\nhttp://localhost/files/ENCFF807TRA/@@download/ENCFF807TRA.gtf.gz\nhttp://localhost/files/ENCFF107ADP/@@download/ENCFF107ADP.txt\nhttp://localhost/files/ENCFF003EPI/@@download/ENCFF003EPI.fastq.gz\nhttp://localhost/files/ENCFF004EPI/@@download/ENCFF004EPI.bam\nhttp://localhost/files/ENCFF001ISO/@@download/ENCFF001ISO.fastq.gz\nhttp://localhost/files/ENCFF002ISO/@@download/ENCFF002ISO.fastq.gz\nhttp://localhost/files/ENCFF003ISO/@@download/ENCFF003ISO.bam\nhttp://localhost/files/ENCFF004ISO/@@download/ENCFF004ISO.bam\nhttp://localhost/files/ENCFF005ISO/@@download/ENCFF005ISO.tsv\nhttp://localhost/files/ENCFF006ISO/@@download/ENCFF006ISO.tsv\nhttp://localhost/files/ENCFF007ISO/@@download/ENCFF007ISO.db\nhttp://localhost/files/ENCFF002BAR/@@download/ENCFF002BAR.tsv\nhttp://localhost/files/ENCFF002COS/@@download/ENCFF002COS.bed.gz\nhttp://localhost/files/ENCFF003COS/@@download/ENCFF003COS.bigBed\nhttp://localhost/files/ENCFF001CON/@@download/ENCFF001CON.bam\nhttp://localhost/files/ENCFF003CON/@@download/ENCFF003CON.bam\nhttp://localhost/files/ENCFF001REP/@@download/ENCFF001REP.bam\nhttp://localhost/files/ENCFF003REP/@@download/ENCFF003REP.bam\nhttp://localhost/files/ENCFF008EPI/@@download/ENCFF008EPI.bam'),
    ('/batch_download/type=Experiment&files.file_type=bed bed6+', 'http://localhost/metadata/type%3DExperiment%26files.file_type%3Dbed%20bed6%2B/metadata.tsv'),
    ('/batch_download/type=Annotation&organism.scientific_name!=Homo sapiens&organism.scientific_name=Mus musculus', 'http://localhost/metadata/type%3DAnnotation%26organism.scientific_name%21%3DHomo%20sapiens%26organism.scientific_name%3DMus%20musculus/metadata.tsv\nhttp://localhost/files/ENCFF015OKV/@@download/ENCFF015OKV.bed.gz'),
])
def test_batch_download_files(testapp, workbook, test_url, expected):
    response = testapp.get(test_url)
    target = response.body.decode('utf-8')
    assert sorted(target) == sorted(expected)


@pytest.mark.parametrize('test_url, expected_row_0, expected_row_n', [
    ('/metadata/type=Experiment&format=json/metadata.tsv', 'ENCFF000DAT\tidat\treporter code counts\tENCSR000AAL\tRNA-seq\tEFO:0002067\tK562\tcell line\tHomo sapiens\t\t\t\t\t\t\t\t\t\t\tDNA\t\t\t\t\tFalse\t2016-01-01\tENCODE\t\t\t\t2\t1\t\t\t\t\t\t\t37300\tMichael Snyder, Stanford\t4b7283c78f5c553a72174f850468b688\t\thttp://localhost/files/ENCFF000DAT/@@download/ENCFF000DAT.idat\t\t\tApplied Biosystems SOLiD System 3 Plus\t\treleased\t\t\tmismatched status, experiment not submitted to GEO, biological replicates with identical biosample\tmissing documents\tinconsistent library biosample', 'SRR1270627\tsra\treads\tENCSR765JPC\twhole-genome shotgun bisulfite sequencing\tEFO:0002067\tK562\tcell line\tHomo sapiens\t\t\t\t\t\t\t\t\t\t\tDNA\t\t\t\t\tFalse\t2016-01-01\tENCODE\t\t\t\t1\t1\t36\t\tsingle-ended\t\t\t\t1247813024\tRichard Myers, HAIB\tb52abba2d1e08ea93c527e38aff96e11\tSRA:SRR1270627\thttp://localhost/files/SRR1270627/@@download/SRR1270627.sra\t\t\tIllumina Genome Analyzer IIx\t\treleased\t\t\tmismatched status, mismatched file status, experiment not submitted to GEO\tunreplicated experiment, missing documents, insufficient read length\t',),
    ('/metadata/type=Experiment&biosample_ontology.term_name!=basal cell of epithelium of terminal bronchiole&format=json/metadata.tsv', 'ENCFF000DAT\tidat\treporter code counts\tENCSR000AAL\tRNA-seq\tEFO:0002067\tK562\tcell line\tHomo sapiens\t\t\t\t\t\t\t\t\t\t\tDNA\t\t\t\t\tFalse\t2016-01-01\tENCODE\t\t\t\t2\t1\t\t\t\t\t\t\t37300\tMichael Snyder, Stanford\t4b7283c78f5c553a72174f850468b688\t\thttp://localhost/files/ENCFF000DAT/@@download/ENCFF000DAT.idat\t\t\tApplied Biosystems SOLiD System 3 Plus\t\treleased\t\t\tmismatched status, experiment not submitted to GEO, biological replicates with identical biosample\tmissing documents\tinconsistent library biosample', 'SRR1270627\tsra\treads\tENCSR765JPC\twhole-genome shotgun bisulfite sequencing\tEFO:0002067\tK562\tcell line\tHomo sapiens\t\t\t\t\t\t\t\t\t\t\tDNA\t\t\t\t\tFalse\t2016-01-01\tENCODE\t\t\t\t1\t1\t36\t\tsingle-ended\t\t\t\t1247813024\tRichard Myers, HAIB\tb52abba2d1e08ea93c527e38aff96e11\tSRA:SRR1270627\thttp://localhost/files/SRR1270627/@@download/SRR1270627.sra\t\t\tIllumina Genome Analyzer IIx\t\treleased\t\t\tmismatched status, mismatched file status, experiment not submitted to GEO\tunreplicated experiment, missing documents, insufficient read length\t',),
    ('/metadata/type=Experiment&assembly=hg19&assembly=GRCh38&format=json/metadata.tsv', 'ENCFF000VUS\tbam\talignments\tENCSR000ACY\tDNA methylation profiling by array assay\tCL:1000350\tbasal cell of epithelium of terminal bronchiole\tprimary cell\tHomo sapiens\t\t\t\t\t\t\t\t\t\t\tDNA\t\tQIAGEN DNeasy Blood & Tissue Kit\tQIAGEN DNeasy Blood & Tissue Kit\t\tFalse\t2016-01-01\tENCODE\t\t\t\t2\t1\t\t\t\t\t\t\t473944988\tMichael Snyder, Stanford\t91d0dd9e0df439dd6599914b5275e7b2\t\thttp://localhost/files/ENCFF000VUS/@@download/ENCFF000VUS.bam\thg19\t\t\t\treleased\t\t\tmismatched status, missing derived_from\t\tinconsistent replicate', 'SRR1270627\tsra\treads\tENCSR765JPC\twhole-genome shotgun bisulfite sequencing\tEFO:0002067\tK562\tcell line\tHomo sapiens\t\t\t\t\t\t\t\t\t\t\tDNA\t\t\t\t\tFalse\t2016-01-01\tENCODE\t\t\t\t1\t1\t36\t\tsingle-ended\t\t\t\t1247813024\tRichard Myers, HAIB\tb52abba2d1e08ea93c527e38aff96e11\tSRA:SRR1270627\thttp://localhost/files/SRR1270627/@@download/SRR1270627.sra\t\t\tIllumina Genome Analyzer IIx\t\treleased\t\t\tmismatched status, mismatched file status, experiment not submitted to GEO\tunreplicated experiment, missing documents, insufficient read length\t',),
    ('/metadata/type=Annotation&organism.scientific_name%21=Homo+sapiens&organism.scientific_name=Mus+musculus&format=json/metadata.tsv','ENCFF015OKV\tbed enhancer predictions\tpredicted heart enhancers\tENCSR356VQT\tlong-range chromatin interactions\tSamtools, Picard\t2\tUBERON:0000948\theart\ttissue\tembryonic\t11.5\tday\tMus musculus\t\t2015-02-27\tENCODE\tJ. Michael Cherry, Stanford\ta5f849c78025c80dca58771492c97318\t\thttp://localhost/files/ENCFF015OKV/@@download/ENCFF015OKV.bed.gz\tmm10\t\treleased\t\t\t1544154147\tmissing analysis_step_run\tmismatched status, missing derived_from','File accession\tFile format\tOutput type\tDataset accession\tAnnotation type\tSoftware used\tEncyclopedia Version\tBiosample term id\tBiosample term name\tBiosample type\tLife stage\tAge\tAge units\tOrganism\tTargets\tDataset date released\tProject\tLab\tmd5sum\tdbxrefs\tFile download URL\tAssembly\tControlled by\tFile Status\tDerived from\tS3 URL\tSize\tAudit WARNING\tAudit INTERNAL_ACTION\tAudit NOT_COMPLIANT\tAudit ERROR\r',),
])
def test_batch_download_meta_files(testapp, workbook, test_url, expected_row_0, expected_row_n):
    # compare only ids, as it is the only essential field
    response = testapp.get(test_url)
    target = sorted(response.body.decode('utf-8').strip().split('\n'))
    # testing only uuids (values- 1 - 11)
    assert expected_row_0[:11] == target[0][:11]
    assert expected_row_n[:11] == target[-1][:11]
    

@pytest.mark.parametrize("test_input,expected", [
    (files_prop_param_list(exp_file_1, param_list_2), True),
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
    r = testapp.get('/metadata/type%3DExperiment/metadata.tsv')
    metadata_file = r.body.decode('UTF-8').split('\n')
    actual_headers = metadata_file[0].split('\t')
    assert len(actual_headers) == len(set(actual_headers))
    expected_headers = set(_tsv_mapping.keys()) - set(_excluded_columns)
    assert len(expected_headers - set(actual_headers)) == 0
