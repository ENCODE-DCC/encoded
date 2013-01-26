# -*- coding: utf-8 -*-

ORGANISMS = [
    {
    '_links': {
        'self': {'href': '/organisms/human'},
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
    '_links': {
        'self': {'href': '/targets/tbd'},
        'organism': {'href': '/organisms/human'},
        },
    'target_term_id': '468',
    'target_label': 'ATF4',
    'organism_name': 'human',  # link to organism
    'target_symbol': None,
    'target_gene_name': 'ATF4',
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
]

SOURCES = [
    {
    '_links': {
        'self': {'href': '/sources/sigma'},
        },
    'source_name': 'sigma',
    'source_title': 'Sigma-Aldrich',
    'url': 'http://www.sigmaaldrich.com',
    },
]

ANTIBODIES = [
    {
    '_links': {
        'self': {'href': '/antibodies/s123'},
        'source': {'href': '/sources/sigma'},
        },
    'antibody_term_id': 'tbd-taxonomic-id',
    'antibody_name': 's123',
    'clonality': 'Monoclonal',
    'host_orgnamism': 'Mouse',
    'source_name': 'Sigma-Aldrich',  # PK
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
    '_links': {
        'self': {'href': '/antibodies/s123/validations/v456'},
        'antibody': {'href': '/antibodies/sigma'},
        'target': {'href': '/targets/tbd'},
        },
    'method': '',
    'doc': '',
    'caption': '',
    'submitter': '',
    'review_state': '',
    },
]

APPROVALS = [
    {
    '_links': {
        'self': {'href': '/antibodies/Sigma-Aldrich,WH0000468M1,CB191-2B3/approvals/tbd'},
        'antibody': {'href': '/antibodies/Sigma-Aldrich,WH0000468M1,CB191-2B3'},
        'target': {'href': '/targets/tbd'},
        'validations': [],
        },
    },
]


def load_antibodies(testapp):
    for item in ANTIBODIES:
        testapp.post_json('/antibodies/', item, status=201)
