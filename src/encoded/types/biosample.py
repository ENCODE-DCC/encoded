from snovault import (
    abstract_collection,
    calculated_property,
    collection,
    load_schema,
)
from .base import (
    Item,
)
from .shared_calculated_properties import (
    CalculatedDonors,
    CalculatedTreatmentSummary,
)


@abstract_collection(
    name='biosamples',
    unique_key='accession',
    properties={
        'title': 'Biosamples',
        'description': 'Listing of all types of biosample.',
    })
class Biosample(Item, CalculatedDonors, CalculatedTreatmentSummary):
    base_types = ['Biosample'] + Item.base_types
    name_key = 'accession'
    rev = {}
    embedded = [
        'biosample_ontology',
        'diseases',
        'donors',
        'donors.organism',
        'donors.ethnicity',
        'donors.development_ontology',
        'treatments'
    ]

    @calculated_property(schema={
        "title": "Summary",
        "description": "A summary of the treatments applied to the Biosample.",
        "comment": "Do not submit. This is a calculated property",
        "type": "string",
        "notSubmittable": True,
    })
    def summary(self, request, biosample_ontology, derived_from, genetic_modifications=None):
        summ = []
        my_type = self.item_type.replace('_',' ')
        if my_type == 'organoid':
            dfrom = set()
            for df in derived_from:
                obj = request.embed(df, '@@object?skip_calculated=true')
                ontology = obj.get('biosample_ontology')
                ontology_obj = request.embed(ontology, '@@object?skip_calculated=true')
                name = ontology_obj.get('term_name')
                if obj.get('genetic_modifications'):
                    gms = ','.join(obj.get('genetic_modifications'))
                    name += ' ({})'.format(gms)
                dfrom.add(name)
            summ.append(','.join(dfrom) + '-derived')
        bo_obj = request.embed(biosample_ontology, '@@object?skip_calculated=true')
        summ.append(bo_obj.get('term_name'))
        if genetic_modifications:
            gms = ','.join(genetic_modifications)
            summ.append('({})'.format(gms))
        summ.append(my_type)

        return ' '.join(summ)


@abstract_collection(
    name='cultures',
    unique_key='accession',
    properties={
        'title': 'Cultures',
        'description': 'Listing of all types of culture.',
    })
class Culture(Biosample):
    item_type = 'analysis_file'
    base_types = ['Culture'] + Biosample.base_types
    schema = load_schema('encoded:schemas/culture.json')
    embedded = Biosample.embedded + []


@collection(
    name='cell-cultures',
    unique_key='accession',
    properties={
        'title': 'Cell cultures',
        'description': 'Listing of Cell cultures',
    })
class CellCulture(Culture):
    item_type = 'cell_culture'
    schema = load_schema('encoded:schemas/cell_culture.json')
    embedded = Culture.embedded + []


@collection(
    name='organoids',
    unique_key='accession',
    properties={
        'title': 'Organoids',
        'description': 'Listing of Organoids',
    })
class Organoid(Culture):
    item_type = 'organoid'
    schema = load_schema('encoded:schemas/organoid.json')
    embedded = Culture.embedded + []


@collection(
    name='tissues',
    unique_key='accession',
    properties={
        'title': 'Tissues',
        'description': 'Listing of Tissues',
    })
class Tissue(Biosample):
    item_type = 'tissue'
    schema = load_schema('encoded:schemas/tissue.json')
    embedded = Biosample.embedded + []
