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
    CalculatedVisualize,
    CalculatedBiosampleSummary,
    CalculatedReplicates,
    CalculatedAssaySlims,
    CalculatedAssayTitle,
    CalculatedCategorySlims,
    CalculatedTypeSlims,
    CalculatedObjectiveSlims,
    CalculatedReplicationType
)

from .assay_data import assay_terms
from snovault.util import try_to_get_field_from_item_with_skip_calculated_first

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
                 CalculatedBiosampleSummary,
                 CalculatedReplicates,
                 CalculatedAssaySlims,
                 CalculatedAssayTitle,
                 CalculatedCategorySlims,
                 CalculatedTypeSlims,
                 CalculatedObjectiveSlims,
                 CalculatedReplicationType):
    item_type = 'experiment'
    schema = load_schema('encoded:schemas/experiment.json')
    embedded = Dataset.embedded + [
        'biosample_ontology',
        'files.platform',
        'files.analysis_step_version.analysis_step',
        'files.analysis_step_version.analysis_step.pipelines',
        'files.quality_metrics',
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
        "title": "Protein tags",
        "description": "The protein tags introduced through the genetic modifications of biosamples investigated in the experiment.",
        "type": "array",
        "notSubmittable": True,
        "items": {
            "title": "Protein tag",
            "description": "The protein tag introduced in the modification.",
            "comment": "See genetic_modification.json for available identifiers.",
            "type": "object",
            "additionalProperties": False,
            "linkTo": "GeneticModification",
            "properties": {
                "name": {
                    "title": "Tag name",
                    "type": "string"
                },
                "location": {
                    "title": "Tag location",
                    "type": "string"
                },
                "target": {
                    "title": "Tagged target",
                    "type": "string",
                    "linkTo": "Target"
                }
            }
        }
    })
    def protein_tags(self, request, replicates=None):
        protein_tags = None
        modification_tags = None
        tag_list = None
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
                        genetic_modifications = biosampleObject.get('applied_modifications')
                        if genetic_modifications:
                            protein_tags = []
                            tag_list = []
                            for gm in genetic_modifications:
                                gm_object = request.embed(gm, '@@object')
                                if gm_object.get('introduced_tags') is None:
                                    continue
                                if gm_object.get('introduced_tags'):
                                    modification_tags = []
                                    for tag in gm_object.get('introduced_tags'):
                                        tag_dict = {'location': tag['location'], 'name': tag['name'], 'target': gm_object.get('modified_site_by_target_id')}
                                        modification_tags.append(tag_dict)
                                tag_list.append(modification_tags)
                                protein_tags = [item for sublist in tag_list for item in sublist]
        return protein_tags

    matrix = {
        'y': {
            'group_by': ['biosample_ontology.classification', 'biosample_ontology.term_name'],
            'label': 'Biosample',
        },
        'x': {
            'group_by': 'assay_title',
            'label': 'Assay',
        },
    }

    summary = {
        'x': {
            'group_by': 'status'
        },
        'y': {
            'group_by': ['replication_type']
        }
    }

    reference_epigenome = {
        'y': {
            'group_by': ['biosample_ontology.classification', 'biosample_ontology.term_name'],
            'label': 'Biosample',
        },
        'x': {
            'group_by': ['assay_title', 'target.label'],
            'label': 'Assay',
        },
    }

    entex = {
        'y': {
            'group_by': ['biosample_ontology.classification', 'biosample_ontology.term_name'],
            'label': 'Biosample',
        },
        'x': {
            'group_by': ['assay_title', ('target.label', 'no_target'), 'replicates.library.biosample.donor.sex', 'replicates.library.biosample.donor.accession'],
            'label': 'Assay',
        },
    }

    audit = {
        'audit.ERROR.category': {
            'group_by': 'audit.ERROR.category',
            'label': 'Error'
        },
        'audit.INTERNAL_ACTION.category': {
            'group_by': 'audit.INTERNAL_ACTION.category',
            'label': 'Internal Action'},
        'audit.NOT_COMPLIANT.category': {
            'group_by': 'audit.NOT_COMPLIANT.category',
            'label': 'Not Compliant'
        },
        'audit.WARNING.category': {
            'group_by': 'audit.WARNING.category',
            'label': 'Warning'
        },
        'x': {
            'group_by': 'assay_title',
            'label': 'Assay'
        }
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
