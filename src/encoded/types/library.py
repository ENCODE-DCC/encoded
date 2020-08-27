from snovault import (
    CONNECTION,
    calculated_property,
    collection,
    load_schema,
)
from .base import (
    Item,
    paths_filtered_by_status,
)
import re


def property_closure(request, propname, root_uuid):
    # Must avoid cycles
    conn = request.registry[CONNECTION]
    seen = set()
    remaining = {str(root_uuid)}
    while remaining:
        seen.update(remaining)
        next_remaining = set()
        for uuid in remaining:
            obj = conn.get_by_uuid(uuid)
            next_remaining.update(obj.__json__(request).get(propname, ()))
        remaining = next_remaining - seen
    return seen

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
    rev = {}
    embedded = [
        'derived_from',
        'derived_from.biosample_ontology',
        'protocol',
        'dataset',
        'dataset.award',
        'lab'
    ]

    @calculated_property(condition='derived_from', schema={
        "title": "Donor accessions",
        "type": "array",
        "items": {
            "type": "string",
            "linkTo": "Donor"
        },
    })
    def donor_accessions(self, request, registry, derived_from, status):
        conn = registry[CONNECTION]
        derived_from_closure = property_closure(request, 'derived_from', self.uuid)
        obj_props = (conn.get_by_uuid(uuid).__json__(request) for uuid in derived_from_closure)
        # use organism as a proxy for donors because 'Donor in props['@type']' returned keyError
        donor_accs = {
            props['accession']
            for props in obj_props
            if 'organism' in props
        }
        return donor_accs

    @calculated_property(condition='biological_macromolecule_term_name', schema={
        "title": "Nucleic acid term ID",
        "type": "string",
    })
    def biological_macromolecule_term_id(self, request, biological_macromolecule_term_name):
        term_lookup = {
            'DNA': 'SO:0000352',
            'RNA': 'SO:0000356',
            'polyadenylated mRNA': 'SO:0000871',
            'miRNA': 'SO:0000276',
            'protein': 'SO:0000104'
        }
        term_id = None
        if biological_macromolecule_term_name in term_lookup:
            term_id = term_lookup.get(biological_macromolecule_term_name)
        return term_id

    @calculated_property(condition='depleted_in_term_name', schema={
        "title": "Depleted in term ID",
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

