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
        'description': 'Listing of all types of genetic modifications.'
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
        'title': "Transcription activator-like effector genetic modifications",
        'description': 'Listing of all TALE genetic modifications.'
    })
class Tale(ModificationTechnique):
    item_type = 'tale'
    schema = load_schema('encoded:schemas/tale.json')
    embedded = ModificationTechnique.embedded


@collection(
    name='plasmids',
    properties={
        'title': "General plasmid-based genetic modifications",
        'description': 'Listing of all general plasmid-based genetic modifications.'
    })
class Plasmid(ModificationTechnique):
    item_type = 'plasmid'
    schema = load_schema('encoded:schemas/plasmid.json')
    embedded = ModificationTechnique.embedded
