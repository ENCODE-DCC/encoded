# -*- coding: utf-8 -*-

ORGANISMS = [
    {
    '_uuid': '4826a8a7-8b48-4d34-b8de-9f07d95f9ba5',
    '_links': {
        'self': {'href': '/organisms/{_uuid}', 'templated': True},
        },
    'organism_name': 'human',
    'genus': 'Homo',
    'species': 'sapiens',
    'taxon_id': 9606,
    'strain': None,  # Strains and individuals feel like different types
    'individual': None,
    },
]

TARGETS = [
    {
    '_uuid': 'dcd60c9f-7f2e-4d75-8276-9c9a9c6c7669',
    '_links': {
        'self': {'href': '/targets/{_uuid}', 'templated': True},
        'organism': {'href': '/organisms/{organism_uuid}', 'templated': True},
        },
    'target_term_id': '786', # changed to HNGC
    'target_label': 'ATF4',
    'organism_name': 'human',  # link to organism
    'organism_uuid': '4826a8a7-8b48-4d34-b8de-9f07d95f9ba5',  # looked up on insert?
    'target_symbol': 'ATF4',
    'target_gene_name': 'ATF4', # totally redundant column
    'target_class': 'generated',
    'aliases': [
        {'alias': 'CREB2', 'source': 'HGNC'},
        {'alias': 'TXREB', 'source': 'HGNC'},
        {'alias': 'CREB-2', 'source': 'HGNC'},
        {'alias': 'TAXREB67', 'source': 'HGNC'},
        ],
    'dbxref': [
        {'db': 'UniProt', 'id': 'P....'},
    ],

    'is_current': True,
    'date_created': '2013-01-17',
    'created_by': 'Myers-Pauli-Behn',
    },
    {
    '_uuid': 'BAF56297-9628-418F-B78E-95EDD524E4F6',
    '_links': {
        'self': {'href': '/targets/{_uuid}', 'templated': True},
        'organism': {'href': '/organisms/{organism_uuid}', 'templated': True},
        'modification': {'href': '/modifications/{modification_uuid}', 'templated': True}, # possibly unnecessary...
        },
    'target_term_id': '4764',
    'target_label': 'H3K4me3',
    'organism_name': 'human',  # link to organism
    'organism_uuid': '4826a8a7-8b48-4d34-b8de-9f07d95f9ba5',  # looked up on insert?
    'target_symbol': 'H3F3A',
    'target_gene_name': 'H3F3A',
    'target_class': 'generated',
    'modification': {
        'type': 'trimethylation',
        'residue': 'K', # lysine
        'position': 4,
    },
    'modification_uuid': '756AFFF-C67C-4D51-B665-8C35D3BC0EB7',
    'aliases': [
        {'alias': 'H3.3', 'source': 'HGNC'},
        {'alias': 'H3F3', 'source': 'HGNC'},
        {'alias': 'histone H3.3', 'source': 'HGNC'},
        ],
    'dbxref': [
        {'db': 'UniProt', 'id': 'P84243'},
    ],

    'is_current': True,
    'date_created': '2013-02-06',
    'created_by': 'Myers-Pauli-Behn',
    },
]

SOURCES = [
    {
    '_uuid': '3aa827c3-92f8-41fa-9608-201558f7a1c4',
    '_links': {
        'self': {'href': '/sources/{_uuid}', 'templated': True},
        },
    'source_name': 'sigma',
    'source_title': 'Sigma-Aldrich',
    'url': 'http://www.sigmaaldrich.com',
    },
    {
    '_uuid': '3aa827c3-92f8-41fa-9608-2aac58f7a1c4',
    '_links': {
        'self': {'href': '/sources/{_uuid}', 'templated': True},
        },
    'source_name': 'gingeras',
    'source_title': 'Gingeras Lab',
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
    'source_name': 'Sigma-Aldrich',  # PK
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
    'source_name': 'Gingeras',
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


def test_load_all(testapp):
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
