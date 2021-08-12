import pytest

from encoded.tests.features.conftest import app, app_settings, index_workbook


pytestmark = [
    pytest.mark.indexing,
    pytest.mark.usefixtures('index_workbook'),
]


def test_reports_batch_download_view(index_workbook, testapp):
    r = testapp.get('/batch_download/?type=Experiment&status=released')
    lines = r.text.split('\n')
    assert lines[0] == (
        '"http://localhost/metadata/?type=Experiment&status=released"'
    )
    assert len(lines) >= 79
    assert 'http://localhost/files/ENCFF002MXF/@@download/ENCFF002MXF.fastq.gz' in lines


def test_reports_batch_download_header_and_rows(index_workbook, testapp):
    results = testapp.get('/batch_download/?type=Experiment')
    assert results.headers['Content-Type'] == 'text/plain; charset=UTF-8'
    assert results.headers['Content-Disposition'] == 'attachment; filename="files.txt"'
    lines = results.text.strip().split('\n')
    assert len(lines) > 0
    assert '/metadata/?type=Experiment' in lines[0]
    for line in lines[1:]:
        assert '@@download' in line, f'{line} not download'


def test_reports_batch_download_view_file_plus(index_workbook, testapp):
    r = testapp.get(
        '/batch_download/?type=Experiment&files.file_type=bigBed+bed3%2B&format=json'
    )
    lines = r.text.split('\n')
    assert lines[0] == (
        '"http://localhost/metadata/?type=Experiment&files.file_type=bigBed+bed3%2B&format=json"'
    )
    assert 'http://localhost/files/ENCFF880XNW/@@download/ENCFF880XNW.bigBed' in lines


def test_reports_batch_download_contains_all_values(index_workbook, testapp):
    from pkg_resources import resource_filename
    r = testapp.get('/batch_download/?type=Experiment')
    actual = r.text.strip().split('\n')
    expected_path = resource_filename('encoded', 'tests/data/inserts/expected_batch_download.tsv')
    # To write new expected_batch_download.tsv change 'r' to 'w' and f.write(r.text); return;
    with open(expected_path, 'r') as f:
        expected = [x.strip() for x in f.readlines()]
    assert set(actual) == set(expected), f'{set(actual) - set(expected)} not expected'


def test_reports_batch_download_contains_all_values_file_size_inequality(index_workbook, testapp):
    from pkg_resources import resource_filename
    r = testapp.get('/batch_download/?type=Experiment&files.file_size=lte:99')
    actual = r.text.strip().split('\n')
    expected_path = resource_filename('encoded', 'tests/data/inserts/expected_batch_download_file_size_inequality.tsv')
    # To write new expected_batch_download.tsv change 'r' to 'w' and f.write(r.text); return;
    with open(expected_path, 'r') as f:
        expected = [x.strip() for x in f.readlines()]
    assert set(actual) == set(expected), f'{set(actual) - set(expected)} not expected'


def test_reports_batch_download_contains_all_annotation_values(index_workbook, testapp):
    from pkg_resources import resource_filename
    r = testapp.get('/batch_download/?type=Annotation')
    actual = r.text.strip().split('\n')
    expected_path = resource_filename('encoded', 'tests/data/inserts/expected_annotation_batch_download.tsv')
    # To write new expected_batch_download.tsv change 'r' to 'w' and f.write(r.text); return;
    with open(expected_path, 'r') as f:
        expected = [x.strip() for x in f.readlines()]
    assert set(actual) == set(expected), f'{set(actual) - set(expected)} not expected'


def test_reports_batch_download_contains_all_publication_data_values(index_workbook, testapp):
    from pkg_resources import resource_filename
    r = testapp.get('/batch_download/?type=PublicationData&@id=/publication-data/ENCSR727WCB/')
    actual = r.text.strip().split('\n')
    expected_path = resource_filename('encoded', 'tests/data/inserts/expected_publication_data_batch_download.tsv')
    # To write new expected_batch_download.tsv change 'r' to 'w' and f.write(r.text); return;
    with open(expected_path, 'r') as f:
        expected = [x.strip() for x in f.readlines()]
    assert set(actual) == set(expected), f'{set(actual) - set(expected)} not expected'


def test_reports_batch_download_and_metadata_contain_same_number_of_results(index_workbook, testapp):
    batch_download_results = testapp.get('/batch_download/?type=Experiment').text.strip().split('\n')
    metadata_results = testapp.get('/metadata/?type=Experiment').text.strip().split('\n')
    assert len(batch_download_results) > 1
    assert len(metadata_results) == len(batch_download_results)
    batch_download_results = testapp.get('/batch_download/?type=Experiment&files.file_format=bigWig').text.strip().split('\n')
    metadata_results = testapp.get('/metadata/?type=Experiment&files.file_format=bigWig').text.strip().split('\n')
    assert len(batch_download_results) > 1
    assert len(metadata_results) == len(batch_download_results)
    batch_download_results = testapp.get('/batch_download/?type=Experiment&files.file_format=bigWig&files.file_format=tsv').text.strip().split('\n')
    metadata_results = testapp.get('/metadata/?type=Experiment&files.file_format=bigWig&files.file_format=tsv').text.strip().split('\n')
    assert len(batch_download_results) > 1
    assert len(metadata_results) == len(batch_download_results)
    batch_download_results = testapp.get('/batch_download/?type=Experiment&files.status=released').text.strip().split('\n')
    metadata_results = testapp.get('/metadata/?type=Experiment&files.status=released').text.strip().split('\n')
    assert len(batch_download_results) > 1
    assert len(metadata_results) == len(batch_download_results)
    batch_download_results = testapp.get('/batch_download/?type=Experiment&files.file_type=bed+narrowPeak').text.strip().split('\n')
    metadata_results = testapp.get('/metadata/?type=Experiment&files.file_type=bed+narrowPeak').text.strip().split('\n')
    assert len(batch_download_results) > 1
    assert len(metadata_results) == len(batch_download_results)
    batch_download_results = testapp.get('/batch_download/?type=Experiment&files.file_type!=bed+narrowPeak').text.strip().split('\n')
    metadata_results = testapp.get('/metadata/?type=Experiment&files.file_type!=bed+narrowPeak').text.strip().split('\n')
    assert len(batch_download_results) > 1
    assert len(metadata_results) == len(batch_download_results)
    batch_download_results = testapp.get('/batch_download/?type=Experiment&files.assay_term_name=ChIP-seq').text.strip().split('\n')
    metadata_results = testapp.get('/metadata/?type=Experiment&files.assay_term_name=ChIP-seq').text.strip().split('\n')
    assert len(batch_download_results) > 1
    assert len(metadata_results) == len(batch_download_results)
    batch_download_results = testapp.get('/batch_download/?type=Experiment&files.biological_replicates=2').text.strip().split('\n')
    metadata_results = testapp.get('/metadata/?type=Experiment&files.biological_replicates=2').text.strip().split('\n')
    assert len(batch_download_results) > 1
    assert len(metadata_results) == len(batch_download_results)


def test_reports_annotation_batch_download_and_metadata_contain_same_number_of_results(index_workbook, testapp):
    batch_download_results = testapp.get('/batch_download/?type=Annotation').text.strip().split('\n')
    metadata_results = testapp.get('/metadata/?type=Annotation').text.strip().split('\n')
    assert len(batch_download_results) > 1
    assert len(metadata_results) == len(batch_download_results)
    batch_download_results = testapp.get('/batch_download/?type=Annotation&files.file_format=bigWig').text.strip().split('\n')
    metadata_results = testapp.get('/metadata/?type=Annotation&files.file_format=bigWig').text.strip().split('\n')
    assert len(batch_download_results) > 1
    assert len(metadata_results) == len(batch_download_results)
    batch_download_results = testapp.get('/batch_download/?type=Annotation&files.file_format=bigWig&files.file_format=tsv').text.strip().split('\n')
    metadata_results = testapp.get('/metadata/?type=Annotation&files.file_format=bigWig&files.file_format=tsv').text.strip().split('\n')
    assert len(batch_download_results) > 1
    assert len(metadata_results) == len(batch_download_results)
    batch_download_results = testapp.get('/batch_download/?type=Annotation&files.status=released').text.strip().split('\n')
    metadata_results = testapp.get('/metadata/?type=Annotation&files.status=released').text.strip().split('\n')
    assert len(batch_download_results) > 1
    assert len(metadata_results) == len(batch_download_results)
    batch_download_results = testapp.get('/batch_download/?type=Annotation&files.file_type=bed+bed3%2B').text.strip().split('\n')
    metadata_results = testapp.get('/metadata/?type=Annotation&files.file_type=bed+bed3%2B').text.strip().split('\n')
    assert len(batch_download_results) > 1
    assert len(metadata_results) == len(batch_download_results)
    batch_download_results = testapp.get('/batch_download/?type=Annotation&files.file_type!=bed+bed3%2B').text.strip().split('\n')
    metadata_results = testapp.get('/metadata/?type=Annotation&files.file_type!=bed+bed3%2B').text.strip().split('\n')
    assert len(batch_download_results) > 1
    assert len(metadata_results) == len(batch_download_results)
    batch_download_results = testapp.get('/batch_download/?type=Annotation&annotation_type=candidate+Cis-Regulatory+Elements').text.strip().split('\n')
    metadata_results = testapp.get('/metadata/?type=Annotation&annotation_type=candidate+Cis-Regulatory+Elements').text.strip().split('\n')
    assert len(batch_download_results) > 1
    assert len(metadata_results) == len(batch_download_results)
    batch_download_results = testapp.get('/batch_download/?type=Annotation&files.lab.title=John+Stamatoyannopoulos%2C+UW').text.strip().split('\n')
    metadata_results = testapp.get('/metadata/?type=Annotation&files.lab.title=John+Stamatoyannopoulos%2C+UW').text.strip().split('\n')
    assert len(batch_download_results) > 1
    assert len(metadata_results) == len(batch_download_results)


def test_reports_publication_data_batch_download_and_metadata_contain_same_number_of_results(index_workbook, testapp):
    batch_download_results = testapp.get('/batch_download/?type=PublicationData').text.strip().split('\n')
    metadata_results = testapp.get('/metadata/?type=PublicationData').text.strip().split('\n')
    assert len(batch_download_results) > 1
    assert len(metadata_results) == len(batch_download_results)
    batch_download_results = testapp.get('/batch_download/?type=PublicationData&files.file_format=tsv').text.strip().split('\n')
    metadata_results = testapp.get('/metadata/?type=PublicationData&files.file_format=tsv').text.strip().split('\n')
    assert len(batch_download_results) > 1
    assert len(metadata_results) == len(batch_download_results)
    batch_download_results = testapp.get('/batch_download/?type=PublicationData&files.file_format=hic&files.file_format=tsv').text.strip().split('\n')
    metadata_results = testapp.get('/metadata/?type=PublicationData&files.file_format=hic&files.file_format=tsv').text.strip().split('\n')
    assert len(batch_download_results) > 1
    assert len(metadata_results) == len(batch_download_results)
    batch_download_results = testapp.get('/batch_download/?type=PublicationData&files.status=released').text.strip().split('\n')
    metadata_results = testapp.get('/metadata/?type=PublicationData&files.status=released').text.strip().split('\n')
    assert len(batch_download_results) > 1
    assert len(metadata_results) == len(batch_download_results)
    batch_download_results = testapp.get('/batch_download/?type=PublicationData&files.file_type=bed+narrowPeak').text.strip().split('\n')
    metadata_results = testapp.get('/metadata/?type=PublicationData&files.file_type=bed+narrowPeak').text.strip().split('\n')
    assert len(batch_download_results) > 1
    assert len(metadata_results) == len(batch_download_results)
    batch_download_results = testapp.get('/batch_download/?type=PublicationData&files.file_type!=bed+narrowPeak').text.strip().split('\n')
    metadata_results = testapp.get('/metadata/?type=PublicationData&files.file_type!=bed+narrowPeak').text.strip().split('\n')
    assert len(batch_download_results) > 1
    assert len(metadata_results) == len(batch_download_results)
    batch_download_results = testapp.get('/batch_download/?type=PublicationData&files.assay_term_name=ChIP-seq').text.strip().split('\n')
    metadata_results = testapp.get('/metadata/?type=PublicationData&files.assay_term_name=ChIP-seq').text.strip().split('\n')
    assert len(batch_download_results) > 1
    assert len(metadata_results) == len(batch_download_results)
    batch_download_results = testapp.get('/batch_download/?type=PublicationData&files.file_size=2433593').text.strip().split('\n')
    metadata_results = testapp.get('/metadata/?type=PublicationData&files.file_size=2433593').text.strip().split('\n')
    assert len(batch_download_results) > 1
    assert len(metadata_results) == len(batch_download_results)


def test_reports_series_batch_download_and_metadata_contain_same_number_of_results(index_workbook, testapp):
    batch_download_results = testapp.get('/batch_download/?type=ReferenceEpigenome').text.strip().split('\n')
    metadata_results = testapp.get('/metadata/?type=ReferenceEpigenome').text.strip().split('\n')
    assert len(batch_download_results) > 1
    assert len(metadata_results) == len(batch_download_results)
    batch_download_results = testapp.get('/batch_download/?type=ReferenceEpigenome&related_datasets.files.preferred_default=true').text.strip().split('\n')
    metadata_results = testapp.get('/metadata/?type=ReferenceEpigenome&related_datasets.files.preferred_default=true').text.strip().split('\n')
    assert len(batch_download_results) > 1
    assert len(metadata_results) == len(batch_download_results)
    batch_download_results = testapp.get('/batch_download/?type=ReferenceEpigenome&related_datasets.files.preferred_default=true&related_datasets.files.output_type=signal+of+all+reads').text.strip().split('\n')
    metadata_results = testapp.get('/metadata/?type=ReferenceEpigenome&related_datasets.files.preferred_default=true&related_datasets.files.output_type=signal+of+all+reads').text.strip().split('\n')
    assert len(batch_download_results) > 1
    assert len(metadata_results) == len(batch_download_results)


def get_batch_download_and_metadata_results(testapp, query_string):
    batch_download_results = testapp.get(
        '/batch_download/' + query_string
    ).text.strip().split('\n')
    metadata_results = testapp.get(
        '/metadata/' + query_string
    ).text.strip().split('\n')
    return batch_download_results, metadata_results


def test_reports_batch_download_and_metadata_specific_filters(index_workbook, testapp):
    query_string = (
        '?type=Experiment&status=released'
        '&perturbed=false&assay_title=DNase-seq'
        '&files.run_type=single-ended&files.file_type=fastq'
    )
    batch_download_results, metadata_results = get_batch_download_and_metadata_results(
        testapp, query_string
    )
    # Two results plus header.
    assert len(batch_download_results) == len(metadata_results) == 3

    query_string = (
        '?type=Experiment&status=released'
        '&perturbed=false&assay_title=DNase-seq'
        '&files.run_type=single-ended'
        '&files.file_type=fastq&assembly=GRCh38'
    )
    batch_download_results, metadata_results = get_batch_download_and_metadata_results(
        testapp, query_string
    )
    assert len(batch_download_results) == len(metadata_results) == 2

    query_string = (
        '?type=Experiment&status=released'
        '&perturbed=false&assay_title=DNase-seq'
        '&files.run_type=single-ended'
        '&files.file_type=fastq&files.assembly=GRCh38'
    )
    batch_download_results, metadata_results = get_batch_download_and_metadata_results(
        testapp, query_string
    )
    # Header only, zero files.
    assert len(batch_download_results) == len(metadata_results) == 1

    query_string = (
        '?type=Experiment&files.no_file_available=true'
    )
    batch_download_results, metadata_results = get_batch_download_and_metadata_results(
        testapp, query_string
    )
    assert len(batch_download_results) == len(metadata_results) == 1

    query_string = (
        '?type=Experiment&files.restricted=true'
    )
    batch_download_results, metadata_results = get_batch_download_and_metadata_results(
        testapp, query_string
    )
    assert len(batch_download_results) == len(metadata_results) == 1

    query_string = (
        '?type=Experiment&files.no_file_available=*&target.label=H3K4me3&perturbed=true'
    )
    batch_download_results, metadata_results = get_batch_download_and_metadata_results(
        testapp, query_string
    )
    assert len(batch_download_results) == len(metadata_results) == 2

    query_string = (
        '?type=Experiment&files.no_file_available=*&target.label=H3K4me3&assembly=mm10'
    )
    batch_download_results, metadata_results = get_batch_download_and_metadata_results(
        testapp, query_string
    )
    assert len(batch_download_results) == len(metadata_results) == 8

    query_string = (
        '?type=Experiment&files.no_file_available=*&target.label=H3K4me3&files.assembly=mm10'
    )
    batch_download_results, metadata_results = get_batch_download_and_metadata_results(
        testapp, query_string
    )
    assert len(batch_download_results) == len(metadata_results) == 2

    query_string = (
        '?type=Experiment&files.no_file_available=false'
        '&target.label=H3K4me3&assembly!=mm10'
        '&target.label=TCF4&files.read_length=50'
    )
    batch_download_results, metadata_results = get_batch_download_and_metadata_results(
        testapp, query_string
    )
    assert len(batch_download_results) == len(metadata_results) == 3

    query_string = (
        '?type=Experiment&files.no_file_available=false'
        '&target.label=H3K4me3&assembly!=mm10'
        '&target.label=TCF4&files.file_type=bam'
    )
    batch_download_results, metadata_results = get_batch_download_and_metadata_results(
        testapp, query_string
    )
    assert len(batch_download_results) == len(metadata_results) == 5

    query_string = (
        '?type=Experiment&files.no_file_available=false'
        '&target.label=H3K4me3&assembly!=mm10'
        '&target.label=TCF4&files.file_type=bam'
        '&lab.title=Sherman+Weissman%2C+Yale'
    )
    batch_download_results, metadata_results = get_batch_download_and_metadata_results(
        testapp, query_string
    )
    assert len(batch_download_results) == len(metadata_results) == 2

    query_string = (
        '?type=Experiment&files.no_file_available=false'
        '&target.label=H3K4me3&assembly!=mm10'
        '&target.label=TCF4&files.file_type=bam'
        '&lab.title=Sherman+Weissman%2C+Yale&status!=released'
    )
    batch_download_results, metadata_results = get_batch_download_and_metadata_results(
        testapp, query_string
    )
    assert len(batch_download_results) == len(metadata_results) == 1

    query_string = (
        '?type=Experiment&files.replicate.library=/libraries/ENCLB058ZZZ/'
    )
    batch_download_results, metadata_results = get_batch_download_and_metadata_results(
        testapp, query_string
    )
    assert len(batch_download_results) == len(metadata_results) == 5

    query_string = (
        '?type=Experiment&files.replicate.library=/libraries/ENCLB058ZZZ/'
        '&files.file_type=bigWig'
    )
    batch_download_results, metadata_results = get_batch_download_and_metadata_results(
        testapp, query_string
    )
    assert len(batch_download_results) == len(metadata_results) == 3

    query_string = (
        '?type=Experiment&files.replicate.library=/libraries/ENCLB058ZZZ/'
        '&files.file_type=bigWig&option=visualizable'
    )
    batch_download_results, metadata_results = get_batch_download_and_metadata_results(
        testapp, query_string
    )
    assert len(batch_download_results) == len(metadata_results) == 3

    query_string = (
        '?type=Experiment&files.replicate.library=/libraries/ENCLB058ZZZ/'
        '&files.file_type=bigWig&option=raw'
    )
    batch_download_results, metadata_results = get_batch_download_and_metadata_results(
        testapp, query_string
    )
    assert len(batch_download_results) == len(metadata_results) == 1

    query_string = (
        '?type=Experiment&files.replicate.library=/libraries/ENCLB058ZZZ/'
        '&files.file_type=fastq&files.read_length=50'
    )
    batch_download_results, metadata_results = get_batch_download_and_metadata_results(
        testapp, query_string
    )
    assert len(batch_download_results) == len(metadata_results) == 2

    query_string = (
        '?type=Experiment&files.replicate.library=/libraries/ENCLB058ZZZ/'
        '&files.file_type=fastq&files.read_length=50&option=raw'
    )
    batch_download_results, metadata_results = get_batch_download_and_metadata_results(
        testapp, query_string
    )
    assert len(batch_download_results) == len(metadata_results) == 2

    query_string = (
        '?type=Experiment&files.replicate.library=/libraries/ENCLB058ZZZ/'
        '&files.file_type=fastq&files.read_length=50&option=visualizable'
    )
    batch_download_results, metadata_results = get_batch_download_and_metadata_results(
        testapp,query_string
    )
    assert len(batch_download_results) == len(metadata_results) == 1

    query_string = (
        '?type=Experiment&files.replicate.library=/libraries/ENCLB058ZZZ/'
        '&files.file_type=fastq&files.read_length=50&option=visualizable'
    )
    batch_download_results, metadata_results = get_batch_download_and_metadata_results(
        testapp, query_string
    )
    assert len(batch_download_results) == len(metadata_results) == 1

    query_string = (
        '?type=Experiment&files.derived_from=*&files.file_type=bam'
    )
    batch_download_results, metadata_results = get_batch_download_and_metadata_results(
        testapp, query_string
    )
    assert len(batch_download_results) == len(metadata_results) == 13

    query_string = (
        '?type=Experiment&files.derived_from=*&files.file_type=bam&files.file_type=fastq'
    )
    batch_download_results, metadata_results = get_batch_download_and_metadata_results(
        testapp, query_string
    )
    assert len(batch_download_results) == len(metadata_results) == 14

    query_string = (
        '?type=Experiment&files.file_type=bam&files.file_type=fastq'
    )
    batch_download_results, metadata_results = get_batch_download_and_metadata_results(
        testapp, query_string
    )
    assert len(batch_download_results) == len(metadata_results) == 71

    query_string = (
        '?type=Experiment&files.derived_from=*&files.file_type=bam'
        '&files.file_type=fastq&files.file_type=bigWig'
    )
    batch_download_results, metadata_results = get_batch_download_and_metadata_results(
        testapp, query_string
    )
    assert len(batch_download_results) == len(metadata_results) == 21

    query_string = (
        '?type=Experiment&files.derived_from=*&files.file_type=bam'
        '&files.file_type=fastq&files.file_type=bigWig&files.read_length=76'
    )
    batch_download_results, metadata_results = get_batch_download_and_metadata_results(
        testapp, query_string
    )
    assert len(batch_download_results) == len(metadata_results) == 2

    query_string = (
        '?type=Experiment&files.derived_from=*&files.file_type=bam'
        '&files.file_type=fastq&files.file_type=bigWig&files.read_length=76'
        '&audit.NOT_COMPLIANT.category=missing+documents'
    )
    batch_download_results, metadata_results = get_batch_download_and_metadata_results(
        testapp, query_string
    )
    assert len(batch_download_results) == len(metadata_results) == 2


def test_reports_annotation_batch_download_and_metadata_specific_filters(index_workbook, testapp):
    query_string = (
        '?type=Annotation&files.file_type=bed+enhancer+predictions'
    )
    batch_download_results, metadata_results = get_batch_download_and_metadata_results(
        testapp, query_string
    )
    assert len(batch_download_results) == len(metadata_results) == 2

    query_string = (
        '?type=Annotation&files.file_type=bed+enhancer+predictions&files.assembly=mm10'
    )
    batch_download_results, metadata_results = get_batch_download_and_metadata_results(
        testapp, query_string
    )
    assert len(batch_download_results) == len(metadata_results) == 2

    query_string = (
        '?type=Annotation&files.file_type=bed+enhancer+predictions&files.assembly!=mm10'
    )
    batch_download_results, metadata_results = get_batch_download_and_metadata_results(
        testapp, query_string
    )
    assert len(batch_download_results) == len(metadata_results) == 1

    query_string = (
        '?type=Annotation&files.file_type=bed+enhancer+predictions&files.biosample_ontology=*'
    )
    batch_download_results, metadata_results = get_batch_download_and_metadata_results(
        testapp, query_string
    )
    assert len(batch_download_results) == len(metadata_results) == 2

    query_string = (
        '?type=Annotation&files.file_type=bed+enhancer+predictions'
        '&files.biosample_ontology=/biosample-types/tissue_UBERON_0000948/'
    )
    batch_download_results, metadata_results = get_batch_download_and_metadata_results(
        testapp, query_string
    )
    assert len(batch_download_results) == len(metadata_results) == 2

    query_string = (
        '?type=Annotation&files.file_type=bed+enhancer+predictions'
        '&files.biosample_ontology!=/biosample-types/tissue_UBERON_0000948/'
    )
    batch_download_results, metadata_results = get_batch_download_and_metadata_results(
        testapp, query_string
    )
    assert len(batch_download_results) == len(metadata_results) == 1

    query_string = (
        '?type=Annotation&files.file_size=1544154147'
    )
    batch_download_results, metadata_results = get_batch_download_and_metadata_results(
        testapp, query_string
    )
    assert len(batch_download_results) == len(metadata_results) == 2

    query_string = (
        '?type=Annotation&files.file_size=1544154147&files.assembly!=mm10'
    )
    batch_download_results, metadata_results = get_batch_download_and_metadata_results(
        testapp, query_string
    )
    assert len(batch_download_results) == len(metadata_results) == 1

    query_string = (
        '?type=Annotation&files.file_size=1544154147&files.assembly=mm10'
    )
    batch_download_results, metadata_results = get_batch_download_and_metadata_results(
        testapp, query_string
    )
    assert len(batch_download_results) == len(metadata_results) == 2


def test_reports_publication_data_batch_download_and_metadata_specific_filters(index_workbook, testapp):
    query_string = (
        '?type=PublicationData&files.dataset=/experiments/ENCSR000ADH/'
    )
    batch_download_results, metadata_results = get_batch_download_and_metadata_results(
        testapp, query_string
    )
    assert len(batch_download_results) == len(metadata_results) == 2

    query_string = (
        '?type=PublicationData&files.dataset!=/experiments/ENCSR000ADH/'
    )
    batch_download_results, metadata_results = get_batch_download_and_metadata_results(
        testapp, query_string
    )
    assert len(batch_download_results) == len(metadata_results) == 6

    query_string = (
        '?type=PublicationData&files.file_type=tsv'
    )
    batch_download_results, metadata_results = get_batch_download_and_metadata_results(
        testapp, query_string
    )
    assert len(batch_download_results) == len(metadata_results) == 3

    query_string = (
        '?type=PublicationData&files.file_type=tsv&files.md5sum=69031443b66578d55b5c4a039d55cceb'
    )
    batch_download_results, metadata_results = get_batch_download_and_metadata_results(
        testapp, query_string
    )
    assert len(batch_download_results) == len(metadata_results) == 2

    query_string = (
        '?type=PublicationData&files.file_type=tsv&files.md5sum=69031443b66578d55b5c4a039d55cceb'
        '&files.file_size=984865'
    )
    batch_download_results, metadata_results = get_batch_download_and_metadata_results(
        testapp, query_string
    )
    assert len(batch_download_results) == len(metadata_results) == 2

    query_string = (
        '?type=PublicationData&files.file_type=tsv&files.md5sum=69031443b66578d55b5c4a039d55cceb'
        '&files.file_size=3838'
    )
    batch_download_results, metadata_results = get_batch_download_and_metadata_results(
        testapp, query_string
    )
    assert len(batch_download_results) == len(metadata_results) == 1


def test_reports_batch_download_init_batch_download_mixin(dummy_request):
    from encoded.reports.batch_download import BatchDownloadMixin
    bdm = BatchDownloadMixin()
    assert isinstance(bdm, BatchDownloadMixin)


def test_reports_batch_download_init_batch_download(dummy_request):
    from encoded.reports.batch_download import BatchDownload
    dummy_request.environ['QUERY_STRING'] = (
        'type=Experiment&files.file_type=bigWig&files.file_type=bam'
        '&files.replicate.library.size_range=50-100'
        '&files.status!=archived&files.biological_replicates=2'
    )
    bd = BatchDownload(dummy_request)
    assert isinstance(bd, BatchDownload)


def test_reports_batch_download_should_add_json_elements_to_metadata_link(dummy_request):
    from encoded.reports.batch_download import BatchDownload
    dummy_request.environ['QUERY_STRING'] = (
        'type=Experiment&files.file_type=bigWig&files.file_type=bam'
        '&files.replicate.library.size_range=50-100'
        '&files.status!=archived&files.biological_replicates=2'
    )
    bd = BatchDownload(dummy_request)
    assert not bd._should_add_json_elements_to_metadata_link()
    dummy_request.json = {'elements': ['/experiments/ENCSR123ABC/']}
    bd = BatchDownload(dummy_request)
    assert bd._should_add_json_elements_to_metadata_link()
    dummy_request.json = {'elements': []}
    bd = BatchDownload(dummy_request)
    assert not bd._should_add_json_elements_to_metadata_link()
    dummy_request.environ['QUERY_STRING'] = (
        'type=Experiment&files.file_type=bigWig&files.file_type=bam'
        '&files.replicate.library.size_range=50-100'
        '&files.status!=archived&files.biological_replicates=2'
        '&cart=xyz123'
    )
    dummy_request.json = {
        'elements': [
            '/experiments/ENCSR123ABC/',
            '/experiments/ENCSRDEF567/'
        ]
    }
    bd = BatchDownload(dummy_request)
    assert not bd._should_add_json_elements_to_metadata_link()


def test_reports_batch_download_maybe_add_json_elements_to_metadata_link(dummy_request):
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
    dummy_request.environ['QUERY_STRING'] = (
        'type=Experiment&files.file_type=bigWig&files.file_type=bam'
        '&files.replicate.library.size_range=50-100'
        '&files.status!=archived&files.biological_replicates=2'
        '&cart=xyz123'
    )
    dummy_request.json = {
        'elements': [
            '/experiments/ENCSR123ABC/',
            '/experiments/ENCSRDEF567/'
        ]
    }
    bd = BatchDownload(dummy_request)
    metadata_link = bd._maybe_add_json_elements_to_metadata_link('')
    assert metadata_link == ''


def test_reports_batch_download_get_metadata_link(dummy_request):
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


def test_reports_batch_download_get_encoded_metadata_link_with_newline(dummy_request):
    from encoded.reports.batch_download import BatchDownload
    dummy_request.environ['QUERY_STRING'] = (
        'type=Experiment&files.file_type=bigWig&files.file_type=bam'
        '&files.replicate.library.size_range=50-100'
        '&files.status!=archived&files.biological_replicates=2'
    )
    bd = BatchDownload(dummy_request)
    metadata_link = bd._get_encoded_metadata_link_with_newline()
    assert metadata_link == (
        '"http://localhost/metadata/?type=Experiment'
        '&files.file_type=bigWig&files.file_type=bam'
        '&files.replicate.library.size_range=50-100'
        '&files.status%21=archived&files.biological_replicates=2"'
        '\n'
    ).encode('utf-8')
    dummy_request.json = {
        'elements': [
            '/experiments/ENCSR123ABC/',
            '/experiments/ENCSRDEF567/'
        ]
    }
    bd = BatchDownload(dummy_request)
    metadata_link = bd._get_encoded_metadata_link_with_newline()
    assert metadata_link == (
        '"http://localhost/metadata/?type=Experiment'
        '&files.file_type=bigWig&files.file_type=bam'
        '&files.replicate.library.size_range=50-100'
        '&files.status%21=archived&files.biological_replicates=2"'
        ' -X GET -H "Accept: text/tsv" -H "Content-Type: application/json"'
        ' --data \'{"elements": ["/experiments/ENCSR123ABC/", "/experiments/ENCSRDEF567/"]}\''
        '\n'
    ).encode('utf-8')


def test_reports_batch_download_default_params(dummy_request):
    from encoded.reports.batch_download import BatchDownload
    dummy_request.environ['QUERY_STRING'] = (
        'type=Experiment&files.file_type=bigWig&files.file_type=bam'
        '&files.replicate.library.size_range=50-100'
        '&files.status!=archived&files.biological_replicates=2'
    )
    bd = BatchDownload(dummy_request)
    assert bd.DEFAULT_PARAMS == [
        ('limit', 'all'),
        ('field', 'files.@id'),
        ('field', 'files.href'),
        ('field', 'files.restricted'),
        ('field', 'files.no_file_available'),
        ('field', 'files.file_format'),
        ('field', 'files.file_format_type'),
        ('field', 'files.status'),
        ('field', 'files.assembly'),
    ]


def test_reports_batch_download_build_header(dummy_request):
    from encoded.reports.batch_download import BatchDownload
    dummy_request.environ['QUERY_STRING'] = (
        'type=Experiment&files.file_type=bigWig&files.file_type=bam'
        '&files.replicate.library.size_range=50-100'
        '&files.status!=archived&files.biological_replicates=2'
    )
    bd = BatchDownload(dummy_request)
    bd._build_header()
    assert bd.header == ['File download URL']


def test_reports_batch_download_get_column_to_field_mapping(dummy_request):
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


def test_reports_batch_download_build_params(dummy_request):
    from encoded.reports.batch_download import BatchDownload
    dummy_request.environ['QUERY_STRING'] = (
        'type=Experiment&files.file_type=bigWig&files.file_type=bam'
        '&files.replicate.library.size_range=50-100'
        '&files.status!=archived&files.biological_replicates=2'
    )
    dummy_request.json = {'elements': ['/experiments/ENCSR123ABC/']}
    bd = BatchDownload(dummy_request)
    bd._build_params()
    assert len(bd.param_list['field']) == 5, f'{len(bd.param_list["field"])} not expected'
    assert len(bd.param_list['@id']) == 1


def test_reports_batch_download_build_query_string(dummy_request):
    from encoded.reports.batch_download import BatchDownload
    dummy_request.environ['QUERY_STRING'] = (
        'type=Experiment&files.file_type=bigWig&files.file_type=bam'
    )
    bd = BatchDownload(dummy_request)
    bd._initialize_report()
    bd._build_params()
    bd._build_query_string()
    bd.query_string.deduplicate()
    assert str(bd.query_string) == (
        'type=Experiment&files.file_type=bigWig'
        '&files.file_type=bam&limit=all&field=files.%40id'
        '&field=files.href&field=files.restricted'
        '&field=files.no_file_available&field=files.file_format'
        '&field=files.file_format_type&field=files.status'
        '&field=files.assembly&field=files.file_type'
    )
    dummy_request.environ['QUERY_STRING'] = (
        'type=Experiment&files.file_type=bigWig&files.file_type=bam'
        '&files.replicate.library.size_range=50-100'
        '&files.status!=archived&files.biological_replicates=2'
    )
    bd = BatchDownload(dummy_request)
    bd._initialize_report()
    bd._build_params()
    bd._build_query_string()
    assert str(bd.query_string) == (
        'type=Experiment&files.file_type=bigWig'
        '&files.file_type=bam&files.replicate.library.size_range=50-100'
        '&files.status%21=archived&files.biological_replicates=2'
        '&limit=all&field=files.%40id&field=files.href&field=files.restricted'
        '&field=files.no_file_available&field=files.file_format'
        '&field=files.file_format_type&field=files.status&field=files.assembly'
        '&field=files.href&field=files.file_type&field=files.file_type'
        '&field=files.replicate.library.size_range&field=files.biological_replicates'
    )


def test_reports_batch_download_generate(index_workbook, dummy_request):
    from types import GeneratorType
    from encoded.reports.batch_download import BatchDownload
    from pyramid.response import Response
    dummy_request.environ['QUERY_STRING'] = (
        'type=Experiment'
    )
    bd = BatchDownload(dummy_request)
    response = bd.generate()
    assert isinstance(response, Response)
    assert response.content_type == 'text/plain'
    assert response.content_disposition == 'attachment; filename="files.txt"'
    assert len(list(response.body)) >= 100


def test_reports_publication_data_batch_download_generate_rows(index_workbook, dummy_request):
    from encoded.reports.batch_download import PublicationDataBatchDownload
    dummy_request.environ['QUERY_STRING'] = (
        'type=PublicationData'
        '&@id=/publication-data/ENCSR727WCB/'
        '&files.file_type=tsv'
    )
    pdbd = PublicationDataBatchDownload(dummy_request)
    pdbd._initialize_report()
    pdbd._build_params()
    results = list(pdbd._generate_rows())
    # One metadata link, two TSV.
    assert len(results) == 3


def test_reports_publication_data_batch_download_generate_rows_no_files_in_publication_data(dummy_request, mocker):
    from types import GeneratorType
    from encoded.reports.batch_download import PublicationDataBatchDownload
    dummy_request.environ['QUERY_STRING'] = (
        'type=PublicationData'
    )
    pdbd = PublicationDataBatchDownload(dummy_request)
    pdbd._initialize_report()
    pdbd._build_params()
    mocker.patch.object(pdbd, '_get_search_results_generator')
    pdbd._get_search_results_generator.return_value = (
        x for x in [{'files': []}]
    )
    row_generator = pdbd._generate_rows()
    assert isinstance(row_generator, GeneratorType)
    assert len(list(row_generator)) == 1
