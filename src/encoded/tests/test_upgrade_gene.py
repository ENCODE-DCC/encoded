import pytest


@pytest.fixture
def gene_1(gene):
    item = gene.copy()
    item.update({
        'go_annotations': [
            {
                "go_id": "GO:0000122",
                "go_name": "negative regulation of transcription by RNA polymerase II",
                "go_evidence_code": "IDA",
                "go_aspect": "P"
            },
            {
                "go_id": "GO:0000775",
                "go_name": "chromosome, centromeric region",
                "go_evidence_code": "IDA",
                "go_aspect": "C"
            },
            {
                "go_id": "GO:0000793",
                "go_name": "condensed chromosome",
                "go_evidence_code": "IDA",
                "go_aspect": "C"
            },
        ],
    })
    return item


def test_gene_upgrade_remove_go_annotations(
    upgrader,
    gene_1,
):
    new_gene = upgrader.upgrade(
        'gene', gene_1, current_version='1', target_version='2'
    )
    assert new_gene['schema_version'] == '2'
    assert 'go_annotations' not in new_gene
