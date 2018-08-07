from snovault import (
    calculated_property,
    collection,
    load_schema,
)
from .base import (
    SharedItem,
)


@collection(
    name='genes',
    unique_key='gene:geneid',
    properties={
        'title': 'Genes',
        'description': 'Listing of genes',
    })
class Gene(SharedItem):
    item_type = 'gene'
    schema = load_schema('encoded:schemas/gene.json')
    name_key = "geneid"
    embedded = ['organism']
    audit_inherit = ['*']

    @calculated_property(schema={
        "title": "Title",
        "type": "string",
    })
    def title(self, request, organism, symbol):
        organism_props = request.embed(organism, '@@object')
        return u'{} ({})'.format(symbol, organism_props['scientific_name'])
