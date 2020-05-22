from snovault import calculated_property
from snovault.util import ensurelist
from urllib.parse import urljoin
from encoded.vis_defines import (
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
