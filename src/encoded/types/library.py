from snovault import (
    calculated_property,
    collection,
    load_schema,
)
from .base import (
    Item,
)
from .shared_calculated_properties import (
    CalculatedAward,
)


@collection(
    name='libraries',
    unique_key='accession',
    properties={
        'title': 'Libraries',
        'description': 'Libraries used in the ENCODE project',
    })
class Library(Item, CalculatedAward):
    item_type = 'library'
    schema = load_schema('encoded:schemas/library.json')
    name_key = 'accession'
    rev = {}
    embedded = [
        'award',
        'lab',
        'protocol',
        'donors',
        'donors.ethnicity',
        'donors.diseases',
        'derived_from',
        'derived_from.biosample_ontology'
    ]


    @calculated_property(condition='protocol', schema={
        "title": "Assay",
        "description": "The general assay used for this Library.",
        "comment": "Do not submit. This is a calculated property",
        "type": "string",
        "enum": [
            "scATAC-seq",
            "snATAC-seq",
            "scRNA-seq",
            "snRNA-seq",
            "CITE-seq",
            "bulk ATAC-seq",
            "bulk RNA-seq"
        ]
    })
    def assay(self, request, derived_from, protocol):
        protocolObject = request.embed(protocol, '@@object?skip_calculated=true')
        if protocolObject.get('library_type') in ['CITE-seq']:
            return protocolObject.get('library_type')
        elif derived_from:
            derfrObject = request.embed(derived_from[0], '@@object?skip_calculated=true')
            if derfrObject.get('suspension_type') == 'cell':
                mat_type = 'sc'
            elif derfrObject.get('suspension_type') == 'nucleus':
                mat_type = 'sn'
            else:
                mat_type = 'bulk '
            return mat_type + protocolObject.get('library_type')
        else:
            return protocolObject.get('library_type')


    @calculated_property(condition='derived_from', schema={
        "title": "Donors",
        "description": "The donors from which samples were taken from to generate this Library.",
        "comment": "Do not submit. This is a calculated property",
        "type": "array",
        "items": {
            "type": "string",
            "linkTo": "Donor"
        },
    })
    def donors(self, request, derived_from):
        all_donors = set()
        for bs in derived_from:
            bs_obj = request.embed(bs, '@@object')
            all_donors.update(bs_obj.get('donors'))
        return sorted(all_donors)
