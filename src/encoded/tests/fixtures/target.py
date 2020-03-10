import pytest
from ..constants import *


@pytest.fixture
def target(testapp, organism):
    item = {
        'label': 'ATF4',
        'target_organism': organism['@id'],
        'investigated_as': ['transcription factor'],
    }
    return testapp.post_json('/target', item).json['@graph'][0]


@pytest.fixture
def target_H3K27ac(testapp, organism):
    item = {
        'label': 'H3K27ac',
        'target_organism': organism['@id'],
        'investigated_as': ['histone',
                            'narrow histone mark']
    }
    return testapp.post_json('/target', item).json['@graph'][0]


@pytest.fixture
def target_H3K9me3(testapp, organism):
    item = {
        'label': 'H3K9me3',
        'target_organism': organism['@id'],
        'investigated_as': ['histone',
                            'broad histone mark']
    }
    return testapp.post_json('/target', item).json['@graph'][0]


@pytest.fixture
def target_promoter(testapp, fly):
    item = {
        'label': 'daf-2',
        'target_organism': fly['@id'],
        'investigated_as': ['other context']
    }
    return testapp.post_json('/target', item).json['@graph'][0]

@pytest.fixture
def target_H3K27me3_1(testapp, organism):
    item = {
        'label': 'H3K27me3',
        'target_organism': organism['@id'],
        'investigated_as': ['histone']
    }
    return testapp.post_json('/target', item).json['@graph'][0]


@pytest.fixture
def target_H3K36me3_1(testapp, organism):
    item = {
        'label': 'H3K36me3',
        'target_organism': organism['@id'],
        'investigated_as': ['histone']
    }
    return testapp.post_json('/target', item).json['@graph'][0]


@pytest.fixture
def target_H3K4me1_1(testapp, organism):
    item = {
        'label': 'H3K4me1',
        'target_organism': organism['@id'],
        'investigated_as': ['histone']
    }
    return testapp.post_json('/target', item).json['@graph'][0]


@pytest.fixture
def target_H3K4me3_1(testapp, organism):
    item = {
        'label': 'H3K4me3',
        'target_organism': organism['@id'],
        'investigated_as': ['histone']
    }
    return testapp.post_json('/target', item).json['@graph'][0]


@pytest.fixture
def target_H3K27ac_1(testapp, organism):
    item = {
        'label': 'H3K27ac',
        'target_organism': organism['@id'],
        'investigated_as': ['histone']
    }
    return testapp.post_json('/target', item).json['@graph'][0]


@pytest.fixture
def target_H3K9me3_1(testapp, organism):
    item = {
        'label': 'H3K9me3',
        'target_organism': organism['@id'],
        'investigated_as': ['histone']
    }
    return testapp.post_json('/target', item).json['@graph'][0]

@pytest.fixture
def tagged_target(testapp, gene):
    item = {
        'genes': [gene['uuid']],
        'modifications': [{'modification': 'eGFP'}],
        'label': 'eGFP-CTCF',
        'investigated_as': ['transcription factor']
    }
    return testapp.post_json('/target', item, status=201).json['@graph'][0]

@pytest.fixture
def target_H3K4me3_1(testapp, organism):
    item = {
        'label': 'H3K4me3',
        'target_organism': organism['@id'],
        'investigated_as': ['histone']
    }
    return testapp.post_json('/target', item).json['@graph'][0]


@pytest.fixture
def target_CTCF_1(testapp, organism):
    item = {
        'label': 'CTCF',
        'target_organism': organism['@id'],
        'investigated_as': ['transcription factor']
    }
    return testapp.post_json('/target', item).json['@graph'][0]

@pytest.fixture
def base_target(testapp, organism):
    item = {
        'target_organism': organism['uuid'],
        'label': 'TAF1',
        'investigated_as': ['transcription factor']
    }
    return testapp.post_json('/target', item, status=201).json['@graph'][0]


@pytest.fixture
def tag_target(testapp, organism):
    item = {
        'target_organism': organism['uuid'],
        'label': 'eGFP',
        'investigated_as': ['tag']
    }
    return testapp.post_json('/target', item, status=201).json['@graph'][0]

@pytest.fixture
def recombinant_target(testapp, gene):
    item = {
        'label': 'HA-ABCD',
        'investigated_as': ['transcription factor'],
        'genes': [gene['uuid']],
        'modifications': [{'modification': 'HA'}]
    }
    return testapp.post_json('/target', item, status=201).json['@graph'][0]

@pytest.fixture
def base_target_1(testapp, gene):
    item = {
        'genes': [gene['uuid']],
        'label': 'XYZ',
        'investigated_as': ['transcription factor']
    }
    return testapp.post_json('/target', item, status=201).json['@graph'][0]


@pytest.fixture
def tag_target(testapp, organism):
    item = {
        'target_organism': organism['uuid'],
        'label': 'eGFP',
        'investigated_as': ['tag']
    }
    return testapp.post_json('/target', item, status=201).json['@graph'][0]

@pytest.fixture
def mouse_H3K9me3(testapp, mouse):
    item = {
        'target_organism': mouse['@id'],
        'label': 'H3K9me3',
        'investigated_as': ['histone', 'broad histone mark']
    }
    return testapp.post_json('/target', item, status=201).json['@graph'][0]


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


@pytest.fixture
def target_11_control(human):
    item = {
        'investigated_as': ['control'],
        'target_organism': human['uuid'],
        'label': 'No protein target control'
    }
    return item


@pytest.fixture
def target_12_recombinant(ctcf):
    item = {
        'investigated_as': [
            'recombinant protein',
            'chromatin remodeller',
            'RNA binding protein'
        ],
        'genes': [ctcf['uuid']],
        'modifications': [{'modification': 'eGFP'}],
        'label': 'eGFP-CTCF'
    }
    return item

@pytest.fixture
def target_nongene(mouse):
    return {
        'label': 'nongene',
        'target_organism': mouse['uuid'],
        'investigated_as': ['other context'],
    }


@pytest.fixture
def target_one_gene(ctcf):
    return {
        'label': 'one-gene',
        'genes': [ctcf['uuid']],
        'investigated_as': ['other context'],
    }


@pytest.fixture
def target_two_same_org(ctcf, myc):
    return {
        'label': 'two-same-org',
        'genes': [ctcf['uuid'], myc['uuid']],
        'investigated_as': ['other context'],
    }


@pytest.fixture
def target_two_diff_orgs(ctcf, tbp):
    return {
        'label': 'two-diff-org',
        'genes': [ctcf['uuid'], tbp['uuid']],
        'investigated_as': ['other context'],
    }


@pytest.fixture
def target_genes_org(human, ctcf, myc):
    return {
        'label': 'genes-org',
        'target_organism': human['uuid'],
        'genes': [ctcf['uuid'], myc['uuid']],
        'investigated_as': ['other context'],
    }


@pytest.fixture
def target_synthetic_tag():
    return {
        'label': 'FLAG',
        'investigated_as': ['synthetic tag'],
    }


@pytest.fixture
def target_10_nt_mod(organism):
    item = {
        'investigated_as': ['nucleotide modification'],
        'target_organism': organism['uuid'],
        'label': 'nucleotide-modification-target'
    }
    return item


