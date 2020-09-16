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
    unique_key='gene:geneid',
    properties={
        'title': 'Genes',
        'description': 'Listing of genes',
    })
class Gene(SharedItem):
    item_type = 'gene'
    schema = load_schema('encoded:schemas/gene.json')
    name_key = "geneid"
    rev = {
        'targets': ('Target', 'genes')
    }

    @calculated_property(schema={
        "title": "Title",
        "type": "string",
    })
    def title(self, request, organism, symbol):
        organism_props = request.embed(organism, '@@object')
        return u'{} ({})'.format(symbol, organism_props['scientific_name'])

    @calculated_property(schema={
        "description": "List of associated targets.",
        "comment": "Do not submit. Values in the list are reverse links of a"
                   " target that have this gene under its genes property.",
        "title": "Target",
        "type": "array",
        "items": {
            "type": ['string', 'object'],
            "linkFrom": "Target.genes"
        },
        "notSubmittable": True,
    })
    def targets(self, request, targets):
        return paths_filtered_by_status(request, targets)
