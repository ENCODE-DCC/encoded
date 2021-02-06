from snovault import (
    calculated_property,
    collection,
    load_schema,
)
from .base import (
    Item,
)


@collection(
    name='cell-annotations',
    properties={
        'title': 'Cell annotations',
        'description': 'Listing of cell annotations',
    })
class CellAnnotation(Item):
    item_type = 'cell_annotation'
    schema = load_schema('encoded:schemas/cell_annotation.json')
    embedded = [
        'cell_ontology',
        'tissues_sampled'
    ]


    @calculated_property(schema={
        "title": "Tissues sampled",
        "description": "",
        "comment": "Do not submit. This is a calculated property",
        "type": "array",
        "items": {
            "type": "string",
            "linkTo": "OntologyTerm"
        },
        "notSubmittable": True,
    })
    def tissues_sampled(self, request, matrix_files=None):
        if matrix_files:
            libs = set()
            for mf in matrix_files:
                mf_obj = request.embed(mf, '@@object')
                libs.update(mf_obj.get('libraries'))
            onts = set()
            for l in libs:
                lib_obj = request.embed(l, '@@object')
                onts.update(lib_obj.get('biosample_ontologies'))
            return list(onts)
