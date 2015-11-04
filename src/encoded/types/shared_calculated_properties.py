from contentbase import (
    calculated_property
)

from .base import (
    paths_filtered_by_status,
)


class CalculatedSlims:

    @calculated_property(condition='biosample_term_id', schema={
        "title": "Organ slims",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def organ_slims(self, registry, biosample_term_id):
        if biosample_term_id in registry['ontology']:
            return registry['ontology'][biosample_term_id]['organs']
        return []

    @calculated_property(condition='biosample_term_id', schema={
        "title": "System slims",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def system_slims(self, registry, biosample_term_id):
        if biosample_term_id in registry['ontology']:
            return registry['ontology'][biosample_term_id]['systems']
        return []

    @calculated_property(condition='biosample_term_id', schema={
        "title": "Developmental slims",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def developmental_slims(self, registry, biosample_term_id):
        if biosample_term_id in registry['ontology']:
            return registry['ontology'][biosample_term_id]['developmental']
        return []


class CalculatedSynonyms:

    @calculated_property(condition='biosample_term_id', schema={
        "title": "Biosample synonyms",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def biosample_synonyms(self, registry, biosample_term_id):
        if biosample_term_id in registry['ontology']:
            return registry['ontology'][biosample_term_id]['synonyms']
        return []

    @calculated_property(condition='assay_term_id', schema={
        "title": "Assay synonyms",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def assay_synonyms(self, registry, assay_term_id):
        if assay_term_id in registry['ontology']:
            return registry['ontology'][assay_term_id]['synonyms'] + [
                registry['ontology'][assay_term_id]['name'],
            ]
        return []


class CalculatedAssay:

    @calculated_property(schema={
        "title": "assay_term_name",
        "type": "array",
        "items": {
            "type": ['string'],
        },
    })
    def assay_term_name(self, request, related_datasets):
        assays = []
        for path in related_datasets:
            properties = request.embed(path, '@@object')
            if 'assay_term_name' in properties:
                assays.append(properties['assay_term_name'])
        return list(set(assays))


class CalculatedBiosample:

    @calculated_property(schema={
        "title": "biosample_term_name",
        "type": "array",
        "items": {
            "type": ['string'],
        },
    })
    def biosample_term_name(self, request, related_datasets):
        biosamples = []
        for path in related_datasets:
            properties = request.embed(path, '@@object')
            if 'biosample_term_name' in properties:
                biosamples.append(properties['biosample_term_name'])
        return list(set(biosamples))

    @calculated_property(schema={
        "title": "biosample_type",
        "type": "array",
        "items": {
            "type": ['string'],
        },
    })
    def biosample_type(self, request, related_datasets):
        biosample_types = []
        for path in related_datasets:
            properties = request.embed(path, '@@object')
            if 'biosample_type' in properties:
                biosample_types.append(properties['biosample_type'])
        return list(set(biosample_types))


class CalculatedTreatment:

    @calculated_property(schema={
        "title": "treatment_term_name",
        "type": "array",
        "items": {
            "type": ['string'],
        },
    })
    def treatment_term_name(self, request, related_datasets):
        treatments = []
        for path in related_datasets:
            dataset = request.embed(path, '@@object')
            if 'replicates' in dataset:
                for rep_path in dataset['replicates']:
                    rep = request.embed(rep_path, '@@object')
                    if 'library' in rep:
                        lib = request.embed(rep['library'], '@@object')
                        if 'biosample' in lib:
                            bio = request.embed(lib['biosample'], '@@object')
                            if 'treatments' in bio:
                                for treat_path in bio['treatments']:
                                    treatment = request.embed(treat_path, '@@object')
                                    if 'treatment_term_name' in treatment:
                                        treatments.append(treatment['treatment_term_name'])
        return list(set(treatments))

    @calculated_property(schema={
        "title": "treatment_type",
        "type": "array",
        "items": {
            "type": ['string'],
        },
    })
    def treatment_type(self, request, related_datasets):
        treatment_types = []
        for path in related_datasets:
            dataset = request.embed(path, '@@object')
            if 'replicates' in dataset:
                for rep_path in dataset['replicates']:
                    rep = request.embed(rep_path, '@@object')
                    if 'library' in rep:
                        lib = request.embed(rep['library'], '@@object')
                        if 'biosample' in lib:
                            bio = request.embed(lib['biosample'], '@@object')
                            if 'treatments' in bio:
                                for treat_path in bio['treatments']:
                                    treatment = request.embed(treat_path, '@@object')
                                    if 'treatment_type' in treatment:
                                        treatment_types.append(treatment['treatment_type'])
        return list(set(treatment_types))


class CalculatedTarget:

    @calculated_property(schema={
        "title": "targets",
        "type": "array",
        "items": {
            "type": ['string', 'object'],
            "linkTo": "Target",
        },
    })
    def targets(self, request, related_datasets):
        targets = []
        for path in related_datasets:
            properties = request.embed(path, '@@object')
            if 'target' in properties:
                targets.append(properties['target'])

            if targets:
                return paths_filtered_by_status(request, targets, include=('current', 'proposed'),)
