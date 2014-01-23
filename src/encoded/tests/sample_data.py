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
    'clonality': 'monoclonal',
    'host_organism': 'mouse',
    'source': 'sigma',  # PK
    'product_id': 'WH0000468M1',  # PK
    'lot_id': 'CB191-2B3',  # PK
    'url': 'http://www.sigmaaldrich.com/catalog/product/sigma/wh0000468m1?lang=en&region=US',
    'isotype': u'IgG1κ',
    'antigen_description': 'ATF4 (NP_001666, a.a. 171-271) partial recombinant protein with GST tag.',
    'lab': 'myers',
    'award': 'Myers',
    },
]

ANTIBODY_CHARACTERIZATIONS = [
    {
    'uuid': 'c4da2e0c-149f-4aee-ac21-8690dfdadb1f',
    'characterizes': 'bc293400-eab3-41fb-a41e-35552686b67d',
    'target': 'dcd60c9f-7f2e-4d75-8276-9c9a9c6c7669',
    'lab': 'myers',
    'award': 'Myers',
    },
]

ANTIBODY_APPROVALS = [
    {
    'uuid': 'a8f94078-2d3b-4647-91a2-8ec91b096708',
    'antibody': 'bc293400-eab3-41fb-a41e-35552686b67d',
    'target': 'dcd60c9f-7f2e-4d75-8276-9c9a9c6c7669',
    'characterizations': [
        'c4da2e0c-149f-4aee-ac21-8690dfdadb1f',
        ],
    'lab': 'myers',
    'award': 'Myers',
    'status': 'SUBMITTED',
    },
]

BIOSAMPLES = [
    {
    'uuid': '7c245cea-7d59-45fb-9ebe-f0454c5fe950',
    'biosample_term_id': 'UBERON:349829',
    'biosample_term_name': 'Liver',
    'biosample_type': 'tissue',
    'source': '3aa827c3-92f8-41fa-9608-2aac58f7a1c4',
    'product_id': 'fridge1a',
    'lot_id': '1',
    'lab': 'myers',
    'award': 'Myers',
    'organism': 'human',
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
    'uuid': 'cfb789b8-46f3-4d59-a2b3-adc39e7df93a',
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
    'groups': ['admin', 'programmer'],
    },
    {
    'uuid': '1e945b04-aa54-4732-8b81-b41d4565f5f9',
    'first_name': 'Cricket',
    'last_name': 'Sloan',
    'email': 'cricket@stanford.edu',
    'submits_for': ['cfb789b8-46f3-4d59-a2b3-adc39e7df93a'],
    'groups': ['admin', 'wrangler'],
    },
    {
    'uuid': 'bb319896-3f78-4e24-b6e1-e4961822bc9b',
    'first_name': 'Florencia',
    'last_name': 'Pauli-Behn',
    'email': 'paulibehn@hudsonalpha.org',
    'submits_for': ['b635b4ed-dba3-4672-ace9-11d76a8d03af'],
    },
    {
    'uuid': '2aaf75d9-4273-4bd8-9fd1-217e3d0af7cc',
    'first_name': 'No',
    'last_name': 'Login',
    'email': 'nologin@example.org',
    'submits_for': ['b635b4ed-dba3-4672-ace9-11d76a8d03af'],
    'status': 'DISABLED',
    },
]

URL_COLLECTION = OrderedDict([
    ('lab', LABS),
    ('user', USERS),
    ('award', AWARDS),
    ('organism', ORGANISMS),
    ('target', TARGETS),
    ('source', SOURCES),
    ('antibody_lot', ANTIBODY_LOTS),
    ('antibody_characterization', ANTIBODY_CHARACTERIZATIONS),
    ('antibody_approval', ANTIBODY_APPROVALS),
    ('biosample', BIOSAMPLES),
])


def load(testapp, item_type):
    items = []
    for item in URL_COLLECTION[item_type]:
        res = testapp.post_json('/' + item_type, item, status=201)
        items.append(res.json['@graph'][0])
    return items
