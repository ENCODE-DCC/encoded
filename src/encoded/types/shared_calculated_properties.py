from snovault import calculated_property
from snovault.util import ensurelist
from .assay_data import assay_terms
from urllib.parse import urljoin
from ..vis_defines import (
    vis_format_url,
    browsers_available
    )
from .biosample import (
    construct_biosample_summary,
    generate_summary_dictionary
)
from .base import (
    paths_filtered_by_status
)


class CalculatedAssaySynonyms:
    @calculated_property(condition='assay_term_id', schema={
        "title": "Assay synonyms",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def assay_synonyms(self, registry, assay_term_id):
        assay_term_id = ensurelist(assay_term_id)
        syns = set()
        for term_id in assay_term_id:
            if term_id in registry['ontology']:
                syns.update(registry['ontology'][term_id]['synonyms'] + [
                    registry['ontology'][term_id]['name'],
                ])
        return list(syns)


class CalculatedFileSetBiosample:
    @calculated_property(condition='related_files', schema={
        "title": "Biosample ontology",
        "type": "array",
        "items": {
            "type": 'string',
            "linkTo": "BiosampleType"
        },
    })
    def biosample_ontology(self, request, related_files):
        return request.select_distinct_values(
            'dataset.biosample_ontology', *related_files)

    @calculated_property(condition='related_files', schema={
        "title": "Organism",
        "type": "array",
        "items": {
            "type": 'string',
            "linkTo": "Organism"
        },
    })
    def organism(self, request, related_files):
        return request.select_distinct_values(
            'library.biosample.organism', *related_files)


class CalculatedFileSetAssay:
    @calculated_property(define=True, condition='related_files', schema={
        "title": "Assay name",
        "type": "array",
        "items": {
            "type": 'string',
        },
    })
    def assay_term_name(self, request, related_files):
        return request.select_distinct_values(
            'dataset.assay_term_name', *related_files)

    @calculated_property(define=True, condition='assay_term_name', schema={
        "title": "Assay term ID",
        "type": "array",
        "items": {
            "type": 'string',
        },
    })
    def assay_term_id(self, request, assay_term_name):
        return [
            assay_terms.get(x)
            for x in assay_term_name
            if assay_terms.get(x)
        ]


class CalculatedSeriesAssay:
    @calculated_property(condition='related_datasets', schema={
        "title": "Assay name",
        "type": "array",
        "items": {
            "type": 'string',
        },
    })
    def assay_term_name(self, request, related_datasets):
        return request.select_distinct_values(
            'assay_term_name', *related_datasets)

    @calculated_property(define=True, condition='related_datasets', schema={
        "title": "Assay term ID",
        "type": "array",
        "items": {
            "type": 'string',
        },
    })
    def assay_term_id(self, request, related_datasets):
        return request.select_distinct_values(
            'assay_term_id', *related_datasets)


class CalculatedSeriesBiosample:
    @calculated_property(condition='related_datasets', schema={
        "title": "Biosample ontology",
        "type": "array",
        "items": {
            "type": 'string',
            "linkTo": "BiosampleType"
        },
    })
    def biosample_ontology(self, request, related_datasets):
        return request.select_distinct_values(
            'biosample_ontology', *related_datasets)

    @calculated_property(condition='related_datasets', schema={
        "title": "Organism",
        "type": "array",
        "items": {
            "type": 'string',
            "linkTo": "Organism"
        },
    })
    def organism(self, request, related_datasets):
        return request.select_distinct_values(
            'replicates.libraries.biosample.organism', *related_datasets)


class CalculatedSeriesTreatment:
    @calculated_property(condition='related_datasets', schema={
        "title": "Biosample treatment",
        "type": "array",
        "items": {
            "type": 'string',
        },
    })
    def treatment_term_name(self, request, related_datasets):
        return request.select_distinct_values(
            'replicates.libraries.biosample.treatments.treatment_term_name',
            *related_datasets)


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
        return request.select_distinct_values('target', *related_datasets)


class CalculatedAssayTermID:
    @calculated_property(condition='assay_term_name', schema={
        "title": "Assay term ID",
        "description": "OBI (Ontology for Biomedical Investigations) ontology identifier for the assay.",
        "type": "string",
        "comment": "Calculated based on the choice of assay_term_name"
    })
    def assay_term_id(self, request, assay_term_name):
        term_id = None
        if assay_term_name in assay_terms:
            term_id = assay_terms.get(assay_term_name)
        return term_id


class CalculatedVisualize:
    @calculated_property(condition='hub', category='page', schema={
        "title": "Visualize Data",
        "type": "string",
    })
    def visualize(self, request, hub, accession, assembly, status, files):
        hub_url = urljoin(request.resource_url(request.root), hub)
        viz = {}
        vis_assembly = set()
        viewable_file_formats = ['bigWig', 'bigBed', 'hic']
        viewable_file_status = ['released', 'in progress']
        vis_assembly = {
            properties['assembly']
            for properties in files
            if properties.get('file_format') in viewable_file_formats
            if properties.get('status') in viewable_file_status
            if 'assembly' in properties
        }
        for assembly_name in vis_assembly:
            if assembly_name in viz:
                continue
            browsers = browsers_available(status, [assembly_name],
                                          self.base_types, self.item_type,
                                          files, accession, request)
            if len(browsers) > 0:
                viz[assembly_name] = browsers
        if viz:
            return viz
        else:
            return None


class CalculatedBiosampleSummary:
    @calculated_property(schema={
        "title": "Biosample summary",
        "type": "string",
    })
    def biosample_summary(self,
                          request,
                          replicates=None):
        drop_age_sex_flag = False
        dictionaries_of_phrases = []
        biosample_accessions = set()
        if replicates is not None:
            for rep in replicates:
                replicateObject = request.embed(rep, '@@object')
                if replicateObject['status'] == 'deleted':
                    continue
                if 'library' in replicateObject:
                    libraryObject = request.embed(replicateObject['library'], '@@object')
                    if libraryObject['status'] == 'deleted':
                        continue
                    if 'biosample' in libraryObject:
                        biosampleObject = request.embed(libraryObject['biosample'], '@@object')
                        if biosampleObject['status'] == 'deleted':
                            continue
                        if biosampleObject['accession'] not in biosample_accessions:
                            biosample_accessions.add(biosampleObject['accession'])

                            biosampleTypeObject = request.embed(
                                biosampleObject['biosample_ontology'],
                                '@@object'
                            )
                            if biosampleTypeObject.get('classification') in [
                                    'in vitro differentiated cells']:
                                drop_age_sex_flag = True

                            organismObject = None
                            if 'organism' in biosampleObject:
                                organismObject = request.embed(biosampleObject['organism'],
                                                               '@@object')
                            donorObject = None
                            if 'donor' in biosampleObject:
                                donorObject = request.embed(biosampleObject['donor'], '@@object')

                            treatment_objects_list = None
                            treatments = biosampleObject.get('treatments')
                            if treatments is not None and len(treatments) > 0:
                                treatment_objects_list = []
                                for t in treatments:
                                    treatment_objects_list.append(request.embed(t, '@@object'))

                            part_of_object = None
                            if 'part_of' in biosampleObject:
                                part_of_object = request.embed(biosampleObject['part_of'],
                                                               '@@object')
                            originated_from_object = None
                            if 'originated_from' in biosampleObject:
                                originated_from_object = request.embed(biosampleObject['originated_from'],
                                                                       '@@object')

                            modifications_list = None
                            genetic_modifications = biosampleObject.get('applied_modifications')
                            if genetic_modifications:
                                modifications_list = []
                                for gm in genetic_modifications:
                                    gm_object = request.embed(gm, '@@object')
                                    modification_dict = {'category': gm_object.get('category')}
                                    if gm_object.get('modified_site_by_target_id'):
                                        modification_dict['target'] = request.embed(
                                            gm_object.get('modified_site_by_target_id'),
                                                          '@@object')['label']
                                    if gm_object.get('introduced_tags_array'):
                                        modification_dict['tags'] = []
                                        for tag in gm_object.get('introduced_tags_array'):
                                            tag_dict = {'location': tag['location']}
                                            if tag.get('promoter_used'):
                                                tag_dict['promoter'] = request.embed(
                                                    tag.get('promoter_used'),
                                                            '@@object').get['label']
                                            modification_dict['tags'].append(tag_dict)

                                    modifications_list.append((gm_object['method'], modification_dict))

                            preservation_method = None
                            dictionary_to_add = generate_summary_dictionary(
                                request,
                                organismObject,
                                donorObject,
                                biosampleObject.get('age'),
                                biosampleObject.get('age_units'),
                                biosampleObject.get('life_stage'),
                                biosampleObject.get('sex'),
                                biosampleTypeObject.get('term_name'),
                                biosampleTypeObject.get('classification'),
                                biosampleObject.get('starting_amount'),
                                biosampleObject.get('starting_amount_units'),
                                biosampleObject.get('depleted_in_term_name'),
                                biosampleObject.get('phase'),
                                biosampleObject.get('subcellular_fraction_term_name'),
                                biosampleObject.get('synchronization'),
                                biosampleObject.get('post_synchronization_time'),
                                biosampleObject.get('post_synchronization_time_units'),
                                biosampleObject.get('post_treatment_time'),
                                biosampleObject.get('post_treatment_time_units'),
                                treatment_objects_list,
                                preservation_method,
                                part_of_object,
                                originated_from_object,
                                modifications_list,
                                True)

                            dictionaries_of_phrases.append(dictionary_to_add)

        if drop_age_sex_flag is True:
            sentence_parts = [
                'strain_background',
                'experiment_term_phrase',
                'phase',
                'fractionated',
                'synchronization',
                'modifications_list',
                'originated_from',
                'treatments_phrase',
                'depleted_in'
            ]
        else:
            sentence_parts = [
                'strain_background',
                'experiment_term_phrase',
                'phase',
                'fractionated',
                'sex_stage_age',
                'synchronization',
                'modifications_list',
                'originated_from',
                'treatments_phrase',
                'depleted_in'
            ]
        if len(dictionaries_of_phrases) > 0:
            return construct_biosample_summary(dictionaries_of_phrases, sentence_parts)


class CalculatedReplicates:
    @calculated_property(schema={
        "title": "Replicates",
        "type": "array",
        "items": {
            "type": ['string', 'object'],
            "linkFrom": "Replicate.experiment",
        },
    })
    def replicates(self, request, replicates):
        return paths_filtered_by_status(request, replicates)


class CalculatedAssaySlims:
    @calculated_property(condition='assay_term_name', schema={
        "title": "Assay type",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def assay_slims(self, registry, assay_term_name):
        assay_term_id = assay_terms.get(assay_term_name, None)
        if assay_term_id in registry['ontology']:
            return registry['ontology'][assay_term_id]['assay']
        return []


class CalculatedAssayTitle:
    @calculated_property(condition='assay_term_name', schema={
        "title": "Assay title",
        "type": "string",
    })
    def assay_title(self, request, registry, assay_term_name,
                    replicates=None, target=None):
        # This is the preferred name in generate_ontology.py if exists
        assay_term_id = assay_terms.get(assay_term_name, None)
        if assay_term_id in registry['ontology']:
            preferred_name = registry['ontology'][assay_term_id].get('preferred_name',
                                                                     assay_term_name)
            if preferred_name == 'RNA-seq' and replicates is not None:
                for rep in replicates:
                    replicate_object = request.embed(rep, '@@object')
                    if replicate_object['status'] == 'deleted':
                        continue
                    if 'libraries' in replicate_object:
                        preferred_name = 'total RNA-seq'
                        for lib in replicate_object['libraries']:
                            library_object = request.embed(lib, '@@object')
                            if 'size_range' in library_object and \
                            library_object['size_range'] == '<200':
                                preferred_name = 'small RNA-seq'
                                break
                            elif 'depleted_in_term_name' in library_object and \
                                'polyadenylated mRNA' in library_object['depleted_in_term_name']:
                                preferred_name = 'polyA minus RNA-seq'
                                break
                            elif 'nucleic_acid_term_name' in library_object and \
                                library_object['nucleic_acid_term_name'] == 'polyadenylated mRNA':
                                preferred_name = 'polyA plus RNA-seq'
                                break
                        else:
                            continue
                        break
            elif preferred_name == 'ChIP-seq':
                if target is not None:
                    target_object = request.embed(target,'@@object')
                    target_categories = target_object['investigated_as']
                    if 'histone' in target_categories:
                        preferred_name = 'Histone ChIP-seq'
                    elif 'control' in target_categories:
                        preferred_name = 'Control ChIP-seq'
                    else:
                        preferred_name = 'TF ChIP-seq'
                else:
                    preferred_name = 'Control ChIP-seq'
            return preferred_name or assay_term_name
        return assay_term_name


class CalculatedCategorySlims:
    @calculated_property(condition='assay_term_name', schema={
        "title": "Assay category",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def category_slims(self, registry, assay_term_name):
        assay_term_id = assay_terms.get(assay_term_name, None)
        if assay_term_id in registry['ontology']:
            return registry['ontology'][assay_term_id]['category']
        return []


class CalculatedTypeSlims:
    @calculated_property(condition='assay_term_name', schema={
        "title": "Assay type slims",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def type_slims(self, registry, assay_term_name):
        assay_term_id = assay_terms.get(assay_term_name, None)
        if assay_term_id in registry['ontology']:
            return registry['ontology'][assay_term_id]['types']
        return []


class CalculatedObjectiveSlims:
    @calculated_property(condition='assay_term_name', schema={
        "title": "Assay objective",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def objective_slims(self, registry, assay_term_name):
        assay_term_id = assay_terms.get(assay_term_name, None)
        if assay_term_id in registry['ontology']:
            return registry['ontology'][assay_term_id]['objectives']
        return []


class CalculatedReplicationType:
    @calculated_property(schema={
        "title": "Replication type",
        "description": "Calculated field that indicates the replication model",
        "type": "string"
    })
    def replication_type(
        self, 
        request, 
        original_files=None, 
        replicates=None, 
        assay_term_name=None,
    ):
        # ENCD-4251 loop through replicates and select one replicate, which has
        # the smallest technical_replicate_number, per biological replicate.
        # That replicate should have a libraries property which, as calculated
        # in replicate.libraries (ENCD-4251), should have collected all
        # possible technical replicates belong to the biological replicate.
        # TODO: change this once we remove technical_replicate_number.
        # replication_type for experiment without data files is not defined
        # In case of "RNA Bind-n-Seq" experiments we need to make sure experiments
        # contain replicates and libraries, and only then lack of biosamples is 
        # acceptable to deem these experiments "unreplicated"
        if not original_files:
            return None
        # replication_type for experiment without replicates is not defined
        if not replicates:
            return None
        excluded_statuses = (
            'uploading',
            'content error',
            'upload failed',
            'deleted',
            'replaced',
        )
        filtered_file_objects = [
            request.embed(f, '@@object')
            for f in paths_filtered_by_status(
                request,
                original_files,
                exclude=excluded_statuses
            )
        ]
        related_replicates_from_filtered_files = [
            f.get('replicate')
            for f in filtered_file_objects 
            if f.get('replicate') and f.get('replicate') in replicates
        ]
        filtered_replicate_objects = [
            request.embed(r, '@@object')
            for r in paths_filtered_by_status(
                request,
                related_replicates_from_filtered_files,
                exclude=excluded_statuses,
            )
        ]
        bio_rep_dict = {}
        for r in filtered_replicate_objects:
            bio_rep_num = r['biological_replicate_number']
            if bio_rep_num not in bio_rep_dict:
                bio_rep_dict[bio_rep_num] = r
                continue
            tech_rep_num = r['technical_replicate_number']
            if tech_rep_num < bio_rep_dict[bio_rep_num]['technical_replicate_number']:
                bio_rep_dict[bio_rep_num] = r
        biosample_donors_set = set()
        biosample_numbers_set = set()
        for r in bio_rep_dict.values():
            library = r.get('library')
            if not library:
                # If I have a replicate without a library I cannot make a
                # call about the replication type
                return None
            library_object = request.embed(library, '@@object')
            biosample = library_object.get('biosample')
            if not biosample:
                if assay_term_name == 'RNA Bind-n-Seq':
                    return 'unreplicated'
                # If I have a library without a biosample I cannot make a
                # call about the replication type
                return None
            biosample_object = request.embed(biosample, '@@object')
            donor = biosample_object.get('donor')
            if not donor:
                # If I have a biosample without a donor,
                # I cannot make a call about the replication type
                return None
            biosample_donors_set.add(donor)
            biosample_numbers_set.add(r.get('biological_replicate_number'))
        if len(biosample_numbers_set) == 1:
            return 'unreplicated'
        if len(biosample_donors_set) == 0:
            return None
        if len(biosample_donors_set) == 1:
            return 'isogenic'
        return 'anisogenic'
