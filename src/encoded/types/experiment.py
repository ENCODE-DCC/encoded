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
        'analysis_objects',
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
        'replicates.library.construction_platform',
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
        "comment": "Do not submit. This field is calculated through applied_modifications.",
        "type": "array",
        "notSubmittable": True,
        "minItems": 1,
        "items": {
            "title": "Protein tag",
            "description": "The protein tag introduced in the modification.",
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "name": {
                    "title": "Tag name",
                    "type": "string",
                    "enum": [
                        "3xFLAG",
                        "6XHis",
                        "DsRed",
                        "eGFP",
                        "ER",
                        "FLAG",
                        "GFP",
                        "HA",
                        "mCherry",
                        "T2A",
                        "TagRFP",
                        "TRE",
                        "V5",
                        "YFP",
                        "mAID-mClover",
                        "mAID-mClover-NeoR",
                        "mAID-mClover-Hygro"
                    ]
                },
                "location": {
                    "title": "Tag location",
                    "type": "string",
                    "enum": [
                        "C-terminal",
                        "internal",
                        "N-terminal",
                        "other",
                        "unknown"
                    ]
                },
                "target": {
                    "title": "Tagged protein",
                    "type": "string",
                    "linkTo": "Target",
                }
            }
        }
    })
    def protein_tags(self, request, replicates=None):
        protein_tags = []
        if replicates is not None:
            for rep in replicates:
                replicateObject = request.embed(rep, '@@object?skip_calculated=true')
                if replicateObject['status'] in ('deleted', 'revoked'):
                    continue
                if 'library' in replicateObject:
                    libraryObject = request.embed(replicateObject['library'], '@@object?skip_calculated=true')
                    if libraryObject['status'] in ('deleted', 'revoked'):
                        continue
                    if 'biosample' in libraryObject:
                        biosampleObject = request.embed(libraryObject['biosample'], '@@object')
                        if biosampleObject['status'] in ('deleted', 'revoked'):
                            continue
                        genetic_modifications = biosampleObject.get('applied_modifications')
                        if genetic_modifications:
                            for gm in genetic_modifications:
                                gm_object = request.embed(gm, '@@object?skip_calculated=true')
                                if gm_object.get('introduced_tags') is None:
                                    continue
                                if gm_object.get('introduced_tags'):
                                    for tag in gm_object.get('introduced_tags'):
                                        tag_dict = {'location': tag['location'], 'name': tag['name']}
                                        if gm_object.get('modified_site_by_target_id'):
                                            tag_dict.update({'target': gm_object.get('modified_site_by_target_id')})
                                            protein_tags.append(tag_dict)
        if len(protein_tags) > 0:
            return protein_tags

    # Don't specify schema as this just overwrites the existing value
    @calculated_property(condition='analyses')
    def analyses(self, request, analyses):
        updated_analyses = []
        for analysis in analyses:
            assemblies = set()
            genome_annotations = set()
            pipelines = set()
            pipeline_award_rfas = set()
            pipeline_labs = set()
            for f in analysis.get('files', []):
                file_object = request.embed(
                    f,
                    '@@object_with_select_calculated_properties?field=analysis_step_version'
                )
                if 'assembly' in file_object:
                    assemblies.add(file_object['assembly'])
                if 'genome_annotation' in file_object:
                    genome_annotations.add(file_object['genome_annotation'])
                if 'analysis_step_version' in file_object:
                    analysis_step = request.embed(
                        file_object['analysis_step_version'],
                        '@@object?skip_calculated=true'
                    )['analysis_step']
                    pipelines |= set(
                        request.embed(
                            analysis_step,
                            '@@object_with_select_calculated_properties?field=pipelines'
                        ).get('pipelines', [])
                    )
                    for pipeline in pipelines:
                        pipeline_object = request.embed(
                            pipeline,
                            '@@object?skip_calculated=true'
                        )
                        pipeline_award_rfas.add(
                            request.embed(
                                pipeline_object['award'],
                                '@@object?skip_calculated=true'
                            )['rfa']
                        )
                        pipeline_labs.add(pipeline_object['lab'])
            analysis['assemblies'] = sorted(assemblies)
            analysis['genome_annotations'] = sorted(genome_annotations)
            analysis['pipelines'] = sorted(pipelines)
            analysis['pipeline_award_rfas'] = sorted(pipeline_award_rfas)
            analysis['pipeline_labs'] = sorted(pipeline_labs)
            updated_analyses.append(analysis)
        return analyses

    @calculated_property(schema={
        "title": "Perturbed",
        "description": "A flag to indicate whether any biosamples have been perturbed with treatments or genetic modifications.",
        "type": "boolean",
    })
    def perturbed(self, request, replicates=None):
        if replicates is not None:
            bio_perturbed = set()
            for rep in replicates:
                replicateObject = request.embed(rep, '@@object?skip_calculated=true')
                if replicateObject['status'] in ('deleted', 'revoked'):
                    continue
                if 'library' in replicateObject:
                    libraryObject = request.embed(replicateObject['library'], '@@object?skip_calculated=true')
                    if libraryObject['status'] in ('deleted', 'revoked'):
                        continue
                    if 'biosample' in libraryObject:
                        biosampleObject = request.embed(libraryObject['biosample'], '@@object')
                        if biosampleObject['status'] in ('deleted', 'revoked'):
                            continue
                        bio_perturbed.add(biosampleObject['perturbed'])
            return any(bio_perturbed)
        return False

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

    sescc_stem_cell_matrix = {
        'y': {
            'group_by': ['biosample_ontology.classification', 'biosample_ontology.term_name'],
            'label': 'Biosample',
        },
        'x': {
            'group_by': ['assay_title', 'target.label'],
            'label': 'Assay',
        },
    }

    chip_seq_matrix = {
        'y': {
            'group_by': [
                'replicates.library.biosample.donor.organism.scientific_name',
                'target.label',
            ],
            'label': 'Target',
        },
        'x': {
            'group_by': ['biosample_ontology.classification', 'biosample_ontology.term_name'],
            'label': 'Term Name',
        },
    }

    summary_matrix = {
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

    mouse_development = {
        'y': {
            'group_by': ['biosample_ontology.term_name', 'biosample_summary'],
            'label': 'Biosample',
        },
        'x': {
            'group_by': ['assay_title', 'target.label'],
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
    def libraries(self, request, status, biological_replicate_number,
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
        return [request.resource_path(root.get_by_uuid(lib)) for lib in libraries]
