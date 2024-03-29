from pyramid.traversal import find_root
from snovault import (
    calculated_property,
    collection,
    load_schema,
)
from snovault.util import Path
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
                 CalculatedSimpleSummary,
                 CalculatedReplicates,
                 CalculatedAssaySlims,
                 CalculatedAssayTitle,
                 CalculatedCategorySlims,
                 CalculatedTypeSlims,
                 CalculatedObjectiveSlims,
                 CalculatedReplicationType,
                 CalculatedReplicationCounts):
    item_type = 'experiment'
    schema = load_schema('encoded:schemas/experiment.json')
    embedded = Dataset.embedded + [
        'biosample_ontology',
        'files.platform',
        'files.analysis_step_version.analysis_step',
        'files.analysis_step_version.analysis_step.pipelines',
        'files.quality_metrics',
        'related_series',
        'related_annotations',
        'replicates.antibody',
        'replicates.library',
        'replicates.library.biosample.biosample_ontology',
        'replicates.library.biosample.submitted_by',
        'replicates.library.biosample.source',
        'replicates.library.biosample.applied_modifications',
        'replicates.library.biosample.applied_modifications.introduced_gene.organism',
        'replicates.library.biosample.applied_modifications.modified_site_by_target_id.organism',
        'replicates.library.biosample.organism',
        'replicates.library.biosample.donor',
        'replicates.library.biosample.donor.organism',
        'replicates.library.biosample.genetic_modifications.modified_site_by_target_id',
        'replicates.library.biosample.part_of',
        'replicates.library.biosample.part_of.donor',
        'replicates.library.biosample.part_of.treatments',
        'replicates.library.biosample.treatments',
        'replicates.library.biosample.originated_from.biosample_ontology',
        'replicates.library.biosample.expressed_genes',
        'replicates.library.biosample.expressed_genes.gene',
        'replicates.library.construction_platform',
        'replicates.library.treatments',
        'possible_controls',
        'target.genes',
        'target.organism'
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
        'replicates': ('Replicate', 'experiment'),
        'related_series': ('Series', 'related_datasets'),
        'superseded_by': ('Experiment', 'supersedes'),
        'related_annotations': ('Annotation', 'experimental_input')
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
        "title": "Related annotations",
        "type": "array",
        "items": {
            "type": ['string', 'object'],
            "linkFrom": "Annotation.experimental_input",
        },
        "notSubmittable": True,
    })
    def related_annotations(self, request, related_annotations):
        return paths_filtered_by_status(request, related_annotations)

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

    @calculated_property(schema={
        "title": "Life stage and age summary",
        "description": "Life stage and age display summary to be used for the mouse development matrix.",
        "type": "string",
        "notSubmittable": True,
    })
    def life_stage_age(self, request, replicates=None):
        biosample_accessions = set()
        all_life_stage = set()
        all_age_display = set()
        life_stage_age = ''
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
                        if biosampleObject['accession'] not in biosample_accessions:
                            biosample_accessions.add(biosampleObject['accession'])
                            life_stage = biosampleObject.get('life_stage')
                            if life_stage:
                                all_life_stage.add(life_stage)
                            age_display = biosampleObject.get('age_display')
                            if age_display:
                                all_age_display.add(age_display)
        # Only return life_stage_age if all biosamples have the same life_stage and age_display
        if len(all_life_stage) == 1 and len(all_age_display) == 1:
            life_stage_age = ''.join(all_life_stage) + ' ' + ''.join(all_age_display)
            return life_stage_age

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
    
    human_donor_matrix = {
        'y': {    
            'group_by': ['replicates.library.biosample.donor.accession'],
            'label': 'Donor',
         },
        'x': {
            'group_by': [
                ('assay_title', 'n/a'),
                'replicates.library.biosample.disease_term_name',     
            ],
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

    immune_cells = {
        'y': {
            'group_by': ['biosample_ontology.cell_slims', 'biosample_ontology.term_name'],
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
            'group_by': ['biosample_ontology.classification', 'biosample_ontology.term_name', ('protein_tags.name', 'no_protein_tags')],
            'label': 'Term Name',
        },
    }

    deeply_profiled_uniform_batch_matrix = {
        'y': {
            'group_by': ['replicates.library.biosample.biosample_ontology.term_name', 'replicates.library.biosample.origin_batch'],
            'label': 'Biosample',
        },
        'x': {
            'group_by': ['assay_title', 'replicates.library.biosample.biosample_ontology.term_name', '@id'],
            'label': 'Assay',
        },
    }

    deeply_profiled_matrix = {
        'y': {
            'group_by': ['biosample_ontology.classification', 'biosample_ontology.term_name'],
            'label': 'Biosample',
        },
        'x': {
            'group_by': 'assay_title',
            'label': 'Assay',
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

    brain_matrix = {
        'y': {
            'group_by': [
                'replicates.library.biosample.donor.accession',
            ],
            'label': 'Donor',
        },
        'x': {
            'group_by': [
                ('assay_title'),
                ('target.label', 'no_target'),
                'replicates.library.biosample.donor.age',
                'replicates.library.biosample.donor.sex',
                'replicates.library.biosample.biosample_ontology.term_name',
                'replicates.library.biosample.disease_term_name',
            ],
            'label': 'Assay',
        }
    }

    mouse_development = {
        'y': {
            'group_by': ['biosample_ontology.term_name', 'life_stage_age'],
            'label': 'Biosample',
        },
        'x': {
            'group_by': ['assay_title', 'target.label'],
            'label': 'Assay',
        },
    }

    encore_matrix = {
        'y': {
            'group_by': ['target.label'],
            'label': 'Target',
        },
        'x': {
            'group_by': ['assay_title', 'biosample_ontology.term_name'],
            'label': 'Assay',
        },
    }

    encore_rna_seq_matrix = {
        'y': {
            'group_by': [('replicates.library.biosample.subcellular_fraction_term_name', 'no_term_name')],
            'label': 'Subcellular localization',
        },
        'x': {
            'group_by': ['assay_title', 'biosample_ontology.term_name'],
            'label': 'Assay',
        },
    }

    degron_matrix = {
        'y': {
            'group_by': ['replicates.library.biosample.genetic_modifications.modified_site_by_target_id.label'],
            'label': 'Degron target',
        },
        'x': {
            'group_by': ['assay_title', ('target.label', 'no_target')],
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
