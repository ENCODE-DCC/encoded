from snovault import (
    calculated_property,
    collection,
    load_schema,
)
from .base import (
    SharedItem,
)


developmental_slims = {
    'UBERON:0000926': 'mesoderm',
    'UBERON:0000924': 'ectoderm',
    'UBERON:0000925': 'endoderm'
}

system_slims = {
    'UBERON:0000383': 'musculature of body',
    'UBERON:0000949': 'endocrine system',
    'UBERON:0002330': 'exocrine system',
    'UBERON:0000990': 'reproductive system',
    'UBERON:0001004': 'respiratory system',
    'UBERON:0001007': 'digestive system',
    'UBERON:0001008': 'excretory system',
    'UBERON:0001009': 'circulatory system',
    'UBERON:0001434': 'skeletal system',
    'UBERON:0002405': 'immune system',
    'UBERON:0002416': 'integumental system',
    'UBERON:0001032': 'sensory system',
    'UBERON:0001016': 'nervous system',
    'UBERON:0001017': 'central nervous system',
    'UBERON:0000010': 'peripheral nervous system',
    'UBERON:0002390': 'hematopoietic system',
    'UBERON:0004535': 'cardiovascular system',
    'UBERON:0000363': 'reticuloendothelial system'
}

organ_slims = {
    'UBERON:0002369': 'adrenal gland',
    'UBERON:0002110': 'gallbladder',
    'UBERON:0002106': 'spleen',
    'UBERON:0001043': 'esophagus',
    'UBERON:0000004': 'nose',
    'UBERON:0000056': 'ureter',
    'UBERON:0000057': 'urethra',
    'UBERON:0000059': 'large intestine',
    'UBERON:0000165': 'mouth',
    'UBERON:0000945': 'stomach',
    'UBERON:0000948': 'heart',
    'UBERON:0000955': 'brain',
    'UBERON:0000970': 'eye',
    'UBERON:0000991': 'gonad',
    'UBERON:0001255': 'urinary bladder',
    'UBERON:0001264': 'pancreas',
    'UBERON:0001474': 'bone element',
    'UBERON:0002048': 'lung',
    'UBERON:0002097': 'skin of body',
    'UBERON:0002107': 'liver',
    'UBERON:0002108': 'small intestine',
    'UBERON:0002113': 'kidney',
    'UBERON:0002240': 'spinal cord',
    'UBERON:0002367': 'prostate gland',
    'UBERON:0002370': 'thymus',
    'UBERON:0003126': 'trachea',
    'UBERON:0001723': 'tongue',
    'UBERON:0001737': 'larynx',
    'UBERON:0006562': 'pharynx',
    'UBERON:0001103': 'diaphragm',
    'UBERON:0002185': 'bronchus',
    'UBERON:0000029': 'lymph node',
    'UBERON:0001132': 'parathyroid gland',
    'UBERON:0002046': 'thyroid gland',
    'UBERON:0001981': 'blood vessel',
    'UBERON:0001473': 'lymphatic vessel',
    'UBERON:0000178': 'blood',
    'UBERON:0007844': 'cartilage element',
    'UBERON:0001690': 'ear',
    'UBERON:0001987': 'placenta',
    'UBERON:0001911': 'mammary gland',
    'UBERON:0000007': 'pituitary gland',
    'UBERON:0016887': 'extraembryonic component',
    'UBERON:0001013': 'adipose tissue',
    'UBERON:0000310': 'breast',
    'UBERON:0000989': 'penis',
    'UBERON:0004288': 'skeleton',
    'UBERON:0000995': 'uterus',
    'UBERON:0000996': 'vagina',
    'UBERON:0000992': 'ovary',
    'UBERON:0000473': 'testis',
    'UBERON:0003509': 'arterial blood vessel',
    'UBERON:0001638': 'vein',
    'UBERON:0000160': 'intestine',
    'UBERON:0002384': 'connective tissue',
    'UBERON:0002101': 'limb',
    'UBERON:0000922': 'embryo',
    'UBERON:0001021': 'nerve',
    'UBERON:0002371': 'bone marrow',
    'UBERON:0006314': 'bodily fluid',
    'UBERON:0002049': 'vasculature',
    'UBERON:0000483': 'epithelium',
    'UBERON:0002407': 'pericardium',
    'UBERON:0001744': 'lymphoid tissue',
    'UBERON:0001155': 'colon',
    'UBERON:0003547': 'brain meninx',
    'UBERON:0001350': 'coccyx',
    'UBERON:0002368': 'endocrine gland',
    'UBERON:0002365': 'exocrine gland',
    'UBERON:0002073': 'hair follicle',
    'UBERON:0005057': 'immune organ',
    'UBERON:0001817': 'lacrimal gland',
    'UBERON:0002182': 'main bronchus',
    'UBERON:0001829': 'major salivary gland',
    'UBERON:0000414': 'mucous gland',
    'UBERON:0001821': 'sebaceous gland',
    'UBERON:0000998': 'seminal vesicle',
    'UBERON:0001820': 'sweat gland',
    'UBERON:0001555': 'digestive tract',
    'UBERON:0000043': 'tendon'
}

cell_slims = {
    'CL:0000236': 'B cell',
    'EFO:0001640': 'B cell',  # B cell derived cell line
    'EFO:0001639': 'cancer cell',  # cancer cell line
    'CL:0002494': 'cardiocyte',
    'CL:0002320': 'connective tissue cell',
    'CL:0002321': 'embryonic cell',
    'CL:0000115': 'endothelial cell',
    'EFO:0005730': 'endothelial cell',  # endothelial cell derived cell line
    'CL:0000066': 'epithelial cell',
    'EFO:0001641': 'epithelial cell',  # epithelial cell derived cell line
    'CL:0000057': 'fibroblast',
    'EFO:0002009': 'fibroblast',  # fibroblast derived cell line
    'CL:0000988': 'hematopoietic cell',
    'EFO:0004905': 'induced pluripotent stem cell',
    'EFO:0005740': 'induced pluripotent stem cell',  # ipsc derived cell line
    'CL:0000312': 'keratinocyte',
    'CL:0000738': 'leukocyte',
    'EFO:0005292': 'lymphoblast',  # lymphoblastoid cell line
    'CL:0000148': 'melanocyte',
    'CL:0000576': 'monocyte',
    'CL:0000763': 'myeloid cell',
    'CL:0000056': 'myoblast',
    'CL:0002319': 'neural cell',
    'EFO:0005214': 'neuroblastoma cell',  # neuroblastoma cell line
    'CL:0000669': 'pericyte',
    'CL:0000192': 'smooth muscle cell',
    'EFO:0005735': 'smooth muscle cell',  # smooth muscle cell derived cell line
    'CL:0000034': 'stem cell',
    'EFO:0002886': 'stem cell',  # stem cell derived cell line
    'CL:0000084': 'T cell',
    'NTR:0000550': 'progenitor cell'
}

disease_slims = {
    'MONDO:0002280': 'anemia',
    'MONDO:0005578': 'arthritis',
    'MONDO:0005113': 'bacterial infection',
    'MONDO:0004992': 'cancer',
    'MONDO:0005015': 'diabetes',
    'MONDO:0004335': 'digestive system disease',
    'MONDO:0005044': 'hypertensive disorder',
    'MONDO:0005240': 'kidney disease',
    'MONDO:0005084': 'mental disorder',
    'MONDO:0005066': 'metabolic disease',
    'MONDO:0100081': 'sleep disorder'
}


@collection(
    name='ontology-terms',
    unique_key='ontology_term:name',
    properties={
        'title': 'Ontology term',
        'description': 'Ontology terms in the Lattice metadata.',
    })
class OntologyTerm(SharedItem):
    item_type = 'ontology_term'
    schema = load_schema('encoded:schemas/ontology_term.json')

    def unique_keys(self, properties):
        keys = super(OntologyTerm, self).unique_keys(properties)
        keys.setdefault('ontology_term:name', []).append(self.name(properties))
        return keys

    @calculated_property(schema={
        "title": "Name",
        "description": "The name used for the system to identify this object.",
        "comment": "Do not submit. This is a calculated property",
        "type": "string",
    })
    def name(self, properties=None):
        if properties is None:
            properties = self.upgrade_properties()
        return properties['term_id'].replace(':', '_')


    @property
    def __name__(self):
        return self.name()


    @staticmethod
    def _get_ontology_slims(registry, term_id, anc_list, slimTerms):
        if term_id not in registry['ontology']:
            return []
        ancestor_list = registry['ontology'][term_id][anc_list]
        slims = []
        for slimTerm in slimTerms:
            if slimTerm in ancestor_list:
                slims.append(slimTerms[slimTerm])
        return slims


    @calculated_property(condition='term_id', schema={
        "title": "Organ",
        "description": "The organs that this term is an ontological descendent of.",
        "comment": "Do not submit. This is a calculated property",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def organ_slims(self, registry, term_id):
        return self._get_ontology_slims(registry, term_id, 'closure', organ_slims)


    @calculated_property(condition='term_id', schema={
        "title": "Cell",
        "description": "The cell types that this term is an ontological descendent of.",
        "comment": "Do not submit. This is a calculated property",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def cell_slims(self, registry, term_id):
        return self._get_ontology_slims(registry, term_id, 'closure', cell_slims)


    @calculated_property(condition='term_id', schema={
        "title": "Developmental slims",
        "description": "The developmental stages that this term is an ontological descendent of.",
        "comment": "Do not submit. This is a calculated property",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def developmental_slims(self, registry, term_id):
        return self._get_ontology_slims(registry, term_id, 'closure_with_develops_from', developmental_slims)


    @calculated_property(condition='term_id', schema={
        "title": "System slims",
        "description": "The biological systems that this term is an ontological descendent of.",
        "comment": "Do not submit. This is a calculated property",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def system_slims(self, registry, term_id):
        return self._get_ontology_slims(registry, term_id, 'closure', system_slims)


    @calculated_property(condition='term_id', schema={
        "title": "Disease slims",
        "description": "The diseases that this term is an ontological descendent of.",
        "comment": "Do not submit. This is a calculated property",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def disease_slims(self, registry, term_id):
        return self._get_ontology_slims(registry, term_id, 'closure', disease_slims)


    @calculated_property(condition='term_id', schema={
        "title": "Synonyms",
        "description": "The synonyms of this term, as listed by the ontology database.",
        "comment": "Do not submit. This is a calculated property",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def synonyms(self, registry, term_id):
        if term_id not in registry['ontology']:
            return []
        return list(set(
            slim for slim in registry['ontology'][term_id]['synonyms']
        ))


    @calculated_property(condition='term_id', schema={
        "title": "Ontology DB",
        "description": "The ontology database for which this term belongs.",
        "comment": "Do not submit. This is a calculated property",
        "type": "string",
    })
    def ontology_database(self, registry, term_id):
        return term_id.split(':')[0]
