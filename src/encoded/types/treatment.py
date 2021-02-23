from snovault import (
    calculated_property,
    collection,
    load_schema,
)
from .base import (
    Item,
)


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
            amt = '{} {} of'.format(amount, amount_units)
            summ.append(amt)
        summ.append(treatment_term_name)
        if duration:
            dur = 'for {} {}'.format(duration, duration_units)
            summ.append(dur)
        if temperature:
            temp = 'at {} {}'.format(temperature, temperature_units)
            summ.append(temp)
        return ' '.join(summ)
