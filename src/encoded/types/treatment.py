from snovault import (
    calculated_property,
    collection,
    load_schema,
)
from .base import (
    Item,
)


def pluralize(value, value_units):
    try:
        if float(value) == 1:
            return str(value) + ' ' + value_units
        else:
            return str(value) + ' ' + value_units + 's'
    except:
        return str(value) + ' ' + value_units + 's'


@collection(
    name='treatments',
    properties={
        'title': 'Treatments',
        'description': 'Listing Biosample Treatments',
    })
class Treatment(Item):
    item_type = 'treatment'
    schema = load_schema('encoded:schemas/treatment.json')


    @calculated_property(schema={
        "title": "Summary",
        "description": "A summary of the treatment.",
        "comment": "Do not submit. This is a calculated property",
        "type": "string",
        "notSubmittable": True,
    })
    def summary(self, request, treatment_term_name, duration=None, duration_units=None,
            amount=None, amount_units=None, temperature=None, temperature_units=None):
        summ = []
        if amount:
            a = str(amount)
            if a.endswith('.0'):
                a = a[:-2]
            amt = '{} {} of'.format(a, amount_units)
            summ.append(amt)
        summ.append(treatment_term_name)
        if duration:
            d = str(duration)
            if d.endswith('.0'):
                d = d[:-2]
            dur = 'for {}'.format(pluralize(d, duration_units))
            summ.append(dur)
        if temperature:
            t = str(temperature)
            if t.endswith('.0'):
                t = t[:-2]
            temp = 'at {} {}'.format(t, temperature_units)
            summ.append(temp)
        return ' '.join(summ)
