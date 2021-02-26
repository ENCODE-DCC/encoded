import pytest

from encoded.tests.features.conftest import app, app_settings, index_workbook
from pyramid.exceptions import HTTPBadRequest


pytestmark = [
    pytest.mark.indexing,
    pytest.mark.usefixtures('index_workbook'),
]


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
        "analysis_objects": [
            "/analyses/ENCAN823NHJ/"
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


def embedded_experiment():
    return {
        '@id': '/experiments/ENCSR434TGY/',
        '@type': ['Experiment', 'Dataset', 'Item'],
        'accession': 'ENCSR434TGY',
        'assay_title': 'DNase-seq',
        'award': {'project': 'ENCODE'},
        'biosample_ontology': {
            'term_name': 'ZHBTc4',
            'term_id': 'EFO:0005914',
            'classification': 'cell line'
        },
        'date_released': '2020-07-28',
        'files': [
            {
                'dbxrefs': [],
                'file_format_type': 'bed3+',
                'output_type': 'DHS peaks',
                'technical_replicates': ['1_1'],
                'lab': {'title': 'John Stamatoyannopoulos, UW'},
                'title': 'ENCFF237ENG',
                'file_size': 642625,
                's3_uri': 's3://encode-public/2020/07/28/d24b3680-9453-403e-94b8-2393ed02ccb6/ENCFF237ENG.bed.gz',
                'md5sum': 'c954093c70a9c0f2067dc480a5135936',
                'file_type': 'bed bed3+',
                'no_file_available': False,
                'assembly': 'mm10',
                'biological_replicates': [1],
                'href': '/files/ENCFF237ENG/@@download/ENCFF237ENG.bed.gz',
                'read_length': 36,
                'file_format': 'bed',
                'status': 'released'
            },
            {
                'dbxrefs': [],
                'output_type': 'reads',
                'run_type': 'single-ended',
                'technical_replicates': ['1_1'],
                'lab': {
                    'title': 'John Stamatoyannopoulos, UW'
                },
                'title': 'ENCFF001QIF',
                'platform': {
                    'title': 'Illumina HiSeq 2000'
                },
                'file_size': 237982153,
                's3_uri': 's3://encode-public/2011/05/06/7c35d915-aea2-4f20-9f52-b2af18991cab/ENCFF001QIF.fastq.gz',
                'md5sum': 'cfb4e7dd7dbb0add6efbe0e52ae5618a',
                'file_type': 'fastq',
                'no_file_available': False,
                'biological_replicates': [1],
                'href': '/files/ENCFF001QIF/@@download/ENCFF001QIF.fastq.gz',
                'read_length': 36,
                'file_format': 'fastq',
                'status': 'released'
            },
            {
                'dbxrefs': [],
                'output_type': 'reads',
                'run_type': 'single-ended',
                'technical_replicates': ['1_1'],
                'lab': {
                    'title': 'John Stamatoyannopoulos, UW'
                },
                'title': 'ENCFF001QIE',
                'platform': {
                    'title': 'Illumina Genome Analyzer'
                },
                'file_size': 1338237475,
                's3_uri': 's3://encode-public/2011/05/06/11f63cfc-6da6-4f23-a9a0-1b1b04744dbd/ENCFF001QIE.fastq.gz',
                'md5sum': '315ebbab452358fe188024e3637fd965',
                'file_type': 'fastq',
                'no_file_available': False,
                'biological_replicates': [1],
                'href': '/files/ENCFF001QIE/@@download/ENCFF001QIE.fastq.gz',
                'read_length': 36,
                'file_format': 'fastq',
                'status': 'released'}
        ],
        'replicates': [
            {
                'library': {
                    'nucleic_acid_term_name': 'DNA',
                    'biosample': {
                        'organism': {
                            'scientific_name': 'Mus musculus'
                        },
                        'treatments': [
                            {
                                'duration': 96,
                                'treatment_term_name': 'doxycycline hyclate',
                                'amount': 100,
                                'duration_units': 'hour',
                                'amount_units': 'ng/mL'
                            }
                        ]
                    }
                }
            }
        ]
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
        },
        'preferred_default': True
    }


def abstract_file():
    return {
        'nested': {
            'boolean': True,
            'list': ['a', 'b', 'c'],
            'int': 2,
            'str': 'xyz',
            'empty_list': []
        },
        'empty_list': []
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


def test_metadata_file_matches_file_params():
    from encoded.reports.metadata import file_matches_file_params
    file_param_list = {}
    assert file_matches_file_params(file_(), file_param_list)
    file_param_list = {'assembly': set(['GRCh38'])}
    assert file_matches_file_params(file_(), file_param_list)
    file_param_list = {'assembly': set(['hg19'])}
    assert not file_matches_file_params(file_(), file_param_list)
    file_param_list = {'no_such_thing': set(['abc'])}
    assert not file_matches_file_params(file_(), file_param_list)
    file_param_list = {'missing_field': set(['missing_value'])}
    assert not file_matches_file_params(file_(), file_param_list)
    file_param_list = {'derived_from': set(['/files/ENCFF089RYQ/'])}
    assert file_matches_file_params(file_(), file_param_list)
    file_param_list = {'derived_from': set(['/files/ENCFF089RYQ/', '/files/ENCFFABC123/'])}
    assert file_matches_file_params(file_(), file_param_list)
    file_param_list = {'derived_from': set(['/files/ENCFF895UWM/', '/files/ENCFF089RYQ/'])}
    assert file_matches_file_params(file_(), file_param_list)
    file_param_list = {'technical_replicates': set(['2_1'])}
    assert file_matches_file_params(file_(), file_param_list)
    file_param_list = {'biological_replicates': set([2])}
    assert file_matches_file_params(file_(), file_param_list)
    file_param_list = {'file_size': set([3356650])}
    assert file_matches_file_params(file_(), file_param_list)
    file_param_list = {'replicate.rbns_protein_concentration': set([20])}
    assert file_matches_file_params(file_(), file_param_list)
    file_param_list = {'replicate.rbns_protein_concentration_units': set(['nM'])}
    assert file_matches_file_params(file_(), file_param_list)
    file_param_list = {'preferred_default': set([True])}
    assert file_matches_file_params(file_(), file_param_list)
    file_param_list = {'no_file_available': set([False])}
    assert file_matches_file_params(file_(), file_param_list)
    file_param_list = {'restricted': set([True])}
    assert not file_matches_file_params(file_(), file_param_list)
    file_param_list = {'assembly': set(['*'])}
    assert file_matches_file_params(file_(), file_param_list)
    file_param_list = {'no_such_thing': set(['*'])}
    assert not file_matches_file_params(file_(), file_param_list)
    file_param_list = {'preferred_default': set(['*'])}
    assert file_matches_file_params(file_(), file_param_list)
    file_param_list = {
        'derived_from': set(['*'])
    }
    assert file_matches_file_params(file_(), file_param_list)
    file_param_list = {
        'derived_from': set(['*']),
        'title': set(['ENCFF244PJU'])
    }
    assert file_matches_file_params(file_(), file_param_list)
    file_param_list = {
        'derived_from': set(['/files/ENCFF895UWM/', '/files/ENCFF089RYQ/']),
        'title': set(['ENCFF244PJU'])
    }
    assert file_matches_file_params(file_(), file_param_list)
    file_param_list = {
        'preferred_default': set(['*']),
        'assembly': set(['GRCh38']),
        'replicate.rbns_protein_concentration': set([20]),
        'derived_from': set(['/files/ENCFF895UWM/', '/files/ENCFF089RYQ/']),
        'file_size': set([3356650]),
        'no_file_available': set([False])
    }
    assert file_matches_file_params(file_(), file_param_list)
    file_param_list = {
        'preferred_default': set(['*']),
        'assembly': set(['GRCh38']),
        'replicate.rbns_protein_concentration': set([20]),
        'derived_from': set(['/files/ENCFF895UWM/', '/files/ENCFF089RYQ/']),
        'file_size': set([3356650]),
        'no_file_available': set([False]),
        'restricted': set([True])
    }
    assert not file_matches_file_params(file_(), file_param_list)
    file_param_list = {'nested.empty_list': set(['*'])}
    assert not file_matches_file_params(abstract_file(), file_param_list)
    file_param_list = {'nested.empty_list': set([])}
    assert not file_matches_file_params(abstract_file(), file_param_list)
    file_param_list = {'nested.list': set(['a'])}
    assert file_matches_file_params(abstract_file(), file_param_list)
    file_param_list = {'nested.list': set(['a', 'b'])}
    assert file_matches_file_params(abstract_file(), file_param_list)
    file_param_list = {'empty_list': set([])}
    assert not file_matches_file_params(abstract_file(), file_param_list)
    file_param_list = {'nested.str': set(['xyz'])}
    assert file_matches_file_params(abstract_file(), file_param_list)
    file_param_list = {'nested.str': set(['zxyz'])}
    assert not file_matches_file_params(abstract_file(), file_param_list)
    file_param_list = {'nested.int': set([2])}
    assert file_matches_file_params(abstract_file(), file_param_list)
    file_param_list = {'nested.int': set([2, 3])}
    assert file_matches_file_params(abstract_file(), file_param_list)
    file_param_list = {'nested.int': set([3])}
    assert not file_matches_file_params(abstract_file(), file_param_list)
    file_param_list = {'nested.boolean': set([True])}
    assert file_matches_file_params(abstract_file(), file_param_list)
    file_param_list = {'nested.boolean': set([True, False])}
    assert file_matches_file_params(abstract_file(), file_param_list)
    file_param_list = {'nested.boolean': set([False])}
    assert not file_matches_file_params(abstract_file(), file_param_list)


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
            assert tuple(sorted(set(audits[audit]))) == audit_value
    for audit, audit_value in grouped_other_audits.items():
        assert tuple(sorted(set(audit_value))) == expected_grouped_other_audits[audit]


def test_metadata_metadata_report_init(dummy_request):
    from encoded.reports.metadata import MetadataReport
    dummy_request.environ['QUERY_STRING'] = (
        'type=Experiment'
    )
    mr = MetadataReport(dummy_request)
    assert isinstance(mr, MetadataReport)


def test_metadata_metadata_report_query_string_init_and_param_list(dummy_request):
    from encoded.reports.metadata import MetadataReport
    from snovault.elasticsearch.searches.parsers import QueryString
    dummy_request.environ['QUERY_STRING'] = (
        'type=Experiment'
    )
    mr = MetadataReport(dummy_request)
    assert isinstance(mr.query_string, QueryString)
    expected_param_list = {'type': ['Experiment']}
    assert mr.param_list['type'] == expected_param_list['type']


def test_metadata_metadata_report_visualizable_and_raw_only_boolean(dummy_request):
    from encoded.reports.metadata import MetadataReport
    dummy_request.environ['QUERY_STRING'] = (
        'type=Experiment'
    )
    mr = MetadataReport(dummy_request)
    assert not mr.visualizable_only
    assert not mr.raw_only
    dummy_request.environ['QUERY_STRING'] = (
        'type=Experiment&option=visualizable'
    )
    mr = MetadataReport(dummy_request)
    assert mr.visualizable_only
    assert not mr.raw_only
    dummy_request.environ['QUERY_STRING'] = (
        'type=Experiment&option=raw'
    )
    mr = MetadataReport(dummy_request)
    assert not mr.visualizable_only
    assert mr.raw_only
    dummy_request.environ['QUERY_STRING'] = (
        'type=Experiment&option=visualizable&option=raw'
    )
    mr = MetadataReport(dummy_request)
    assert mr.visualizable_only
    assert mr.raw_only


def test_metadata_metadata_report_excluded_columns(dummy_request):
    from encoded.reports.metadata import MetadataReport
    dummy_request.environ['QUERY_STRING'] = (
        'type=Experiment'
    )
    mr = MetadataReport(dummy_request)
    assert mr.EXCLUDED_COLUMNS == (
        'Restricted',
        'No File Available'
    )


def test_metadata_metadata_report_get_column_to_fields_mapping(dummy_request):
    from encoded.reports.metadata import MetadataReport
    from encoded.reports.constants import METADATA_COLUMN_TO_FIELDS_MAPPING
    dummy_request.environ['QUERY_STRING'] = (
        'type=Experiment'
    )
    mr = MetadataReport(dummy_request)
    assert mr._get_column_to_fields_mapping() == METADATA_COLUMN_TO_FIELDS_MAPPING


def test_metadata_metadata_report_build_header(dummy_request):
    from encoded.reports.metadata import MetadataReport
    dummy_request.environ['QUERY_STRING'] = (
        'type=Experiment'
    )
    mr = MetadataReport(dummy_request)
    mr._build_header()
    expected_header = [
        'File accession',
        'File format',
        'File type',
        'File format type',
        'Output type',
        'File assembly',
        'Experiment accession',
        'Assay',
        'Biosample term id',
        'Biosample term name',
        'Biosample type',
        'Biosample organism',
        'Biosample treatments',
        'Biosample treatments amount',
        'Biosample treatments duration',
        'Biosample genetic modifications methods',
        'Biosample genetic modifications categories',
        'Biosample genetic modifications targets',
        'Biosample genetic modifications gene targets',
        'Biosample genetic modifications site coordinates',
        'Biosample genetic modifications zygosity',
        'Experiment target',
        'Library made from',
        'Library depleted in',
        'Library extraction method',
        'Library lysis method',
        'Library crosslinking method',
        'Library strand specific',
        'Experiment date released',
        'Project',
        'RBNS protein concentration',
        'Library fragmentation method',
        'Library size range',
        'Biological replicate(s)',
        'Technical replicate(s)',
        'Read length',
        'Mapped read length',
        'Run type',
        'Paired end',
        'Paired with',
        'Index of',
        'Derived from',
        'Size',
        'Lab',
        'md5sum',
        'dbxrefs',
        'File download URL',
        'Genome annotation',
        'Platform',
        'Controlled by',
        'File Status',
        's3_uri',
        'File analysis title',
        'File analysis status',
        'Audit WARNING',
        'Audit NOT_COMPLIANT',
        'Audit ERROR'
    ]
    assert mr.header == expected_header


def test_metadata_metadata_report_split_column_and_fields_by_experiment_and_file(dummy_request):
    from encoded.reports.metadata import MetadataReport
    dummy_request.environ['QUERY_STRING'] = (
        'type=Experiment'
    )
    mr = MetadataReport(dummy_request)
    mr._split_column_and_fields_by_experiment_and_file()
    expected_file_column_to_fields_mapping = {
        'File accession': ['title'],
        'File format': ['file_type'],
        'File type': ['file_format'],
        'File format type': ['file_format_type'],
        'Output type': ['output_type'],
        'File assembly': ['assembly'],
        'Biological replicate(s)': ['biological_replicates'],
        'Technical replicate(s)': ['technical_replicates'],
        'Read length': ['read_length'],
        'Mapped read length': ['mapped_read_length'],
        'Run type': ['run_type'],
        'Paired end': ['paired_end'],
        'Paired with': ['paired_with'],
        'Index of': ['index_of'],
        'Derived from': ['derived_from'],
        'RBNS protein concentration': [
            'replicate.rbns_protein_concentration',
            'replicate.rbns_protein_concentration_units'
        ],
        'Size': ['file_size'],
        'Lab': ['lab.title'],
        'md5sum': ['md5sum'],
        'dbxrefs': ['dbxrefs'],
        'File download URL': ['href'],
        'Genome annotation': ['genome_annotation'],
        'Platform': ['platform.title'],
        'Controlled by': ['controlled_by'],
        'File Status': ['status'],
        'No File Available': ['no_file_available'],
        'Restricted': ['restricted'],
        's3_uri': ['s3_uri'],
        'File analysis title': ['analyses.title'],
        'File analysis status': ['analyses.status']
    }
    expected_experiment_column_to_fields_mapping = {
        'Experiment accession': ['accession'],
        'Assay': ['assay_title'],
        'Biosample term id': ['biosample_ontology.term_id'],
        'Biosample term name': ['biosample_ontology.term_name'],
        'Biosample type': ['biosample_ontology.classification'],
        'Biosample organism': ['replicates.library.biosample.organism.scientific_name'],
        'Biosample treatments': ['replicates.library.biosample.treatments.treatment_term_name'],
        'Biosample treatments amount': [
            'replicates.library.biosample.treatments.amount',
            'replicates.library.biosample.treatments.amount_units'
        ],
        'Biosample treatments duration': [
            'replicates.library.biosample.treatments.duration',
            'replicates.library.biosample.treatments.duration_units'
        ],
        'Biosample genetic modifications methods': ['replicates.library.biosample.applied_modifications.method'],
        'Biosample genetic modifications categories': ['replicates.library.biosample.applied_modifications.category'],
        'Biosample genetic modifications targets': ['replicates.library.biosample.applied_modifications.modified_site_by_target_id'],
        'Biosample genetic modifications gene targets': ['replicates.library.biosample.applied_modifications.modified_site_by_gene_id'],
        'Biosample genetic modifications site coordinates': [
            'replicates.library.biosample.applied_modifications.modified_site_by_coordinates.assembly',
            'replicates.library.biosample.applied_modifications.modified_site_by_coordinates.chromosome',
            'replicates.library.biosample.applied_modifications.modified_site_by_coordinates.start',
            'replicates.library.biosample.applied_modifications.modified_site_by_coordinates.end'
        ],
        'Biosample genetic modifications zygosity': [
            'replicates.library.biosample.applied_modifications.zygosity'
        ],
        'Experiment target': ['target.name'],
        'Library made from': ['replicates.library.nucleic_acid_term_name'],
        'Library depleted in': ['replicates.library.depleted_in_term_name'],
        'Library extraction method': ['replicates.library.extraction_method'],
        'Library lysis method': ['replicates.library.lysis_method'],
        'Library crosslinking method': ['replicates.library.crosslinking_method'],
        'Library strand specific': ['replicates.library.strand_specificity'],
        'Library fragmentation method': ['replicates.library.fragmentation_methods'],
        'Library size range': ['replicates.library.size_range'],
        'Experiment date released': ['date_released'],
        'Project': ['award.project']
    }
    for k, v in mr.file_column_to_fields_mapping.items():
        assert tuple(expected_file_column_to_fields_mapping[k]) == tuple(v), f'{k, v} not in expected'
    for k, v in mr.experiment_column_to_fields_mapping.items():
        assert tuple(expected_experiment_column_to_fields_mapping[k]) == tuple(v), f'{k, v} not in expected'


def test_metadata_metadata_report_set_positive_file_param_set(dummy_request):
    from encoded.reports.metadata import MetadataReport
    dummy_request.environ['QUERY_STRING'] = (
        'type=Experiment&files.file_type=bigWig&files.file_type=bam'
        '&files.replicate.library.size_range=50-100'
        '&files.status!=archived&files.biological_replicates=2'
    )
    mr = MetadataReport(dummy_request)
    mr._set_positive_file_param_set()
    expected_positive_file_param_set = {
        'file_type': set(['bigWig', 'bam']),
        'replicate.library.size_range': set(['50-100']),
        'biological_replicates': set([2])
    }
    for k, v in mr.positive_file_param_set.items():
        assert tuple(sorted(expected_positive_file_param_set[k])) == tuple(sorted(v))


def test_metadata_metadata_report_add_positive_file_filters_as_fields_to_param_list(dummy_request):
    from encoded.reports.metadata import MetadataReport
    dummy_request.environ['QUERY_STRING'] = (
        'type=Experiment&files.file_type=bigWig&files.file_type=bam'
        '&files.replicate.library.size_range=50-100'
        '&files.status!=archived&files.biological_replicates=2'
        '&files.read_count=123'
    )
    mr = MetadataReport(dummy_request)
    assert mr.param_list.get('field', []) == []
    mr._add_positive_file_filters_as_fields_to_param_list()
    assert mr.param_list.get('field') == [
        'files.file_type',
        'files.file_type',
        'files.replicate.library.size_range',
        'files.biological_replicates',
        'files.read_count',
    ]


def test_metadata_metadata_report_add_fields_to_param_list(dummy_request):
    from encoded.reports.metadata import MetadataReport
    dummy_request.environ['QUERY_STRING'] = (
        'type=Experiment&files.file_type=bigWig&files.file_type=bam'
        '&replicates.library.size_range=50-100'
        '&files.status!=archived&files.biological_replicates=2'
        '&files.read_count=123'
    )
    mr = MetadataReport(dummy_request)
    mr._add_fields_to_param_list()
    expected_fields = [
        'files.title',
        'files.file_type',
        'files.file_format',
        'files.file_format_type',
        'files.output_type',
        'files.assembly',
        'accession',
        'assay_title',
        'biosample_ontology.term_id',
        'biosample_ontology.term_name',
        'biosample_ontology.classification',
        'replicates.library.biosample.organism.scientific_name',
        'replicates.library.biosample.treatments.treatment_term_name',
        'replicates.library.biosample.treatments.amount',
        'replicates.library.biosample.treatments.amount_units',
        'replicates.library.biosample.treatments.duration',
        'replicates.library.biosample.treatments.duration_units',
        'replicates.library.biosample.applied_modifications.method',
        'replicates.library.biosample.applied_modifications.category',
        'replicates.library.biosample.applied_modifications.modified_site_by_target_id',
        'replicates.library.biosample.applied_modifications.modified_site_by_gene_id',
        'replicates.library.biosample.applied_modifications.modified_site_by_coordinates.assembly',
        'replicates.library.biosample.applied_modifications.modified_site_by_coordinates.chromosome',
        'replicates.library.biosample.applied_modifications.modified_site_by_coordinates.start',
        'replicates.library.biosample.applied_modifications.modified_site_by_coordinates.end',
        'replicates.library.biosample.applied_modifications.zygosity',
        'replicates.library.fragmentation_methods',
        'replicates.library.size_range',
        'target.name',
        'replicates.library.nucleic_acid_term_name',
        'replicates.library.depleted_in_term_name',
        'replicates.library.extraction_method',
        'replicates.library.lysis_method',
        'replicates.library.crosslinking_method',
        'replicates.library.strand_specificity',
        'date_released',
        'award.project',
        'files.replicate.rbns_protein_concentration',
        'files.replicate.rbns_protein_concentration_units',
        'files.biological_replicates',
        'files.technical_replicates',
        'files.read_length',
        'files.mapped_read_length',
        'files.run_type',
        'files.paired_end',
        'files.paired_with',
        'files.index_of',
        'files.derived_from',
        'files.file_size',
        'files.lab.title',
        'files.md5sum',
        'files.dbxrefs',
        'files.href',
        'files.genome_annotation',
        'files.platform.title',
        'files.controlled_by',
        'files.status',
        'files.no_file_available',
        'files.restricted',
        'files.s3_uri',
        'files.analyses.title',
        'files.analyses.status',
        'files.read_count',
    ]
    assert set(mr.param_list['field']) == set(expected_fields), f"{set(mr.param_list['field']) - set(expected_fields)}"


def test_metadata_metadata_report_initialize_at_id_param(dummy_request):
    from encoded.reports.metadata import MetadataReport
    dummy_request.environ['QUERY_STRING'] = (
        'type=Experiment&files.file_type=bigWig&files.file_type=bam'
        '&replicates.library.size_range=50-100'
        '&files.status!=archived&files.biological_replicates=2'
    )
    mr = MetadataReport(dummy_request)
    mr._initialize_at_id_param()
    assert mr.param_list['@id'] == []
    dummy_request.environ['QUERY_STRING'] = (
        'type=Experiment&files.file_type=bigWig&files.file_type=bam'
        '&replicates.library.size_range=50-100'
        '&files.status!=archived&files.biological_replicates=2'
        '&@id=/experiments/ENCSR123ABC/'
    )
    mr = MetadataReport(dummy_request)
    mr._initialize_at_id_param()
    assert mr.param_list['@id'] == ['/experiments/ENCSR123ABC/']


def test_metadata_metadata_report_maybe_add_cart_elements_to_param_list(dummy_request, mocker):
    from encoded.reports.metadata import MetadataReport
    mocker.patch.object(dummy_request, 'embed')
    dummy_request.embed.return_value = {
        "status": "current",
        "date_created": "2018-11-29T22:36:42.389928+00:00",
        "submitted_by": "/users/7e95dcd6-9c35-4082-9c53-09d14c5752be/",
        "schema_version": "1",
        "name": "Keenan Graham cart",
        "locked": False,
        "elements": [
            "/experiments/ENCSR483RKN/",
            "/experiments/ENCSR514NTD/"
        ],
        "@id": "/carts/8759684c-9f00-4300-a72f-5eea736adb4a/",
        "@type": ["Cart", "Item"],
        "uuid": "8759684c-9f00-4300-a72f-5eea736adb4a",
        "@context": "/terms/",
        "audit": {}
    }
    dummy_request.environ['QUERY_STRING'] = (
        'type=Experiment&files.file_type=bigWig&files.file_type=bam'
        '&replicates.library.size_range=50-100'
        '&files.status!=archived&files.biological_replicates=2'
    )
    mr = MetadataReport(dummy_request)
    mr._initialize_at_id_param()
    mr._maybe_add_cart_elements_to_param_list()
    assert mr.param_list['@id'] == []
    dummy_request.environ['QUERY_STRING'] = (
        'type=Experiment&files.file_type=bigWig&files.file_type=bam'
        '&files.replicate.library.size_range=50-100'
        '&files.status!=archived&files.biological_replicates=2'
        '&cart=1234'
    )
    mr = MetadataReport(dummy_request)
    mr._initialize_at_id_param()
    mr._maybe_add_cart_elements_to_param_list()
    assert mr.param_list['@id'] == [
        "/experiments/ENCSR483RKN/",
        "/experiments/ENCSR514NTD/"
    ]
    dummy_request.embed.side_effect = KeyError
    mr = MetadataReport(dummy_request)
    mr._initialize_at_id_param()
    with pytest.raises(HTTPBadRequest):
        mr._maybe_add_cart_elements_to_param_list()


def test_metadata_metadata_report_get_json_elements_or_empty_list(dummy_request):
    from encoded.reports.metadata import MetadataReport
    dummy_request.environ['QUERY_STRING'] = (
        'type=Experiment&files.file_type=bigWig&files.file_type=bam'
        '&replicates.library.size_range=50-100'
        '&files.status!=archived&files.biological_replicates=2'
    )
    mr = MetadataReport(dummy_request)
    mr._initialize_at_id_param()
    at_ids = mr._get_json_elements_or_empty_list()
    assert at_ids == []
    dummy_request.json = {'elements': ['/experiments/ENCSR123ABC/']}
    mr = MetadataReport(dummy_request)
    mr._initialize_at_id_param()
    at_ids = mr._get_json_elements_or_empty_list()
    assert at_ids == [
        '/experiments/ENCSR123ABC/'
    ]
    dummy_request.json = {'elements': []}
    mr = MetadataReport(dummy_request)
    mr._initialize_at_id_param()
    at_ids = mr._get_json_elements_or_empty_list()
    assert at_ids == []


def test_metadata_metadata_report_maybe_add_json_elements_to_param_list(dummy_request):
    from encoded.reports.metadata import MetadataReport
    dummy_request.environ['QUERY_STRING'] = (
        'type=Experiment&files.file_type=bigWig&files.file_type=bam'
        '&replicates.library.size_range=50-100'
        '&files.status!=archived&files.biological_replicates=2'
    )
    mr = MetadataReport(dummy_request)
    mr._initialize_at_id_param()
    mr._maybe_add_json_elements_to_param_list()
    assert mr.param_list['@id'] == []
    dummy_request.json = {'elements': ['/experiments/ENCSR123ABC/']}
    mr = MetadataReport(dummy_request)
    mr._initialize_at_id_param()
    mr._maybe_add_json_elements_to_param_list()
    assert mr.param_list['@id'] == [
        '/experiments/ENCSR123ABC/'
    ]
    dummy_request.json = {'elements': []}
    mr = MetadataReport(dummy_request)
    mr._initialize_at_id_param()
    mr._maybe_add_json_elements_to_param_list()
    assert mr.param_list['@id'] == []


def test_metadata_metadata_report_get_field_params(dummy_request):
    from encoded.reports.metadata import MetadataReport
    dummy_request.environ['QUERY_STRING'] = (
        'type=Experiment&files.file_type=bigWig&files.file_type=bam'
        '&replicates.library.size_range=50-100'
        '&files.status!=archived&files.biological_replicates=2'
    )
    mr = MetadataReport(dummy_request)
    mr._add_fields_to_param_list()
    expected_field_params = [
        ('field', 'files.title'),
        ('field', 'files.file_type'),
        ('field', 'files.file_format'),
        ('field', 'files.file_format_type'),
        ('field', 'files.output_type'),
        ('field', 'files.assembly'),
        ('field', 'accession'),
        ('field', 'assay_title'),
        ('field', 'biosample_ontology.term_id'),
        ('field', 'biosample_ontology.term_name'),
        ('field', 'biosample_ontology.classification'),
        ('field', 'replicates.library.biosample.organism.scientific_name'),
        ('field', 'replicates.library.biosample.treatments.treatment_term_name'),
        ('field', 'replicates.library.biosample.treatments.amount'),
        ('field', 'replicates.library.biosample.treatments.amount_units'),
        ('field', 'replicates.library.biosample.treatments.duration'),
        ('field', 'replicates.library.biosample.treatments.duration_units'),
        ('field', 'replicates.library.biosample.applied_modifications.method'),
        ('field', 'replicates.library.biosample.applied_modifications.category'),
        ('field', 'replicates.library.biosample.applied_modifications.modified_site_by_target_id'),
        ('field', 'replicates.library.biosample.applied_modifications.modified_site_by_gene_id'),
        ('field', 'replicates.library.biosample.applied_modifications.modified_site_by_coordinates.assembly'),
        ('field', 'replicates.library.biosample.applied_modifications.modified_site_by_coordinates.chromosome'),
        ('field', 'replicates.library.biosample.applied_modifications.modified_site_by_coordinates.start'),
        ('field', 'replicates.library.biosample.applied_modifications.modified_site_by_coordinates.end'),
        ('field', 'replicates.library.biosample.applied_modifications.zygosity'),
        ('field', 'target.name'),
        ('field', 'replicates.library.nucleic_acid_term_name'),
        ('field', 'replicates.library.depleted_in_term_name'),
        ('field', 'replicates.library.extraction_method'),
        ('field', 'replicates.library.lysis_method'),
        ('field', 'replicates.library.crosslinking_method'),
        ('field', 'replicates.library.strand_specificity'),
        ('field', 'date_released'),
        ('field', 'award.project'),
        ('field', 'files.replicate.rbns_protein_concentration'),
        ('field', 'files.replicate.rbns_protein_concentration_units'),
        ('field', 'replicates.library.fragmentation_methods'),
        ('field', 'replicates.library.size_range'),
        ('field', 'files.biological_replicates'),
        ('field', 'files.technical_replicates'),
        ('field', 'files.read_length'),
        ('field', 'files.mapped_read_length'),
        ('field', 'files.run_type'),
        ('field', 'files.paired_end'),
        ('field', 'files.paired_with'),
        ('field', 'files.index_of'),
        ('field', 'files.derived_from'),
        ('field', 'files.file_size'),
        ('field', 'files.lab.title'),
        ('field', 'files.md5sum'),
        ('field', 'files.dbxrefs'),
        ('field', 'files.href'),
        ('field', 'files.genome_annotation'),
        ('field', 'files.platform.title'),
        ('field', 'files.controlled_by'),
        ('field', 'files.status'),
        ('field', 'files.no_file_available'),
        ('field', 'files.restricted'),
        ('field', 'files.s3_uri'),
        ('field', 'files.analyses.title'),
        ('field', 'files.analyses.status'),
    ]
    for param in mr._get_field_params():
        assert param in expected_field_params, f'{param}'


def test_metadata_metadata_report_get_at_id_params(dummy_request):
    from encoded.reports.metadata import MetadataReport
    dummy_request.environ['QUERY_STRING'] = (
        'type=Experiment&files.file_type=bigWig&files.file_type=bam'
        '&replicates.library.size_range=50-100'
        '&files.status!=archived&files.biological_replicates=2'
    )
    dummy_request.json = {'elements': ['/experiments/ENCSR123ABC/']}
    mr = MetadataReport(dummy_request)
    mr._initialize_at_id_param()
    mr._maybe_add_json_elements_to_param_list()
    assert mr._get_at_id_params() == [('@id', '/experiments/ENCSR123ABC/')]


def test_metadata_metadata_report_get_default_params(dummy_request):
    from encoded.reports.metadata import MetadataReport
    dummy_request.environ['QUERY_STRING'] = (
        'type=Experiment&files.file_type=bigWig&files.file_type=bam'
        '&replicates.library.size_range=50-100'
        '&files.status!=archived&files.biological_replicates=2'
    )
    dummy_request.json = {'elements': ['/experiments/ENCSR123ABC/']}
    mr = MetadataReport(dummy_request)
    assert mr._get_default_params() == [
        ('field', 'audit'),
        ('field', 'files.@id'),
        ('field', 'files.restricted'),
        ('field', 'files.no_file_available'),
        ('field', 'files.file_format'),
        ('field', 'files.file_format_type'),
        ('field', 'files.status'),
        ('field', 'files.assembly'),
        ('limit', 'all'),
    ]

def test_metadata_metadata_report_build_query_string(dummy_request):
    from encoded.reports.metadata import MetadataReport
    dummy_request.environ['QUERY_STRING'] = (
        'type=Experiment&files.file_type=bigWig&files.file_type=bam'
        '&replicates.library.size_range=50-100'
        '&files.status!=archived&files.biological_replicates=2'
    )
    mr = MetadataReport(dummy_request)
    mr._build_query_string()
    assert str(mr.query_string) == (
        'type=Experiment&files.file_type=bigWig'
        '&files.file_type=bam&replicates.library.size_range=50-100'
        '&files.status%21=archived&files.biological_replicates=2'
        '&field=audit&field=files.%40id&field=files.restricted'
        '&field=files.no_file_available&field=files.file_format'
        '&field=files.file_format_type&field=files.status'
        '&field=files.assembly&limit=all'
    )


def test_metadata_metadata_report_get_search_path(dummy_request):
    from encoded.reports.metadata import MetadataReport
    dummy_request.environ['QUERY_STRING'] = (
        'type=Experiment&files.file_type=bigWig&files.file_type=bam'
        '&replicates.library.size_range=50-100'
        '&files.status!=archived&files.biological_replicates=2'
    )
    mr = MetadataReport(dummy_request)
    assert mr._get_search_path() == '/search/'


def test_metadata_metadata_report_validate_request(dummy_request):
    from encoded.reports.metadata import MetadataReport
    dummy_request.environ['QUERY_STRING'] = (
        'type=Experiment&files.file_type=bigWig&files.file_type=bam'
        '&replicates.library.size_range=50-100'
        '&files.status!=archived&files.biological_replicates=2'
    )
    mr = MetadataReport(dummy_request)
    assert mr._validate_request()
    dummy_request.environ['QUERY_STRING'] = (
        'type=Experiment&type=Annotation&files.file_type=bigWig&files.file_type=bam'
        '&replicates.library.size_range=50-100'
        '&files.status!=archived&files.biological_replicates=2'
    )
    mr = MetadataReport(dummy_request)
    with pytest.raises(HTTPBadRequest):
        mr._validate_request()
    dummy_request.environ['QUERY_STRING'] = (
        'files.file_type=bigWig&files.file_type=bam'
        '&replicates.library.size_range=50-100'
        '&files.status!=archived&files.biological_replicates=2'
    )
    mr = MetadataReport(dummy_request)
    with pytest.raises(HTTPBadRequest):
        mr._validate_request()


def test_metadata_metadata_report_initialize_report(dummy_request):
    from encoded.reports.metadata import MetadataReport
    dummy_request.environ['QUERY_STRING'] = (
        'type=Experiment&files.file_type=bigWig&files.file_type=bam'
        '&replicates.library.size_range=50-100'
        '&files.status!=archived&files.biological_replicates=2'
    )
    mr = MetadataReport(dummy_request)
    mr._initialize_report()
    assert len(mr.header) == 57
    assert len(mr.experiment_column_to_fields_mapping.keys()) == 26, f'{len(mr.experiment_column_to_fields_mapping.keys())}'
    assert len(mr.file_column_to_fields_mapping.keys()) == 30, f'{len(mr.file_column_to_fields_mapping.keys())}'


def test_metadata_metadata_report_build_params(dummy_request):
    from encoded.reports.metadata import MetadataReport
    dummy_request.environ['QUERY_STRING'] = (
        'type=Experiment&files.file_type=bigWig&files.file_type=bam'
        '&replicates.library.size_range=50-100'
        '&files.status!=archived&files.biological_replicates=2'
    )
    dummy_request.json = {'elements': ['/experiments/ENCSR123ABC/']}
    mr = MetadataReport(dummy_request)
    mr._build_params()
    assert len(mr.param_list['field']) == 65, f'{len(mr.param_list["field"])} not expected'
    assert len(mr.param_list['@id']) == 1


def test_metadata_metadata_report_build_new_request(dummy_request):
    from encoded.reports.metadata import MetadataReport
    dummy_request.environ['QUERY_STRING'] = (
        'type=Experiment&files.file_type=bigWig&files.file_type=bam'
        '&replicates.library.size_range=50-100'
        '&files.status!=archived&files.biological_replicates=2'
        '&files.derived_from=/experiments/ENCSR123ABC/'
        '&files.replicate.library=*'
    )
    dummy_request.json = {'elements': ['/experiments/ENCSR123ABC/']}
    mr = MetadataReport(dummy_request)
    mr._build_params()
    new_request = mr._build_new_request()
    assert new_request.path_info == '/search/'
    assert new_request.registry
    assert str(new_request.query_string) == (
        'type=Experiment&files.file_type=bigWig&files.file_type=bam'
        '&replicates.library.size_range=50-100&files.status%21=archived'
        '&files.biological_replicates=2&files.derived_from=%2Fexperiments%2FENCSR123ABC%2F'
        '&files.replicate.library=%2A&field=audit&field=files.%40id&field=files.restricted'
        '&field=files.no_file_available&field=files.file_format&field=files.file_format_type'
        '&field=files.status&field=files.assembly&limit=all&field=files.title&field=files.file_type'
        '&field=files.output_type&field=accession&field=assay_title&field=biosample_ontology.term_id'
        '&field=biosample_ontology.term_name&field=biosample_ontology.classification'
        '&field=replicates.library.biosample.organism.scientific_name'
        '&field=replicates.library.biosample.treatments.treatment_term_name'
        '&field=replicates.library.biosample.treatments.amount&field=replicates.library.biosample.treatments.amount_units'
        '&field=replicates.library.biosample.treatments.duration&field=replicates.library.biosample.treatments.duration_units'
        '&field=replicates.library.biosample.applied_modifications.method'
        '&field=replicates.library.biosample.applied_modifications.category'
        '&field=replicates.library.biosample.applied_modifications.modified_site_by_target_id'
        '&field=replicates.library.biosample.applied_modifications.modified_site_by_gene_id'
        '&field=replicates.library.biosample.applied_modifications.modified_site_by_coordinates.assembly'
        '&field=replicates.library.biosample.applied_modifications.modified_site_by_coordinates.chromosome'
        '&field=replicates.library.biosample.applied_modifications.modified_site_by_coordinates.start'
        '&field=replicates.library.biosample.applied_modifications.modified_site_by_coordinates.end'
        '&field=replicates.library.biosample.applied_modifications.zygosity&field=target.name'
        '&field=replicates.library.nucleic_acid_term_name&field=replicates.library.depleted_in_term_name'
        '&field=replicates.library.extraction_method&field=replicates.library.lysis_method'
        '&field=replicates.library.crosslinking_method&field=replicates.library.strand_specificity'
        '&field=date_released&field=award.project&field=files.replicate.rbns_protein_concentration'
        '&field=files.replicate.rbns_protein_concentration_units&field=replicates.library.fragmentation_methods'
        '&field=replicates.library.size_range&field=files.biological_replicates&field=files.technical_replicates'
        '&field=files.read_length&field=files.mapped_read_length&field=files.run_type&field=files.paired_end'
        '&field=files.paired_with&field=files.index_of&field=files.derived_from&field=files.file_size'
        '&field=files.lab.title&field=files.md5sum&field=files.dbxrefs&field=files.href&field=files.genome_annotation'
        '&field=files.platform.title&field=files.controlled_by&field=files.s3_uri&field=files.analyses.title'
        '&field=files.analyses.status&field=files.replicate.library'
        '&%40id=%2Fexperiments%2FENCSR123ABC%2F'
    )
    assert new_request.effective_principals == ['system.Everyone']


def test_metadata_metadata_report_should_not_report_file(dummy_request):
    from encoded.reports.metadata import MetadataReport
    dummy_request.environ['QUERY_STRING'] = (
        'type=Experiment&files.file_type=bigWig&files.file_type=bam'
        '&replicates.library.size_range=50-100'
        '&files.status!=archived&files.biological_replicates=2'
    )
    mr = MetadataReport(dummy_request)
    mr._initialize_report()
    mr._build_params()
    # File attribute mismatch.
    assert mr._should_not_report_file(file_())
    from encoded.reports.metadata import MetadataReport
    dummy_request.environ['QUERY_STRING'] = (
        'type=Experiment&files.file_format=bed'
    )
    mr = MetadataReport(dummy_request)
    mr._initialize_report()
    mr._build_params()
    # File attribute match.
    assert not mr._should_not_report_file(file_())
    dummy_request.environ['QUERY_STRING'] = (
        'type=Experiment&files.file_format=bed'
    )
    mr = MetadataReport(dummy_request)
    mr._initialize_report()
    mr._build_params()
    modified_file = file_()
    modified_file['restricted'] = True
    # File restricted.
    assert mr._should_not_report_file(modified_file)
    dummy_request.environ['QUERY_STRING'] = (
        'type=Experiment&files.file_format=bed'
    )
    mr = MetadataReport(dummy_request)
    mr._initialize_report()
    mr._build_params()
    modified_file = file_()
    modified_file['no_file_available'] = True
    # File not available.
    assert mr._should_not_report_file(modified_file)
    dummy_request.environ['QUERY_STRING'] = (
        'type=Experiment&files.file_format=bed'
        '&option=visualizable'
    )
    mr = MetadataReport(dummy_request)
    mr._initialize_report()
    mr._build_params()
    # File not visualizable.
    assert mr._should_not_report_file(file_())
    dummy_request.environ['QUERY_STRING'] = (
        'type=Experiment&files.file_format=bed'
        '&option=raw'
    )
    mr = MetadataReport(dummy_request)
    mr._initialize_report()
    mr._build_params()
    # File not raw.
    assert mr._should_not_report_file(file_())


def test_metadata_metadata_report_get_experiment_data(dummy_request):
    from encoded.reports.metadata import MetadataReport
    dummy_request.environ['QUERY_STRING'] = (
        'type=Experiment&files.file_type=bigWig&files.file_type=bam'
        '&replicates.library.size_range=50-100'
        '&files.status!=archived&files.biological_replicates=2'
    )
    mr = MetadataReport(dummy_request)
    mr._initialize_report()
    mr._build_params()
    expected_experiment_data = {
        'Experiment accession': 'ENCSR434TGY',
        'Assay': 'DNase-seq',
        'Biosample term id': 'EFO:0005914',
        'Biosample term name': 'ZHBTc4',
        'Biosample type': 'cell line',
        'Biosample organism': 'Mus musculus',
        'Biosample treatments': 'doxycycline hyclate',
        'Biosample treatments amount': '100 ng/mL',
        'Biosample treatments duration': '96 hour',
        'Biosample genetic modifications methods': '',
        'Biosample genetic modifications categories': '',
        'Biosample genetic modifications targets': '',
        'Biosample genetic modifications gene targets': '',
        'Biosample genetic modifications site coordinates': '',
        'Biosample genetic modifications zygosity': '',
        'Experiment target': '',
        'Library made from': 'DNA',
        'Library depleted in': '',
        'Library extraction method': '',
        'Library lysis method': '',
        'Library crosslinking method': '',
        'Library strand specific': '',
        'Library fragmentation method': '',
        'Library size range': '',
        'Experiment date released': '2020-07-28',
        'Project': 'ENCODE'
    }
    experiment_data = mr._get_experiment_data(embedded_experiment())
    for k, v in expected_experiment_data.items():
        assert experiment_data[k] == v, f'{experiment_data[k]} not equal to {v}'


def test_metadata_metadata_report_get_file_data(dummy_request):
    from encoded.reports.metadata import MetadataReport
    dummy_request.environ['QUERY_STRING'] = (
        'type=Experiment'
    )
    mr = MetadataReport(dummy_request)
    mr._initialize_report()
    mr._build_params()
    expected_file_data = {
        'File accession': 'ENCFF244PJU',
        'File format': 'bed idr_ranked_peak',
        'File type': 'bed',
        'File format type': 'idr_ranked_peak',
        'Output type': 'IDR ranked peaks',
        'File assembly': 'GRCh38',
        'Biological replicate(s)': '2',
        'Technical replicate(s)': '2_1',
        'Read length': '',
        'Mapped read length': '',
        'Run type': '',
        'Paired end': '',
        'Paired with': '',
        'Index of': '',
        'RBNS protein concentration': '20 nM',
        'Derived from': '/files/ENCFF895UWM/, /files/ENCFF089RYQ/',
        'Size': 3356650,
        'Lab': 'ENCODE Processing Pipeline',
        'md5sum': '335b6066a184f30f225aec79b376c7e8',
        'dbxrefs': '',
        'File download URL': 'http://localhost/files/ENCFF244PJU/@@download/ENCFF244PJU.bed.gz',
        'Genome annotation': '',
        'Platform': '',
        'Controlled by': '',
        'File Status': 'released',
        'No File Available': False,
        'Restricted': '',
        's3_uri': 's3://encode-public/2020/07/09/dc068c0a-d1c8-461a-a208-418d35121f3b/ENCFF244PJU.bed.gz'
    }
    file_data = mr._get_file_data(file_())
    for k, v in expected_file_data.items():
        assert file_data[k] == v


def test_metadata_metadata_report_get_audit_data(dummy_request):
    from encoded.reports.metadata import MetadataReport
    from encoded.reports.metadata import group_audits_by_files_and_type
    grouped_file_audits, grouped_other_audits = group_audits_by_files_and_type(audits_())
    dummy_request.environ['QUERY_STRING'] = (
        'type=Experiment'
    )
    mr = MetadataReport(dummy_request)
    mr._initialize_report()
    mr._build_params()
    audit_data = mr._get_audit_data(
        grouped_file_audits.get('/files/ENCFF783ZRQ/'),
        grouped_other_audits
    )
    expected_audit_data = {
        'Audit WARNING': [
            'inconsistent control read length',
            'inconsistent platforms',
            'low read length',
            'mild to moderate bottlenecking',
            'moderate library complexity'
        ],
        'Audit NOT_COMPLIANT': ['insufficient read depth'],
        'Audit ERROR': ['extremely low read depth']
    }
    for k, v in expected_audit_data.items():
        assert sorted(audit_data[k].split(', ')) == v, f'{sorted(audit_data[k].split(", "))} does not match {v}'


def test_metadata_metadata_report_output_sorted_row(dummy_request):
    from encoded.reports.metadata import MetadataReport
    from encoded.reports.metadata import group_audits_by_files_and_type
    grouped_file_audits, grouped_other_audits = group_audits_by_files_and_type(audits_())
    dummy_request.environ['QUERY_STRING'] = (
        'type=Experiment'
    )
    mr = MetadataReport(dummy_request)
    mr._initialize_report()
    mr._build_params()
    file_data = mr._get_file_data(file_())
    experiment_data = mr._get_experiment_data(embedded_experiment())
    audit_data = mr._get_audit_data(
        grouped_file_audits.get('/files/ENCFF783ZRQ/'),
        grouped_other_audits
    )
    file_data.update(audit_data)
    actual_sorted_row = mr._output_sorted_row(experiment_data, file_data)
    expected_sorted_row = [
        'ENCFF244PJU',
        'bed idr_ranked_peak',
        'bed',
        'idr_ranked_peak',
        'IDR ranked peaks',
        'GRCh38',
        'ENCSR434TGY',
        'DNase-seq',
        'EFO:0005914',
        'ZHBTc4',
        'cell line',
        'Mus musculus',
        'doxycycline hyclate',
        '100 ng/mL',
        '96 hour',
        '',
        '',
        '',
        '',
        '',
        '',
        '',
        'DNA',
        '',
        '',
        '',
        '',
        '',
        '2020-07-28',
        'ENCODE',
        '20 nM',
        '',
        '',
        '2',
        '2_1',
        '',
        '',
        '',
        '',
        '',
        '',
        (
            '/files/ENCFF895UWM/',
            '/files/ENCFF089RYQ/'
        ),
        3356650,
        'ENCODE Processing Pipeline',
        '335b6066a184f30f225aec79b376c7e8',
        '',
        'http://localhost/files/ENCFF244PJU/@@download/ENCFF244PJU.bed.gz',
        '',
        '',
        '',
        'released',
        's3://encode-public/2020/07/09/dc068c0a-d1c8-461a-a208-418d35121f3b/ENCFF244PJU.bed.gz',
        '',
        '',
        (
            'inconsistent control read length',
            'low read length',
            'mild to moderate bottlenecking',
            'moderate library complexity',
            'inconsistent platforms',
        ),
        'insufficient read depth',
        'extremely low read depth'
    ]
    for expected, actual in zip(expected_sorted_row, actual_sorted_row):
        if isinstance(expected, tuple):
            assert list(sorted(expected)) == sorted(actual.split(', '))
        else:
            assert expected == actual, f'{expected} not equal to {actual}'


def test_metadata_metadata_report_get_search_results_generator(index_workbook, dummy_request):
    from types import GeneratorType
    from encoded.reports.metadata import MetadataReport
    dummy_request.environ['QUERY_STRING'] = (
        'type=Experiment'
    )
    mr = MetadataReport(dummy_request)
    mr._build_params()
    search_results = mr._get_search_results_generator()
    assert isinstance(search_results, GeneratorType)
    assert len(list(search_results)) >= 63


def test_metadata_metadata_report_generate_rows(index_workbook, dummy_request):
    from types import GeneratorType
    from encoded.reports.metadata import MetadataReport
    dummy_request.environ['QUERY_STRING'] = (
        'type=Experiment'
    )
    mr = MetadataReport(dummy_request)
    mr._initialize_report()
    mr._build_params()
    row_generator = mr._generate_rows()
    assert isinstance(row_generator, GeneratorType)
    assert len(list(row_generator)) >= 100


def test_metadata_metadata_report_generate_rows_no_files_in_experiment(dummy_request, mocker):
    from types import GeneratorType
    from encoded.reports.metadata import MetadataReport
    dummy_request.environ['QUERY_STRING'] = (
        'type=Experiment'
    )
    modified_experiment = experiment()
    modified_experiment['files'] = []
    mr = MetadataReport(dummy_request)
    mr._initialize_report()
    mr._build_params()
    mocker.patch.object(mr, '_get_search_results_generator')
    mr._get_search_results_generator.return_value = (
        x for x in [modified_experiment]
    )
    row_generator = mr._generate_rows()
    assert isinstance(row_generator, GeneratorType)
    assert len(list(row_generator)) == 1


def test_metadata_metadata_report_generate(index_workbook, dummy_request):
    from types import GeneratorType
    from encoded.reports.metadata import MetadataReport
    from pyramid.response import Response
    dummy_request.environ['QUERY_STRING'] = (
        'type=Experiment'
    )
    mr = MetadataReport(dummy_request)
    response = mr.generate()
    assert isinstance(response, Response)
    assert response.content_type == 'text/tsv'
    assert response.content_disposition == 'attachment; filename="metadata.tsv"'
    assert len(list(response.body)) >= 100


def test_metadata_view(index_workbook, testapp):
    r = testapp.get('/metadata/?type=Experiment')
    assert len(r.text.split('\n')) >= 100


def test_metadata_view_annotation(index_workbook, testapp):
    r = testapp.get('/metadata/?type=Annotation')
    assert len(r.text.split('\n')) >= 7


def test_metadata_view_publication_data(index_workbook, testapp):
    r = testapp.get(
        '/metadata/?type=PublicationData&@id=/publication-data/ENCSR727WCB/'
    )
    assert len(r.text.split('\n')) >= 7


def test_metadata_contains_audit_values(index_workbook, testapp):
    r = testapp.get('/metadata/?type=Experiment')
    audit_values = [
        'inconsistent library biosample',
        'lacking processed data',
        'inconsistent platforms',
        'missing documents',
        'unreplicated experiment'
    ]
    for value in audit_values:
        assert value in r.text, f'{value} not in metadata report'


def test_metadata_contains_all_values(index_workbook, testapp):
    from pkg_resources import resource_filename
    r = testapp.get('/metadata/?type=Experiment')
    actual = sorted([tuple(x.split('\t')) for x in r.text.strip().split('\n')])
    expected_path = resource_filename('encoded', 'tests/data/inserts/expected_metadata.tsv')
    # To write new expected_metadata.tsv change 'r' to 'w' and f.write(r.text); return;
    with open(expected_path, 'r') as f:
        expected = sorted([tuple(x.split('\t')) for x in f.readlines()])
    for i, row in enumerate(actual):
        for j, column in enumerate(row):
            # Sometimes lists are out of order.
            expected_value = tuple(sorted([x.strip() for x in expected[i][j].split(',')]))
            actual_value = tuple(sorted([x.strip() for x in column.split(',')]))
            assert expected_value == actual_value, f'Mistmatch on row {i} column {j}. {expected_value} != {actual_value}'


def test_metadata_contains_all_annotation_values(index_workbook, testapp):
    from pkg_resources import resource_filename
    r = testapp.get('/metadata/?type=Annotation')
    actual = sorted([tuple(x.split('\t')) for x in r.text.strip().split('\n')])
    expected_path = resource_filename('encoded', 'tests/data/inserts/expected_annotation_metadata.tsv')
    # To write new expected_metadata.tsv change 'r' to 'w' and f.write(r.text); return;
    with open(expected_path, 'r') as f:
        expected = sorted([tuple(x.split('\t')) for x in f.readlines()])
    for i, row in enumerate(actual):
        for j, column in enumerate(row):
            # Sometimes lists are out of order.
            expected_value = tuple(sorted([x.strip() for x in expected[i][j].split(',')]))
            actual_value = tuple(sorted([x.strip() for x in column.split(',')]))
            assert expected_value == actual_value, f'Mistmatch on row {i} column {j}. {expected_value} != {actual_value}'


def test_metadata_contains_all_publication_data_values(index_workbook, testapp):
    from pkg_resources import resource_filename
    r = testapp.get('/metadata/?type=PublicationData&@id=/publication-data/ENCSR727WCB/')
    actual = sorted([tuple(x.split('\t')) for x in r.text.strip().split('\n')])
    expected_path = resource_filename('encoded', 'tests/data/inserts/expected_publication_data_metadata.tsv')
    # To write new expected_metadata.tsv change 'r' to 'w' and f.write(r.text); return;
    with open(expected_path, 'r') as f:
        expected = sorted([tuple(x.split('\t')) for x in f.readlines()])
    for i, row in enumerate(actual):
        for j, column in enumerate(row):
            # Sometimes lists are out of order.
            expected_value = tuple(sorted([x.strip() for x in expected[i][j].split(',')]))
            actual_value = tuple(sorted([x.strip() for x in column.split(',')]))
            assert expected_value == actual_value, f'Mistmatch on row {i} column {j}. {expected_value} != {actual_value}'


def test_metadata_annotation_metadata_report_get_column_to_fields_mapping(dummy_request):
    from encoded.reports.metadata import AnnotationMetadataReport
    from encoded.reports.constants import ANNOTATION_METADATA_COLUMN_TO_FIELDS_MAPPING
    dummy_request.environ['QUERY_STRING'] = (
        'type=Experiment'
    )
    amr = AnnotationMetadataReport(dummy_request)
    assert amr._get_column_to_fields_mapping() == ANNOTATION_METADATA_COLUMN_TO_FIELDS_MAPPING


def test_metadata_publication_data_metadata_report_init(dummy_request):
    from encoded.reports.metadata import PublicationDataMetadataReport
    dummy_request.environ['QUERY_STRING'] = (
        'type=PublicationData'
    )
    pdmr = PublicationDataMetadataReport(dummy_request)
    assert isinstance(pdmr, PublicationDataMetadataReport)
    assert pdmr.file_query_string


def test_metadata_publication_data_metadata_report_get_column_to_field_mapping(dummy_request):
    from encoded.reports.metadata import PublicationDataMetadataReport
    from encoded.reports.constants import PUBLICATION_DATA_METADATA_COLUMN_TO_FIELDS_MAPPING
    dummy_request.environ['QUERY_STRING'] = (
        'type=PublicationData'
    )
    pdmr = PublicationDataMetadataReport(dummy_request)
    assert pdmr._get_column_to_fields_mapping() == PUBLICATION_DATA_METADATA_COLUMN_TO_FIELDS_MAPPING


def test_metadata_publication_data_metadata_report_build_header(dummy_request):
    from encoded.reports.metadata import PublicationDataMetadataReport
    dummy_request.environ['QUERY_STRING'] = (
        'type=PublicationData'
    )
    pdmr = PublicationDataMetadataReport(dummy_request)
    pdmr._build_header()
    assert pdmr.header == [
        'File accession',
        'File dataset',
        'File type',
        'File format',
        'File output type',
        'Assay term name',
        'Biosample term id',
        'Biosample term name',
        'Biosample type',
        'File target',
        'Dataset accession',
        'Dataset date released',
        'Project',
        'Lab',
        'md5sum',
        'dbxrefs',
        'File download URL',
        'Assembly',
        'File status',
        'Derived from',
        'S3 URL',
        'Size'
    ]


def test_metadata_publication_data_metadata_report_split_column_and_fields_by_experiment_and_file(dummy_request):
    from encoded.reports.metadata import PublicationDataMetadataReport
    dummy_request.environ['QUERY_STRING'] = (
        'type=PublicationData&files.file_type=bigWig'
    )
    pdmr = PublicationDataMetadataReport(dummy_request)
    pdmr._split_column_and_fields_by_experiment_and_file()
    expected_file_column_to_fields_mapping = {
        'File accession': ['title'],
        'File dataset': ['dataset'],
        'File type': ['file_format'],
        'File format': ['file_type'],
        'File output type': ['output_type'],
        'Assay term name': ['assay_term_name'],
        'Biosample term id': ['biosample_ontology.term_id'],
        'Biosample term name': ['biosample_ontology.term_name'],
        'Biosample type': ['biosample_ontology.classification'],
        'File target': ['target.label'],
        'Lab': ['lab.title'],
        'md5sum': ['md5sum'],
        'dbxrefs': ['dbxrefs'],
        'File download URL': ['href'],
        'Assembly': ['assembly'],
        'File status': ['status'],
        'Derived from': ['derived_from'],
        'S3 URL': ['cloud_metadata.url'],
        'Size': ['file_size'],
        'No File Available': ['no_file_available'],
        'Restricted': ['restricted']
    }
    expected_experiment_column_to_fields_mapping = {
        'Dataset accession': ['accession'],
        'Dataset date released': ['date_released'],
        'Project': ['award.project']
    }
    for k, v in pdmr.file_column_to_fields_mapping.items():
        assert expected_file_column_to_fields_mapping[k] == v
    for k, v in pdmr.experiment_column_to_fields_mapping.items():
        assert expected_experiment_column_to_fields_mapping[k] == v


def test_metadata_publication_data_metadata_report_add_fields_to_param_list(dummy_request):
    from encoded.reports.metadata import PublicationDataMetadataReport
    dummy_request.environ['QUERY_STRING'] = (
        'type=PublicationData&files.file_type=bigWig'
    )
    pdmr = PublicationDataMetadataReport(dummy_request)
    pdmr._initialize_report()
    pdmr._add_fields_to_param_list()
    expected_fields = [
        'accession',
        'date_released',
        'award.project',
    ]
    actual_fields = pdmr.param_list['field']
    assert set(expected_fields) == set(actual_fields)


def test_metadata_publication_data_metadata_report_add_default_file_params_to_file_params(dummy_request):
    from encoded.reports.metadata import PublicationDataMetadataReport
    dummy_request.environ['QUERY_STRING'] = (
        'type=PublicationData&files.file_type=bigWig'
    )
    pdmr = PublicationDataMetadataReport(dummy_request)
    pdmr._add_default_file_params_to_file_params()
    assert pdmr.file_params == [
        ('type', 'File'),
        ('limit', 'all'),
        ('field', '@id'),
        ('field', 'href'),
        ('field', 'restricted'),
        ('field', 'no_file_available'),
        ('field', 'file_format'),
        ('field', 'file_format_type'),
        ('field', 'status'),
        ('field', 'assembly'),
    ]


def test_metadata_publication_data_metadata_report_add_report_file_fields_to_file_params(dummy_request):
    from encoded.reports.metadata import PublicationDataMetadataReport
    dummy_request.environ['QUERY_STRING'] = (
        'type=PublicationData&files.file_type=bigWig'
    )
    pdmr = PublicationDataMetadataReport(dummy_request)
    pdmr._initialize_report()
    pdmr._add_report_file_fields_to_file_params()
    assert pdmr.file_params == [
        ('field', 'title'),
        ('field', 'dataset'),
        ('field', 'file_format'),
        ('field', 'file_type'),
        ('field', 'output_type'),
        ('field', 'assay_term_name'),
        ('field', 'biosample_ontology.term_id'),
        ('field', 'biosample_ontology.term_name'),
        ('field', 'biosample_ontology.classification'),
        ('field', 'target.label'),
        ('field', 'lab.title'),
        ('field', 'md5sum'),
        ('field', 'dbxrefs'),
        ('field', 'href'),
        ('field', 'assembly'),
        ('field', 'status'),
        ('field', 'derived_from'),
        ('field', 'cloud_metadata.url'),
        ('field', 'file_size'),
        ('field', 'no_file_available'),
        ('field', 'restricted')
    ]


def test_metadata_publication_data_metadata_report_convert_experiment_params_to_file_params(dummy_request):
    from encoded.reports.metadata import PublicationDataMetadataReport
    dummy_request.environ['QUERY_STRING'] = (
        'type=PublicationData&files.file_type=bigWig'
        '&files.biological_replicates=2&files.file_type=bigBed+narrowPeak'
        '&files.file_size=3000&status=released'
        '&files.derived_from=/experiments/ENCSR123ABC/'
    )
    pdmr = PublicationDataMetadataReport(dummy_request)
    assert pdmr._convert_experiment_params_to_file_params() == [
        ('file_type', 'bigWig'),
        ('biological_replicates', '2'),
        ('file_type', 'bigBed narrowPeak'),
        ('file_size', '3000'),
        ('derived_from', '/experiments/ENCSR123ABC/'),
    ]


def test_metadata_publication_data_metadata_report_add_experiment_file_filters_as_fields_to_file_params(dummy_request):
    from encoded.reports.metadata import PublicationDataMetadataReport
    dummy_request.environ['QUERY_STRING'] = (
        'type=PublicationData&files.file_type=bigWig'
        '&files.biological_replicates=2&files.file_type=bigBed+narrowPeak'
        '&replicates.library.size_range=200-500'
        '&files.file_size=3000&status=released'
        '&files.derived_from=/experiments/ENCSR123ABC/'
        '&files.preferred_default=*'
    )
    pdmr = PublicationDataMetadataReport(dummy_request)
    pdmr._add_experiment_file_filters_as_fields_to_file_params()
    assert pdmr.file_params == [
        ('field', 'file_type'),
        ('field', 'biological_replicates'),
        ('field', 'file_type'),
        ('field', 'file_size'),
        ('field', 'derived_from'),
        ('field', 'preferred_default'),
    ]


def test_metadata_publication_data_metadata_report_add_experiment_file_filters_to_file_params(dummy_request):
    from encoded.reports.metadata import PublicationDataMetadataReport
    dummy_request.environ['QUERY_STRING'] = (
        'type=PublicationData&files.file_type=bigWig'
        '&files.biological_replicates=2&files.file_type=bigBed+narrowPeak'
        '&replicates.library.size_range=200-500'
        '&files.file_size=3000&status=released'
        '&files.derived_from=/experiments/ENCSR123ABC/'
        '&files.preferred_default=*'
    )
    pdmr = PublicationDataMetadataReport(dummy_request)
    pdmr._add_experiment_file_filters_to_file_params()
    assert pdmr.file_params == [
        ('file_type', 'bigWig'),
        ('biological_replicates', '2'),
        ('file_type', 'bigBed narrowPeak'),
        ('file_size', '3000'),
        ('derived_from', '/experiments/ENCSR123ABC/'),
        ('preferred_default', '*'),
    ]


def test_metadata_publication_data_metadata_report_build_file_params(dummy_request):
    from encoded.reports.metadata import PublicationDataMetadataReport
    dummy_request.environ['QUERY_STRING'] = (
        'type=PublicationData&files.file_type=bigWig'
        '&files.biological_replicates=2&files.file_type=bigBed+narrowPeak'
        '&replicates.library.size_range=200-500&status=released'
    )
    pdmr = PublicationDataMetadataReport(dummy_request)
    pdmr._initialize_report()
    pdmr._build_file_params()
    assert pdmr.file_params == [
        ('type', 'File'),
        ('limit', 'all'),
        ('field', '@id'),
        ('field', 'href'),
        ('field', 'restricted'),
        ('field', 'no_file_available'),
        ('field', 'file_format'),
        ('field', 'file_format_type'),
        ('field', 'status'),
        ('field', 'assembly'),
        ('field', 'title'),
        ('field', 'dataset'),
        ('field', 'file_format'),
        ('field', 'file_type'),
        ('field', 'output_type'),
        ('field', 'assay_term_name'),
        ('field', 'biosample_ontology.term_id'),
        ('field', 'biosample_ontology.term_name'),
        ('field', 'biosample_ontology.classification'),
        ('field', 'target.label'),
        ('field', 'lab.title'),
        ('field', 'md5sum'),
        ('field', 'dbxrefs'),
        ('field', 'href'),
        ('field', 'assembly'),
        ('field', 'status'),
        ('field', 'derived_from'),
        ('field', 'cloud_metadata.url'),
        ('field', 'file_size'),
        ('field', 'no_file_available'),
        ('field', 'restricted'),
        ('field', 'file_type'),
        ('field', 'biological_replicates'),
        ('field', 'file_type'),
        ('file_type', 'bigWig'),
        ('biological_replicates', '2'),
        ('file_type', 'bigBed narrowPeak')
    ]


def test_metadata_publication_data_metadata_report_filter_file_params_from_query_string(dummy_request):
    from encoded.reports.metadata import PublicationDataMetadataReport
    dummy_request.environ['QUERY_STRING'] = (
        'type=PublicationData&files.file_type=bigWig'
        '&files.biological_replicates=2&files.file_type=bigBed+narrowPeak'
        '&replicates.library.size_range=200-500&status=released'
        '&files.file_size=3000'
    )
    pdmr = PublicationDataMetadataReport(dummy_request)
    pdmr._filter_file_params_from_query_string()
    assert pdmr.query_string.params == [
        ('type', 'PublicationData'),
        ('replicates.library.size_range', '200-500'),
        ('status', 'released'),
    ]


def test_metadata_publication_data_metadata_report_build_params(dummy_request):
    from encoded.reports.metadata import PublicationDataMetadataReport
    dummy_request.environ['QUERY_STRING'] = (
        'type=PublicationData&files.file_type=bigWig'
        '&files.biological_replicates=2&files.file_type=bigBed+narrowPeak'
        '&replicates.library.size_range=200-500&status=released'
        '&files.file_size=3000'
    )
    pdmr = PublicationDataMetadataReport(dummy_request)
    pdmr._initialize_report()
    pdmr._build_params()
    assert pdmr.file_params == [
        ('type', 'File'),
        ('limit', 'all'),
        ('field', '@id'),
        ('field', 'href'),
        ('field', 'restricted'),
        ('field', 'no_file_available'),
        ('field', 'file_format'),
        ('field', 'file_format_type'),
        ('field', 'status'),
        ('field', 'assembly'),
        ('field', 'title'),
        ('field', 'dataset'),
        ('field', 'file_format'),
        ('field', 'file_type'),
        ('field', 'output_type'),
        ('field', 'assay_term_name'),
        ('field', 'biosample_ontology.term_id'),
        ('field', 'biosample_ontology.term_name'),
        ('field', 'biosample_ontology.classification'),
        ('field', 'target.label'),
        ('field', 'lab.title'),
        ('field', 'md5sum'),
        ('field', 'dbxrefs'),
        ('field', 'href'),
        ('field', 'assembly'),
        ('field', 'status'),
        ('field', 'derived_from'),
        ('field', 'cloud_metadata.url'),
        ('field', 'file_size'),
        ('field', 'no_file_available'),
        ('field', 'restricted'),
        ('field', 'file_type'),
        ('field', 'biological_replicates'),
        ('field', 'file_type'),
        ('field', 'file_size'),
        ('file_type', 'bigWig'),
        ('biological_replicates', '2'),
        ('file_type', 'bigBed narrowPeak'),
        ('file_size', '3000'),
    ]
    assert pdmr.query_string.params == [
        ('type', 'PublicationData'),
        ('replicates.library.size_range', '200-500'),
        ('status', 'released'),
    ]


def test_metadata_publication_data_metadata_report_get_at_id_file_params(dummy_request):
    from encoded.reports.metadata import PublicationDataMetadataReport
    dummy_request.environ['QUERY_STRING'] = (
        'type=PublicationData&files.file_type=bigWig'
    )
    pdmr = PublicationDataMetadataReport(dummy_request)
    assert pdmr._get_at_id_file_params() == []
    pdmr.file_at_ids = ['/files/ENCFFABC123/', '/files/ENCFFDEF345/']
    assert pdmr._get_at_id_file_params() == [
        ('@id', '/files/ENCFFABC123/'),
        ('@id', '/files/ENCFFDEF345/')
    ]


def test_metadata_publication_data_metadata_report_build_new_file_request(dummy_request):
    from encoded.reports.metadata import PublicationDataMetadataReport
    dummy_request.environ['QUERY_STRING'] = (
        'type=PublicationData&files.file_type=bigWig'
        '&files.biological_replicates=2&files.file_type=bigBed+narrowPeak'
        '&replicates.library.size_range=200-500&status=released'
    )
    pdmr = PublicationDataMetadataReport(dummy_request)
    pdmr._initialize_report()
    pdmr._build_params()
    request = pdmr._build_new_file_request()
    assert str(request.query_string) == (
        'type=File&limit=all&field=%40id&field=href&field=restricted'
        '&field=no_file_available&field=file_format&field=file_format_type'
        '&field=status&field=assembly&field=title&field=dataset&field=file_type'
        '&field=output_type&field=assay_term_name&field=biosample_ontology.term_id'
        '&field=biosample_ontology.term_name&field=biosample_ontology.classification'
        '&field=target.label&field=lab.title&field=md5sum&field=dbxrefs&field=derived_from'
        '&field=cloud_metadata.url&field=file_size&field=biological_replicates'
        '&file_type=bigWig&biological_replicates=2&file_type=bigBed+narrowPeak'
    )
    assert request.registry
    assert request.path_info == '/search/'
    pdmr.file_at_ids = ['/files/ENCFFABC123/', '/files/ENCFFDEF345/']
    request = pdmr._build_new_file_request()
    assert str(request.query_string) == (
        'type=File&limit=all&field=%40id&field=href&field=restricted'
        '&field=no_file_available&field=file_format&field=file_format_type'
        '&field=status&field=assembly&field=title&field=dataset&field=file_type'
        '&field=output_type&field=assay_term_name&field=biosample_ontology.term_id'
        '&field=biosample_ontology.term_name&field=biosample_ontology.classification'
        '&field=target.label&field=lab.title&field=md5sum&field=dbxrefs&field=derived_from'
        '&field=cloud_metadata.url&field=file_size&field=biological_replicates'
        '&file_type=bigWig&biological_replicates=2&file_type=bigBed+narrowPeak'
        '&%40id=%2Ffiles%2FENCFFABC123%2F&%40id=%2Ffiles%2FENCFFDEF345%2F'
    )


def test_metadata_publication_data_metadata_report_get_file_search_results_generator(index_workbook, dummy_request):
    from encoded.reports.metadata import PublicationDataMetadataReport
    dummy_request.environ['QUERY_STRING'] = (
        'type=PublicationData'
        '&id=/publication-data/ENCSR727WCB/'
        '&files.file_type=hic'
    )
    pdmr = PublicationDataMetadataReport(dummy_request)
    pdmr._initialize_report()
    pdmr._build_params()
    pdmr.file_at_ids = [
        '/files/ENCFF002COS/',
        '/files/ENCFF003COS/',
        '/files/ENCFF002ENO/',
        '/files/ENCFF002ENS/',
        '/files/ENCFF037HIC/'
    ]
    results = list(pdmr._get_file_search_results_generator())
    # One hic file.
    assert len(results) == 1


def test_metadata_publication_data_metadata_report_generate_rows(index_workbook, dummy_request):
    from encoded.reports.metadata import PublicationDataMetadataReport
    dummy_request.environ['QUERY_STRING'] = (
        'type=PublicationData'
        '&@id=/publication-data/ENCSR727WCB/'
        '&files.file_type=tsv'
    )
    pdmr = PublicationDataMetadataReport(dummy_request)
    pdmr._initialize_report()
    pdmr._build_params()
    results = list(pdmr._generate_rows())
    # One header, two TSV.
    assert len(results) == 3
