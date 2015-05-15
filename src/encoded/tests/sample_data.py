# -*- coding: utf-8 -*-
from collections import OrderedDict

RED_DOT = """data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUA
AAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO
9TXL0Y4OHwAAAABJRU5ErkJggg=="""

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
        'investigated_as': ['transcription factor']
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
        'investigated_as': ['histone modification']
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
        'uuid': '1d5be796-8f80-4fd4-b6c7-6674318657eb',
        'name': 'gingeras',
        'title': 'Gingeras Lab',
        'url': 'http://www.gingeraslab.edu',
    },
]

ANTIBODY_LOTS = [
    {
        'uuid': 'bc293400-eab3-41fb-a41e-35552686b67d',
        'accession': 'ENCAB000TST',
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
        'targets': ['ATF4-human']
    },
]

ANTIBODY_CHARACTERIZATIONS = [
    {
        'uuid': 'c4da2e0c-149f-4aee-ac21-8690dfdadb1f',
        'characterizes': 'bc293400-eab3-41fb-a41e-35552686b67d',
        'target': 'dcd60c9f-7f2e-4d75-8276-9c9a9c6c7669',
        'lab': 'myers',
        'award': 'Myers',
        'attachment': {'download': 'red-dot.png', 'href': RED_DOT},
        'secondary_characterization_method': 'dot blot assay',
        'status': 'pending dcc review'
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
        'status': 'pending dcc review',
    },
]

BIOSAMPLES = [
    {
        'uuid': '7c245cea-7d59-45fb-9ebe-f0454c5fe950',
        'accession': 'ENCBS000TST',
        'biosample_term_id': 'UBERON:349829',
        'biosample_term_name': 'Liver',
        'biosample_type': 'tissue',
        'source': 'gingeras',
        'lab': 'myers',
        'award': 'Myers',
        'organism': 'human',
    },
]

LIBRARIES = [
    {
        'uuid': 'a95b00ea-fc13-42ee-a322-e36793f1325d',
        'accession': 'ENCLB000TST',
        'nucleic_acid_term_id': 'SO:0000352',
        'nucleic_acid_term_name': 'DNA',
        'biosample': 'ENCBS000TST',
        'status': 'released',
        'lab': 'myers',
        'award': 'Myers',
    },
]

AWARDS = [
    {
        'uuid': '529e3e74-3caa-4842-ae64-18c8720e610e',
        'name': 'ENCODE3-DCC',
        'rfa': 'ENCODE3',
        'project': 'ENCODE',
    },
    {
        'uuid': 'fae1bd8b-0d90-4ada-b51f-0ecc413e904d',
        'name': 'Myers',
        'rfa': 'ENCODE3',
        'project': 'ENCODE',

    },
    {
        'uuid': '2a27a363-6bb5-43cc-99c4-d58bf06d3d8e',
        'name': 'ENCODE2',
        'rfa': 'ENCODE2',
        'project': 'ENCODE',
    }
]

BAD_AWARDS = [  # UUID same as one of labs
    {
        'uuid': '529e3e74-3caa-4842-ae64-18c8720e610e',
        'name': 'ENCODE3-DCC',
        'project': 'ENCODE',
    },
    {
        'uuid': 'b635b4ed-dba3-4672-ace9-11d76a8d03af',
        'name': 'Myers',
        'project': 'ENCODE',
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
        'uuid': '81a6cc12-2847-4e2e-8f2c-f566699eb29e',
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
        'status': 'disabled',
    },
]

EXPERIMENTS = [
    {
        'uuid': 'fa3e286d-a44c-41e0-bcce-3c24fe9aa02d',
        'accession': 'ENCSR000TST',
        'lab': 'myers',
        'award': 'Myers',
    },
    {
        'uuid': 'f26eeb63-e77c-47e9-b8fd-e21b24065424',
        'accession': 'ENCSR001TST',
        'lab': 'myers',
        'award': 'Myers',
    },
]

DATASETS = [
    {
        'uuid': 'd2470afe-ac68-4489-8f51-90ddfbc8e00b',
        'accession': 'ENCSR002TST',
        'lab': 'myers',
        'award': 'Myers',
        'dataset_type': 'composite',
    },
]

REPLICATES = [
    {
        'uuid': '13468ab5-2369-4857-a303-7c5f28918190',
        'experiment': 'ENCSR000TST',
        'library': 'ENCLB000TST',
        'biological_replicate_number': 1,
        'technical_replicate_number': 1,
    },
    {
        'uuid': 'df38fd69-8c4b-4870-86a4-55f4b355324e',
        'experiment': 'ENCSR000TST',
        'library': 'ENCLB000TST',
        'biological_replicate_number': 1,
        'technical_replicate_number': 2,
    },
]

RNAIS = [
    {
        'uuid': '8d155bde-8ebc-11e3-baa8-0800200c9a66',
        'lab': 'myers',
        'award': 'Myers',
        'rnai_sequence': 'TATATGGGGAA',
        'target': 'dcd60c9f-7f2e-4d75-8276-9c9a9c6c7669',
        'rnai_type': 'shRNA',
    },
]

CONSTRUCTS = [
    {
        'uuid': '86b968ae-e5d3-4562-bd8e-e20e7ba40119',
        'lab': 'myers',
        'award': 'Myers',
        'target': 'dcd60c9f-7f2e-4d75-8276-9c9a9c6c7669',
        'source': 'gingeras',
        'construct_type': 'fusion protein',
        'tags': [],
    },
]

FILES = [
    {
        'uuid': 'c22e0390-af36-483c-950d-5a2e0efe37ec',
        'accession': 'ENCFF000TST',
        'dataset': 'ENCSR000TST',
        'file_format': 'fasta',
        'md5sum': 'd41d8cd98f00b204e9800998ecf8427e',
        'output_type': 'raw data',
        'status': 'in progress',
        'lab': 'myers',
        'award': 'Myers',
    },
    {
        'uuid': '0a38fea0-c067-415a-9710-c887aff95767',
        'accession': 'ENCFF001TST',
        'dataset': 'ENCSR001TST',
        'file_format': 'fasta',
        'md5sum': '3f9ae164abb55a93bcd891b192d86164',
        'output_type': 'raw data',
        'status': 'in progress',
        'lab': 'myers',
        'award': 'Myers',
    },
]

PUBLICATIONS = [
    {
        "uuid": '8312fc0c-b241-4cb2-9b01-1438910550ad',
        "authors": "Li Q, Brown JB, Huang H, Bickel PJ",
        "date_published": "2011 Oct 21",
        "issue": "3",
        "journal": "Annals of Applied Statistics",
        "page": "1752-1779",
        "identifiers": [
            "doi:10.1214/11-AOAS466"
        ],
        "status": "published",
        "title": "Measuring reproducibility of high-throughput experiments",
        "volume": "5",
        'lab': 'myers',
        'award': 'Myers',
    },
    {
        'uuid': '4c0a722c-a4f6-481f-b181-1a5330660d73',
        "authors": "Venken KJ, Carlson JW, Schulze KL, Pan H, He Y, Spokony R, Wan KH, Koriabine M, de Jong PJ, White KP, Bellen HJ, Hoskins RA",
        "date_published": "2009 Jun",
        "issue": "6",
        "journal": "Nature methods",
        "page": "431-4",
        "identifiers": [
            "PMID:19465919",
            "PMCID:PMC2784134"
        ],
        "status": "published",
        "title": "Versatile P[acman] BAC libraries for transgenesis studies in Drosophila melanogaster.",
        "volume": "6",
        'lab': 'myers',
        'award': 'Myers',
    },
    {
        'uuid': "b42b2990-fa96-48e2-a2b1-501a1a83a068",
        "authors": "Robertson G, Hirst M, Bainbridge M, Bilenky M, Zhao Y, Zeng T, Euskirchen G, Bernier B, Varhol R, Delaney A, Thiessen N, Griffith OL, He A, Marra M, Snyder M, Jones S",
        "date_published": "2007 Aug",
        "issue": "8",
        "journal": "Nature methods",
        "page": "651-7",
        "identifiers": [
            "doi:10.1038/nmeth1068",
            "PMID:17558387"
        ],
        "status": "published",
        "title": "Genome-wide profiles of STAT1 DNA association using chromatin immunoprecipitation and massively parallel sequencing.",
        "volume": "4",
        'lab': 'myers',
        'award': 'Myers',
    },
    {
        "uuid": "719ee795-ba05-48ab-93ea-0c07100bc92e",
        "authors": "Hirsch HA, Iliopoulos D, Tsichlis PN, Struhl K",
        "date_published": "2009 Oct 1",
        "issue": "19",
        "journal": "Cancer research",
        "page": "7507-11",
        "identifiers": [
            "doi:10.1158/0008-5472.CAN-09-2994",
            "PMID:19752085",
            "PMCID:PMC2756324"
        ],
        "status": "published",
        "title": "Metformin selectively targets cancer stem cells, and acts together with chemotherapy to block tumor growth and prolong remission.",
        "volume": "69",
        'lab': 'myers',
        'award': 'Myers',
    }
]

PIPELINES = [
    {
        'uuid': '4079755c-af30-44de-9545-e744f000f534',
        'title': 'mysterious-pipeline',
    }
]

DOCUMENTS = [
    {
        'uuid': 'f7b7b690-919b-4e87-bec2-58b5bb76418b',
        'lab': 'myers',
        'award': 'Myers',
        'document_type': 'growth protocol',
    }
]

BIOSAMPLE_CHARACTERIZATIONS = [
    {
        'uuid': 'ccd9c90b-fe51-41ce-9885-818d261c745a',
        'characterizes': '7c245cea-7d59-45fb-9ebe-f0454c5fe950',
        'lab': 'myers',
        'award': 'Myers',
        'attachment': {'download': 'red-dot.png', 'href': RED_DOT},
    },
]

MOUSE_DONORS = [
    {
        'uuid': '6d36247e-1f64-4e72-b8cb-7b6cce827635',
        'lab': 'myers',
        'award': 'Myers',
        'organism': '3413218c-3d86-498b-a0a2-9a406638e786',
    }
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
    ('library', LIBRARIES),
    ('experiment', EXPERIMENTS),
    ('dataset', DATASETS),
    ('replicate', REPLICATES),
    ('rnai', RNAIS),
    ('construct', CONSTRUCTS),
    ('file', FILES),
    ('publication', PUBLICATIONS),
    ('pipeline', PIPELINES),
    ('document', DOCUMENTS),
    ('biosample_characterization', BIOSAMPLE_CHARACTERIZATIONS),
    ('mouse_donor', MOUSE_DONORS),
])


def load(testapp, item_type):
    items = []
    for item in URL_COLLECTION[item_type]:
        res = testapp.post_json('/' + item_type, item, status=201)
        items.append(res.json['@graph'][0])
    return items
