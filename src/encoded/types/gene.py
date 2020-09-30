from snovault import (
    calculated_property,
    collection,
    load_schema,
)
from .base import (
    SharedItem,
    paths_filtered_by_status,
)


@collection(
    name='genes',
    unique_key='gene:gene_id',
    properties={
        'title': 'Genes',
        'description': 'Listing of genes',
    })
class Gene(SharedItem):
    item_type = 'gene'
    schema = load_schema('encoded:schemas/gene.json')
    name_key = "gene_id"

    @calculated_property(schema={
        "title": "Title",
        "comment": "Do not submit. This is a calculated property",
        "type": "string",
    })
    def title(self, request, assembly, symbol):
        return u'{} ({})'.format(symbol, assembly)