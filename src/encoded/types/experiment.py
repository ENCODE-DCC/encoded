from pyramid.traversal import find_root
from snovault import (
    calculated_property,
    collection,
    load_schema,
)
from .base import (
    ALLOW_SUBMITTER_ADD,
    Item,
    paths_filtered_by_status,
    SharedItem
)
from .dataset import Dataset
from .shared_calculated_properties import (
    CalculatedAssaySynonyms,
    CalculatedAssayTermID,
    CalculatedVisualize
)

# importing biosample function to allow calculation of experiment biosample property
from .biosample import (
    construct_biosample_summary,
    generate_summary_dictionary
)

from .assay_data import assay_terms


@collection(
    name='experiments',
    unique_key='accession',
    properties={
        'title': 'Experiments',
        'description': 'Listing of Experiments',
    })
class Experiment(Dataset,
                 CalculatedAssaySynonyms,
                 CalculatedAssayTermID,
                 CalculatedVisualize,
                 CalculatedBiosampleSummary):
    item_type = 'experiment'
    schema = load_schema('encoded:schemas/experiment.json')
    embedded = Dataset.embedded + [
        'biosample_ontology',
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
        'replicates.library.biosample.organism',
        'replicates.library.biosample.donor',
        'replicates.library.biosample.donor.organism',
        'replicates.library.biosample.part_of',
        'replicates.library.biosample.part_of.donor',
        'replicates.library.biosample.part_of.treatments',
        'replicates.library.biosample.treatments',
        'replicates.library.treatments',
        'replicates.libraries',
        'replicates.libraries.biosample.submitted_by',
        'replicates.libraries.biosample.source',
        'replicates.libraries.biosample.applied_modifications',
        'replicates.libraries.biosample.organism',
        'replicates.libraries.biosample.donor',
        'replicates.libraries.biosample.donor.organism',
        'replicates.libraries.biosample.part_of',
        'replicates.libraries.biosample.part_of.donor',
        'replicates.libraries.biosample.part_of.treatments',
        'replicates.libraries.biosample.treatments',
        'replicates.libraries.treatments',
        'possible_controls',
        'target.genes',
        'target.organism',
        'references',
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
        'documents',
        'replicates.antibody.characterizations.biosample_ontology',
        'replicates.antibody.characterizations.characterization_reviews.biosample_ontology',
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
        'replicates.libraries.documents',
        'replicates.libraries.biosample',
        'replicates.libraries.biosample.organism',
        'replicates.libraries.biosample.treatments',
        'replicates.libraries.biosample.applied_modifications',
        'replicates.libraries.biosample.donor.organism',
        'replicates.libraries.biosample.donor',
        'replicates.libraries.biosample.treatments',
        'replicates.libraries.biosample.originated_from',
        'replicates.libraries.biosample.part_of',
        'replicates.libraries.biosample.pooled_from',
        'replicates.libraries.spikeins_used',
        'replicates.libraries.treatments',
        'target.organism',
    ]
    set_status_up = [
        'original_files',
        'replicates',
        'documents',
        'target',
    ]
    set_status_down = [
        'original_files',
        'replicates',
    ]
    rev = Dataset.rev.copy()
    rev.update({
        'replicates': ('Replicate', 'experiment'),
        'related_series': ('Series', 'related_datasets'),
        'superseded_by': ('Experiment', 'supersedes')
    })

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
            "linkFrom": "Experiment.supersedes",
        },
        "notSubmittable": True,
    })
    def superseded_by(self, request, superseded_by):
        return paths_filtered_by_status(request, superseded_by)

    @calculated_property(schema={
        "title": "Replication type",
        "description": "Calculated field that indicates the replication model",
        "type": "string"
    })
    def replication_type(self, request, replicates=None, assay_term_name=None):
        # ENCD-4251 loop through replicates and select one replicate, which has
        # the smallest technical_replicate_number, per biological replicate.
        # That replicate should have a libraries property which, as calculated
        # in replicate.libraries (ENCD-4251), should have collected all
        # possible technical replicates belong to the biological replicate.
        # TODO: change this once we remove technical_replicate_number.
        bio_rep_dict = {}
        for rep in replicates:
            replicate_object = request.embed(rep, '@@object')
            if replicate_object['status'] == 'deleted':
                continue
            bio_rep_num = replicate_object['biological_replicate_number']
            if bio_rep_num not in bio_rep_dict:
                bio_rep_dict[bio_rep_num] = replicate_object
                continue
            tech_rep_num = replicate_object['technical_replicate_number']
            if tech_rep_num < bio_rep_dict[bio_rep_num]['technical_replicate_number']:
                bio_rep_dict[bio_rep_num] = replicate_object

        # Compare the biosamples to see if for humans they are the same donor and for
        # model organisms if they are sex-matched and age-matched
        biosample_donor_list = []
        biosample_number_list = []

        for replicate_object in bio_rep_dict.values():
            if 'libraries' in replicate_object and replicate_object['libraries']:
                biosamples = request.select_distinct_values(
                    'biosample', *replicate_object['libraries']
                )
                if biosamples:
                    for b in biosamples:
                        biosample_object = request.embed(b, '@@object')
                        biosample_donor_list.append(
                            biosample_object.get('donor')
                        )
                        biosample_number_list.append(
                            replicate_object.get('biological_replicate_number')
                        )
                        biosample_species = biosample_object.get('organism')
                        biosample_type_object = request.embed(
                            biosample_object['biosample_ontology'],
                            '@@object'
                        )
                        biosample_type = biosample_type_object.get('classification')
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

    matrix = {
        'y': {
            'facets': [
                'status',
                'replicates.library.biosample.donor.organism.scientific_name',
                'biosample_ontology.classification',
                'biosample_ontology.term_name',
                'biosample_ontology.organ_slims',
                'biosample_ontology.cell_slims',
                'award.project',
                'assembly',
                'month_released',
                'internal_status',
                'audit_category', # Added for auditmatrix
                'lab.title'
            ],
            'group_by': ['biosample_ontology.classification', 'biosample_ontology.term_name'],
            'label': 'Biosample',
        },
        'x': {
            'facets': [
                'assay_slims',
                'assay_title',
                'target.investigated_as',
                'target.label',
                'files.file_type',
            ],
            'group_by': 'assay_title',
            'label': 'Assay',
        },
    }

    summary_data = {
        'y': {
            'facets': [
                'replicates.library.biosample.donor.organism.scientific_name',
                'biosample_ontology.classification',
                'biosample_ontology.term_name',
                'biosample_ontology.organ_slims',
                'biosample_ontology.cell_slims',
                'award.project',
                'award.rfa',
                'status',
                'assembly',
                'internal_status',
                'audit_category',
                'lab.title',
                'month_released',
                'date_submitted',
            ],
            'group_by': ['biosample_ontology.classification', 'biosample_ontology.term_name'],
            'label': 'Biosample',
        },
        'x': {
            'facets': [
                'assay_slims',
                'assay_title',
                'target.investigated_as',
                'target.label',
                'files.file_type',
            ],
            'group_by': 'assay_title',
            'label': 'Assay',
        },
        'grouping': ['replication_type', 'status'],
    }


@collection(
    name='replicates',
    acl=ALLOW_SUBMITTER_ADD,
    properties={
        'title': 'Replicates',
        'description': 'Listing of Replicates',
    })
class Replicate(Item):
    item_type = 'replicate'
    schema = load_schema('encoded:schemas/replicate.json')
    embedded = [
        'antibody',
        'experiment',
        'library',
        'library.biosample',
        'library.biosample.donor',
        'library.biosample.donor.organism',
        'libraries',
        'libraries.biosample',
        'libraries.biosample.donor',
        'libraries.biosample.donor.organism',
    ]
    set_status_up = [
        'library',
        'antibody',
    ]
    set_status_down = []

    def unique_keys(self, properties):
        keys = super(Replicate, self).unique_keys(properties)
        value = u'{experiment}/{biological_replicate_number}/{technical_replicate_number}'.format(
            **properties)
        keys.setdefault('replicate:experiment_biological_technical', []).append(value)
        return keys

    def __ac_local_roles__(self):
        properties = self.upgrade_properties()
        root = find_root(self)
        experiment = root.get_by_uuid(properties['experiment'])
        return experiment.__ac_local_roles__()

    @calculated_property(schema={
        "title": "Libraries",
        "description": "The nucleic acid libraries used in this replicate.",
        "type": "array",
        "uniqueItems": True,
        "items": {
            "title": "Library",
            "description": "The nucleic acid library used in this replicate.",
            "comment": "See library.json for available identifiers.",
            "type": "string",
            "linkTo": "Library"
        }
    })
    def libraries(self, status, biological_replicate_number,
                  technical_replicate_number):
        if status == 'deleted':
            return []
        # Use root.get_by_uuid instead of embed to get reverse link
        # specifically. This helps avoid infinite loop since calculated
        # properties of experiment need to embed replicate.
        properties = self.upgrade_properties()
        root = find_root(self)
        experiment = root.get_by_uuid(properties['experiment'])
        libraries = set()
        for rep_uuid in experiment.get_rev_links('replicates'):
            rep_props = root.get_by_uuid(rep_uuid).upgrade_properties()
            # Only care (check and add to the list) about non-deleted technical
            # replicates of this replicate, meaning belonging to the same
            # biological replicate.
            if (rep_props['biological_replicate_number'] != biological_replicate_number
                or rep_props['status'] == 'deleted'):
                continue
            if rep_props['technical_replicate_number'] < technical_replicate_number:
                # Found smaller technical replicate, libraries will be
                # calculated there rather than here.
                return []
            if 'library' in rep_props:
                libraries.add(rep_props['library'])
        # This is the "first" techinical replicate within the isogenic
        # replciate. Therefore, libraries should be calculated.
        return list(libraries)
