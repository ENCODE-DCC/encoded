import pytest

from encoded.tests.features.conftest import app, app_settings, index_workbook
from pyramid.exceptions import HTTPBadRequest


def experiment():
    return {
        "assay_term_name": "ChIP-seq",
        "biosample_ontology": "/biosample-types/cell_line_EFO_0002067/",
        "documents": [
            "/documents/efac5344-6834-4e12-b971-94994d992e86/",
            "/documents/d00ffce2-e72c-44d7-a71f-73fd163c2426/",
            "/documents/73c95206-fc02-41ea-93e0-a929a6939aaf/"
        ],
        "references": [],
        "schema_version": "30",
        "accession": "ENCSR153HNT",
        "alternate_accessions": [],
        "description": "ChIP-Seq on K562",
        "dbxrefs": [],
        "date_released": "2020-07-15",
        "internal_tags": [],
        "status": "released",
        "date_created": "2020-03-26T19:57:31.454124+00:00",
        "submitted_by": "/users/5e189705-c6ca-4849-ab5c-e6d679dc96ae/",
        "lab": "/labs/richard-myers/",
        "award": "/awards/UM1HG009411/",
        "aliases": ["richard-myers:SL414442-SL414443"],
        "date_submitted": "2020-04-17",
        "target": "/targets/STAG1-human/",
        "possible_controls": [
            "/experiments/ENCSR516XLO/"
        ],
        "supersedes": [],
        "related_files": [],
        "internal_status": "release ready",
        "analyses": [
            {
                "files": [
                    "/files/ENCFF304IDX/",
                    "/files/ENCFF197UGS/",
                    "/files/ENCFF335MIH/",
                    "/files/ENCFF895UWM/",
                    "/files/ENCFF688OGD/",
                    "/files/ENCFF604DWO/",
                    "/files/ENCFF211SCG/",
                    "/files/ENCFF744MWW/",
                    "/files/ENCFF683WMJ/",
                    "/files/ENCFF032KSP/",
                    "/files/ENCFF677HXK/",
                    "/files/ENCFF507JEH/",
                    "/files/ENCFF244PJU/",
                    "/files/ENCFF028UYG/",
                    "/files/ENCFF762SFI/",
                    "/files/ENCFF921BXP/",
                    "/files/ENCFF644IZV/",
                    "/files/ENCFF282TIA/",
                    "/files/ENCFF910JDS/",
                    "/files/ENCFF415QDT/",
                    "/files/ENCFF674HJF/",
                    "/files/ENCFF881NAX/"
                ],
                "assemblies": [
                    "GRCh38"
                ],
                "genome_annotations": [],
                "pipelines": [
                    "/pipelines/ENCPL367MAS/",
                    "/pipelines/ENCPL481MLO/",
                    "/pipelines/ENCPL612HIG/",
                    "/pipelines/ENCPL809GEM/"
                ],
                "pipeline_award_rfas": [
                    "ENCODE4"
                ],
                "pipeline_labs": [
                    "/labs/encode-processing-pipeline/"
                ]
            }
        ],
        "replication_type": "isogenic",
        "objective_slims": [],
        "type_slims": [],
        "category_slims": [],
        "assay_title": "TF ChIP-seq",
        "assay_slims": [
            "DNA binding"
        ],
        "replicates": [
            "/replicates/3b653ab4-7773-45b1-90f6-003aa9d0881f/",
            "/replicates/3210b1a4-a0c0-44c2-b3e4-796b0cfb8fcb/"
        ],
        "biosample_summary": "K562 genetically modified using CRISPR",
        "assay_term_id": "OBI:0000716",
        "@id": "/experiments/ENCSR153HNT/",
        "@type": [
            "Experiment",
            "Dataset",
            "Item"
        ],
        "uuid": "d5167d89-b29f-4d83-900d-d7276ec3adec",
        "original_files": [
            "/files/ENCFF901WEB/",
            "/files/ENCFF766UOD/",
            "/files/ENCFF304IDX/",
            "/files/ENCFF881NAX/"
        ],
        "contributing_files": [
            "/files/ENCFF089RYQ/",
            "/files/ENCFF356LFX/",
            "/files/ENCFF110MCL/"
        ],
        "files": [
            "/files/ENCFF901WEB/",
            "/files/ENCFF766UOD/",
            "/files/ENCFF304IDX/",
            "/files/ENCFF895UWM/",
            "/files/ENCFF744MWW/"
        ],
        "revoked_files": [],
        "assembly": [
            "GRCh38"
        ],
        "hub": "/experiments/ENCSR153HNT/@@hub/hub.txt",
        "related_series": [],
        "superseded_by": [],
        "protein_tags": [
            {"location": "C-terminal", "name": "3xFLAG", "target": "/targets/STAG1-human/"},
            {"location": "C-terminal", "name": "3xFLAG", "target": "/targets/STAG2-human/"}
        ],
        "perturbed": False
    }


def file_():
    return {
        'dbxrefs': [],
        'file_format_type': 'idr_ranked_peak',
        'output_type': 'IDR ranked peaks',
        'technical_replicates': ['2_1'],
        'lab': {
            'title': 'ENCODE Processing Pipeline'
        },
        'title': 'ENCFF244PJU',
        'file_size': 3356650,
        's3_uri': 's3://encode-public/2020/07/09/dc068c0a-d1c8-461a-a208-418d35121f3b/ENCFF244PJU.bed.gz',
        'md5sum': '335b6066a184f30f225aec79b376c7e8',
        'file_type': 'bed idr_ranked_peak',
        'no_file_available': False,
        'derived_from': [
            '/files/ENCFF895UWM/',
            '/files/ENCFF089RYQ/'
        ],
        'assembly': 'GRCh38',
        'biological_replicates': [
            2
        ],
        'href': '/files/ENCFF244PJU/@@download/ENCFF244PJU.bed.gz',
        'file_format': 'bed',
        'status': 'released',
        'replicate': {
            'rbns_protein_concentration': 20,
            'rbns_protein_concentration_units': 'nM'
        }
    }


def audits_():
    return {
        "WARNING": [
            {
                "category": "inconsistent control read length",
                "detail": "File {ENCFF783ZRQ|/files/ENCFF783ZRQ/} is 36 but its control file {ENCFF454ZHO|/files/ENCFF454ZHO/} is 30.",
                "level": 40,
                "level_name": "WARNING",
                "path": "/files/ENCFF783ZRQ/",
                "name": "audit_file"
            },
            {
                "category": "inconsistent platforms",
                "detail": "possible_controls is a list of experiment(s) that can serve as analytical controls for a given experiment. Experiment {ENCSR814EAU|/experiments/ENCSR814EAU/} found in possible_controls list of this experiment contains data produced on platform Illumina Genome Analyzer II/e/x which is not compatible with platform Illumina HiSeq 2000/2500 used in this experiment.",
                "level": 40,
                "level_name": "WARNING",
                "path": "/experiments/ENCSR891KGZ/",
                "name": "audit_experiment"
            }, {
                "category": "low read length",
                "detail": "Fastq file {ENCFF557LZC|/files/ENCFF557LZC/} has read length of 36bp. For mapping accuracy ENCODE standards recommend that sequencing reads should be at least 50bp long. (See {ENCODE ChIP-seq data standards|/data-standards/chip-seq/} )",
                "level": 40,
                "level_name": "WARNING",
                "path": "/experiments/ENCSR891KGZ/",
                "name": "audit_experiment"
            },
            {
                "category": "low read length",
                "detail": "Fastq file {ENCFF783ZRQ|/files/ENCFF783ZRQ/} has read length of 36bp. For mapping accuracy ENCODE standards recommend that sequencing reads should be at least 50bp long. (See {ENCODE ChIP-seq data standards|/data-standards/chip-seq/} )",
                "level": 40,
                "level_name": "WARNING",
                "path": "/experiments/ENCSR891KGZ/",
                "name": "audit_experiment"
            },
            {
                "category": "moderate library complexity",
                "detail": "NRF (Non Redundant Fraction) is equal to the result of the division of the number of reads after duplicates removal by the total number of reads. An NRF value in the range 0 - 0.5 is poor complexity, 0.5 - 0.8 is moderate complexity, and > 0.8 high complexity. NRF value > 0.8 is recommended, but > 0.5 is acceptable.  ENCODE processed alignments file {ENCFF553TUY|/files/ENCFF553TUY/} was generated from a library with NRF value of 0.64.",
                "level": 40,
                "level_name": "WARNING",
                "path": "/experiments/ENCSR891KGZ/",
                "name": "audit_experiment"
            },
            {
                "category": "mild to moderate bottlenecking",
                "detail": "PBC1 (PCR Bottlenecking Coefficient 1, M1/M_distinct) is the ratio of the number of genomic locations where exactly one read maps uniquely (M1) to the number of genomic locations where some reads map (M_distinct). A PBC1 value in the range 0 - 0.5 is severe bottlenecking, 0.5 - 0.8 is moderate bottlenecking, 0.8 - 0.9 is mild bottlenecking, and > 0.9 is no bottlenecking. PBC1 value > 0.9 is recommended, but > 0.8 is acceptable.  ENCODE processed alignments file {ENCFF553TUY|/files/ENCFF553TUY/} was generated from a library with PBC1 value of 0.73.",
                "level": 40,
                "level_name": "WARNING",
                "path": "/experiments/ENCSR891KGZ/",
                "name": "audit_experiment"
            },
            {
                "category": "mild to moderate bottlenecking",
                "detail": "PBC2 (PCR Bottlenecking Coefficient 2, M1/M2) is the ratio of the number of genomic locations where exactly one read maps uniquely (M1) to the number of genomic locations where two reads map uniquely (M2). A PBC2 value in the range 0 - 1 is severe bottlenecking, 1 - 3 is moderate bottlenecking, 3 - 10 is mild bottlenecking, > 10 is no bottlenecking. PBC2 value > 10 is recommended, but > 3 is acceptable.  ENCODE processed alignments file {ENCFF553TUY|/files/ENCFF553TUY/} was generated from a library with PBC2 value of 4.26.",
                "level": 40,
                "level_name": "WARNING",
                "path": "/experiments/ENCSR891KGZ/",
                "name": "audit_experiment"
            }, {
                "category": "moderate library complexity",
                "detail": "NRF (Non Redundant Fraction) is equal to the result of the division of the number of reads after duplicates removal by the total number of reads. An NRF value in the range 0 - 0.5 is poor complexity, 0.5 - 0.8 is moderate complexity, and > 0.8 high complexity. NRF value > 0.8 is recommended, but > 0.5 is acceptable.  ENCODE processed alignments file {ENCFF349SRS|/files/ENCFF349SRS/} was generated from a library with NRF value of 0.64.",
                "level": 40,
                "level_name": "WARNING",
                "path": "/experiments/ENCSR891KGZ/",
                "name": "audit_experiment"
            },
            {
                "category": "mild to moderate bottlenecking",
                "detail": "PBC1 (PCR Bottlenecking Coefficient 1, M1/M_distinct) is the ratio of the number of genomic locations where exactly one read maps uniquely (M1) to the number of genomic locations where some reads map (M_distinct). A PBC1 value in the range 0 - 0.5 is severe bottlenecking, 0.5 - 0.8 is moderate bottlenecking, 0.8 - 0.9 is mild bottlenecking, and > 0.9 is no bottlenecking. PBC1 value > 0.9 is recommended, but > 0.8 is acceptable.  ENCODE processed alignments file {ENCFF349SRS|/files/ENCFF349SRS/} was generated from a library with PBC1 value of 0.73.",
                "level": 40,
                "level_name": "WARNING",
                "path": "/experiments/ENCSR891KGZ/",
                "name": "audit_experiment"
            },
            {
                "category": "mild to moderate bottlenecking",
                "detail": "PBC2 (PCR Bottlenecking Coefficient 2, M1/M2) is the ratio of the number of genomic locations where exactly one read maps uniquely (M1) to the number of genomic locations where two reads map uniquely (M2). A PBC2 value in the range 0 - 1 is severe bottlenecking, 1 - 3 is moderate bottlenecking, 3 - 10 is mild bottlenecking, > 10 is no bottlenecking. PBC2 value > 10 is recommended, but > 3 is acceptable.  ENCODE processed alignments file {ENCFF349SRS|/files/ENCFF349SRS/} was generated from a library with PBC2 value of 4.26.",
                "level": 40,
                "level_name": "WARNING", "path": "/experiments/ENCSR891KGZ/", "name": "audit_experiment"
            },
            {
                "category": "moderate library complexity", "detail": "NRF (Non Redundant Fraction) is equal to the result of the division of the number of reads after duplicates removal by the total number of reads. An NRF value in the range 0 - 0.5 is poor complexity, 0.5 - 0.8 is moderate complexity, and > 0.8 high complexity. NRF value > 0.8 is recommended, but > 0.5 is acceptable.  ENCODE processed alignments file {ENCFF293PPG|/files/ENCFF293PPG/} was generated from a library with NRF value of 0.80.",
                "level": 40,
                "level_name": "WARNING", "path": "/experiments/ENCSR891KGZ/",
                "name": "audit_experiment"
            },
            {
                "category": "mild to moderate bottlenecking", "detail": "PBC1 (PCR Bottlenecking Coefficient 1, M1/M_distinct) is the ratio of the number of genomic locations where exactly one read maps uniquely (M1) to the number of genomic locations where some reads map (M_distinct). A PBC1 value in the range 0 - 0.5 is severe bottlenecking, 0.5 - 0.8 is moderate bottlenecking, 0.8 - 0.9 is mild bottlenecking, and > 0.9 is no bottlenecking. PBC1 value > 0.9 is recommended, but > 0.8 is acceptable.  ENCODE processed alignments file {ENCFF293PPG|/files/ENCFF293PPG/} was generated from a library with PBC1 value of 0.88.",
                "level": 40,
                "level_name": "WARNING",
                "path": "/experiments/ENCSR891KGZ/",
                "name": "audit_experiment"
            },
            {
                "category": "mild to moderate bottlenecking",
                "detail": "PBC1 (PCR Bottlenecking Coefficient 1, M1/M_distinct) is the ratio of the number of genomic locations where exactly one read maps uniquely (M1) to the number of genomic locations where some reads map (M_distinct). A PBC1 value in the range 0 - 0.5 is severe bottlenecking, 0.5 - 0.8 is moderate bottlenecking, 0.8 - 0.9 is mild bottlenecking, and > 0.9 is no bottlenecking. PBC1 value > 0.9 is recommended, but > 0.8 is acceptable.  ENCODE processed alignments file {ENCFF610NUD|/files/ENCFF610NUD/} was generated from a library with PBC1 value of 0.88.",
                "level": 40,
                "level_name": "WARNING", "path": "/experiments/ENCSR891KGZ/",
                "name": "audit_experiment"
            }
        ],
        "NOT_COMPLIANT": [
            {
                "category": "insufficient read depth",
                "detail": "Processed alignments file {ENCFF553TUY|/files/ENCFF553TUY/} produced by ChIP-seq read mapping pipeline ( {ENCPL220NBH|/pipelines/ENCPL220NBH/} ) using the hg19 assembly has 8345584 usable fragments. The minimum ENCODE standard for each replicate in a ChIP-seq experiment targeting H4K8ac-human and investigated as a transcription factor is 10 million usable fragments. The recommended value is > 20 million, but > 10 million is acceptable. (See {ENCODE ChIP-seq data standards|/data-standards/chip-seq/} )",
                "level": 50,
                "level_name": "NOT_COMPLIANT",
                "path": "/experiments/ENCSR891KGZ/",
                "name": "audit_experiment"
            },
            {
                "category": "insufficient read depth",
                "detail": "Processed alignments file {ENCFF349SRS|/files/ENCFF349SRS/} produced by ChIP-seq read mapping pipeline ( {ENCPL220NBH|/pipelines/ENCPL220NBH/} ) using the GRCh38 assembly has 8338604 usable fragments. The minimum ENCODE standard for each replicate in a ChIP-seq experiment targeting H4K8ac-human and investigated as a transcription factor is 10 million usable fragments. The recommended value is > 20 million, but > 10 million is acceptable. (See {ENCODE ChIP-seq data standards|/data-standards/chip-seq/} )",
                "level": 50,
                "level_name": "NOT_COMPLIANT",
                "path": "/experiments/ENCSR891KGZ/",
                "name": "audit_experiment"
            }
        ],
        "ERROR": [
            {
                "category": "extremely low read depth",
                "detail": "Processed alignments file {ENCFF293PPG|/files/ENCFF293PPG/} produced by ChIP-seq read mapping pipeline ( {ENCPL220NBH|/pipelines/ENCPL220NBH/} ) using the GRCh38 assembly has 1372444 usable fragments. The minimum ENCODE standard for each replicate in a ChIP-seq experiment targeting H4K8ac-human and investigated as a transcription factor is 10 million usable fragments. The recommended value is > 20 million, but > 10 million is acceptable. (See {ENCODE ChIP-seq data standards|/data-standards/chip-seq/} )",
                "level": 60,
                "level_name": "ERROR",
                "path": "/experiments/ENCSR891KGZ/",
                "name": "audit_experiment"
            },
            {
                "category": "extremely low read depth",
                "detail": "Processed alignments file {ENCFF610NUD|/files/ENCFF610NUD/} produced by ChIP-seq read mapping pipeline ( {ENCPL220NBH|/pipelines/ENCPL220NBH/} ) using the hg19 assembly has 1374194 usable fragments. The minimum ENCODE standard for each replicate in a ChIP-seq experiment targeting H4K8ac-human and investigated as a transcription factor is 10 million usable fragments. The recommended value is > 20 million, but > 10 million is acceptable. (See {ENCODE ChIP-seq data standards|/data-standards/chip-seq/} )",
                "level": 60,
                "level_name": "ERROR",
                "path": "/experiments/ENCSR891KGZ/",
                "name": "audit_experiment"
            }
        ]
    }


def test_metadata_allowed_types_decorator_raises_error():
    from encoded.reports.metadata import allowed_types

    @allowed_types(['MyType'])
    def endpoint(context, request):
        return True

    class Request:
        def __init__(self, params):
            self.params = params

    context = {}
    request = Request({})
    with pytest.raises(HTTPBadRequest) as error:
        endpoint(context, request)
    assert str(error.value) == 'URL requires one type parameter.'
    request = Request({'type': 'WrongType'})
    with pytest.raises(HTTPBadRequest) as error:
        endpoint(context, request)
    assert str(error.value) == 'WrongType not a valid type for endpoint.'
    request = Request({'type': 'MyType'})
    assert endpoint(context, request)


def test_metadata_make_experiment_cell():
    from encoded.reports.metadata import make_experiment_cell
    assert make_experiment_cell(['assembly'], experiment()) == 'GRCh38'
    assert make_experiment_cell(['protein_tags.location'], experiment()) == 'C-terminal'
    unsorted_cell = make_experiment_cell(['protein_tags.target'], experiment())
    assert (
        unsorted_cell == '/targets/STAG1-human/, /targets/STAG2-human/'
        or unsorted_cell == '/targets/STAG2-human/, /targets/STAG1-human/'
    )


def test_metadata_make_file_cell():
    from encoded.reports.metadata import make_file_cell
    assert make_file_cell(['assembly'], file_()) == 'GRCh38'
    assert make_file_cell(['dbxrefs'], file_()) == ''
    assert make_file_cell(['technical_replicates'], file_()) == '2_1'
    assert make_file_cell(['biological_replicates'], file_()) == '2'
    assert make_file_cell(['status'], file_()) == 'released'
    assert make_file_cell(['lab.title'], file_()) == 'ENCODE Processing Pipeline'
    assert make_file_cell(['file_format', 'file_format_type'], file_()) == 'bed idr_ranked_peak'


def test_metadata_file_matches_file_params():
    from encoded.reports.metadata import file_matches_file_params
    file_param_list = {'assembly': ['GRCh38']}
    assert file_matches_file_params(file_(), file_param_list)
    file_param_list = {'assembly': ['hg19']}
    assert not file_matches_file_params(file_(), file_param_list)
    file_param_list = {'missing_field': ['missing_value']}
    assert not file_matches_file_params(file_(), file_param_list)
    file_param_list = {'derived_from': ['/files/ENCFF089RYQ/']}
    assert file_matches_file_params(file_(), file_param_list)
    file_param_list = {'derived_from': ['/files/ENCFF089RYQ/', '/files/ENCFFABC123/']}
    assert file_matches_file_params(file_(), file_param_list)
    file_param_list = {'derived_from': ['/files/ENCFF895UWM/', '/files/ENCFF089RYQ/']}
    assert file_matches_file_params(file_(), file_param_list)
    file_param_list = {'technical_replicates': ['2_1']}
    assert file_matches_file_params(file_(), file_param_list)
    file_param_list = {'biological_replicates': ['2']}
    assert file_matches_file_params(file_(), file_param_list)
    file_param_list = {'file_size': ['3356650']}
    assert file_matches_file_params(file_(), file_param_list)
    file_param_list = {'replicate.rbns_protein_concentration': ['20']}
    assert file_matches_file_params(file_(), file_param_list)
    file_param_list = {'replicate.rbns_protein_concentration_units': ['nM']}
    assert file_matches_file_params(file_(), file_param_list)


def test_metadata_group_audits_by_files_and_type():
    from encoded.reports.metadata import group_audits_by_files_and_type
    grouped_file_audits, grouped_other_audits = group_audits_by_files_and_type(audits_())
    expected_grouped_file_audits = {
        '/files/ENCFF783ZRQ/': {
            'WARNING': (
                'inconsistent control read length',
            )
        }
    }
    expected_grouped_other_audits = {
        'WARNING': (
            'inconsistent platforms',
            'low read length',
            'mild to moderate bottlenecking',
            'moderate library complexity'
        ),
        'NOT_COMPLIANT': (
            'insufficient read depth',
        ),
        'ERROR': (
            'extremely low read depth',
        )
    }
    for file_id, audits in grouped_file_audits.items():
        for audit, audit_value in expected_grouped_file_audits[file_id].items():
            assert tuple(sorted(audits[audit])) == audit_value
    for audit, audit_value in grouped_other_audits.items():
        assert tuple(sorted(audit_value)) == expected_grouped_other_audits[audit]


@pytest.mark.indexing
def test_metadata_view(testapp, index_workbook):
    r = testapp.get('/metadata/?type=Experiment')
    assert len(r.text.split('\n')) >= 81


@pytest.mark.indexing
def test_metadata_contains_audit_values(testapp, index_workbook):
    r = testapp.get('/metadata/?type=Experiment')
    audit_values = [
        'inconsistent library biosample',
        'lacking processed data',
        'inconsistent platforms',
        'missing documents',
        'unreplicated experiment'
    ]
    for value in audit_values:
        assert (
            value in r.text,
            f'{value} not in metadata report'
        )


@pytest.mark.indexing
def test_metadata_contains_all_values(testapp, index_workbook):
    from pkg_resources import resource_filename
    r = testapp.get('/metadata/?type=Experiment')
    actual = sorted([tuple(x.split('\t')) for x in r.text.strip().split('\n')])
    expected_path = resource_filename('encoded', 'tests/data/inserts/expected_metadata.tsv')
    with open(expected_path, 'r') as f:
        expected = sorted([tuple(x.split('\t')) for x in f.readlines()])
    for i, row in enumerate(actual):
        for j, column in enumerate(row):
            # Sometimes lists are out of order.
            expected_value = tuple(sorted([x.strip() for x in expected[i][j].split(',')]))
            actual_value = tuple(sorted([x.strip() for x in column.split(',')]))
            assert (
                expected_value == actual_value,
                f'Mistmatch on row {i} column {j}. {expected_value} != {actual_value}'
            )
