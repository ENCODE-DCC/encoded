import pytest


@pytest.fixture
def target(organism):
    return{
        'organism': organism['uuid'],
        'label': 'TEST'
    }


@pytest.fixture
def target_1(target):
    item = target.copy()
    item.update({
        'schema_version': '1',
        'status': 'CURRENT',
    })
    return item


@pytest.fixture
def target_2(target):
    item = target.copy()
    item.update({
        'schema_version': '2',
    })
    return item


@pytest.fixture
def target_5(target):
    item = target.copy()
    item.update({
        'schema_version': '5',
        'status': 'proposed'
    })
    return item


@pytest.fixture
def target_6(target):
    item = target.copy()
    item.update({
        'schema_version': '6',
        'status': 'current',
        'investigated_as': ['histone modification', 'histone']
    })
    return item


@pytest.fixture
def target_8_no_genes(target):
    item = target.copy()
    item.update({
        'schema_version': '8',
        'dbxref': [
            'UniProtKB:P04908'
        ]
    })
    return item


@pytest.fixture
def target_8_one_gene(target_8_no_genes):
    item = target_8_no_genes.copy()
    item.update({
        'gene_name': 'HIST1H2AE',
        'dbxref': [
            'GeneID:3012',
            'UniProtKB:P04908'
        ]
    })
    return item


@pytest.fixture
def target_8_two_genes(target_8_one_gene):
    item = target_8_one_gene.copy()
    item.update({
        'gene_name': 'Histone H2A',
        'dbxref': [
            'GeneID:8335',
            'GeneID:3012',
            'UniProtKB:P04908'
        ]
    })
    return item


@pytest.fixture
def target_9_empty_modifications(target_8_one_gene):
    item = {
        'investigated_as': ['other context'],
        'modifications': [],
        'label': 'empty-modifications'
    }
    return item


@pytest.fixture
def target_9_real_modifications(target_8_one_gene):
    item = {
        'investigated_as': ['other context'],
        'modifications': [{'modification': '3xFLAG'}],
        'label': 'empty-modifications'
    }
    return item


@pytest.fixture
def gene3012(testapp, organism):
    item = {
        'dbxrefs': ['HGNC:4724'],
        'organism': organism['uuid'],
        'symbol': 'HIST1H2AE',
        'ncbi_entrez_status': 'live',
        'geneid': '3012',
    }
    return testapp.post_json('/gene', item).json['@graph'][0]


@pytest.fixture
def gene8335(testapp, organism):
    item = {
        'dbxrefs': ['HGNC:4734'],
        'organism': organism['uuid'],
        'symbol': 'HIST1H2AB',
        'ncbi_entrez_status': 'live',
        'geneid': '8335',
    }
    return testapp.post_json('/gene', item).json['@graph'][0]


@pytest.fixture
def target_10_nt_mod(organism):
    item = {
        'investigated_as': ['nucleotide modification'],
        'target_organism': organism['uuid'],
        'label': 'nucleotide-modification-target'
    }
    return item


@pytest.fixture
def target_10_other_ptm(gene8335):
    item = {
        'investigated_as': [
            'other post-translational modification',
            'chromatin remodeller',
            'RNA binding protein'
        ],
        'genes': [gene8335['uuid']],
        'modifications': [{'modification': 'Phosphorylation'}],
        'label': 'nucleotide-modification-target'
    }
    return item


def test_target_upgrade(upgrader, target_1):
    value = upgrader.upgrade('target', target_1, target_version='2')
    assert value['schema_version'] == '2'
    assert value['status'] == 'current'


def test_target_investigated_as_upgrade(upgrader, target_2):
    value = upgrader.upgrade('target', target_2, target_version='3')
    assert value['schema_version'] == '3'
    assert value['investigated_as'] == ['transcription factor']


def test_target_investigated_as_upgrade_tag(upgrader, target_2):
    target_2['label'] = 'eGFP'
    value = upgrader.upgrade('target', target_2, target_version='3')
    assert value['schema_version'] == '3'
    assert value['investigated_as'] == ['tag']


def test_target_investigated_as_upgrade_recombinant(upgrader, target_2):
    target_2['label'] = 'eGFP-test'
    value = upgrader.upgrade('target', target_2, target_version='3')
    assert value['schema_version'] == '3'
    assert value['investigated_as'] == [
        'recombinant protein', 'transcription factor']


def test_target_upgrade_status_5_6(upgrader, target_5):
    value = upgrader.upgrade(
        'target', target_5, current_version='5', target_version='6')
    assert value['schema_version'] == '6'
    assert value['status'] == 'current'


def test_target_upgrade_remove_histone_modification_6_7(upgrader, target_6):
    value = upgrader.upgrade(
        'target', target_6, current_version='6', target_version='7')
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


def test_target_upgrade_link_to_gene(root, upgrader, target_control,
                                     target_8_no_genes, target_8_one_gene,
                                     target_8_two_genes, gene3012, gene8335):
    context = root.get_by_uuid(target_control['uuid'])
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
