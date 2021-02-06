from snovault import calculated_property


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
