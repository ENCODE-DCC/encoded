# Use workbook fixture from BDD tests (including elasticsearch)
import json
import pytest
from encoded.tests.features.conftest import app
from encoded.tests.features.conftest import app_settings
from encoded.tests.features.conftest import workbook
from encoded.batch_download import lookup_column_value
from encoded.batch_download import restricted_files_present
from encoded.batch_download import files_prop_param_list


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

    #if test_url == '/batch_download/type=Annotation&organism.scientific_name!=Homo sapiens&organism.scientific_name=Mus musculus':
        #import pdb; pdb.set_trace();

    assert response.body.decode('utf-8') == expected


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
