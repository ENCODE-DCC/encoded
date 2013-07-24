# -*- coding: utf-8 -*-
from collections import OrderedDict

ORGANISMS = [
    {
    'uuid': '7745b647-ff15-4ff3-9ced-b897d4e2983c',
    'name': 'human',
    'scientific_name': 'Homo sapiens',
    'taxon_id': "9606",
    },
    {
    'uuid': '3413218c-3d86-498b-a0a2-9a406638e786',
    'name': 'mouse',
    'scientific_name': 'Mus musculus',
    'taxon_id': "10090",
    },
]

TARGETS = [
    {
        'uuid': 'dcd60c9f-7f2e-4d75-8276-9c9a9c6c7669',
        'label': 'ATF4',
        'organism': '7745b647-ff15-4ff3-9ced-b897d4e2983c',  # looked up on insert?
        'gene_name': 'ATF4',
        'lab': 'c0a3540e-8ef0-4d4d-a449-ae47c2475838',
        'award': '7fd6664b-17f5-4bfe-9fdf-ed7481cf4d24',
        # 'aliases': [
        #     {'alias': 'CREB2', 'source': 'HGNC'},
        #     {'alias': 'TXREB', 'source': 'HGNC'},
        #     {'alias': 'CREB-2', 'source': 'HGNC'},
        #     {'alias': 'TAXREB67', 'source': 'HGNC'},
        # ],
        # 'dbxref': {
        #     'UniProtKB': ['Q96AQ3'],
        #     'HGNC': ['786']
        # }
    },
    {
        'uuid': 'BAF56297-9628-418F-B78E-95EDD524E4F6',
        'lab': 'c0a3540e-8ef0-4d4d-a449-ae47c2475838',
        'award': '7fd6664b-17f5-4bfe-9fdf-ed7481cf4d24',
        'label': 'H3K4me3',
        'organism': '7745b647-ff15-4ff3-9ced-b897d4e2983c',  # looked up on insert?
        'gene_name': 'H3F3A',
        # 'aliases': [
        #     {'alias': 'H3.3', 'source': 'HGNC'},
        #     {'alias': 'H3F3', 'source': 'HGNC'},
        #     {'alias': 'histone H3.3', 'source': 'HGNC'},
        # ],
        # 'dbxref': {
        #     'UniProtKB': ['P84243'],
        #     'HGNC': ['4764']
        # },
   },
]

SOURCES = [
    {
    'uuid': '3aa827c3-92f8-41fa-9608-201558f7a1c4',
    'name': 'sigma',
    'title': 'Sigma-Aldrich',
    'url': 'http://www.sigmaaldrich.com',
    },
    {
    'uuid': '3aa827c3-92f8-41fa-9608-2aac58f7a1c4',
    'name': 'gingeras',
    'title': 'Gingeras Lab',
    'url': 'http://www.gingeraslab.edu',
    },
]

ANTIBODY_LOTS = [
    {
    'uuid': 'bc293400-eab3-41fb-a41e-35552686b67d',
    'antibody_term_id': 'tbd-taxonomic-id',
    'antibody_name': 's123',
    'clonality': 'Monoclonal',
    'host_orgnanism': 'Mouse',
    'name': 'Sigma-Aldrich',  # PK
    'source': '3aa827c3-92f8-41fa-9608-201558f7a1c4',
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
    'uuid': 'c4da2e0c-149f-4aee-ac21-8690dfdadb1f',
    'antibody': 'bc293400-eab3-41fb-a41e-35552686b67d',
    'target': 'dcd60c9f-7f2e-4d75-8276-9c9a9c6c7669',
    'method': '',
    'doc': '',
    'caption': '',
    'submitter': '',
    'review_state': '',
    },
]

ANTIBODY_APPROVALS = [
    {
    'uuid': 'a8f94078-2d3b-4647-91a2-8ec91b096708',
    'antibody_lot': 'bc293400-eab3-41fb-a41e-35552686b67d',
    'target': 'dcd60c9f-7f2e-4d75-8276-9c9a9c6c7669',
    'validations': [
        'c4da2e0c-149f-4aee-ac21-8690dfdadb1f',
        ],
    },
]

BIOSAMPLES = [
    {
    'uuid': '7c245cea-7d59-45fb-9ebe-f0454c5fe950',
    'biosample_ontology': 'UBERON',
    'biosample_term_id': 'U:349829',
    'biosample_term': 'Liver',
    'biosample_type': 'Tissue',
    'antibody_accession': 'ENCBS001ZZZ',
    'name': 'Gingeras',
    'source': '3aa827c3-92f8-41fa-9608-2aac58f7a1c4',
    'product_id': 'fridge1a',
    'lot_id': '1',
    'treatment': None,
    'donors': ['a59b301a-782f-449e-bce4-9f0a6141b97b'],
    'is_pooled': False,
    'relateds': [],
    'protocols': [
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
    'uuid': '529e3e74-3caa-4842-ae64-18c8720e610e',
    'name': 'ENCODE3-DCC',
    },
    {
    'uuid': 'fae1bd8b-0d90-4ada-b51f-0ecc413e904d',
    'name': 'Myers',
    },
]

BAD_AWARDS = [  # UUID same as one of labs
    {
    'uuid': '529e3e74-3caa-4842-ae64-18c8720e610e',
    'name': 'ENCODE3-DCC',
    },
    {
    'uuid': 'b635b4ed-dba3-4672-ace9-11d76a8d03af',
    'name': 'Myers',
    },
]
LABS = [
    {
    'uuid': '2c334112-288e-4d45-9154-3f404c726daf',
    'name': 'cherry',
    'title': 'Cherry Lab',
    'institute_name': 'Stanford University'
    },
    {
    'uuid': 'b635b4ed-dba3-4672-ace9-11d76a8d03af',
    'name': 'myers',
    'title': 'Myers Lab',
    'institute_name': 'HudsonAlpha Institute for Biotechnology'
    },
]

BAD_LABS = [  # same UUID
    {
    'uuid': '2c334112-288e-4d45-9154-3f404c726daf',
    'name': 'cherry',
    'title': 'Cherry Lab',
    'institute_name': 'Stanford University'
    },
    {
    'uuid': '2c334112-288e-4d45-9154-3f404c726daf',
    'name': 'myers',
    'title': 'Myers Lab',
    'institute_name': 'HudsonAlpha Institute for Biotechnology'
    },
]


USERS = [
    {
    'uuid': 'e9be360e-d1c7-4cae-9b3a-caf588e8bb6f',
    'first_name': 'Benjamin',
    'last_name': 'Hitz',
    'email': 'hitz@stanford.edu',
    'submits_for': ['cherry'],
    },
    {
    'uuid': '1e945b04-aa54-4732-8b81-b41d4565f5f9',
    'first_name': 'Cricket',
    'last_name': 'Sloan',
    'email': 'cricket@stanford.edu',
    'submits_for': ['2c334112-288e-4d45-9154-3f404c726daf'],
    },
    {
    'uuid': 'bb319896-3f78-4e24-b6e1-e4961822bc9b',
    'first_name': 'Florencia',
    'last_name': 'Pauli-Behn',
    'email': 'paulibehn@hudsonalpha.org',
    'submits_for': ['b635b4ed-dba3-4672-ace9-11d76a8d03af'],
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
