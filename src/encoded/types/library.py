from contentbase import (
    calculated_property,
    collection,
    load_schema,
)
from .base import (
    Item
)


@collection(
    name='libraries',
    unique_key='accession',
    properties={
        'title': 'Libraries',
        'description': 'Libraries used in the ENCODE project',
    })
class Library(Item):
    item_type = 'library'
    schema = load_schema('encoded:schemas/library.json')
    name_key = 'accession'
    embedded = [
        'biosample',
        'biosample.donor',
        'biosample.donor.organism',
    ]

    @calculated_property(condition='nucleic_acid_term_name', schema={
        "title": "nucleic_acid_term_id",
        "type": "string",
    })
    def nucleic_acid_term_id(self, request, nucleic_acid_term_name):
        term_lookup = {
            'DNA': 'SO:0000352',
            'RNA': 'SO:0000356',
            'polyadenylated mRNA': 'SO:0000871',
            'miRNA': 'SO:0000276',
            'protein': 'SO:0000104'
        }

        if nucleic_acid_term_name in term_lookup:
            return term_lookup.get(nucleic_acid_term_name)
        else:
            return 'Term ID unknown'


    @calculated_property(condition='depleted_in_term_name', schema={
        "title": "depleted_in_term_id",
        "type": "string",
    })
    def depleted_in_term_id(self, request, depleted_in_term_name):
        term_lookup = {
            'rRNA': 'SO:0000252',
            'polyadenylated mRNA': 'SO:0000871',
            'capped mRNA': 'SO:0000862'
        }

        term_id = list()
        for term_name in depleted_in_term_name:
            if term_name in term_lookup:
                term_id.append(term_lookup.get(term_name))
            else:
                term_id.append('Term ID unknown')

        return term_id
