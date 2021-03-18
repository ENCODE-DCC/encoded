from pyramid.traversal import find_root
from snovault import (
    calculated_property,
    collection,
    load_schema,
)
from .base import (
    paths_filtered_by_status
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
    name='low-throughput-single-cell-experiments',
    unique_key='accession',
    properties={
        'title': 'Low throughput single cell experiments',
        'description': 'Listing of Low Throughput Single Cell Experiments',
    })
class LowThroughputSingleCellExperiment(
    Dataset,
    CalculatedAssaySynonyms,
    CalculatedAssayTermID,
    CalculatedVisualize,
    CalculatedBiosampleSummary,
    CalculatedReplicates,
    CalculatedAssaySlims,
    CalculatedAssayTitle,
    CalculatedCategorySlims,
    CalculatedTypeSlims,
    CalculatedObjectiveSlims):
    item_type = 'low_throughput_single_cell_experiment'
    schema = load_schema('encoded:schemas/low_throughput_single_cell_experiment.json')
    embedded = [
        'submitted_by',
        'lab',
        'award.pi.lab',
        'biosample_ontology',       
        'related_series',
        'possible_controls',
        'target.genes',
        'target.organism',
    ]
    audit_inherit = [
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
        'related_series': ('Series', 'related_datasets'),
        'replicates': ('Replicate', 'experiment'),
        'superseded_by': ('LowThroughputSingleCellExperiment', 'supersedes')
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
                "linkFrom": "LowThroughputSingleCellExperiment.supersedes",
            },
            "notSubmittable": True,
    })
    def superseded_by(self, request, superseded_by):
        return paths_filtered_by_status(request, superseded_by)