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


class CalculatedFileSetBiosample:
    @calculated_property(define=True, condition='files', schema={
        "title": "Biosample term name",
        "type": "array",
        "items": {
            "type": 'string',
        },
    })
    def biosample_term_name(self, request, files):
        biosamples = []
        for idx, path in enumerate(files):
            # Need to cap this due to the large numbers of files in related_files
            if idx < 100:
                f = request.embed(path, '@@object')
                if 'replicate' in f:
                    rep = request.embed(f['replicate'], '@@object')
                    if 'experiment' in rep:
                        expt = request.embed(rep['experiment'], '@@object')
                        if 'biosample_term_name' in expt:
                            biosamples.append(expt['biosample_term_name'])
        return list(set(biosamples))

    @calculated_property(define=True, condition='files', schema={
        "title": "Biosample type",
        "type": "array",
        "items": {
            "type": 'string',
        },
    })
    def biosample_type(self, request, files):
        biosamples = []
        for idx, path in enumerate(files):
            # Need to cap this due to the large numbers of files in related_files
            if idx < 100:
                f = request.embed(path, '@@object')
                if 'replicate' in f:
                    rep = request.embed(f['replicate'], '@@object')
                    if 'experiment' in rep:
                        expt = request.embed(rep['experiment'], '@@object')
                        if 'biosample_type' in expt:
                            biosamples.append(expt['biosample_type'])
        return list(set(biosamples))

    @calculated_property(condition='files', schema={
        "title": "Organism",
        "type": "array",
        "items": {
            "type": 'string',
            "linkTo": "Organism"
        },
    })
    def organism(self, request, files):
        organisms = []
        if files:
            for idx, path in enumerate(files):
                # Need to cap this due to the large numbers of files in related_files
                if idx < 100:
                    f = request.embed(path, '@@object')
                    if 'replicate' in f:
                        rep = request.embed(f['replicate'], '@@object')
                        if 'library' in rep:
                            lib = request.embed(rep['library'], '@@object')
                            if 'biosample' in lib:
                                bio = request.embed(lib['biosample'], '@@object')
                                if 'organism' in bio:
                                    organisms.append(bio['organism'])
            if organisms:
                return paths_filtered_by_status(request, list(set(organisms)))
            else:
                return organisms


class CalculatedFileSetAssay:
    @calculated_property(condition='files', schema={
        "title": "Assay term name",
        "type": "array",
        "items": {
            "type": 'string',
        },
    })
    def assay_term_name(self, request, files):
        assays = []
        for idx, path in enumerate(files):
            # Need to cap this due to the large numbers of files in related_files
            if idx < 100:
                f = request.embed(path, '@@object')
                if 'replicate' in f:
                    rep = request.embed(f['replicate'], '@@object')
                    if 'experiment' in rep:
                        expt = request.embed(rep['experiment'])
                        if 'assay_term_name' in expt:
                            assays.append(expt['assay_term_name'])
        return list(set(assays))


class CalculatedSeriesAssay:
    @calculated_property(condition='related_datasets', schema={
        "title": "Assay term name",
        "type": "array",
        "items": {
            "type": 'string',
        },
    })
    def assay_term_name(self, request, related_datasets):
        assays = []
        for path in related_datasets:
            properties = request.embed(path, '@@object')
            if 'assay_term_name' in properties:
                assays.append(properties['assay_term_name'])
        if assays:
            return list(set(assays))
        else:
            return assays


class CalculatedSeriesBiosample:
    @calculated_property(condition='related_datasets', schema={
        "title": "Biosample term name",
        "type": "array",
        "items": {
            "type": 'string',
        },
    })
    def biosample_term_name(self, request, related_datasets):
        biosamples = []
        for path in related_datasets:
            properties = request.embed(path, '@@object')
            if 'biosample_term_name' in properties:
                biosamples.append(properties['biosample_term_name'])
        if biosamples:
            return list(set(biosamples))
        else:
            return biosamples

    @calculated_property(condition='related_datasets', schema={
        "title": "Biosample type",
        "type": "array",
        "items": {
            "type": 'string',
        },
    })
    def biosample_type(self, request, related_datasets):
        biosample_types = []
        for path in related_datasets:
            properties = request.embed(path, '@@object')
            if 'biosample_type' in properties:
                biosample_types.append(properties['biosample_type'])
        if biosample_types:
            return list(set(biosample_types))
        else:
            return biosample_types


    @calculated_property(condition='related_datasets', schema={
        "title": "Organism",
        "type": "array",
        "items": {
            "type": 'string',
            "linkTo": "Organism"
        },
    })
    def organism(self, request, related_datasets):
        organisms = []
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
        else:
            return organisms


class CalculatedSeriesTreatment:
    @calculated_property(condition='related_datasets', schema={
        "title": "Treatment term name",
        "type": "array",
        "items": {
            "type": 'string',
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

    @calculated_property(condition='related_datasets', schema={
        "title": "Treatment type",
        "type": "array",
        "items": {
            "type": 'string',
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
    @calculated_property(condition='related_datasets', schema={
        "title": "Target",
        "type": "array",
        "items": {
            "type": 'string',
            "linkTo": "Target",
        },
    })
    def target(self, request, related_datasets):
        targets = []
        if related_datasets:
            for path in related_datasets:
                properties = request.embed(path, '@@object')
                if 'target' in properties:
                    targets.append(properties['target'])

            if targets:
                return paths_filtered_by_status(request, list(set(targets)))
        return []
