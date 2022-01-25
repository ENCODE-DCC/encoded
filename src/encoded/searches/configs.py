from snovault.elasticsearch.searches.interfaces import SEARCH_CONFIG
from snovault.elasticsearch.searches.configs import search_config


def includeme(config):
    config.scan(__name__)
    config.registry[SEARCH_CONFIG].add_aliases(ALIASES)
    config.registry[SEARCH_CONFIG].add_defaults(DEFAULTS)


@search_config(
    name='custom'
)
def custom_search_config():
    return {
        'facets': {
            'assay_title': {
                'title': 'Assay title',
                'type': 'typeahead',
                'open_on_load': True
            },
            'status': {
                'title': 'Status',
                'open_on_load': True
            },
            'target.label': {
                'title': 'Target of assay',
                'type': 'typeahead',
                'length': 'long',
                'open_on_load': True
            },
            'biosample_ontology.term_name' : {
                'title': 'Biosample term name',
                'type': 'typeahead',
                'length': 'long',
                'open_on_load': True
            },
        },
        'columns': {},
        'matrix': {},
        'boost_values': {},
        'fields': {},
    }


@search_config(
    name='immune'
)
def immune_search_config():
    return {
        'facets': {
            "replicates.library.biosample.disease_term_name": {
                "title": "Disease",
                "open_on_load": True
            },
            "biosample_ontology.term_name" : {
                "title": "Biosample",
                "type": "typeahead",
                "length": "long",
                "open_on_load": True
            },
        },
    }


@search_config(
    name='custom-matrix'
)
def custom_matrix_config():
    return {
        'matrix': {
            'y': {
                'group_by': [
                    'award.rfa',
                    'lab.title',
                ],
                'label': 'Lab',
            },
            'x': {
                'group_by': 'assay_title',
                'label': 'Assay',
            }
        }
    }


@search_config(
    name='custom-columns'
)
def custom_columns_config():
    return {
        'columns': {
            'award.rfa': {
                'title': 'Project',
            },
            'assay_title': {
                'title': 'Assay',
            },
            'lab.title': {
                'title': 'Lab',
            },
            'assembly': {
                'title': 'Assembly',
            },
            'status': {
                'title': 'Status',
            },
        }
    }


# To allow FunctionalCharacterizationSeries columns properties to pass through for the search:
# type=FunctionalCharacterizationExperiment&type=FunctionalCharacterizationSeries&type=TransgenicEnhancerExperiment
# with effectively the FunctionalCharacterizationExperiment config.
@search_config(
    name='FunctionalCharacterization'
)
def functional_characterization_data_view():
    return {
        'facets': {
            'assay_slims': {
                'title': 'Assay type'
            },
            'assay_title': {
                'title': 'Assay title',
                'open_on_load': True
            },
            'status': {
                'title': 'Status',
                'open_on_load': True
            },
            'elements_references.examined_loci.symbol': {
                'title': 'Targeted loci',
                'type': 'typeahead',
                'open_on_load': True
            },
            'elements_references.elements_selection_method': {
                'title': 'Elements selection method'
            },
            'elements_references.crispr_screen_tiling': {
                'title': 'CRISPR screen tiling'
            },
            'examined_loci.gene.symbol': {
                'title': 'Examined loci',
                'type': 'typeahead',
                'open_on_load': True
            },
            'biosamples.applied_modifications.guide_type': {
                'title': 'Guide type'
            },
            'biosamples.applied_modifications.reagents.promoter_details': {
                'title': 'Promoter details'
            },
            'biosamples.applied_modifications.MOI': {
                'title': 'Multiplicity of infection'
            },
            'biosamples.donor.organism.scientific_name': {
                'title': 'Organism',
                'open_on_load': True
            },
            'biosamples.life_stage': {
            'replicates.library.biosample.sex': {
                'title': 'Sex',
                'type': 'typeahead'
            },
            'replicates.library.biosample.life_stage': {
                'title': 'Life stage'
            },
            'biosample_ontology.classification': {
                'title': 'Biosample classification'
            },
            'biosample_ontology.term_name' : {
                'title': 'Biosample',
                'type': 'typeahead',
                'length': 'long',
                'open_on_load': True
            },
            'biosample_ontology.organ_slims': {
                'title': 'Organ',
                'type': 'typeahead'
            },
            'biosample_ontology.cell_slims': {
                'title': 'Cell',
                'type': 'typeahead'
            },
            'biosamples.disease_term_name': {
                'title': 'Disease'
            },
            'biosamples.treatments.treatment_term_name': {
                'title': 'Biosample treatment'
            },
            'control_type': {
                'type': 'exists',
                'title': 'Hide control experiments'
            },
            'award.project': {
                'title': 'Project'
            },
            'assembly': {
                'title': 'Genome assembly'
            },
            'files.file_type': {
                'title': 'Available file types'
            },
            'date_released': {
                'title': 'Date released'
            },
            'date_submitted': {
                'title': 'Date submitted'
            },
            'lab.title': {
                'title': 'Lab'
            }
        },
        'facet_groups': [
            {
                'title': 'Assay',
                'facet_fields': [
                    'assay_slims',
                    'assay_title',
                    'control_type',
                    'elements_references.crispr_screen_tiling',
                    'biosamples.applied_modifications.guide_type',
                    'biosamples.applied_modifications.MOI',
                    'biosamples.applied_modifications.reagents.promoter_details'
                ]
            },
            {
                'title': 'Elements',
                'facet_fields': [
                    'elements_references.examined_loci.symbol',
                    'examined_loci.gene.symbol',
                    'elements_references.elements_selection_method'
                ]
            },
            {
                'title': 'Biosample',
                'facet_fields': [
                    'biosamples.donor.organism.scientific_name',
                    'biosample_ontology.term_name',
                    'biosample_ontology.classification',
                    'biosample_ontology.organ_slims',
                    'biosample_ontology.cell_slims',
                    'biosamples.life_stage',
                    'biosamples.treatments.treatment_term_name',
                    'biosamples.disease_term_name'
                    'replicates.library.biosample.sex',
                    'replicates.library.biosample.life_stage',
                    'replicates.library.biosample.treatments.treatment_term_name',
                    'replicates.library.biosample.disease_term_name'
                ]
            },
            {
                'title': 'Analysis',
                'facet_fields': [
                    'assembly',
                    'files.file_type'
                ]
            },
            {
                'title': 'Provenance',
                'facet_fields': [
                    'award.project',
                    'lab.title',
                    'date_submitted',
                    'date_released'
                ]
            },
            {
                'title': 'Quality',
                'facet_fields': [
                    'status',
                    'audit.ERROR.category',
                    'audit.NOT_COMPLIANT.category',
                    'audit.WARNING.category',
                    'audit.INTERNAL_ACTION.category'
                ]
            }
        ]
    }
    

@search_config(
    name='HumanDonorMatrix'
)
def human_donor_data_view():
    return {
        'facets': {
            'assay_title': {
                'title': 'Assay title',
                'type': 'typeahead',
                'open_on_load': True
            },
            'status': {
                'title': 'Status',
                'open_on_load': True
            },
            'target.label': {
                'title': 'Target of assay',
                'type': 'typeahead',
                'length': 'long',
                'open_on_load': True
            },
            'biosample_ontology.term_name' : {
                'title': 'Biosample',
                'type': 'typeahead',
                'length': 'long',
                'open_on_load': True
            },
            'replicates.library.biosample.sex': {
                'title': 'Sex',
                'type': 'typeahead'
            },
            'biosample_ontology.organ_slims': {
                'title': 'Organ',
                'type': 'typeahead'
            },
            'biosample_ontology.cell_slims': {
                'title': 'Cell',
                'type': 'typeahead'
            },
            "biosample_ontology.system_slims": {
                "title": "Systems"
            },
            'replicates.library.biosample.life_stage': {
                'title': 'Life stage'
            },
            'replicates.library.biosample.disease_term_name': {
                'title': 'Disease'
            },
            'award.project': {
                'title': 'Project'
            },
            'lab.title': {
                'title': 'Lab'
            },
        },
        'columns': {},
        'matrix': {},
        'boost_values': {},
        'fields': {},
    }


ALIASES = {
    'DonorSubtypes': [
        'HumanDonor',
        'FlyDonor',
        'WormDonor',
        'MouseDonor',
    ]
}


DEFAULTS = {
    ('Experiment', 'FunctionalCharacterizationExperiment'): ['Experiment'],
}
