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
                "open_on_load": True
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
                "open_on_load": True
            },
        },
        'columns': {},
        'matrix': {},
        'boost_values': {},
        'fields': {},
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


@search_config(
    name='FCC'
)
def functional_characterization_data_view():
    return {
        'facets': {
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
            'perturbation_type': {
                'title': 'Perturbation type'
            },
            'replicates.library.biosample.applied_modifications.guide_type': {
                'title': 'Guide type'
            },
            'crispr_screen_readout': {
                'title': 'CRISPR screen readout'
            },
            'replicates.library.biosample.applied_modifications.reagents.promoter_details': {
                'title': 'Promoter details'
            },
            'replicates.library.biosample.applied_modifications.MOI': {
                'title': 'Multiplicity of infection'
            },
            'replicates.library.biosample.donor.organism.scientific_name': {
                'title': 'Organism',
                'open_on_load': True
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
            'replicates.library.biosample.disease_term_name': {
                'title': 'Disease'
            },
            'replicates.library.biosample.treatments.treatment_term_name': {
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
            'files.platform.term_name': {
                'title': 'Platform'
            },
            'replicates.library.nucleic_acid_term_name': {
                'title': 'Library material'
            },
            'date_released': {
                'title': 'Date released'
            },
            'date_submitted': {
                'title': 'Date submitted'
            },
            'lab.title': {
                'title': 'Lab'
            },
            'replication_type': {
                'title': 'Replication type'
            },
            'replicates.library.biosample.subcellular_fraction_term_name': {
                'title': 'Cellular component'
            },
            'replicates.library.construction_platform.term_name': {
                'title': 'Library construction platform'
            }
        },
        'facet_groups': [
            {
                'title': 'Assay',
                'facet_fields': [
                    'assay_slims',
                    'assay_title',
                    'control_type',
                    'perturbation_type',
                    'examined_loci.expression_measurement_method',
                    'crispr_screen_return eadout',
                    'elements_references.crispr_screen_tiling',
                    'replicates.library.biosample.applied_modifications.guide_type',
                    'replicates.library.biosample.applied_modifications.MOI',
                    'replicates.library.biosample.applied_modifications.reagents.promoter_details',
                    'replicates.library.construction_platform.term_name'
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
                    'replicates.library.biosample.donor.organism.scientific_name',
                    'biosample_ontology.term_name',
                    'biosample_ontology.classification',
                    'biosample_ontology.organ_slims',
                    'biosample_ontology.cell_slims',
                    'replicates.library.biosample.life_stage',
                    'replicates.library.biosample.treatments.treatment_term_name',
                    'replicates.library.biosample.disease_term_name',
                    'replicates.library.nucleic_acid_term_name'
                ]
            },
            {
                'title': 'Analysis',
                'facet_fields': [
                    'files.platform.term_name',
                    'files.run_type',
                    'assembly',
                    'files.file_type'
                ]
            },
            {
                'title': 'Provenance',
                'facet_fields': [
                    'award.project',
                    'award.rfa',
                    'lab.title',
                    'date_submitted',
                    'date_released'
                ]
            },
            {
                'title': 'Quality',
                'facet_fields': [
                    'replication_type',
                    'replicates.library.size_range',
                    'files.read_length',
                    'files.mapped_read_length',
                    'status',
                    'internal_status',
                    'audit.ERROR.category',
                    'audit.NOT_COMPLIANT.category',
                    'audit.WARNING.category',
                    'audit.INTERNAL_ACTION.category'
                ]
            }
        ]
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
    'Donor': ['DonorSubtypes'],
    ('Experiment', 'FunctionalCharacterizationExperiment'): ['Experiment'],
}
