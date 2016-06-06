from snovault import (
    abstract_collection,
    collection,
    calculated_property,
    load_schema,
)
from snovault.attachment import ItemWithAttachment
from .base import (
    Item,
)


@abstract_collection(
    name='genetic-modifications',
    properties={
        'title': "Genetic modifications",
        'description': 'Listing of all types of genetic modifications.',
    })
class GeneticModification(ItemWithAttachment, Item):
    base_types = ['GeneticModification'] + Item.base_types


@collection(
    name='crispr',
    properties={
        'title': "CRISPR genetic modification",
        'description': 'Listing of all CRISPR genetic modifications.',
    })
class Crispr(GeneticModification):
    item_type = 'crispr'
    schema = load_schema('encoded:schemas/crispr.json')