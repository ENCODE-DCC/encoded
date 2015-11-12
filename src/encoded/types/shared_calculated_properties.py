from contentbase import (
    calculated_property
)

from .base import (
    paths_filtered_by_status,
)


class CalculatedBiosampleSlims:
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


class CalculatedBiosampleSynonyms:
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


class CalculatedAssaySynonyms:
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


class CalculatedFileSetAssayTerm:
    @calculated_property(schema={
        "title": "Assay term name",
        "type": "array",
        "items": {
            "type": ['string'],
        },
    })
    def assay_term_name(self, request, related_files):
        assays = []
        if related_files:
            for path in related_files:
                related_file = request.embed(path, '@@object')
                dataset = request.embed(related_file['dataset'], '@@object')
                if 'assay_term_name' in dataset:
                    assays.append(dataset['assay_term_name'])
            return list(set(assays))
        return []


class CalculatedFileSetAssayId:
    @calculated_property(schema={
        "title": "Assay term id",
        "type": "array",
        "items": {
            "type": ['string'],
        },
    })
    def assay_term_id(self, request, related_files):
        assays = []
        if related_files:
            for path in related_files:
                related_file = request.embed(path, '@@object')
                dataset = request.embed(related_file['dataset'], '@@object')
                if 'assay_term_id' in dataset:
                    assays.append(dataset['assay_term_id'])
            return list(set(assays))
        return []


class CalculatedFileSetAssaySynonyms:
    @calculated_property(condition='assay_term_id', schema={
        "title": "Assay synonyms",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def assay_synonyms(self, registry, assay_term_id):
        if assay_term_id:
            for term_id in assay_term_id:
                if term_id in registry['ontology']:
                    return registry['ontology'][assay_term_id]['synonyms'] + [
                        registry['ontology'][assay_term_id]['name'],
                    ]
                return []


class CalculatedFileSetOrganism:
    @calculated_property(schema={
        "title": "Organism",
        "type": "array",
        "items": {
            "type": ['string', 'object'],
            "linkTo": "Organism"
        },
    })
    def organism(self, request, related_files):
        organisms = []
        if related_files:
            for path in related_files:
                related_file = request.embed(path, '@@object')
                dataset = request.embed(related_file['dataset'], '@@object')
                if 'replicate' in dataset:
                    rep = request.embed(related_file['replicate'], '@@object')
                    if 'library' in rep:
                        lib = request.embed(rep['library'], '@@object')
                        if 'biosample' in lib:
                            bio = request.embed(lib['biosample'], '@@object')
                            if 'organism' in bio:
                                organisms.append(bio['organism'])
            if organisms:
                return paths_filtered_by_status(request, list(set(organisms)))


class CalculatedSeriesAssay:
    @calculated_property(schema={
        "title": "Assay term name",
        "type": "array",
        "items": {
            "type": ['string'],
        },
    })
    def assay_term_name(self, request, related_datasets):
        assays = []
        if related_datasets:
            for path in related_datasets:
                properties = request.embed(path, '@@object')
                if 'assay_term_name' in properties:
                    assays.append(properties['assay_term_name'])
            return list(set(assays))
        return []


class CalculatedSeriesBiosample:
    @calculated_property(schema={
        "title": "Biosample term name",
        "type": "array",
        "items": {
            "type": ['string'],
        },
    })
    def biosample_term_name(self, request, related_datasets):
        biosamples = []
        if related_datasets:
            for path in related_datasets:
                properties = request.embed(path, '@@object')
                if 'biosample_term_name' in properties:
                    biosamples.append(properties['biosample_term_name'])
            return list(set(biosamples))
        return []

    @calculated_property(schema={
        "title": "Biosample type",
        "type": "array",
        "items": {
            "type": ['string'],
        },
    })
    def biosample_type(self, request, related_datasets):
        biosample_types = []
        if related_datasets:
            for path in related_datasets:
                properties = request.embed(path, '@@object')
                if 'biosample_type' in properties:
                    biosample_types.append(properties['biosample_type'])
            return list(set(biosample_types))
        return []

    @calculated_property(schema={
        "title": "Organism",
        "type": "array",
        "items": {
            "type": ['string', 'object'],
            "linkTo": "Organism"
        },
    })
    def organism(self, request, related_datasets):
        organisms = []
        if related_datasets:
            for path in related_datasets:
                dataset = request.embed(path, '@@object')
                if 'replicates' in dataset:
                    for rep_path in dataset['replicates']:
                        rep = request.embed(rep_path, '@@object')
                        if 'library' in rep:
                            lib = request.embed(rep['library'], '@@object')
                            if 'biosample' in lib:
                                bio = request.embed(lib['biosample'], '@@object')
                                if 'organism' in bio:
                                    organisms.append(bio['organism'])
            if organisms:
                return paths_filtered_by_status(request, list(set(organisms)))
        return []


class CalculatedSeriesTreatment:
    @calculated_property(schema={
        "title": "Treatment term name",
        "type": "array",
        "items": {
            "type": ['string'],
        },
    })
    def treatment_term_name(self, request, related_datasets):
        treatments = []
        if related_datasets:
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
        return []

    @calculated_property(schema={
        "title": "Treatment type",
        "type": "array",
        "items": {
            "type": ['string'],
        },
    })
    def treatment_type(self, request, related_datasets):
        treatment_types = []
        if related_datasets:
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
        return []


class CalculatedSeriesTarget:
    @calculated_property(schema={
        "title": "Targets",
        "type": "array",
        "items": {
            "type": ['string', 'object'],
            "linkTo": "Target",
        },
    })
    def targets(self, request, related_datasets):
        targets = []
        if related_datasets:
            for path in related_datasets:
                properties = request.embed(path, '@@object')
                if 'target' in properties:
                    targets.append(properties['target'])

            if targets:
                return paths_filtered_by_status(request, list(set(targets)))
        return []


class CalculatedSeriesAge:
    @calculated_property(define=True, schema={
        "title": "Age",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def age(self, request, related_datasets):
        ages = []
        if related_datasets:
            for path in related_datasets:
                dataset = request.embed(path, '@@object')
                if 'replicates' in dataset:
                    for rep_path in dataset['replicates']:
                        rep = request.embed(rep_path, '@@object')
                        if 'library' in rep:
                            lib = request.embed(rep['library'], '@@object')
                            if 'biosample' in lib:
                                bio = request.embed(lib['biosample'], '@@object')
                                if 'age' in bio:
                                    ages.append(bio['age'])
            return ages
        return []

    @calculated_property(define=True, schema={
        "title": "Age units",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def age_units(self, request, related_datasets):
        age_units = []
        if related_datasets:
            for path in related_datasets:
                dataset = request.embed(path, '@@object')
                if 'replicates' in dataset:
                    for rep_path in dataset['replicates']:
                        rep = request.embed(rep_path, '@@object')
                        if 'library' in rep:
                            lib = request.embed(rep['library'], '@@object')
                            if 'biosample' in lib:
                                bio = request.embed(lib['biosample'], '@@object')
                                if 'age_units' in bio:
                                    age_units.append(bio['age'])
            return age_units
        return []

    @calculated_property(schema={
        "title": "Age display",
        "type": "string",
    })
    def age_display(self, request, age, age_units):
        age_display = []
        if (len(age) == len(age_units)) and (len(age) > 0):
            for idx, elem in enumerate(age):
                age_display.append(u'{age} {age units'.format(age=age[idx], age_units=age_units[idx]))
            return age_display
        return None


class CalculatedSeriesLifeStage:
    @calculated_property(define=True, schema={
        "title": "Life stage",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def life_stages(self, request, related_datasets):
        stages = []
        if related_datasets:
            for path in related_datasets:
                dataset = request.embed(path, '@@object')
                if 'replicates' in dataset:
                    for rep_path in dataset['replicates']:
                        rep = request.embed(rep_path, '@@object')
                        if 'library' in rep:
                            lib = request.embed(rep['library'], '@@object')
                            if 'biosample' in lib:
                                bio = request.embed(lib['biosample'], '@@object')
                                if 'life_stage' in bio:
                                    stages.append(bio['life_stage'])
            return stages
        return []


class CalculatedSeriesSynchronization:
    @calculated_property(define=True, schema={
        "title": "Synchronization stage",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def synchronization(self, request, related_datasets):
        syncs = []
        if related_datasets:
            for path in related_datasets:
                dataset = request.embed(path, '@@object')
                if 'replicates' in dataset:
                    for rep_path in dataset['replicates']:
                        rep = request.embed(rep_path, '@@object')
                        if 'library' in rep:
                            lib = request.embed(rep['library'], '@@object')
                            if 'biosample' in lib:
                                bio = request.embed(lib['biosample'], '@@object')
                                if 'synchronization' in bio:
                                    syncs.append(bio['synchronization'])
            return syncs
        return []

    @calculated_property(define=True, schema={
        "title": "Post-synchronization time",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def post_synchronization_time(self, request, related_datasets):
        times = []
        if related_datasets:
            for path in related_datasets:
                dataset = request.embed(path, '@@object')
                if 'replicates' in dataset:
                    for rep_path in dataset['replicates']:
                        rep = request.embed(rep_path, '@@object')
                        if 'library' in rep:
                            lib = request.embed(rep['library'], '@@object')
                            if 'biosample' in lib:
                                bio = request.embed(lib['biosample'], '@@object')
                                if 'post_synchronization_time' in bio:
                                    times.append(bio['post_synchronization_time'])
            return times
        return []

    @calculated_property(define=True, schema={
        "title": "Post-synchronization time units",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def post_synchronization_time_units(self, request, related_datasets):
        time_units = []
        if related_datasets:
            for path in related_datasets:
                dataset = request.embed(path, '@@object')
                if 'replicates' in dataset:
                    for rep_path in dataset['replicates']:
                        rep = request.embed(rep_path, '@@object')
                        if 'library' in rep:
                            lib = request.embed(rep['library'], '@@object')
                            if 'biosample' in lib:
                                bio = request.embed(lib['biosample'], '@@object')
                                if 'post_synchronization_time_units' in bio:
                                    time_units.append(bio['post_synchronization_time_units'])
            return time_units
        return []

    @calculated_property(schema={
        "title": "Synchronization display",
        "type": "string",
    })
    def synchronization_display(self, request, synchronization, post_synchronization_time, post_synchronization_time_units):
        sync_display = []
        if (len(post_synchronization_time) == len(post_synchronization_time_units)) and (len(post_synchronization_time) > 0):
            if synchronization:
                for idx, elem in enumerate(post_synchronization_time):
                    sync_display.append(u'{sync} + {post_sync_time} {post_sync_units}'.format(sync=synchronization[idx], post_sync_time=post_synchronization_time[idx], post_sync_units=post_synchronization_time_units[idx]))
                return sync_display
        return None
