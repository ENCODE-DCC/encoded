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
    'host_orgnamism': 'Mouse',
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


def load_all(testapp):
    for url, collection in [
        ('/organisms/', ORGANISMS),
        ('/targets/', TARGETS),
        ('/sources/', SOURCES),
        ('/antibody-lots/', ANTIBODY_LOTS),
        ('/validations/', VALIDATIONS),
        ('/antibodies/', ANTIBODY_APPROVALS),
        ]:
        for item in collection:
            testapp.post_json(url, item, status=201)
