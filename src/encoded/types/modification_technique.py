from snovault import (
    abstract_collection,
    collection,
    calculated_property,
    load_schema,
)
from .base import (
    Item,
    paths_filtered_by_status,
)


@abstract_collection(
    name='modification-techniques',
    properties={
        'title': "Genetic modification techniques",
        'description': 'Listing of all types of genetic modification techniques.'
    })
class ModificationTechnique(Item):
    base_types = ['ModificationTechnique'] + Item.base_types
    # embedded = ['lab', 'award', 'source']

    rev = {
        'associated_modifications': ('GeneticModification', 'modification_techniques')
    }

    @calculated_property(schema={
        "title": "Associated modifications",
        "description": "Genetic modifications associated with the application of this technique",
        "type": "array",
        "items": {
            "type": ['string', 'object'],
            "linkFrom": "GeneticModification.modification_techniques",
        },
    })
    def associated_modifications(self, request, associated_modifications):
        return paths_filtered_by_status(request, associated_modifications)


    @calculated_property(schema={
        "title": "targeted_genes",
        "description": "Targets associated with the application of this technique",
        "type": "string",
        "linkTo": "Target",
    }, define=True)
    def targeted_genes(self, request, associated_modifications):
        genes = set()
        for m in associated_modifications:
            mod = request.embed(m, '@@object')
            if 'target' in mod:
                genes.add(mod.get('target'))
        return list(genes)


@collection(
    name='crisprs',
    properties={
        'title': "CRISPR genetic modifications",
        'description': 'Listing of all CRISPR genetic modifications.'
    })
class Crispr(ModificationTechnique):
    item_type = 'crispr'
    schema = load_schema('encoded:schemas/crispr.json')
    embedded = ModificationTechnique.embedded


@collection(
    name='tales',
    properties={
        'title': "Transcription activator-like effector genetic modifications.",
        'description': 'Listing of all TALE genetic modifications.'
    })
class Tale(ModificationTechnique):
    item_type = 'tale'
    schema = load_schema('encoded:schemas/tale.json')
    embedded = ModificationTechnique.embedded


@collection(
    name='transfections',
    properties={
        'title': "General genetic modifications made via transfection.",
        'description': 'Listing of all general transfection-based genetic modifications.'
    })
class Transfection(ModificationTechnique):
    item_type = 'transfection'
    schema = load_schema('encoded:schemas/transfection.json')
    embedded = ModificationTechnique.embedded
