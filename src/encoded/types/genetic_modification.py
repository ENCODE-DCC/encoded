from snovault import (
    abstract_collection,
    collection,
    load_schema,
)
from .base import (
    Item,
)


@abstract_collection(
    name='genetic-modifications',
    properties={
        'title': "Genetic modifications",
        'description': 'Listing of all types of genetic modifications.',
    })
class GeneticModification(Item):
    base_types = ['GeneticModification'] + Item.base_types


@collection(
    name='crisprs',
    properties={
        'title': "CRISPR genetic modifications",
        'description': 'Listing of all CRISPR genetic modifications.',
    })
class Crispr(GeneticModification):
    item_type = 'crispr'
    base_types = ['Crispr'] + GeneticModification.base_types
    schema = load_schema('encoded:schemas/crispr.json')
