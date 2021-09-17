from pyramid.traversal import find_root
from snovault import (
    calculated_property,
    collection,
    load_schema,
)
from snovault.util import Path
from .base import (
    paths_filtered_by_status
)
from .dataset import Dataset
from .shared_calculated_properties import (
    CalculatedAssaySynonyms,
    CalculatedAssayTermID,
    CalculatedVisualize,
    CalculatedBiosampleSummary,
    CalculatedSimpleSummary,
    CalculatedReplicates,
    CalculatedAssaySlims,
    CalculatedAssayTitle,
    CalculatedCategorySlims,
    CalculatedTypeSlims,
    CalculatedObjectiveSlims,
    CalculatedReplicationType,
    CalculatedReplicationCounts,
)

from .assay_data import assay_terms
from .biosample import construct_biosample_summary
from .shared_biosample import biosample_summary_information

@collection(
    name='functional-characterization-experiments',
    unique_key='accession',
    properties={
        'title': 'Functional characterization experiments',
        'description': 'Listing of Functional Characterization Experiments',
    })
class FunctionalCharacterizationExperiment(
    Dataset,
    CalculatedAssaySynonyms,
    CalculatedAssayTermID,
    CalculatedVisualize,
    CalculatedBiosampleSummary,
    CalculatedSimpleSummary,
    CalculatedReplicates,
    CalculatedAssaySlims,
    CalculatedAssayTitle,
    CalculatedCategorySlims,
    CalculatedTypeSlims,
    CalculatedObjectiveSlims,
    CalculatedReplicationType,
    CalculatedReplicationCounts):
    item_type = 'functional_characterization_experiment'
    schema = load_schema('encoded:schemas/functional_characterization_experiment.json')
    embedded = Dataset.embedded + [
        'biosample_ontology',
        'examined_loci',
        'examined_loci.gene',
        'elements_references',
        'elements_references.examined_loci',
        'elements_references.examined_regions',
        'elements_references.files',
        'files.platform',
        'files.analysis_step_version.analysis_step',
        'files.analysis_step_version.analysis_step.pipelines',
        'related_series',
        'replicates.antibody',
        'replicates.library',
        'replicates.library.biosample.biosample_ontology',
        'replicates.library.biosample.submitted_by',
        'replicates.library.biosample.source',
        'replicates.library.biosample.applied_modifications',
        'replicates.library.biosample.applied_modifications.documents',
        'replicates.library.biosample.organism',
        'replicates.library.biosample.donor',
        'replicates.library.biosample.donor.organism',
        'replicates.library.biosample.part_of',
        'replicates.library.biosample.part_of.donor',
        'replicates.library.biosample.part_of.treatments',
        'replicates.library.biosample.treatments',
        'replicates.library.construction_platform',
        'replicates.library.treatments',
        'possible_controls',
        'target.genes',
        'target.organism',
    ]
    audit_inherit = [
        'original_files',
        'original_files.replicate',
        'original_files.platform',
        'target',
        'files.analysis_step_version.analysis_step.pipelines',
        'revoked_files',
        'revoked_files.replicate',
        'submitted_by',
        'lab',
        'award',
        'default_analysis',
        'documents',
        'replicates.antibody.characterizations.biosample_ontology',
        'replicates.antibody.characterizations',
        'replicates.antibody.targets',
        'replicates.library',
        'replicates.library.documents',
        'replicates.library.biosample',
        'replicates.library.biosample.biosample_ontology',
        'replicates.library.biosample.organism',
        'replicates.library.biosample.treatments',
        'replicates.library.biosample.applied_modifications',
        'replicates.library.biosample.donor.organism',
        'replicates.library.biosample.donor',
        'replicates.library.biosample.treatments',
        'replicates.library.biosample.originated_from',
        'replicates.library.biosample.originated_from.biosample_ontology',
        'replicates.library.biosample.part_of',
        'replicates.library.biosample.part_of.biosample_ontology',
        'replicates.library.biosample.pooled_from',
        'replicates.library.biosample.pooled_from.biosample_ontology',
        'replicates.library.spikeins_used',
        'replicates.library.treatments',
        'target.organism',
    ]
    set_status_up = [
        'original_files',
        'replicates',
        'documents',
        'target',
        'analyses',
    ]
    set_status_down = [
        'original_files',
        'replicates',
        'analyses',
    ]
    rev = Dataset.rev.copy()
    rev.update({
        'related_series': ('Series', 'related_datasets'),
        'replicates': ('Replicate', 'experiment'),
        'superseded_by': ('FunctionalCharacterizationExperiment', 'supersedes')
    })

    @calculated_property(schema={
        "title": "Related series",
        "type": "array",
        "items": {
            "type": ['string', 'object'],
            "linkFrom": "Series.related_datasets",
        },
        "notSubmittable": True,
    })
    def related_series(self, request, related_series):
        return paths_filtered_by_status(request, related_series)

    @calculated_property(schema={
            "title": "Superseded by",
            "type": "array",
            "items": {
                "type": ['string', 'object'],
                "linkFrom": "FunctionalCharacterizationExperiment.supersedes",
            },
            "notSubmittable": True,
    })
    def superseded_by(self, request, superseded_by):
        return paths_filtered_by_status(request, superseded_by)

    @calculated_property(schema={
        "title": "Perturbation type",
        "type": "string",
        "notSubmittable": True,
        })
    def perturbation_type(self, request, assay_term_name, replicates=None):
        # https://encodedcc.atlassian.net/browse/ENCD-5911
        perturbation_type = None
        if assay_term_name == 'CRISPR screen':
            if replicates is not None:
                CRISPR_gms = set()
                for rep in replicates:
                    replicate_object = request.embed(rep, '@@object?skip_calculated=true')
                    if replicate_object['status'] in ('deleted', 'revoked'):
                        continue
                    if 'library' in replicate_object:
                        library_object = request.embed(replicate_object['library'], '@@object?skip_calculated=true')
                        if library_object['status'] in ('deleted', 'revoked'):
                            continue
                        if 'biosample' in library_object:
                            biosample_object = request.embed(library_object['biosample'], '@@object')
                            if biosample_object['status'] in ('deleted', 'revoked'):
                                continue
                            genetic_modifications = biosample_object.get('applied_modifications')
                            if genetic_modifications:
                                for gm in genetic_modifications:
                                    gm_object = request.embed(gm, '@@object?skip_calculated=true')
                                    if gm_object.get('purpose') == 'characterization' and gm_object.get('method') == 'CRISPR':
                                        CRISPR_gms.add(gm_object['category'])
                # Return a specific perturbation_type if there is only one category type for CRISPR characterization genetic modifications for all replicate biosample genetic modifications
                if len(CRISPR_gms) == 1:
                    perturbation_type = list(CRISPR_gms)[0]
            return perturbation_type

    @calculated_property(schema={
        "title": "CRISPR screen readout",
        "type": "string",
        "notSubmittable": True,
    })
    def crispr_screen_readout(self, request, assay_term_name, examined_loci=None, control_type=None):
        crispr_screen_readout = None
        if assay_term_name == 'CRISPR screen':
            # Return a specific CRISPR screen readout if there is only one method used in examined_loci, no examined_loci at all indicates a growth screen
            if control_type == 'control':
                return
            if examined_loci == None:
                crispr_screen_readout = 'proliferation'
            else:
                methods = []
                for locus in examined_loci:
                    if 'expression_measurement_method' in locus:
                        methods.append(locus['expression_measurement_method'])
                if len(set(methods)) == 1:
                    crispr_screen_readout = str(methods[0])
            return crispr_screen_readout

    @calculated_property(schema={
        "title": "Datapoint",
        "description": "A flag to indicate whether the FC Experiment is a datapoint that should be displayed only as a part of Series object.",
        "type": "boolean",
        "notSubmittable": True,
    })
    def datapoint(self, request, related_series=None):
        if not related_series:
            return False
        for series in related_series:
            properties = {'series': series}
            path = Path('series', include=["@type"])
            path.expand(request, properties)
            types = properties.get('series', {}).get('@type', [])
            if "FunctionalCharacterizationSeries" in types:
                return True 
        return False

    @calculated_property(schema={
        "title": "Biosample summary",
        "type": "string",
    })
    def biosample_summary(self, request, replicates=None, elements_references=None):
        drop_age_sex_flag = False
        add_classification_flag = False
        drop_originated_from_flag = False
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
                            biosample_info = biosample_summary_information(request, biosampleObject, skip_non_perturbation_treatments_flag=True)
                            biosample_summary_dictionary = biosample_info[0]
                            biosample_drop_age_sex_flag = biosample_info[1]
                            biosample_add_classification_flag = biosample_info[2]
                            biosample_drop_originated_from_flag = biosample_info[3]
                            dictionaries_of_phrases.append(biosample_summary_dictionary)
                            if biosample_drop_age_sex_flag:
                                drop_age_sex_flag = True
                            if biosample_add_classification_flag:
                                add_classification_flag = True
                            if biosample_drop_originated_from_flag:
                                drop_originated_from_flag = True
        if len(dictionaries_of_phrases) > 0:
            if elements_references is not None and len(elements_references) > 0:
                loci_terms = []
                for ref in elements_references:
                    elements_reference_object = request.embed(ref, '@@object')
                    if 'examined_loci' in elements_reference_object:
                        if len(elements_reference_object['examined_loci']) > 1:
                            loci_terms.append('multiple loci')
                        else:
                            examined_loci_object = request.embed(elements_reference_object['examined_loci'][0], '@@object')
                            loci_terms.append(f"{examined_loci_object['symbol']} locus")
                    elif 'examined_regions' in elements_reference_object:
                        if len(elements_reference_object['examined_regions']) > 1:
                            loci_terms.append('multiple loci')
                        else:
                            examined_region_object = elements_reference_object['examined_regions'][0]
                            loci_terms.append(
                                f"{examined_region_object['chromosome']}:"
                                f"{examined_region_object['start']}-{examined_region_object['end']}"
                            )
                    else:
                        loci_terms.append('')

                filtered_loci_terms = [term for term in loci_terms if term not in ['', 'multiple loci']]
                if len(set(loci_terms)) == 1 and '' in set(loci_terms):
                    for entry in dictionaries_of_phrases:
                        entry['elements_references_examined_loci'] = ''
                elif 'multiple loci' in loci_terms or \
                        len(set(filtered_loci_terms)) > 1:
                    for entry in dictionaries_of_phrases:
                        entry['elements_references_examined_loci'] = f'for multiple loci'
                elif len(set(filtered_loci_terms)) == 1:
                    for entry in dictionaries_of_phrases:
                        entry['elements_references_examined_loci'] = f'for {filtered_loci_terms[0]}'

            else:
                for entry in dictionaries_of_phrases:
                    entry['elements_references_examined_loci'] = ''

        sentence_parts = [
            'genotype_strain',
            'experiment_term_phrase',
            'phase',
            'fractionated',
            'sex_stage_age',
            'disease_term_name',
            'post_nucleic_acid_delivery_time',
            'post_differentiation_time',
            'synchronization',
            'modifications_list',
            'originated_from',
            'treatments_phrase',
            'depleted_in',
            'pulse_chase_time',
            'elements_references_examined_loci'
        ]
        if drop_age_sex_flag:
            sentence_parts.remove('sex_stage_age')
        if add_classification_flag:
            sentence_parts.insert(2, 'sample_type')
        if drop_originated_from_flag:
            sentence_parts.remove('originated_from')

        if len(dictionaries_of_phrases) > 0:
            return construct_biosample_summary(dictionaries_of_phrases, sentence_parts)
