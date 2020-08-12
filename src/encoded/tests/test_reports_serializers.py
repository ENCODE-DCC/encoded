import pytest


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


def test_reports_serializers_make_experiment_cell():
    from encoded.reports.serializers import make_experiment_cell
    assert make_experiment_cell(['assembly'], experiment()) == 'GRCh38'
    assert make_experiment_cell(['protein_tags.location'], experiment()) == 'C-terminal'
    unsorted_cell = make_experiment_cell(['protein_tags.target'], experiment())
    assert unsorted_cell == '/targets/STAG1-human/, /targets/STAG2-human/' or unsorted_cell == '/targets/STAG2-human/, /targets/STAG1-human/'


def test_reports_serializers_make_file_cell():
    from encoded.reports.serializers import make_file_cell
    assert make_file_cell(['assembly'], file_()) == 'GRCh38'
    assert make_file_cell(['dbxrefs'], file_()) == ''
    assert make_file_cell(['technical_replicates'], file_()) == '2_1'
    assert make_file_cell(['biological_replicates'], file_()) == '2'
    assert make_file_cell(['status'], file_()) == 'released'
    assert make_file_cell(['lab.title'], file_()) == 'ENCODE Processing Pipeline'
    assert make_file_cell(['file_format', 'file_format_type'], file_()) == 'bed idr_ranked_peak'
