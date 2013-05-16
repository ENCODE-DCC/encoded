# -*- coding: utf-8 -*-
from collections import OrderedDict

ORGANISMS = [
    {
    '_uuid': '7745b647-ff15-4ff3-9ced-b897d4e2983c',
    'name': 'human',
    'scientific_name': 'Homo sapiens',
    'taxon_id': 9606,
    },
    {
    '_uuid': '3413218c-3d86-498b-a0a2-9a406638e786',
    'name': 'mouse',
    'scientific_name': 'Mus musculus',
    'taxon_id': 10090,
    },
]

TARGETS = [
    {
        '_uuid': 'dcd60c9f-7f2e-4d75-8276-9c9a9c6c7669',
        '_links': {
            'self': {'href': '/targets/{_uuid}', 'templated': True},
            'organism': {'href': '/organisms/{organism_uuid}', 'templated': True},
        },
        'label': 'ATF4',
        'organism': '7745b647-ff15-4ff3-9ced-b897d4e2983c',  # looked up on insert?
        'gene_name': 'ATF4',
        'lab': 'c0a3540e-8ef0-4d4d-a449-ae47c2475838',
        'award': '7fd6664b-17f5-4bfe-9fdf-ed7481cf4d24',
        'aliases': [
            {'alias': 'CREB2', 'source': 'HGNC'},
            {'alias': 'TXREB', 'source': 'HGNC'},
            {'alias': 'CREB-2', 'source': 'HGNC'},
            {'alias': 'TAXREB67', 'source': 'HGNC'},
        ],
        'dbxref': {
            'UniProtKB': ['Q96AQ3'],
            'HGNC': ['786']
        }
    },
    {
        '_uuid': 'BAF56297-9628-418F-B78E-95EDD524E4F6',
        '_links': {
            'self': {'href': '/targets/{_uuid}', 'templated': True},
            'organism': {'href': '/organisms/{organism_uuid}', 'templated': True},
        },
        'lab': 'c0a3540e-8ef0-4d4d-a449-ae47c2475838',
        'award': '7fd6664b-17f5-4bfe-9fdf-ed7481cf4d24',
        'label': 'H3K4me3',
        'organism': '7745b647-ff15-4ff3-9ced-b897d4e2983c',  # looked up on insert?
        'gene_name': 'H3F3A',
        'aliases': [
            {'alias': 'H3.3', 'source': 'HGNC'},
            {'alias': 'H3F3', 'source': 'HGNC'},
            {'alias': 'histone H3.3', 'source': 'HGNC'},
        ],
        'dbxref': {
            'UniProtKB': ['P84243'],
            'HGNC': ['4764']
        },
   },
]

SOURCES = [
    {
    '_uuid': '3aa827c3-92f8-41fa-9608-201558f7a1c4',
    'alias': 'sigma',
    'name': 'Sigma-Aldrich',
    'url': 'http://www.sigmaaldrich.com',
    },
    {
    '_uuid': '3aa827c3-92f8-41fa-9608-2aac58f7a1c4',
    'alias': 'gingeras',
    'name': 'Gingeras Lab',
    'url': 'http://www.gingeraslab.edu',
    },
]

ANTIBODY_LOTS = [
    {
    '_uuid': 'bc293400-eab3-41fb-a41e-35552686b67d',
    '_links': {
        'self': {'href': '/antibodies/{_uuid}', 'templated': True},
        'source': {'href': '/sources/{source_uuid}', 'templated': True},
        },
    'antibody_term_id': 'tbd-taxonomic-id',
    'antibody_name': 's123',
    'clonality': 'Monoclonal',
    'host_orgnanism': 'Mouse',
    'name': 'Sigma-Aldrich',  # PK
    'source_uuid': '3aa827c3-92f8-41fa-9608-201558f7a1c4',
    'product_id': 'WH0000468M1',  # PK
    'lot_id': 'CB191-2B3',  # PK
    'url': 'http://www.sigmaaldrich.com/catalog/product/sigma/wh0000468m1?lang=en&region=US',
    'isotype': u'IgG1κ',
    'purification': None,
    'antibody_description': None,
    'antigen_description': 'ATF4 (NP_001666, a.a. 171-271) partial recombinant protein with GST tag.',
    'antigen_sequence': None,

    'is_obsolete': False,  # Antibody should no longer be used
    'submitted_by': 'Myers-Pauli-Behn',
    'date_created': '2009-01-16',
    'created_by': 'Cherry-Sloan',
    },
]

VALIDATIONS = [
    {
    '_uuid': 'c4da2e0c-149f-4aee-ac21-8690dfdadb1f',
    '_links': {
        'self': {'href': '/validations/{_uuid}', 'templated': True},
        'antibody_lot': {'href': '/antibodies/{antibody_uuid}', 'templated': True},
        'target': {'href': '/targets/{target_uuid}', 'templated': True},
        },
    'antibody_uuid': 'bc293400-eab3-41fb-a41e-35552686b67d',
    'target_uuid': 'dcd60c9f-7f2e-4d75-8276-9c9a9c6c7669',
    'method': '',
    'doc': '',
    'caption': '',
    'submitter': '',
    'review_state': '',
    },
]

ANTIBODY_APPROVALS = [
    {
    '_uuid': 'a8f94078-2d3b-4647-91a2-8ec91b096708',
    '_links': {
        'self': {'href': '/approvals/{_uuid}', 'templated': True},
        'antibody_lot': {'href': '/antibody-lots/{antibody_lot_uuid}', 'templated': True},
        'target': {'href': '/targets/{target_uuid}', 'templated': True},
        'validations': [],
        },
    'antibody_lot_uuid': 'bc293400-eab3-41fb-a41e-35552686b67d',
    'target_uuid': 'dcd60c9f-7f2e-4d75-8276-9c9a9c6c7669',
    'validation_uuids': [
        'c4da2e0c-149f-4aee-ac21-8690dfdadb1f',
        ],
    },
]

BIOSAMPLES = [
    {
    '_uuid': '7c245cea-7d59-45fb-9ebe-f0454c5fe950',
    '_links': {
        'self': {'href': '/biosamples/{_uuid}', 'templated': True},
        'source': {'href': '/sources/{source_uuid}', 'templated': True},
        },
    'biosample_ontology': 'UBERON',
    'biosample_term_id': 'U:349829',
    'biosample_term': 'Liver',
    'biosample_type': 'Tissue',
    'antibody_accession': 'ENCBS001ZZZ',
    'name': 'Gingeras',
    'source_uuid': '3aa827c3-92f8-41fa-9608-2aac58f7a1c4',
    'product_id': 'fridge1a',
    'lot_id': '1',
    'treatment': None,
    'donor_uuids': ['a59b301a-782f-449e-bce4-9f0a6141b97b'],
    'is_pooled': False,
    'related_uuids': [],
    'protocol_uuids': [
        'b55b330f-a34a-4bda-b87c-11c863a5ad1e',
        '68b7342a-2d31-4ad7-bbeb-0196993f1752',
        'dfa2a44e-7583-41f2-bc40-fe7c073af2a9',
    ],
    'submitted_by': 'Gingeras-Hapless-Postdoc',
    'date_created': '2009-2-08',
    'created_by': 'Cherry-Chan',
    }
]

AWARDS = [
    {
    '_uuid': '529e3e74-3caa-4842-ae64-18c8720e610e',
    'name': 'ENCODE3-DCC',
    },
    {
    '_uuid': 'fae1bd8b-0d90-4ada-b51f-0ecc413e904d',
    'name': 'Myers',
    },
]

BAD_AWARDS = [  # UUID same as one of labs
    {
    '_uuid': '529e3e74-3caa-4842-ae64-18c8720e610e',
    'name': 'ENCODE3-DCC',
    },
    {
    '_uuid': 'b635b4ed-dba3-4672-ace9-11d76a8d03af',
    'name': 'Myers',
    },
]
LABS = [
    {
    '_uuid': '2c334112-288e-4d45-9154-3f404c726daf',
    'name': 'Cherry Lab',
    'instituition': 'Stanford University'
    },
    {
    '_uuid': 'b635b4ed-dba3-4672-ace9-11d76a8d03af',
    'name': 'Myers Lab',
    'instituition': 'HudsonAlpha Institute for Biotechnology'
    },
]

BAD_LABS = [  # same UUID
    {
    '_uuid': '2c334112-288e-4d45-9154-3f404c726daf',
    'name': 'Cherry Lab',
    'instituition': 'Stanford University'
    },
    {
    '_uuid': '2c334112-288e-4d45-9154-3f404c726daf',
    'name': 'Myers Lab',
    'instituition': 'HudsonAlpha Institute for Biotechnology'
    },
]

USERS = [
    {
    '_uuid': 'e9be360e-d1c7-4cae-9b3a-caf588e8bb6f',
    'full_name': 'Benjamin Hitz',
    'email': 'hitz@stanford.edu',
    'role': 'admin',
    'award_uuids': ['529e3e74-3caa-4842-ae64-18c8720e610e'],
    'lab_uuids': ['2c334112-288e-4d45-9154-3f404c726daf'],
    },
    {
    '_uuid': '1e945b04-aa54-4732-8b81-b41d4565f5f9',
    'full_name': 'Cricket Sloan',
    'email': 'cricket@stanford.edu',
    'role': 'wrangler',
    'award_uuids': ['529e3e74-3caa-4842-ae64-18c8720e610e'],
    'lab_uuids': ['2c334112-288e-4d45-9154-3f404c726daf'],
    },
    {
    '_uuid': 'bb319896-3f78-4e24-b6e1-e4961822bc9b',
    'full_name': 'Florencia Pauli-Behn',
    'email': 'paulibehn@hudsonalpha.org',
    'role': 'submitter',
    'award_uuids': ['fae1bd8b-0d90-4ada-b51f-0ecc413e904d'],
    'lab_uuids': ['b635b4ed-dba3-4672-ace9-11d76a8d03af'],
    },
]

URL_COLLECTION = OrderedDict([
    ('/organisms/', ORGANISMS),
    ('/targets/', TARGETS),
    ('/sources/', SOURCES),
    ('/antibody-lots/', ANTIBODY_LOTS),
    ('/validations/', VALIDATIONS),
    ('/antibodies/', ANTIBODY_APPROVALS),
    ('/biosamples/', BIOSAMPLES),
    ('/users/', USERS),
    ('/labs/', LABS),
    ('/awards/', AWARDS),
])


def test_load_all(testapp):

    from pyramid.security import Everyone
    from pyramid import testing

    security_policy = testing.setUp().testing_securitypolicy(userid=Everyone, permissive=True)
    #import sys
    #sys.stderr.write(testapp.app.registry.settings.items())
    testapp.app.registry.settings['authentication_policy'] = security_policy
    testapp.app.registry.settings['authorization_policy'] = security_policy

    for url, collection in [
        ('/organisms/', ORGANISMS),
        ('/targets/', TARGETS),
        ('/sources/', SOURCES),
        ('/antibody-lots/', ANTIBODY_LOTS),
        ('/validations/', VALIDATIONS),
        ('/antibodies/', ANTIBODY_APPROVALS),
        ('/biosamples/', BIOSAMPLES),
        ('/users/', USERS),
        ('/labs/', LABS),
        ('/awards/', AWARDS),
        ]:
        for item in collection:
            testapp.post_json(url, item, status=201)


def load_sample(testapp):
    for url, collection in [
        ('/organisms/', ORGANISMS),
        ('/sources/', SOURCES),
        ('/biosamples/', BIOSAMPLES),
        ('/users/', USERS),
        ('/labs/', LABS),
        ('/awards/', AWARDS),
        ]:
        for item in collection:
            testapp.post_json(url, item, status=201)
