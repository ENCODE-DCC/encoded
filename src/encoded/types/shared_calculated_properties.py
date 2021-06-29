from snovault import calculated_property
from snovault.util import ensurelist
from .assay_data import assay_terms
from urllib.parse import urljoin
from encoded.vis_defines import (
    vis_format_url,
    browsers_available
    )
from .biosample import construct_biosample_summary
from .shared_biosample import biosample_summary_information
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
            'replicate.library.biosample.organism', *related_files)


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


class CalculatedSeriesAssayType:
    @calculated_property(condition='related_datasets', schema={
        "title": "Assay type",
        "type": "array",
        "items": {
            "type": 'string',
        },
    })
    def assay_slims(self, request, related_datasets):
        return request.select_distinct_values(
            'assay_slims', *related_datasets)


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
            'replicates.library.biosample.organism', *related_datasets)


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
            'replicates.library.biosample.treatments.treatment_term_name',
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
        viewable_file_formats = ['bigWig', 'bigBed', 'hic', 'bigInteract']
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
        add_classification_flag = False
        biosample_drop_originated_from_flag = False
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
                            biosample_info = biosample_summary_information(request, biosampleObject)
                            biosample_summary_dictionary = biosample_info[0]
                            biosample_drop_age_sex_flag = biosample_info[1]
                            biosample_add_classification_flag = biosample_info[2]
                            biosample_drop_originated_from_flag = biosample_info[3]
                            dictionaries_of_phrases.append(biosample_summary_dictionary)
                            if biosample_drop_age_sex_flag is True:
                                drop_age_sex_flag = True
                            if biosample_add_classification_flag is True:
                                add_classification_flag = True
            if len(biosample_accessions) == 0:
                for rep in replicates:
                    replicateObject = request.embed(rep, '@@object')
                    if replicateObject['status'] == 'deleted':
                        continue
                    if 'library' in replicateObject:
                        libraryObject = request.embed(replicateObject['library'], '@@object')
                        if libraryObject['status'] == 'deleted':
                            continue
                        elif 'mixed_biosamples' in libraryObject:
                            for each_biosample in libraryObject['mixed_biosamples']:
                                biosampleObject = request.embed(each_biosample, '@@object')
                                if biosampleObject['status'] == 'deleted':
                                    continue
                                if biosampleObject['accession'] not in biosample_accessions:
                                    biosample_accessions.add(biosampleObject['accession'])
                                    biosample_info = biosample_summary_information(request, biosampleObject)
                                    biosample_summary_dictionary = biosample_info[0]
                                    biosample_drop_age_sex_flag = biosample_info[1]
                                    biosample_add_classification_flag = biosample_info[2]
                                    biosample_drop_originated_from_flag = biosample_info[3]
                                    dictionaries_of_phrases.append(biosample_summary_dictionary)
                                    if biosample_drop_age_sex_flag is True:
                                        drop_age_sex_flag = True
                                    if biosample_add_classification_flag is True:
                                        add_classification_flag = True

        sentence_parts = [
            'strain_background',
            'experiment_term_phrase',
            'phase',
            'fractionated',
            'sex_stage_age',
            'post_nucleic_acid_delivery_time',
            'post_differentiation_time',
            'synchronization',
            'modifications_list',
            'originated_from',
            'treatments_phrase',
            'depleted_in',
            'disease_term_name',
            'pulse_chase_time'
        ]
        if drop_age_sex_flag:
            sentence_parts.remove('sex_stage_age')
        if add_classification_flag:
            sentence_parts.insert(2, 'sample_type')
        if biosample_drop_originated_from_flag:
            sentence_parts.remove('originated_from')

        if len(dictionaries_of_phrases) > 0:
            return construct_biosample_summary(dictionaries_of_phrases, sentence_parts)


class CalculatedSimpleSummary:
    @calculated_property(schema={
        "title": "Simple Biosample summary",
        "type": "string",
    })
    def simple_biosample_summary(self,
                                 request,
                                 replicates=None):
        sub_summaries = set()
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
                            sub_summaries.add(biosampleObject['simple_summary'])
            return " ".join(list(sub_summaries))

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
                    control_type=None, target=None):
        # This is the preferred name in generate_ontology.py if exists
        assay_term_id = assay_terms.get(assay_term_name, None)
        if assay_term_id in registry['ontology']:
            preferred_name = registry['ontology'][assay_term_id].get('preferred_name',
                                                                     assay_term_name)
            if preferred_name == 'RNA-seq':
                preferred_name = 'total RNA-seq'
            elif preferred_name == 'ChIP-seq':
                preferred_name = 'Control ChIP-seq'
                if not control_type and target is not None:
                    target_object = request.embed(target,'@@object')
                    target_categories = target_object['investigated_as']
                    if 'histone' in target_categories:
                        preferred_name = 'Histone ChIP-seq'
                    else:
                        preferred_name = 'TF ChIP-seq'
            elif control_type and assay_term_name in ['eCLIP', 'MPRA', 'CRISPR screen', 'STARR-seq', 'Mint-ChIP-seq']:
                preferred_name = 'Control {}'.format(assay_term_name)
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
    def replication_type(self, request, replicates=None, assay_term_name=None):
        # ENCD-5185 decided to return None for replication type for all
        # pooled clone sequencing
        if assay_term_name == 'pooled clone sequencing':
            return None
        # Compare the biosamples to see if for humans they are the same donor and for
        # model organisms if they are sex-matched and age-matched
        biosample_dict = {}
        biosample_donor_list = []
        biosample_number_list = []

        for rep in replicates:
            replicateObject = request.embed(rep, '@@object')
            if replicateObject['status'] == 'deleted':
                continue
            if 'library' in replicateObject:
                libraryObject = request.embed(replicateObject['library'], '@@object')
                if 'biosample' in libraryObject:
                    biosampleObject = request.embed(libraryObject['biosample'], '@@object')
                    biosample_dict[biosampleObject['accession']] = biosampleObject
                    biosample_donor_list.append(biosampleObject.get('donor'))
                    biosample_number_list.append(replicateObject.get('biological_replicate_number'))
                    biosample_species = biosampleObject.get('organism')
                    biosampleTypeObject = request.embed(
                        biosampleObject['biosample_ontology'],
                        '@@object'
                    )
                    biosample_type = biosampleTypeObject.get('classification')
                else:
                    # special treatment for "RNA Bind-n-Seq" they will be called unreplicated
                    # untill we change our mind
                    if assay_term_name == 'RNA Bind-n-Seq':
                        return 'unreplicated'
                    # If I have a library without a biosample,
                    # I cannot make a call about replicate structure
                    return None
            else:
                # REPLICATES WITH NO LIBRARIES WILL BE CAUGHT BY AUDIT (TICKET 3268)
                # If I have a replicate without a library,
                # I cannot make a call about the replicate structure
                return None

        #  exclude ENCODE2
        if (len(set(biosample_number_list)) < 2):
            return 'unreplicated'

        if biosample_type == 'cell line':
            return 'isogenic'

        # Since we are not looking for model organisms here, we likely need audits
        if biosample_species != '/organisms/human/':
            if len(set(biosample_donor_list)) == 1:
                return 'isogenic'
            else:
                return 'anisogenic'

        if len(set(biosample_donor_list)) == 0:
            return None
        if len(set(biosample_donor_list)) == 1:
            if None in biosample_donor_list:
                return None
            else:
                return 'isogenic'

        return 'anisogenic'
