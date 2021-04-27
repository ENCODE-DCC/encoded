from snovault import calculated_property


def pluralize(value, value_units):
    try:
        if float(value) == 1:
            return str(value) + ' ' + value_units
        else:
            return str(value) + ' ' + value_units + 's'
    except:
        return str(value) + ' ' + value_units + 's'


class CalculatedAward:
    @calculated_property(schema={
        "title": "Award",
        "description": "The HCA Seed Network or HCA Pilot Project award used to fund this data generation.",
        "comment": "Do not submit. This is a calculated property.",
        "type": "string",
        "linkTo": "Award"
    })
    def award(self, request, dataset):
        dataset_obj = request.embed(dataset, '@@object?skip_calculated=true')
        return dataset_obj.get('award')


class CalculatedDonors:
    @calculated_property(define=True,
                         schema={"title": "Donors",
                                 "description": "The donors the sample was derived from.",
                                 "comment": "Do not submit. This is a calculated property",
                                 "type": "array",
                                 "items": {
                                    "type": "string",
                                    "linkTo": "Donor"
                                    }
                                })
    def donors(self, request, derived_from):
        all_donors = set()
        for bs in derived_from:
            bs_obj = request.embed(bs, '@@object')
            if 'Donor' in bs_obj.get('@type'):
                all_donors.add(bs_obj.get('@id'))
            else:
                all_donors.update(bs_obj.get('donors'))
        return sorted(all_donors)


class CalculatedBiosampleOntologies:
    @calculated_property(condition='derived_from', define=True, schema={
        "title": "Biosample ontologies",
        "description": "An embedded property for linking to biosample type which describes the ontology of the samples the suspension derived from.",
        "comment": "Do not submit. This is a calculated property",
        "type": "array",
        "items": {
            "type": "string",
            "linkTo": "OntologyTerm"
        },
    })
    def biosample_ontologies(self, request, derived_from):
        onts = set()
        for bs in derived_from:
            bs_obj = request.embed(bs, '@@object')
            if bs_obj.get('biosample_ontologies'):
                onts.update(bs_obj.get('biosample_ontologies'))
            elif bs_obj.get('biosample_ontology'):
                onts.add(bs_obj.get('biosample_ontology'))
        return sorted(onts)


class CalculatedBiosampleClassification:
    @calculated_property(condition='derived_from', define=True, schema={
        "title": "Biosample classification",
        "description": "A property to summarize if the object derived from a tissue, organoid, or cell culture.",
        "comment": "Do not submit. This is a calculated property",
        "type": "array",
        "items": {
            "type": "string"
        },
    })
    def biosample_classification(self, request, derived_from):
        t = set()
        for bs in derived_from:
            bs_obj = request.embed(bs, '@@object')
            if bs_obj.get('biosample_classification'):
                t.update(bs_obj.get('biosample_classification'))
            else:
                bs_type = bs_obj['@type'][0].lower()
                if bs_type == 'cellculture':
                    t.add('cell culture')
                else:
                    t.add(bs_type)
        return sorted(t)


class CalculatedBiosampleSummary:
    @calculated_property(condition='derived_from', define=True, schema={
        "title": "Biosample summary",
        "description": "A property to summarize the biosample that this object derived from.",
        "comment": "Do not submit. This is a calculated property",
        "type": "array",
        "items": {
            "type": "string"
        },
    })
    def biosample_summary(self, request, derived_from):
        summs = set()
        for bs in derived_from:
            bs_obj = request.embed(bs, '@@object')
            if bs_obj.get('biosample_summary'):
                summs.update(bs_obj.get('biosample_summary'))
            elif bs_obj.get('summary'):
                summs.add(bs_obj.get('summary'))
        return sorted(summs)


class CalculatedTreatmentSummary:
    @calculated_property(condition='treatments', schema={
        "title": "Treatment summary",
        "description": "A summary of the treatments applied to the Biosample.",
        "comment": "Do not submit. This is a calculated property",
        "type": "string",
        "notSubmittable": True,
    })
    def treatment_summary(self, request, treatments):
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
