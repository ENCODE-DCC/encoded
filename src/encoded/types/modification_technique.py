from snovault import (
    abstract_collection,
    collection,
    load_schema,
)
from .base import (
    Item,
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
