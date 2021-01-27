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
        'genes_expressed_high',
        'genes_expressed_low',
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
            susps = set()
            for l in libs:
                lib_obj = request.embed(l, '@@object?skip_calculated=true')
                susps.update(lib_obj.get('derived_from'))
            onts = set()
            for s in susps:
                susp_obj = request.embed(s, '@@object')
                if susp_obj['@type'][0] == 'Suspension':
                    onts.add(susp_obj.get('biosample_ontology'))
            return list(onts)
