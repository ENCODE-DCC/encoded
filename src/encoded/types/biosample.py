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
)


def pluralize(value, value_units):
    try:
        if float(value) == 1:
            return str(value) + ' ' + value_units
        else:
            return str(value) + ' ' + value_units + 's'
    except:
        return str(value) + ' ' + value_units + 's'


@abstract_collection(
    name='biosamples',
    unique_key='accession',
    properties={
        'title': 'Biosamples',
        'description': 'Listing of all types of biosample.',
    })
class Biosample(Item, CalculatedDonors):
    base_types = ['Biosample'] + Item.base_types
    name_key = 'accession'
    rev = {}
    embedded = [
        'biosample_ontology',
        'diseases',
        'donors',
        'donors.organism',
        'donors.ethnicity',
        'treatments'
    ]

    @calculated_property(schema={
        "title": "Treatment summary",
        "description": "A summary of the treatments applied to the Biosample.",
        "comment": "Do not submit. This is a calculated property",
        "type": "string",
        "notSubmittable": True,
    })
    def treatment_summary(self, request, treatments=None):
        if treatments:
            dur_dict = {}
            for t in treatments:
                t_obj = request.embed(t, '@@object?skip_calculated=true')
                summ = ''
                if t_obj.get('amount'):
                    amt = str(t_obj['amount'])
                    if amt.endswith('.0'):
                        amt = amt[:-2]
                    a_units = t_obj['amount_units']
                    summ += (amt + ' ' + a_units + ' of ')
                summ += (t_obj.get('treatment_term_name'))

                if t_obj.get('duration'):
                    d = str(t_obj['duration'])
                    if d.endswith('.0'):
                        d = d[:-2]
                    dur = pluralize(d, t_obj['duration_units'])
                else:
                    dur = 'none'

                if dur_dict.get(dur):
                    if t_obj.get('amount'):
                        dur_dict[dur].append(summ)
                    else:
                        dur_dict[dur].insert(0, summ)
                else:
                    dur_dict[dur] = [summ]

            ovr = []
            for k,v in dur_dict.items():
                temp = (' and '.join(v))
                if k != 'none':
                    temp += (' for ' + k)
                ovr.append(temp)
            return ('; '.join(ovr))


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
