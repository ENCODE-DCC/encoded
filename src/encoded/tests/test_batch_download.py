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

def test__tsv_mapping():
    expected = _tsv_mapping
    target =  OrderedDict([
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


def test__audit_mapping():
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

def test__tsv_mapping_annotation():
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


def test__excluded_columns():
    expected = _excluded_columns
    target = ('Restricted', 'No File Available')
    assert expected == target


@mock.patch('encoded.batch_download._tsv_mapping')
@mock.patch('encoded.batch_download.simple_path_ids')
def test_make_cell_for_vanilla_assignment(simple_path_ids, tsv_mapping):
    expected = ['a1, a2']
    simple_path_ids.return_value = ['a1', 'a2']
    tsv_mapping_data = {'file1': ['f1']}
    tsv_mapping.__getitem__.side_effect = tsv_mapping_data.__getitem__
    tsv_mapping.__iter__.side_effect = tsv_mapping_data.__iter__
    target = []
    make_cell('file1', [], target)
    assert expected == target


@mock.patch('encoded.batch_download._tsv_mapping')
@mock.patch('encoded.batch_download.simple_path_ids')
def test_make_cell_for_post_sychronization(simple_path_ids, tsv_mapping):
    expected = ['a1 + a1, a2']
    simple_path_ids.return_value = ['a1', 'a2']
    tsv_mapping_data = {'file1': [
        'f1',
        'replicates.library.biosample.post_synchronization_time',
    ]}
    tsv_mapping.__getitem__.side_effect = tsv_mapping_data.__getitem__
    tsv_mapping.__iter__.side_effect = tsv_mapping_data.__iter__
    target = []
    make_cell('file1', [], target)
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
    assert len(lines) == 53


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
    ('/batch_download/type=Experiment&format=json', 'http://localhost/metadata/type%3DExperiment%26format%3Djson/metadata.tsv\nhttp://localhost/files/ENCFF002MWZ/@@download/ENCFF002MWZ.bam\nhttp://localhost/files/ENCFF002MXF/@@download/ENCFF002MXF.fastq.gz\nhttp://localhost/files/ENCFF946MFS/@@download/ENCFF946MFS.tsv\nhttp://localhost/files/ENCFF413RGP/@@download/ENCFF413RGP.tsv\nhttp://localhost/files/ENCFF355OWW/@@download/ENCFF355OWW.hic\nhttp://localhost/files/ENCFF784GFP/@@download/ENCFF784GFP.hic\nhttp://localhost/files/ENCFF812THZ/@@download/ENCFF812THZ.hic\nhttp://localhost/files/ENCFF123HIC/@@download/ENCFF123HIC.txt\nhttp://localhost/files/ENCFF880XNW/@@download/ENCFF880XNW.bigBed\nhttp://localhost/files/ENCFF000VUS/@@download/ENCFF000VUS.bam\nhttp://localhost/files/ENCFF001MWZ/@@download/ENCFF001MWZ.bam\nhttp://localhost/files/ENCFF001MXA/@@download/ENCFF001MXA.bam\nhttp://localhost/files/ENCFF001MXD/@@download/ENCFF001MXD.bigWig\nhttp://localhost/files/ENCFF002MXD/@@download/ENCFF002MXD.bigWig\nhttp://localhost/files/ENCFF003MXD/@@download/ENCFF003MXD.bigWig\nhttp://localhost/files/ENCFF001MXF/@@download/ENCFF001MXF.fastq.gz\nhttp://localhost/files/ENCFF001MXH/@@download/ENCFF001MXH.fastq.gz\nhttp://localhost/files/ENCFF000VWO/@@download/ENCFF000VWO.bam\nhttp://localhost/files/ENCFF001MXE/@@download/ENCFF001MXE.bam\nhttp://localhost/files/ENCFF001MXG/@@download/ENCFF001MXG.bigWig\nhttp://localhost/files/ENCFF001MYM/@@download/ENCFF001MYM.fastq.gz\nhttp://localhost/files/ENCFF001RCT/@@download/ENCFF001RCT.fastq.gz\nhttp://localhost/files/ENCFF001RCU/@@download/ENCFF001RCU.fastq.gz\nhttp://localhost/files/ENCFF001RCV/@@download/ENCFF001RCV.bam\nhttp://localhost/files/ENCFF001RCW/@@download/ENCFF001RCW.bam\nhttp://localhost/files/ENCFF001RCY/@@download/ENCFF001RCY.bigWig\nhttp://localhost/files/ENCFF001RCZ/@@download/ENCFF001RCZ.bigWig\nhttp://localhost/files/ENCFF130XXF/@@download/ENCFF130XXF.bigWig\nhttp://localhost/files/ENCFF854KQX/@@download/ENCFF854KQX.bigWig\nhttp://localhost/files/ENCFF119LNR/@@download/ENCFF119LNR.bigWig\nhttp://localhost/files/ENCFF000RCC/@@download/ENCFF000RCC.rcc\nhttp://localhost/files/ENCFF000DAT/@@download/ENCFF000DAT.idat\nhttp://localhost/files/SRR1270627/@@download/SRR1270627.sra\nhttp://localhost/files/ENCFF002REP/@@download/ENCFF002REP.bam\nhttp://localhost/files/ENCFF010EPI/@@download/ENCFF010EPI.bam\nhttp://localhost/files/ENCFF790SUA/@@download/ENCFF790SUA.fastq.gz\nhttp://localhost/files/ENCFF002CON/@@download/ENCFF002CON.bam\nhttp://localhost/files/ENCFF009EPI/@@download/ENCFF009EPI.bam\nhttp://localhost/files/ENCFF001EPI/@@download/ENCFF001EPI.fastq.gz\nhttp://localhost/files/ENCFF002EPI/@@download/ENCFF002EPI.bam\nhttp://localhost/files/ENCFF558BPA/@@download/ENCFF558BPA.fastq.gz\nhttp://localhost/files/ENCFF011EPI/@@download/ENCFF011EPI.bam\nhttp://localhost/files/ENCFF001MRN/@@download/ENCFF001MRN.fastq.gz\nhttp://localhost/files/ENCFF002MRN/@@download/ENCFF002MRN.fastq.gz\nhttp://localhost/files/ENCFF003MRN/@@download/ENCFF003MRN.bam\nhttp://localhost/files/ENCFF004MRN/@@download/ENCFF004MRN.bam\nhttp://localhost/files/ENCFF005MRN/@@download/ENCFF005MRN.tsv\nhttp://localhost/files/ENCFF006MRN/@@download/ENCFF006MRN.tsv\nhttp://localhost/files/ENCFF003EPI/@@download/ENCFF003EPI.fastq.gz\nhttp://localhost/files/ENCFF004EPI/@@download/ENCFF004EPI.bam\nhttp://localhost/files/ENCFF001ISO/@@download/ENCFF001ISO.fastq.gz\nhttp://localhost/files/ENCFF002ISO/@@download/ENCFF002ISO.fastq.gz\nhttp://localhost/files/ENCFF003ISO/@@download/ENCFF003ISO.bam\nhttp://localhost/files/ENCFF004ISO/@@download/ENCFF004ISO.bam\nhttp://localhost/files/ENCFF005ISO/@@download/ENCFF005ISO.tsv\nhttp://localhost/files/ENCFF006ISO/@@download/ENCFF006ISO.tsv\nhttp://localhost/files/ENCFF007ISO/@@download/ENCFF007ISO.db\nhttp://localhost/files/ENCFF005EPI/@@download/ENCFF005EPI.fastq.gz\nhttp://localhost/files/ENCFF002COS/@@download/ENCFF002COS.bed.gz\nhttp://localhost/files/ENCFF003COS/@@download/ENCFF003COS.bigBed\nhttp://localhost/files/ENCFF006EPI/@@download/ENCFF006EPI.fastq.gz\nhttp://localhost/files/ENCFF007EPI/@@download/ENCFF007EPI.fastq.gz\nhttp://localhost/files/ENCFF001CON/@@download/ENCFF001CON.bam\nhttp://localhost/files/ENCFF003CON/@@download/ENCFF003CON.bam\nhttp://localhost/files/ENCFF001REP/@@download/ENCFF001REP.bam\nhttp://localhost/files/ENCFF003REP/@@download/ENCFF003REP.bam\nhttp://localhost/files/ENCFF008EPI/@@download/ENCFF008EPI.bam\nhttp://localhost/files/ENCFF959VGP/@@download/ENCFF959VGP.fastq.gz\nhttp://localhost/files/ENCFF477MLC/@@download/ENCFF477MLC.fastq.gz\nhttp://localhost/files/ENCFF000LBC/@@download/ENCFF000LBC.csqual.gz\nhttp://localhost/files/ENCFF000LBB/@@download/ENCFF000LBB.csqual.gz\nhttp://localhost/files/ENCFF000LBA/@@download/ENCFF000LBA.csfasta.gz\nhttp://localhost/files/ENCFF000LAZ/@@download/ENCFF000LAZ.csfasta.gz\nhttp://localhost/files/ENCFF010LAO/@@download/ENCFF010LAO.csfasta.gz'),
    ('/batch_download/type=Experiment&status=released&format=json', 'http://localhost/metadata/type%3DExperiment%26status%3Dreleased%26format%3Djson/metadata.tsv\nhttp://localhost/files/ENCFF002MWZ/@@download/ENCFF002MWZ.bam\nhttp://localhost/files/ENCFF002MXF/@@download/ENCFF002MXF.fastq.gz\nhttp://localhost/files/ENCFF946MFS/@@download/ENCFF946MFS.tsv\nhttp://localhost/files/ENCFF413RGP/@@download/ENCFF413RGP.tsv\nhttp://localhost/files/ENCFF355OWW/@@download/ENCFF355OWW.hic\nhttp://localhost/files/ENCFF784GFP/@@download/ENCFF784GFP.hic\nhttp://localhost/files/ENCFF812THZ/@@download/ENCFF812THZ.hic\nhttp://localhost/files/ENCFF123HIC/@@download/ENCFF123HIC.txt\nhttp://localhost/files/ENCFF880XNW/@@download/ENCFF880XNW.bigBed\nhttp://localhost/files/ENCFF000VUS/@@download/ENCFF000VUS.bam\nhttp://localhost/files/ENCFF001MWZ/@@download/ENCFF001MWZ.bam\nhttp://localhost/files/ENCFF001MXA/@@download/ENCFF001MXA.bam\nhttp://localhost/files/ENCFF001MXD/@@download/ENCFF001MXD.bigWig\nhttp://localhost/files/ENCFF002MXD/@@download/ENCFF002MXD.bigWig\nhttp://localhost/files/ENCFF003MXD/@@download/ENCFF003MXD.bigWig\nhttp://localhost/files/ENCFF001MXF/@@download/ENCFF001MXF.fastq.gz\nhttp://localhost/files/ENCFF001MXH/@@download/ENCFF001MXH.fastq.gz\nhttp://localhost/files/ENCFF000VWO/@@download/ENCFF000VWO.bam\nhttp://localhost/files/ENCFF001MXE/@@download/ENCFF001MXE.bam\nhttp://localhost/files/ENCFF001MXG/@@download/ENCFF001MXG.bigWig\nhttp://localhost/files/ENCFF001MYM/@@download/ENCFF001MYM.fastq.gz\nhttp://localhost/files/ENCFF001RCT/@@download/ENCFF001RCT.fastq.gz\nhttp://localhost/files/ENCFF001RCU/@@download/ENCFF001RCU.fastq.gz\nhttp://localhost/files/ENCFF001RCV/@@download/ENCFF001RCV.bam\nhttp://localhost/files/ENCFF001RCW/@@download/ENCFF001RCW.bam\nhttp://localhost/files/ENCFF001RCY/@@download/ENCFF001RCY.bigWig\nhttp://localhost/files/ENCFF001RCZ/@@download/ENCFF001RCZ.bigWig\nhttp://localhost/files/ENCFF130XXF/@@download/ENCFF130XXF.bigWig\nhttp://localhost/files/ENCFF854KQX/@@download/ENCFF854KQX.bigWig\nhttp://localhost/files/ENCFF119LNR/@@download/ENCFF119LNR.bigWig\nhttp://localhost/files/ENCFF000RCC/@@download/ENCFF000RCC.rcc\nhttp://localhost/files/ENCFF000DAT/@@download/ENCFF000DAT.idat\nhttp://localhost/files/SRR1270627/@@download/SRR1270627.sra\nhttp://localhost/files/ENCFF002REP/@@download/ENCFF002REP.bam\nhttp://localhost/files/ENCFF010EPI/@@download/ENCFF010EPI.bam\nhttp://localhost/files/ENCFF790SUA/@@download/ENCFF790SUA.fastq.gz\nhttp://localhost/files/ENCFF009EPI/@@download/ENCFF009EPI.bam\nhttp://localhost/files/ENCFF001EPI/@@download/ENCFF001EPI.fastq.gz\nhttp://localhost/files/ENCFF002EPI/@@download/ENCFF002EPI.bam\nhttp://localhost/files/ENCFF558BPA/@@download/ENCFF558BPA.fastq.gz\nhttp://localhost/files/ENCFF011EPI/@@download/ENCFF011EPI.bam\nhttp://localhost/files/ENCFF001MRN/@@download/ENCFF001MRN.fastq.gz\nhttp://localhost/files/ENCFF002MRN/@@download/ENCFF002MRN.fastq.gz\nhttp://localhost/files/ENCFF003MRN/@@download/ENCFF003MRN.bam\nhttp://localhost/files/ENCFF004MRN/@@download/ENCFF004MRN.bam\nhttp://localhost/files/ENCFF005MRN/@@download/ENCFF005MRN.tsv\nhttp://localhost/files/ENCFF006MRN/@@download/ENCFF006MRN.tsv\nhttp://localhost/files/ENCFF003EPI/@@download/ENCFF003EPI.fastq.gz\nhttp://localhost/files/ENCFF004EPI/@@download/ENCFF004EPI.bam\nhttp://localhost/files/ENCFF001ISO/@@download/ENCFF001ISO.fastq.gz\nhttp://localhost/files/ENCFF002ISO/@@download/ENCFF002ISO.fastq.gz\nhttp://localhost/files/ENCFF003ISO/@@download/ENCFF003ISO.bam\nhttp://localhost/files/ENCFF004ISO/@@download/ENCFF004ISO.bam\nhttp://localhost/files/ENCFF005ISO/@@download/ENCFF005ISO.tsv\nhttp://localhost/files/ENCFF006ISO/@@download/ENCFF006ISO.tsv\nhttp://localhost/files/ENCFF007ISO/@@download/ENCFF007ISO.db\nhttp://localhost/files/ENCFF005EPI/@@download/ENCFF005EPI.fastq.gz\nhttp://localhost/files/ENCFF002COS/@@download/ENCFF002COS.bed.gz\nhttp://localhost/files/ENCFF003COS/@@download/ENCFF003COS.bigBed\nhttp://localhost/files/ENCFF006EPI/@@download/ENCFF006EPI.fastq.gz\nhttp://localhost/files/ENCFF007EPI/@@download/ENCFF007EPI.fastq.gz\nhttp://localhost/files/ENCFF001CON/@@download/ENCFF001CON.bam\nhttp://localhost/files/ENCFF003CON/@@download/ENCFF003CON.bam\nhttp://localhost/files/ENCFF001REP/@@download/ENCFF001REP.bam\nhttp://localhost/files/ENCFF003REP/@@download/ENCFF003REP.bam\nhttp://localhost/files/ENCFF008EPI/@@download/ENCFF008EPI.bam\nhttp://localhost/files/ENCFF477MLC/@@download/ENCFF477MLC.fastq.gz\nhttp://localhost/files/ENCFF000LBC/@@download/ENCFF000LBC.csqual.gz\nhttp://localhost/files/ENCFF000LBB/@@download/ENCFF000LBB.csqual.gz\nhttp://localhost/files/ENCFF000LBA/@@download/ENCFF000LBA.csfasta.gz\nhttp://localhost/files/ENCFF000LAZ/@@download/ENCFF000LAZ.csfasta.gz\nhttp://localhost/files/ENCFF010LAO/@@download/ENCFF010LAO.csfasta.gz'),
    ('/batch_download/type=Experiment&award.project!=Roadmap', 'http://localhost/metadata/type%3DExperiment%26award.project%21%3DRoadmap/metadata.tsv\nhttp://localhost/files/ENCFF002MWZ/@@download/ENCFF002MWZ.bam\nhttp://localhost/files/ENCFF002MXF/@@download/ENCFF002MXF.fastq.gz\nhttp://localhost/files/ENCFF946MFS/@@download/ENCFF946MFS.tsv\nhttp://localhost/files/ENCFF413RGP/@@download/ENCFF413RGP.tsv\nhttp://localhost/files/ENCFF355OWW/@@download/ENCFF355OWW.hic\nhttp://localhost/files/ENCFF784GFP/@@download/ENCFF784GFP.hic\nhttp://localhost/files/ENCFF812THZ/@@download/ENCFF812THZ.hic\nhttp://localhost/files/ENCFF123HIC/@@download/ENCFF123HIC.txt\nhttp://localhost/files/ENCFF880XNW/@@download/ENCFF880XNW.bigBed\nhttp://localhost/files/ENCFF000VUS/@@download/ENCFF000VUS.bam\nhttp://localhost/files/ENCFF001MWZ/@@download/ENCFF001MWZ.bam\nhttp://localhost/files/ENCFF001MXA/@@download/ENCFF001MXA.bam\nhttp://localhost/files/ENCFF001MXD/@@download/ENCFF001MXD.bigWig\nhttp://localhost/files/ENCFF002MXD/@@download/ENCFF002MXD.bigWig\nhttp://localhost/files/ENCFF003MXD/@@download/ENCFF003MXD.bigWig\nhttp://localhost/files/ENCFF001MXF/@@download/ENCFF001MXF.fastq.gz\nhttp://localhost/files/ENCFF001MXH/@@download/ENCFF001MXH.fastq.gz\nhttp://localhost/files/ENCFF000VWO/@@download/ENCFF000VWO.bam\nhttp://localhost/files/ENCFF001MXE/@@download/ENCFF001MXE.bam\nhttp://localhost/files/ENCFF001MXG/@@download/ENCFF001MXG.bigWig\nhttp://localhost/files/ENCFF001MYM/@@download/ENCFF001MYM.fastq.gz\nhttp://localhost/files/ENCFF001RCT/@@download/ENCFF001RCT.fastq.gz\nhttp://localhost/files/ENCFF001RCU/@@download/ENCFF001RCU.fastq.gz\nhttp://localhost/files/ENCFF001RCV/@@download/ENCFF001RCV.bam\nhttp://localhost/files/ENCFF001RCW/@@download/ENCFF001RCW.bam\nhttp://localhost/files/ENCFF001RCY/@@download/ENCFF001RCY.bigWig\nhttp://localhost/files/ENCFF001RCZ/@@download/ENCFF001RCZ.bigWig\nhttp://localhost/files/ENCFF130XXF/@@download/ENCFF130XXF.bigWig\nhttp://localhost/files/ENCFF854KQX/@@download/ENCFF854KQX.bigWig\nhttp://localhost/files/ENCFF119LNR/@@download/ENCFF119LNR.bigWig\nhttp://localhost/files/ENCFF000RCC/@@download/ENCFF000RCC.rcc\nhttp://localhost/files/ENCFF000DAT/@@download/ENCFF000DAT.idat\nhttp://localhost/files/SRR1270627/@@download/SRR1270627.sra\nhttp://localhost/files/ENCFF002REP/@@download/ENCFF002REP.bam\nhttp://localhost/files/ENCFF010EPI/@@download/ENCFF010EPI.bam\nhttp://localhost/files/ENCFF790SUA/@@download/ENCFF790SUA.fastq.gz\nhttp://localhost/files/ENCFF002CON/@@download/ENCFF002CON.bam\nhttp://localhost/files/ENCFF009EPI/@@download/ENCFF009EPI.bam\nhttp://localhost/files/ENCFF001EPI/@@download/ENCFF001EPI.fastq.gz\nhttp://localhost/files/ENCFF002EPI/@@download/ENCFF002EPI.bam\nhttp://localhost/files/ENCFF558BPA/@@download/ENCFF558BPA.fastq.gz\nhttp://localhost/files/ENCFF011EPI/@@download/ENCFF011EPI.bam\nhttp://localhost/files/ENCFF003EPI/@@download/ENCFF003EPI.fastq.gz\nhttp://localhost/files/ENCFF004EPI/@@download/ENCFF004EPI.bam\nhttp://localhost/files/ENCFF005EPI/@@download/ENCFF005EPI.fastq.gz\nhttp://localhost/files/ENCFF002COS/@@download/ENCFF002COS.bed.gz\nhttp://localhost/files/ENCFF003COS/@@download/ENCFF003COS.bigBed\nhttp://localhost/files/ENCFF006EPI/@@download/ENCFF006EPI.fastq.gz\nhttp://localhost/files/ENCFF007EPI/@@download/ENCFF007EPI.fastq.gz\nhttp://localhost/files/ENCFF001CON/@@download/ENCFF001CON.bam\nhttp://localhost/files/ENCFF003CON/@@download/ENCFF003CON.bam\nhttp://localhost/files/ENCFF001REP/@@download/ENCFF001REP.bam\nhttp://localhost/files/ENCFF003REP/@@download/ENCFF003REP.bam\nhttp://localhost/files/ENCFF008EPI/@@download/ENCFF008EPI.bam'),
    ('/batch_download/type=Experiment&biosample_ontology.term_name!=basal cell of epithelium of terminal bronchiole', 'http://localhost/metadata/type%3DExperiment%26biosample_ontology.term_name%21%3Dbasal%20cell%20of%20epithelium%20of%20terminal%20bronchiole/metadata.tsv\nhttp://localhost/files/ENCFF002MWZ/@@download/ENCFF002MWZ.bam\nhttp://localhost/files/ENCFF002MXF/@@download/ENCFF002MXF.fastq.gz\nhttp://localhost/files/ENCFF946MFS/@@download/ENCFF946MFS.tsv\nhttp://localhost/files/ENCFF413RGP/@@download/ENCFF413RGP.tsv\nhttp://localhost/files/ENCFF355OWW/@@download/ENCFF355OWW.hic\nhttp://localhost/files/ENCFF784GFP/@@download/ENCFF784GFP.hic\nhttp://localhost/files/ENCFF812THZ/@@download/ENCFF812THZ.hic\nhttp://localhost/files/ENCFF123HIC/@@download/ENCFF123HIC.txt\nhttp://localhost/files/ENCFF880XNW/@@download/ENCFF880XNW.bigBed\nhttp://localhost/files/ENCFF001MWZ/@@download/ENCFF001MWZ.bam\nhttp://localhost/files/ENCFF001MXA/@@download/ENCFF001MXA.bam\nhttp://localhost/files/ENCFF001MXD/@@download/ENCFF001MXD.bigWig\nhttp://localhost/files/ENCFF002MXD/@@download/ENCFF002MXD.bigWig\nhttp://localhost/files/ENCFF003MXD/@@download/ENCFF003MXD.bigWig\nhttp://localhost/files/ENCFF001MXF/@@download/ENCFF001MXF.fastq.gz\nhttp://localhost/files/ENCFF001MXH/@@download/ENCFF001MXH.fastq.gz\nhttp://localhost/files/ENCFF000VWO/@@download/ENCFF000VWO.bam\nhttp://localhost/files/ENCFF001MXE/@@download/ENCFF001MXE.bam\nhttp://localhost/files/ENCFF001MXG/@@download/ENCFF001MXG.bigWig\nhttp://localhost/files/ENCFF001MYM/@@download/ENCFF001MYM.fastq.gz\nhttp://localhost/files/ENCFF001RCT/@@download/ENCFF001RCT.fastq.gz\nhttp://localhost/files/ENCFF001RCU/@@download/ENCFF001RCU.fastq.gz\nhttp://localhost/files/ENCFF001RCV/@@download/ENCFF001RCV.bam\nhttp://localhost/files/ENCFF001RCW/@@download/ENCFF001RCW.bam\nhttp://localhost/files/ENCFF001RCY/@@download/ENCFF001RCY.bigWig\nhttp://localhost/files/ENCFF001RCZ/@@download/ENCFF001RCZ.bigWig\nhttp://localhost/files/ENCFF000RCC/@@download/ENCFF000RCC.rcc\nhttp://localhost/files/ENCFF000DAT/@@download/ENCFF000DAT.idat\nhttp://localhost/files/SRR1270627/@@download/SRR1270627.sra\nhttp://localhost/files/ENCFF002REP/@@download/ENCFF002REP.bam\nhttp://localhost/files/ENCFF010EPI/@@download/ENCFF010EPI.bam\nhttp://localhost/files/ENCFF790SUA/@@download/ENCFF790SUA.fastq.gz\nhttp://localhost/files/ENCFF002CON/@@download/ENCFF002CON.bam\nhttp://localhost/files/ENCFF009EPI/@@download/ENCFF009EPI.bam\nhttp://localhost/files/ENCFF001EPI/@@download/ENCFF001EPI.fastq.gz\nhttp://localhost/files/ENCFF002EPI/@@download/ENCFF002EPI.bam\nhttp://localhost/files/ENCFF558BPA/@@download/ENCFF558BPA.fastq.gz\nhttp://localhost/files/ENCFF011EPI/@@download/ENCFF011EPI.bam\nhttp://localhost/files/ENCFF001MRN/@@download/ENCFF001MRN.fastq.gz\nhttp://localhost/files/ENCFF002MRN/@@download/ENCFF002MRN.fastq.gz\nhttp://localhost/files/ENCFF003MRN/@@download/ENCFF003MRN.bam\nhttp://localhost/files/ENCFF004MRN/@@download/ENCFF004MRN.bam\nhttp://localhost/files/ENCFF005MRN/@@download/ENCFF005MRN.tsv\nhttp://localhost/files/ENCFF006MRN/@@download/ENCFF006MRN.tsv\nhttp://localhost/files/ENCFF003EPI/@@download/ENCFF003EPI.fastq.gz\nhttp://localhost/files/ENCFF004EPI/@@download/ENCFF004EPI.bam\nhttp://localhost/files/ENCFF001ISO/@@download/ENCFF001ISO.fastq.gz\nhttp://localhost/files/ENCFF002ISO/@@download/ENCFF002ISO.fastq.gz\nhttp://localhost/files/ENCFF003ISO/@@download/ENCFF003ISO.bam\nhttp://localhost/files/ENCFF004ISO/@@download/ENCFF004ISO.bam\nhttp://localhost/files/ENCFF005ISO/@@download/ENCFF005ISO.tsv\nhttp://localhost/files/ENCFF006ISO/@@download/ENCFF006ISO.tsv\nhttp://localhost/files/ENCFF007ISO/@@download/ENCFF007ISO.db\nhttp://localhost/files/ENCFF005EPI/@@download/ENCFF005EPI.fastq.gz\nhttp://localhost/files/ENCFF002COS/@@download/ENCFF002COS.bed.gz\nhttp://localhost/files/ENCFF003COS/@@download/ENCFF003COS.bigBed\nhttp://localhost/files/ENCFF006EPI/@@download/ENCFF006EPI.fastq.gz\nhttp://localhost/files/ENCFF007EPI/@@download/ENCFF007EPI.fastq.gz\nhttp://localhost/files/ENCFF001CON/@@download/ENCFF001CON.bam\nhttp://localhost/files/ENCFF003CON/@@download/ENCFF003CON.bam\nhttp://localhost/files/ENCFF001REP/@@download/ENCFF001REP.bam\nhttp://localhost/files/ENCFF003REP/@@download/ENCFF003REP.bam\nhttp://localhost/files/ENCFF008EPI/@@download/ENCFF008EPI.bam\nhttp://localhost/files/ENCFF959VGP/@@download/ENCFF959VGP.fastq.gz\nhttp://localhost/files/ENCFF477MLC/@@download/ENCFF477MLC.fastq.gz\nhttp://localhost/files/ENCFF000LBC/@@download/ENCFF000LBC.csqual.gz\nhttp://localhost/files/ENCFF000LBB/@@download/ENCFF000LBB.csqual.gz\nhttp://localhost/files/ENCFF000LBA/@@download/ENCFF000LBA.csfasta.gz\nhttp://localhost/files/ENCFF000LAZ/@@download/ENCFF000LAZ.csfasta.gz\nhttp://localhost/files/ENCFF010LAO/@@download/ENCFF010LAO.csfasta.gz'),
    ('/batch_download/type=Experiment&assembly=hg19&assembly=GRCh38', 'http://localhost/metadata/type%3DExperiment%26assembly%3Dhg19%26assembly%3DGRCh38/metadata.tsv\nhttp://localhost/files/ENCFF946MFS/@@download/ENCFF946MFS.tsv\nhttp://localhost/files/ENCFF413RGP/@@download/ENCFF413RGP.tsv\nhttp://localhost/files/ENCFF355OWW/@@download/ENCFF355OWW.hic\nhttp://localhost/files/ENCFF784GFP/@@download/ENCFF784GFP.hic\nhttp://localhost/files/ENCFF812THZ/@@download/ENCFF812THZ.hic\nhttp://localhost/files/ENCFF123HIC/@@download/ENCFF123HIC.txt\nhttp://localhost/files/ENCFF880XNW/@@download/ENCFF880XNW.bigBed\nhttp://localhost/files/ENCFF000VUS/@@download/ENCFF000VUS.bam\nhttp://localhost/files/ENCFF000VWO/@@download/ENCFF000VWO.bam\nhttp://localhost/files/ENCFF001RCT/@@download/ENCFF001RCT.fastq.gz\nhttp://localhost/files/ENCFF001RCU/@@download/ENCFF001RCU.fastq.gz\nhttp://localhost/files/ENCFF001RCV/@@download/ENCFF001RCV.bam\nhttp://localhost/files/ENCFF001RCW/@@download/ENCFF001RCW.bam\nhttp://localhost/files/ENCFF001RCY/@@download/ENCFF001RCY.bigWig\nhttp://localhost/files/ENCFF001RCZ/@@download/ENCFF001RCZ.bigWig\nhttp://localhost/files/ENCFF130XXF/@@download/ENCFF130XXF.bigWig\nhttp://localhost/files/ENCFF854KQX/@@download/ENCFF854KQX.bigWig\nhttp://localhost/files/ENCFF119LNR/@@download/ENCFF119LNR.bigWig\nhttp://localhost/files/SRR1270627/@@download/SRR1270627.sra\nhttp://localhost/files/ENCFF002REP/@@download/ENCFF002REP.bam\nhttp://localhost/files/ENCFF010EPI/@@download/ENCFF010EPI.bam\nhttp://localhost/files/ENCFF002CON/@@download/ENCFF002CON.bam\nhttp://localhost/files/ENCFF009EPI/@@download/ENCFF009EPI.bam\nhttp://localhost/files/ENCFF001EPI/@@download/ENCFF001EPI.fastq.gz\nhttp://localhost/files/ENCFF002EPI/@@download/ENCFF002EPI.bam\nhttp://localhost/files/ENCFF011EPI/@@download/ENCFF011EPI.bam\nhttp://localhost/files/ENCFF001MRN/@@download/ENCFF001MRN.fastq.gz\nhttp://localhost/files/ENCFF002MRN/@@download/ENCFF002MRN.fastq.gz\nhttp://localhost/files/ENCFF003MRN/@@download/ENCFF003MRN.bam\nhttp://localhost/files/ENCFF004MRN/@@download/ENCFF004MRN.bam\nhttp://localhost/files/ENCFF005MRN/@@download/ENCFF005MRN.tsv\nhttp://localhost/files/ENCFF006MRN/@@download/ENCFF006MRN.tsv\nhttp://localhost/files/ENCFF003EPI/@@download/ENCFF003EPI.fastq.gz\nhttp://localhost/files/ENCFF004EPI/@@download/ENCFF004EPI.bam\nhttp://localhost/files/ENCFF001ISO/@@download/ENCFF001ISO.fastq.gz\nhttp://localhost/files/ENCFF002ISO/@@download/ENCFF002ISO.fastq.gz\nhttp://localhost/files/ENCFF003ISO/@@download/ENCFF003ISO.bam\nhttp://localhost/files/ENCFF004ISO/@@download/ENCFF004ISO.bam\nhttp://localhost/files/ENCFF005ISO/@@download/ENCFF005ISO.tsv\nhttp://localhost/files/ENCFF006ISO/@@download/ENCFF006ISO.tsv\nhttp://localhost/files/ENCFF007ISO/@@download/ENCFF007ISO.db\nhttp://localhost/files/ENCFF002COS/@@download/ENCFF002COS.bed.gz\nhttp://localhost/files/ENCFF003COS/@@download/ENCFF003COS.bigBed\nhttp://localhost/files/ENCFF001CON/@@download/ENCFF001CON.bam\nhttp://localhost/files/ENCFF003CON/@@download/ENCFF003CON.bam\nhttp://localhost/files/ENCFF001REP/@@download/ENCFF001REP.bam\nhttp://localhost/files/ENCFF003REP/@@download/ENCFF003REP.bam\nhttp://localhost/files/ENCFF008EPI/@@download/ENCFF008EPI.bam'),
    ('/batch_download/type=Experiment&files.file_type=bed bed6+', 'http://localhost/metadata/type%3DExperiment%26files.file_type%3Dbed%20bed6%2B/metadata.tsv'),
    ('/batch_download/type=Annotation&organism.scientific_name!=Homo sapiens&organism.scientific_name=Mus musculus', 'http://localhost/metadata/type%3DAnnotation%26organism.scientific_name%21%3DHomo%20sapiens%26organism.scientific_name%3DMus%20musculus/metadata.tsv\nhttp://localhost/files/ENCFF015OKV/@@download/ENCFF015OKV.bed.gz'),
])
def test_batch_download_files(testapp, workbook, test_url, expected):
    response = testapp.get(test_url)
    assert response.body.decode('utf-8') == expected


@pytest.mark.parametrize('test_url, expected_row_1, expected_row_n', [
    ('/metadata/type=Experiment&format=json/metadata.tsv', 'ENCFF002MWZ\tbam\talignments\tENCSR001ADI\tChIP-seq\tEFO:0005233\tCH12.LX cell\tcell line\tMus musculus\t\t\t\t\t\t\t\t\t\tH3K4me3-mouse\tDNA\t\t\t\t\tFalse\t2016-01-01\tENCODE\t\t\t\t1\t1\t\t\t\t\t\t\t20\tJ. Michael Cherry, Stanford\t91ae74b6e11515393507f4ebfa66d78d\t\thttp://localhost/files/ENCFF002MWZ/@@download/ENCFF002MWZ.bam\tmm9\t\tIllumina Genome Analyzer II\t\treleased\t\tinconsistent platforms\tmismatched file status, mismatched status, missing derived_from\tinconsistent sex\tinconsistent donor, missing antibody', 'ENCFF000LAZ\tcsfasta\treads\tENCSR751YPU\tDNase-seq\tUBERON:0001891\tmidbrain\ttissue\tHomo sapiens\t\t\t\t\t\t\t\t\t\t\tDNA\t\t\t\t\tFalse\t2015-08-31\tRoadmap\t\t\t\t1\t1\t25\t\tpaired-ended\t2\tENCFF000LBA\t\t2314662239\tMichael Snyder, Stanford\t20125f316dafa4daed390afae59e7bb2\t\thttp://localhost/files/ENCFF000LAZ/@@download/ENCFF000LAZ.csfasta.gz\t\t\tApplied Biosystems SOLiD System 3 Plus\t\treleased\t\t\tmismatched status, experiment not submitted to GEO\tmissing documents, unreplicated experiment',),
    ('/metadata/type=Experiment&biosample_ontology.term_name!=basal cell of epithelium of terminal bronchiole&format=json/metadata.tsv', 'ENCFF002MWZ\tbam\talignments\tENCSR001ADI\tChIP-seq\tEFO:0005233\tCH12.LX cell\tcell line\tMus musculus\t\t\t\t\t\t\t\t\t\tH3K4me3-mouse\tDNA\t\t\t\t\tFalse\t2016-01-01\tENCODE\t\t\t\t1\t1\t\t\t\t\t\t\t20\tJ. Michael Cherry, Stanford\t91ae74b6e11515393507f4ebfa66d78d\t\thttp://localhost/files/ENCFF002MWZ/@@download/ENCFF002MWZ.bam\tmm9\t\tIllumina Genome Analyzer II\t\treleased\t\tinconsistent platforms\tmismatched status, missing derived_from, mismatched file status\tinconsistent sex\tinconsistent donor, missing antibody', 'ENCFF000LAZ\tcsfasta\treads\tENCSR751YPU\tDNase-seq\tUBERON:0001891\tmidbrain\ttissue\tHomo sapiens\t\t\t\t\t\t\t\t\t\t\tDNA\t\t\t\t\tFalse\t2015-08-31\tRoadmap\t\t\t\t1\t1\t25\t\tpaired-ended\t2\tENCFF000LBA\t\t2314662239\tMichael Snyder, Stanford\t20125f316dafa4daed390afae59e7bb2\t\thttp://localhost/files/ENCFF000LAZ/@@download/ENCFF000LAZ.csfasta.gz\t\t\tApplied Biosystems SOLiD System 3 Plus\t\treleased\t\t\tmismatched status, experiment not submitted to GEO\tmissing documents, unreplicated experiment',),
    ('/metadata/type=Experiment&assembly=hg19&assembly=GRCh38&format=json/metadata.tsv', 'ENCFF946MFS\ttsv\tgene quantifications\tENCSR000AEM\tRNA-seq\tEFO:0002067\tK562\tcell line\tHomo sapiens\t\t\t\t\t\t\t\t\t\t\tpolyadenylated mRNA\t\tmiRNeasy Mini kit (QIAGEN cat#:217004) (varies, will be same as matched RAMPAGE)\tmiRNeasy Mini kit (QIAGEN cat#:217004) (varies, will be same as matched RAMPAGE)\t\tTrue\t2016-01-01\tENCODE\t\t\t\t2\t1\t\t\t\t\t\t\t9528125\tJ. Michael Cherry, Stanford\tb6bda8755cea56d4741fc027442d370a\t\thttp://localhost/files/ENCFF946MFS/@@download/ENCFF946MFS.tsv\thg19\tV19\t\t\treleased\t\tmissing analysis_step_run\texperiment not submitted to GEO, missing derived_from, mismatched status, missing RIN, mismatched file status\tmissing spikeins\t', 'ENCFF008EPI\tbam\talignments\tENCSR006EPI\tChIP-seq\tEFO:0002067\tK562\tcell line\tHomo sapiens\tdexamethasone\t60 nM\t8 hour\t\t\t\t\t\t\tH3K36me3-human\tDNA\t\t\t\t\tFalse\t2016-01-01\tENCODE\t\t\t\t\t\t\t\t\t\t\t\t473944988\tRobert Waterston, UW\t91be44b6e11514393507f4ebfa66d54a\t\thttp://localhost/files/ENCFF008EPI/@@download/ENCFF008EPI.bam\thg19\t\t\t\treleased\t\t\tmissing raw data in replicate, mismatched status, missing derived_from, experiment not submitted to GEO, characterization(s) pending review\tmissing possible_controls\tinconsistent target',),
    ('/metadata/type=Annotation&organism.scientific_name%21=Homo+sapiens&organism.scientific_name=Mus+musculus&format=json/metadata.tsv', 'ENCFF015OKV\tbed enhancer predictions\tpredicted heart enhancers\tENCSR356VQT\tlong-range chromatin interactions\tSamtools, Picard\t2\tUBERON:0000948\theart\ttissue\tembryonic\t11.5\tday\tMus musculus\t\t2015-02-27\tENCODE\tJ. Michael Cherry, Stanford\ta5f849c78025c80dca58771492c97318\t\thttp://localhost/files/ENCFF015OKV/@@download/ENCFF015OKV.bed.gz\tmm10\t\treleased\t\t\t1544154147\tmissing analysis_step_run\tmismatched status, missing derived_from', 'ENCFF015OKV\tbed enhancer predictions\tpredicted heart enhancers\tENCSR356VQT\tlong-range chromatin interactions\tSamtools, Picard\t2\tUBERON:0000948\theart\ttissue\tembryonic\t11.5\tday\tMus musculus\t\t2015-02-27\tENCODE\tJ. Michael Cherry, Stanford\ta5f849c78025c80dca58771492c97318\t\thttp://localhost/files/ENCFF015OKV/@@download/ENCFF015OKV.bed.gz\tmm10\t\treleased\t\t\t1544154147\tmissing analysis_step_run\tmismatched status, missing derived_from',),
])
def test_batch_download_meta_files(testapp, workbook, test_url, expected_row_1, expected_row_n):
    # compare only ids, as it is the only essential field
    response = testapp.get(test_url)
    target = response.body.decode('utf-8').strip().split('\n')
    assert expected_row_1[:11] == target[1][:11]
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


@pytest.mark.parametrize('test_url,expected', [
    ('/report.tsv?type=User', '2019-06-12 15:57:11.837219\thttp://localhost/report/?type=User&limit=all\r\nID\tTitle\r\n/users/4fa80b58-322a-4c8e-9b33-d2a00c8405bd/\tBrenton Graveley\r\n/users/0d48e8c4-5954-4bf5-8c75-1e386eb27e31/\tAleksandar Milosavljevic\r\n/users/81a6cc12-2847-4e2e-8f2c-f566699eb29e/\tElit Iaculis\r\n/users/5e99a8f5-2808-43c6-b1ba-13d5d110a6c1/\tMi Neque-Primis\r\n/users/9f161054-aa2c-40b7-8239-04eb7f08b15d/\tAli Mortazavi\r\n/users/4c23ec32-c7c8-4ac0-affb-04befcc881d4/\tBibendum Sodales-Luctus\r\n/users/aa57ecb5-3d0e-4b1f-9608-665785270ad7/\tBradley Bernstein\r\n/users/3787a0ac-f13a-40fc-a524-69628b04cd59/\tInceptos Nullam\r\n/users/ea5e2bd6-be7a-4b18-a2e8-dee86005422f/\tBing Ren\r\n/users/4ddf3240-907d-40c1-b4fe-4c1547a89b0e/\tMagnis Senectus\r\n/users/e74547f3-1676-43de-bcfc-9b946f0024c9/\tGregory Crawford\r\n/users/de7f5444-ee87-4e4e-b621-9c136ea1d4b1/\tChris Burge\r\n/users/a53cb5c0-62fd-4da8-a503-48211db16326/\tJoe Ecker\r\n/users/29f3829e-a942-4175-9637-1b691ff268e5/\tTorquent Fusce\r\n/users/ce2bde01-07ec-4b8a-b179-554ef95b71dd/\tEuismod Platea-Ad\r\n/users/1ec85168-059e-407e-9cb1-f96200e72499/\tFaucibus Hac\r\n/users/6667a92a-d202-493a-8c7d-7a56d1380356/\tKhine Lin\r\n/users/ec729133-c5f3-4c53-be5b-a5ea73a367dd/\tJohn Stamatoyannopoulos\r\n/users/09d05b87-4d30-4dfb-b243-3327005095f2/\tThomas Gingeras\r\n/users/4640ff09-f1b4-4cc4-9167-6a36f2b8d9bc/\tGene Yeo\r\n/users/a62cfec5-57a0-45ab-b943-8ca0e0057bb6/\tRichard Myers\r\n/users/860c4750-8d3c-40f5-8f2c-90c5e5d19e88/\tJ. Michael Cherry\r\n/users/f5b7857d-208e-4acc-ac4d-4c2520814fe1/\tErat Commodo\r\n/users/8be3a346-1440-4bd6-85e8-3236ae469c0c/\tJusto Lobortis\r\n/users/f56a4449-1a87-4824-8a34-9c6917544b1b/\tJason Lieb\r\n/users/073079fd-d589-4663-9fd4-3d488208d075/\tSociis Non-Urna\r\n/users/0abbd494-b852-433c-b360-93996f679dae/\tAd Est\r\n/users/8f9f5064-3e2f-4182-8925-c66ab6b24e15/\tFringilla Enim\r\n/users/864c3e01-dce4-4f41-925a-383ccc82ee5d/\tLen Pennacchio\r\n/users/077c758e-f7e9-47f0-bf8d-c862bc45bde8/\tJob Dekker\r\n/users/6282e6de-8696-4fa1-91e4-415e729558e9/\tVishwanath Iyer\r\n/users/df9f3c8e-b819-4885-8f16-08f6ef0001e8/\tTincidunt Volutpat-Ullamcorper\r\n/users/b0a10b06-9ad0-4e59-aac9-a7797781d29e/\tKevin White\r\n/users/cc0edf23-b9fd-48e2-8609-54ad07bdd5f7/\tDonec Arcu\r\n/users/5d76a10b-1f18-4544-a00e-d0d83f1021a1/\tHabitasse Laoreet\r\n/users/7e763d5a-634b-4181-a812-4361183359e9/\tNuech Shueng\r\n/users/9a144e02-c84f-4cc8-b474-49e5c8afa7c7/\tGreg Cooper\r\n/users/f74511d2-d30a-44d9-8e54-79104353e7af/\tNonummy Eros-Cursus\r\n/users/ff7b77e7-bb55-4307-b665-814c9f1e65fb/\tTortor Torquent\r\n/users/d48be354-153c-4ca8-acaa-bf067c1fd836/\tAenean Et-Quisque\r\n/users/45cd6450-c5f0-49dc-9a68-d233f51039c5/\tUlugbek Baymuradov\r\n/users/95f5b53d-d206-4ec3-97ba-7c2abd84aab5/\tParturient Urna\r\n/users/046eea49-9ab6-4e4d-ba42-be8f8fc92de3/\tRoderic Guigo\r\n/users/599e4901-78bf-422f-b65d-f3443c6a6450/\tMagna Bibendum\r\n/users/627eedbc-7cb3-4de3-9743-a86266e435a6/\tForrest Tanaka\r\n/users/7e944358-625c-426c-975c-7d875e22f753/\tZachary Myers\r\n/users/6183c69b-e862-41ab-99be-69214fc9f27e/\tJohn Rinn\r\n/users/261fcf1a-04d9-4879-a56a-320915587586/\tTim Reddy\r\n/users/56ad466b-8711-4b82-8f2c-8db3dc5862fd/\tPhilip Adenekan\r\n/users/7dfbe70c-995d-4bc5-94c3-7d39d2baf001/\tTim Dreszer\r\n/users/473a72c0-6f20-4f81-9093-198e92fee470/\tPaul Sud\r\n/users/746eef27-d857-4b38-a469-cac93fb02164/\tW. James Kent\r\n/users/0598c868-0b4a-4c5b-9112-8f85c5de5374/\tBarbara Wold\r\n/users/75659c39-eaea-47b7-ba26-92e9ff183e6c/\tCasey Litton\r\n/users/76091563-a959-4a9c-929c-9acfa1a0a078/\tYunhai Luo\r\n/users/43f2f757-5cbf-490a-9787-a1ee85a4cdcd/\tJennifer Jou\r\n/users/27e105ca-c741-4459-bf17-90e003508639/\tMichael Snyder\r\n/users/94c85be4-e034-4647-b6b3-15055701a656/\tXiang-Dong Fu\r\n/users/6bae687f-b77a-46b9-af0e-a02c135cf42e/\tMeenakshi Kagda\r\n/users/97d2dfcd-0919-4a27-9797-a6ef25f470a2/\tWeiwei Zhong\r\n/users/9b52a07a-e46f-4b74-bbe3-e5fd45b768e0/\tMaecenas Montes\r\n/users/6800d05f-7213-48b1-9ad8-254c73c5b83f/\tJ. Seth Strattan\r\n/users/332d0e03-a907-4f53-8358-bb00118277c8/\tJason Hilton\r\n/users/2eb068c5-b7a6-48ec-aca2-c439e4dabb08/\tPeggy Farnham\r\n/users/98fb23d3-0d79-4c3d-981d-01539e6589f1/\tIdan Gabdank\r\n/users/0a61ce48-e33d-48bf-8b6b-b085b722b467/\tRoss Hardison\r\n/users/986b362f-4eb6-4a9c-8173-3ab267307e3b/\tBen Hitz\r\n/users/4b135999-ec2d-41b5-b962-fc6a5f8934ac/\tSherman Weissman\r\n/users/04d1cd63-d5d9-4ea4-8d9b-7adad3d5377d/\tDavid Glick\r\n/users/9e889180-9db1-11e4-bd06-0800200c9a66/\tVenkat Malladi\r\n/users/7e95dcd6-9c35-4082-9c53-09d14c5752be/\tKeenan Graham\r\n/users/4136f132-304e-4ddd-b87a-db04605f47b7/\tKriti Jain\r\n/users/af989110-67d2-4c8b-87f0-38d9d6d31868/\tEmma O\'Neill\r\n/users/454435fe-702d-4657-a955-641e5631982c/\tJennifer Zamanian\r\n'),
    ('/report/?type=User&lab.title=Sherman+Weissman%2C+Yale', {"facets": [{"type": "terms", "total": 1, "field": "type", "appended": "false", "terms": [{"doc_count": 1, "key": "User"}], "title": "Data Type"}, {"type": "terms", "total": 74, "field": "lab.title", "appended": "false", "terms": [{"doc_count": 32, "key": "J. Michael Cherry, Stanford"}, {"doc_count": 3, "key": "Michael Snyder, Stanford"}, {"doc_count": 2, "key": "Bradley Bernstein, Broad"}, {"doc_count": 2, "key": "Brenton Graveley, UConn"}, {"doc_count": 2, "key": "John Stamatoyannopoulos, UW"}, {"doc_count": 2, "key": "Kevin White, UChicago"}, {"doc_count": 2, "key": "Len Pennacchio, JGI"}, {"doc_count": 2, "key": "Richard Myers, HAIB"}, {"doc_count": 2, "key": "Roderic Guigo, CRG"}, {"doc_count": 2, "key": "Thomas Gingeras, CSHL"}, {"doc_count": 2, "key": "W. James Kent, UCSC"}, {"doc_count": 2, "key": "Xiang-Dong Fu, UCSD"}, {"doc_count": 1, "key": "Ali Mortazavi, UCI"}, {"doc_count": 1, "key": "Barbara Wold, Caltech"}, {"doc_count": 1, "key": "Bing Ren, UCSD"}, {"doc_count": 1, "key": "Chris Burge, MIT"}, {"doc_count": 1, "key": "ENCODE2 Project, UCSC"}, {"doc_count": 1, "key": "Gene Yeo, UCSD"}, {"doc_count": 1, "key": "Greg Cooper, HAIB"}, {"doc_count": 1, "key": "Gregory Crawford, Duke"}, {"doc_count": 1, "key": "Jason Lieb, UNC"}, {"doc_count": 1, "key": "Job Dekker, UMass"}, {"doc_count": 1, "key": "Joe Ecker, Salk"}, {"doc_count": 1, "key": "John Rinn, Broad"}, {"doc_count": 1, "key": "Peggy Farnham, USC"}, {"doc_count": 1, "key": "Roadmap Epigenomics, Baylor"}, {"doc_count": 1, "key": "Robert Waterston, UW"}, {"doc_count": 1, "key": "Ross Hardison, PennState"}, {"doc_count": 1, "key": "Sherman Weissman, Yale"}, {"doc_count": 1, "key": "Tim Reddy, Duke"}, {"doc_count": 1, "key": "Vishwanath Iyer, UTA"}], "title": "Lab"}, {"type": "terms", "total": 1, "field": "audit.ERROR.category", "appended": "false", "terms": [], "title": "Audit category: ERROR"}, {"type": "terms", "total": 1, "field": "audit.NOT_COMPLIANT.category", "appended": "false", "terms": [], "title": "Audit category: NOT COMPLIANT"}, {"type": "terms", "total": 1, "field": "audit.WARNING.category", "appended": "false", "terms": [], "title": "Audit category: WARNING"}], "@type": ["Report"], "total": 1, "views": [{"href": "/search/?type=User&lab.title=Sherman+Weissman%2C+Yale", "title": "View results as list", "icon": "list-alt"}], "@context": "/terms/", "clear_filters": "/search/?type=User", "sort": {"date_created": {"order": "desc", "unmapped_type": "keyword"}, "label": {"order": "asc", "missing": "_last", "unmapped_type": "keyword"}, "uuid": {"order": "desc", "unmapped_type": "keyword"}}, "notification": "Success", "columns": {"@id": {"title": "ID"}, "title": {"title": "Title"}}, "@graph": [{"@type": ["User", "Item"], "title": "Sherman Weissman", "@id": "/users/4b135999-ec2d-41b5-b962-fc6a5f8934ac/"}], "filters": [{"term": "User", "remove": "/report/?lab.title=Sherman+Weissman%2C+Yale", "field": "type"}, {"term": "Sherman Weissman, Yale", "remove": "/report/?type=User", "field": "lab.title"}], "non_sortable": ["pipeline_error_detail", "description", "notes"], "download_tsv": "/report.tsv?type=User&lab.title=Sherman+Weissman%2C+Yale", "@id": "/report/?type=User&lab.title=Sherman+Weissman%2C+Yale", "title": "Report"}),
])
def test_report_files_download(testapp, workbook, test_url, expected):
    response = testapp.get(test_url)
    body = response.body.decode('utf-8')

    if test_url == '/report.tsv?type=User':
        # excluding year that appears in index- 0:26
        assert body[27:] == expected[27:]
    else:
        body = json.loads(body)
        assert body == expected


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
