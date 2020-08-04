import pytest


def test_target_upgrade(upgrader, target_1_0):
    value = upgrader.upgrade('target', target_1_0, target_version='2')
    assert value['schema_version'] == '2'
    assert value['status'] == 'current'


def test_target_investigated_as_upgrade(upgrader, target_2_0):
    value = upgrader.upgrade('target', target_2_0, target_version='3')
    assert value['schema_version'] == '3'
    assert value['investigated_as'] == ['transcription factor']


def test_target_investigated_as_upgrade_tag(upgrader, target_2_0):
    target_2_0['label'] = 'eGFP'
    value = upgrader.upgrade('target', target_2_0, target_version='3')
    assert value['schema_version'] == '3'
    assert value['investigated_as'] == ['tag']


def test_target_investigated_as_upgrade_recombinant(upgrader, target_2_0):
    target_2_0['label'] = 'eGFP-test'
    value = upgrader.upgrade('target', target_2_0, target_version='3')
    assert value['schema_version'] == '3'
    assert value['investigated_as'] == [
        'recombinant protein', 'transcription factor']


def test_target_upgrade_status_5_6(upgrader, target_5_0):
    value = upgrader.upgrade(
        'target', target_5_0, current_version='5', target_version='6')
    assert value['schema_version'] == '6'
    assert value['status'] == 'current'


def test_target_upgrade_remove_histone_modification_6_7(upgrader, target_6_0):
    value = upgrader.upgrade(
        'target', target_6_0, current_version='6', target_version='7')
    assert value['schema_version'] == '7'
    assert value['investigated_as'] == ['histone']


@pytest.mark.parametrize(
    'old_status, new_status',
    [
        ('current', 'released'),
        ('deleted', 'deleted'),
        ('replaced', 'deleted')
    ]
)
def test_target_upgrade_move_to_standard_status_7_8(old_status, new_status, upgrader, target):
    target.update(
        {
            'status': old_status,
            'schema_version': '7'
        }
    )
    value = upgrader.upgrade(
        'target',
        target,
        current_version='7',
        target_version='8'
    )
    assert value['schema_version'] == '8'
    assert value['status'] == new_status


def test_target_upgrade_link_to_gene(root, upgrader, target_H3K27ac,
                                     target_8_no_genes, target_8_one_gene,
                                     target_8_two_genes, gene3012, gene8335):
    context = root.get_by_uuid(target_H3K27ac['uuid'])
    no_genes = upgrader.upgrade(
        'target', target_8_no_genes, current_version='8', target_version='9',
        context=context)
    one_gene = upgrader.upgrade(
        'target', target_8_one_gene, current_version='8', target_version='9',
        context=context)
    two_genes = upgrader.upgrade(
        'target', target_8_two_genes, current_version='8', target_version='9',
        context=context)

    for new_target in [no_genes, one_gene, two_genes]:
        assert new_target['schema_version'] == '9'
        assert 'gene_name' not in new_target
    assert 'genes' not in no_genes
    assert 'organism' not in no_genes
    assert no_genes['target_organism']
    assert one_gene['genes'] == [gene3012['uuid']]
    assert 'organism' not in one_gene
    assert 'target_organism' not in one_gene
    assert two_genes['genes'] == [gene8335['uuid'], gene3012['uuid']]
    assert 'organism' not in two_genes
    assert 'target_organism' not in one_gene


def test_target_remove_empty_modifications(upgrader,
                                           target_9_empty_modifications,
                                           target_9_real_modifications):
    empty = upgrader.upgrade(
        'target', target_9_empty_modifications,
        current_version='9', target_version='10'
    )
    assert empty['schema_version'] == '10'
    assert 'modifications' not in empty

    nonempty = upgrader.upgrade(
        'target', target_9_real_modifications,
        current_version='9', target_version='10'
    )
    assert nonempty['schema_version'] == '10'
    assert 'modifications' in nonempty


def test_target_upgrade_categories(upgrader,
                                   target_10_nt_mod,
                                   target_10_other_ptm):
    new_target = upgrader.upgrade(
        'target', target_10_nt_mod, current_version='10', target_version='11'
    )
    assert new_target['schema_version'] == '11'
    assert new_target['investigated_as'] == ['other context']

    new_target = upgrader.upgrade(
        'target', target_10_other_ptm, current_version='10', target_version='11'
    )
    assert new_target['schema_version'] == '11'
    assert new_target['investigated_as'] == [
        'RNA binding protein',
        'chromatin remodeler',
    ]


def test_target_upgrade_remove_control(
    upgrader,
    target_11_control,
):
    new_target = upgrader.upgrade(
        'target', target_11_control, current_version='11', target_version='12'
    )
    assert new_target['schema_version'] == '12'
    assert new_target['investigated_as'] == ['other context']


def test_target_upgrade_remove_recombinant(
    upgrader,
    target_12_recombinant,
):
    new_target = upgrader.upgrade(
        'target', target_12_recombinant, current_version='12', target_version='13'
    )
    assert new_target['schema_version'] == '13'
    assert 'recombinant protein' not in new_target['investigated_as']
    assert len(new_target['investigated_as']) != 0


def test_target_upgrade_restrict_dbxrefs(upgrader, target_13_one_gene, target_13_no_genes, target_synthetic_tag):
    target_with_genes = upgrader.upgrade('target', target_13_one_gene, current_version='13', target_version='14')
    assert target_with_genes['schema_version'] == '14'
    assert 'dbxref' not in target_with_genes
    assert 'dbxrefs' not in target_with_genes

    target_no_genes = upgrader.upgrade('target', target_13_no_genes, current_version='13', target_version='14')
    assert target_no_genes['schema_version'] == '14'
    assert 'dbxref' not in target_no_genes
    assert 'dbxrefs' in target_no_genes

    # target no gene and dbxref = []
    target_synthetic_tag = upgrader.upgrade('target', target_synthetic_tag, current_version='13', target_version='14')
    assert target_synthetic_tag['schema_version'] == '14'
    assert 'dbxref' not in target_synthetic_tag
    assert 'dbxrefs' not in target_synthetic_tag
