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
        'title': "Genetic modification techniquess",
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
    name='genetic-modifications',
    properties={
        'title': "Genetic modifications",
        'description': 'Listing of all types of genetic modifications.'
    })
class GeneticModification(Item):
    item_type = 'genetic_modification'
    base_types = ['GeneticModification'] + Item.base_types
    schema = load_schema('encoded:schemas/genetic_modification.json')
    embedded = ['treatment',
                'genetic_modification']
